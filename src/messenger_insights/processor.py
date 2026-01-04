import pandas as pd
from typing import List, Dict, Any, Optional, Union, Generator
import pytz
from pathlib import Path

class MessageProcessor:
    """Converts raw message data into structured Pandas DataFrames for analysis (Batched)."""
    
    def __init__(self, timezone: str = "UTC"):
        self.timezone = pytz.timezone(timezone)

    def process_messages(self, messages: Union[List[Dict], Generator], batch_size: int = 50000) -> pd.DataFrame:
        """Converts a list or generator of message dicts into a clean DataFrame."""
        if isinstance(messages, list):
            return self._process_batch(messages)
            
        # Handle generator (streaming)
        all_dfs = []
        batch = []
        for msg in messages:
            batch.append(msg)
            if len(batch) >= batch_size:
                all_dfs.append(self._process_batch(batch))
                batch = []
        
        if batch:
            all_dfs.append(self._process_batch(batch))
            
        if not all_dfs:
             return pd.DataFrame(columns=['timestamp', 'sender', 'content', 'type', 'is_sender'])
             
        return pd.concat(all_dfs, ignore_index=True)

    def _process_batch(self, messages: List[Dict[str, Any]]) -> pd.DataFrame:
        """Internal method to process a single batch."""
        if not messages:
            return pd.DataFrame()

        df = pd.DataFrame(messages)
        
        # 1. Handle Timestamps
        # Facebook uses milliseconds for 'timestamp_ms'
        if 'timestamp_ms' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp_ms'], unit='ms').dt.tz_localize('UTC')
        elif 'timestamp' in df.columns:
             # Fallback for very old exports which used seconds
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s').dt.tz_localize('UTC')
            
        # Convert to User Timezone
        if self.timezone != pytz.UTC:
            df['timestamp'] = df['timestamp'].dt.tz_convert(self.timezone)

        # 2. Add Helper Columns
        df['date'] = df['timestamp'].dt.date
        df['hour'] = df['timestamp'].dt.hour
        df['year'] = df['timestamp'].dt.year
        df['month'] = df['timestamp'].dt.month_name()
        df['weekday'] = df['timestamp'].dt.day_name()
        
        # 3. Message Length (Words)
        def count_words(text):
            if isinstance(text, str):
                return len(text.split())
            return 0
            
        if 'content' in df.columns:
            df['word_count'] = df['content'].apply(count_words)
            # Create a character count too for efficiency
            df['char_count'] = df['content'].fillna("").apply(len)
        else:
            df['word_count'] = 0
            df['char_count'] = 0

        # Select & Rename Columns
        cols_to_keep = ['timestamp', 'sender_name', 'content', 'type', 'word_count', 'char_count', 'date', 'year', 'month', 'weekday', 'hour']
        # Only keep columns that actually exist in the data
        final_cols = [c for c in cols_to_keep if c in df.columns]
        
        return df[final_cols].rename(columns={'sender_name': 'sender'})

    def save_to_parquet(self, df: pd.DataFrame, file_path: Path):
        """Caches processed DataFrame to Parquet for instant reload."""
        try:
            # Ensure timestamp is timezone-aware or compatible
            df.to_parquet(file_path, index=False)
        except Exception as e:
            print(f"Warning: Could not save parquet cache: {e}")

    def prepare_frontend_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Prepares lightweight JSON-serializable data for client-side interactivity."""
        if df.empty:
            return {'daily_counts': [], 'detailed_activity': [], 'sender_colors': {}}
            
        # 1. Daily Message Counts (for Timeline & filtering)
        # We aggregate by Day and Sender to allow client-side filtering
        daily = df.groupby(['date', 'sender']).size().reset_index(name='count')
        daily['date'] = daily['date'].astype(str) # Serialize date
        
        # 2. Sender Color Mapping (consistent colors in UI)
        senders = df['sender'].unique().tolist()
        # Simple consistent palette generator
        palette = ['#BB86FC', '#03DAC6', '#CF6679', '#FFB74D', '#4FC3F7', '#90CAF9', '#A5D6A7']
        sender_colors = {s: palette[i % len(palette)] for i, s in enumerate(senders)}
        
        # 3. Hourly Activity (Pre-aggregated for performance)
        detailed_activity = df.groupby(['date', 'hour', 'weekday', 'sender']).size().reset_index(name='count')
        detailed_activity['date'] = detailed_activity['date'].astype(str)
        
        # 4. Reaction Matrix (Who reacts to whom) - Requires parsing 'reactions' content if accessible
        # Since 'reactions' might be a list-of-dicts nested in the raw stream, 
        # and we flattened it in the processor, we need to check if we kept it.
        # Current processor keeps 'content' and 'type'. 
        # To support reactions properly, we need to rely on the Analytics module passing it, 
        # or re-aggregate here if we have columns.
        # For this implementation, we will assume 'word_count' is available for Avg Length.
        
        avg_len = df.groupby('sender')['word_count'].mean().reset_index()
        avg_len['word_count'] = avg_len['word_count'].round(1)
        
        return {
            'daily_counts': daily.to_dict(orient='records'),
            'detailed_activity': detailed_activity.to_dict(orient='records'),
            'sender_colors': sender_colors,
            'avg_length': avg_len.to_dict(orient='records')
        }

    def load_from_parquet(self, file_path: Path) -> Optional[pd.DataFrame]:
        """Loads cached DataFrame if exists."""
        if file_path.exists():
            return pd.read_parquet(file_path)
        return None

    def get_conversation_stats(self, df: pd.DataFrame, my_name: Optional[str] = None) -> Dict[str, Any]:
        """Calculates basic stats for a conversation DataFrame."""
        if df.empty:
            return {}
            
        stats = {
            'total_messages': len(df),
            'first_message': df['timestamp'].min(),
            'last_message': df['timestamp'].max(),
            'duration_days': (df['timestamp'].max() - df['timestamp'].min()).days,
            'top_senders': df['sender'].value_counts().to_dict()
        }
        
        if my_name:
            my_msgs = df[df['sender'] == my_name]
            stats['messages_sent_by_me'] = len(my_msgs)
            stats['messages_received'] = len(df) - len(my_msgs)
            
        return stats

# Quick verification block
if __name__ == "__main__":
    # Mock date
    mock_data = [
        {"sender_name": "Armaan", "timestamp_ms": 1672531200000, "content": "Hello world", "type": "Generic"},
        {"sender_name": "Jane", "timestamp_ms": 1672531260000, "content": "Hi there!", "type": "Generic"},
        {"sender_name": "Armaan", "timestamp_ms": 1672531320000, "content": "How are you?", "type": "Generic"}
    ]
    
    processor = MessageProcessor(timezone="America/New_York")
    df = processor.process_messages(mock_data)
    
    print("\n--- DataFrame Head ---")
    print(df.head())
    
    print("\n--- Stats ---")
    stats = processor.get_conversation_stats(df, my_name="Armaan")
    print(stats)
