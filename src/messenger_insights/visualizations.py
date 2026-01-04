import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Optional

class MessageVisualizer:
    """Generates Plotly visualizations for message data."""
    
    # Cyberpunk / Modern Dark Palette
    COLORS = [
        '#BB86FC', # Purple
        '#03DAC6', # Teal
        '#CF6679', # Error Red / Pink
        '#FFB74D', # Orange
        '#4FC3F7', # Light Blue
    ]
    
    TEMPLATE = "plotly_dark"
    BG_COLOR = "rgba(0,0,0,0)" # Transparent to let Card background shine through
    FONT_FAMILY = "Inter, system-ui, sans-serif"

    def _apply_style(self, fig: go.Figure):
        """Applies consistent premium styling to any figure."""
        fig.update_layout(
            template=self.TEMPLATE,
            paper_bgcolor=self.BG_COLOR,
            plot_bgcolor=self.BG_COLOR,
            font=dict(family=self.FONT_FAMILY, size=12),
            title_font=dict(size=20, family=self.FONT_FAMILY),
            hoverlabel=dict(bgcolor="#333", font_size=12, font_family=self.FONT_FAMILY),
            margin=dict(l=40, r=40, t=60, b=40),
        )
        return fig

    def plot_timeline(self, df: pd.DataFrame) -> go.Figure:
        """Plots message volume over time with a range slider."""
        if df.empty:
            return go.Figure()
            
        # Resample to monthly frequency (using 'ME' as 'M' is deprecated)
        # For huge datasets, we might want to let user zoom, so we keep granular data or just stick to Month
        
        # Calculate global volume per month
        timeline = df.set_index('timestamp').resample('ME').size().reset_index(name='count')
        
        fig = px.area( # Area chart looks richer than line
            timeline, 
            x='timestamp', 
            y='count',
            title='Message Volume History',
            labels={'timestamp': 'Date', 'count': 'Messages'},
            color_discrete_sequence=[self.COLORS[0]] # Purple
        )
        
        # Add Range Slider for "Big & Interactive" feel
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                bgcolor="#333",
                activecolor="#555",
                buttons=list([
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            showgrid=False
        )
        fig.update_yaxes(showgrid=True, gridcolor="#333")
        
        return self._apply_style(fig)

    def plot_hourly_activity(self, df: pd.DataFrame) -> go.Figure:
        """Plots activity by hour of day."""
        hourly = df['hour'].value_counts().sort_index().reset_index()
        hourly.columns = ['hour', 'count']
        
        fig = px.bar(
            hourly, 
            x='hour', 
            y='count',
            title='Peak Chat Hours',
            labels={'hour': 'Hour', 'count': 'Messages'},
            color='count', # Gradient effect
            color_continuous_scale='Purples'
        )
        fig.update_xaxes(tickmode='linear', dtick=2, showgrid=False)
        fig.update_yaxes(showgrid=False)
        fig.update_layout(coloraxis_showscale=False) # Hide legend
        
        return self._apply_style(fig)

    def plot_activity_heatmap(self, df: pd.DataFrame) -> go.Figure:
        """Plots a GitHub-style activity heatmap (Day of Week vs Hour)."""
        # Group by Weekday and Hour
        activity = df.groupby(['weekday', 'hour']).size().reset_index(name='count')
        
        # Ensure correct order of weekdays
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        fig = go.Figure(data=go.Heatmap(
            x=activity['hour'],
            y=activity['weekday'],
            z=activity['count'],
            colorscale='Magma', # Better contrast than Viridis for dark mode
            hoverongaps=False,
            hovertemplate='<b>%{y} @ %{x}:00</b><br>Messages: %{z}<extra></extra>'
        ))
        
        fig.update_yaxes(categoryorder='array', categoryarray=days_order)
        fig.update_layout(title='Weekly Rhythm', xaxis_title='Hour', yaxis_title='')
        
        return self._apply_style(fig)

    def get_emoji_data(self, emoji_counts: dict) -> List[Dict]:
        """Returns raw emoji data list for client-side rendering."""
        data = []
        for sender, counts in emoji_counts.items():
            # Return ALL counts, let client slice top N
            for emoji_char, count in counts:
                data.append({'Sender': sender, 'Emoji': emoji_char, 'Count': count})
        return data

    def plot_emoji_stats(self, emoji_counts: dict, top_n: int = 10) -> go.Figure:
        """Plots top emojis per person (Static fallback)."""
        data = self.get_emoji_data(emoji_counts)
        # ... logic to filter top N locally for static plot ...
        # (Simplified for brevity as we are moving to JS)
        data_filtered = sorted(data, key=lambda x: x['Count'], reverse=True)[:top_n*2] 
        
        if not data_filtered:
            return go.Figure()
            
        df_emoji = pd.DataFrame(data_filtered)
        
        fig = px.bar(
            df_emoji, 
            x='Count', 
            y='Emoji', 
            color='Sender', 
            barmode='group',
            orientation='h',
            title=f'Top {top_n} Emojis',
            color_discrete_sequence=self.COLORS
        )
        
        fig.update_layout(yaxis=dict(autorange="reversed"))
        return self._apply_style(fig)

    def plot_initiation_pie(self, initiation_stats: dict) -> go.Figure:
        """Plots a donut chart of who started conversations."""
        if not initiation_stats:
            return go.Figure()
            
        labels = ['Me', 'Them']
        values = [initiation_stats.get('my_initiation_pct', 0), initiation_stats.get('their_initiation_pct', 0)]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values, 
            hole=.6, # Donut style
            marker=dict(colors=[self.COLORS[1], self.COLORS[2]]), # Teal vs Red
            hoverinfo='label+percent',
            textinfo='percent'
        )])
        
        fig.update_layout(title='Conversation Starters')
        return self._apply_style(fig)

# Verification block
if __name__ == "__main__":
    # Mock data pipeline again
    from processor import MessageProcessor
    from analytics import MessageAnalytics
    
    # 1. Mock Data
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    mock_data = []
    for d in dates:
        mock_data.append({"sender_name": "Armaan", "timestamp_ms": d.timestamp()*1000, "content": "Hi", "type": "Generic"})
        mock_data.append({"sender_name": "Jane", "timestamp_ms": (d + pd.Timedelta(hours=1)).timestamp()*1000, "content": "Hello", "type": "Generic"})
    
    # 2. Process
    proc = MessageProcessor()
    df = proc.process_messages(mock_data)
    
    # 3. Analyze
    analytics = MessageAnalytics()
    init_stats = analytics.calculate_initiation_rate(df, my_name="Armaan")
    # Mock emoji counts
    emoji_counts = {'Armaan': [('🍕', 5), ('🔥', 2)], 'Jane': [('😂', 10), ('❤️', 3)]}
    
    # 4. Visualize
    viz = MessageVisualizer()
    fig_timeline = viz.plot_timeline(df)
    print("Timeline Figure Generated:", fig_timeline.layout.title.text)
    
    fig_hourly = viz.plot_hourly_activity(df)
    print("Hourly Figure Generated:", fig_hourly.layout.title.text)
    
    fig_heatmap = viz.plot_activity_heatmap(df)
    print("Heatmap Figure Generated:", fig_heatmap.layout.title.text)
    
    fig_emoji = viz.plot_emoji_stats(emoji_counts)
    print("Emoji Figure Generated:", fig_emoji.layout.title.text)
    
    fig_pie = viz.plot_initiation_pie(init_stats)
    print("Pie Figure Generated:", fig_pie.layout.title.text)
