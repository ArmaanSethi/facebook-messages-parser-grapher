import emoji
import pandas as pd
from typing import Dict, Any, List
from collections import Counter

class MessageAnalytics:
    """Calculates advanced metrics for conversation DataFrames."""
    
    def extract_top_emojis(self, df: pd.DataFrame, top_n: int = 10) -> Dict[str, List[tuple]]:
        """Finds most used emojis per sender."""
        if df.empty or 'content' not in df.columns:
            return {}
            
        emoji_counts = {}
        
        # Filter strictly for messages with content
        # Note: We rely on the 'emoji' library to extract
        senders = df['sender'].unique()
        
        for sender in senders:
            sender_msgs = df[df['sender'] == sender]['content'].dropna()
            all_text = " ".join(sender_msgs.astype(str))
            
            # Extract all emojis
            emojis_list = [c['emoji'] for c in emoji.emoji_list(all_text)]
            
            # Count
            emoji_counts[sender] = Counter(emojis_list).most_common(top_n)
            
        return emoji_counts

    def analyze_reactions(self, messages_stream: List[Dict]) -> Dict[str, Any]:
        """Parses raw message stream to find who reacts to whom.
        
        Returns:
            Dict with 'global' reaction map and 'per_conv' reaction maps
        """
        global_map = {}  # {reactor: {target_sender: count}}
        per_conv = {}    # {conv_title: {reactor: {target_sender: count}}}
        
        for msg in messages_stream:
            target_sender = msg.get('sender_name')
            conv_title = msg.get('conv_title', 'Unknown')
            if not target_sender:
                continue
                
            for reaction in msg.get('reactions', []):
                reactor = reaction.get('actor')
                if not reactor:
                    continue
                
                # Update global map
                if reactor not in global_map:
                    global_map[reactor] = {}
                global_map[reactor][target_sender] = global_map[reactor].get(target_sender, 0) + 1
                
                # Update per-conversation map
                if conv_title not in per_conv:
                    per_conv[conv_title] = {}
                if reactor not in per_conv[conv_title]:
                    per_conv[conv_title][reactor] = {}
                per_conv[conv_title][reactor][target_sender] = per_conv[conv_title][reactor].get(target_sender, 0) + 1
                
        return {'global': global_map, 'per_conv': per_conv}

    def calculate_response_times(self, df: pd.DataFrame, my_name: str) -> Dict[str, float]:
        """Calculates median response times for you vs them."""
        if df.empty or 'sender' not in df.columns:
            return {}
        
        # Copy to avoid mutating caller's DataFrame
        df = df.copy().sort_values('timestamp')
        df['prev_sender'] = df['sender'].shift(1)
        df['prev_timestamp'] = df['timestamp'].shift(1)
        
        # Identify replies: sender != prev_sender
        replies = df[df['sender'] != df['prev_sender']].copy()
        
        # Calculate time delta in minutes
        replies['time_diff'] = (replies['timestamp'] - replies['prev_timestamp']).dt.total_seconds() / 60
        
        # Filter out sessions > 12 hours (likely not a "reply" but a new convo)
        replies = replies[replies['time_diff'] < 720] # 12 hours
        
        my_replies = replies[replies['sender'] == my_name]
        their_replies = replies[replies['sender'] != my_name]
        
        return {
            'my_median_reply_minutes': round(my_replies['time_diff'].median(), 2) if not my_replies.empty else 0,
            'their_median_reply_minutes': round(their_replies['time_diff'].median(), 2) if not their_replies.empty else 0
        }

    def calculate_initiation_rate(self, df: pd.DataFrame, my_name: str, gap_hours: int = 4) -> Dict[str, float]:
        """Calculates who 'activates' the conversation after a silence."""
        if df.empty:
            return {}
        
        # Copy to avoid mutating caller's DataFrame
        df = df.copy().sort_values('timestamp')
        df['time_diff_hours'] = (df['timestamp'] - df['timestamp'].shift(1)).dt.total_seconds() / 3600
        
        # An initiation is a message sent after 'gap_hours' of silence, OR the very first message
        initiations = df[(df['time_diff_hours'] > gap_hours) | (df['time_diff_hours'].isna())]
        
        total_initiations = len(initiations)
        if total_initiations == 0:
            return {}
            
        my_initiations = len(initiations[initiations['sender'] == my_name])
        
        return {
            'my_initiation_pct': round((my_initiations / total_initiations) * 100, 1),
            'their_initiation_pct': round(((total_initiations - my_initiations) / total_initiations) * 100, 1),
            'total_conversations_started': total_initiations
        }

    def get_hourly_activity(self, df: pd.DataFrame) -> Dict[int, int]:
        """Returns message count by hour of day (0-23)."""
        return df['hour'].value_counts().sort_index().to_dict()

# Verification block
if __name__ == "__main__":
    from processor import MessageProcessor
    # Mock data again
    mock_data = [
        {"sender_name": "Armaan", "timestamp_ms": 1672531200000, "content": "Start 🍕", "type": "Generic"},
        {"sender_name": "Jane", "timestamp_ms": 1672531320000, "content": "Reply 😂 😂", "type": "Generic", "reactions": [{"actor": "Armaan", "reaction": "❤️"}]},
    ]
    
    proc = MessageProcessor()
    df = proc.process_messages(mock_data)
    
    analytics = MessageAnalytics()
    print("Emojis:", analytics.extract_top_emojis(df))
    print("Reactions:", analytics.analyze_reactions(mock_data))
