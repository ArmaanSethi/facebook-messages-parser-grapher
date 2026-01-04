"""
Unit tests for Messenger Insights.
Run with: pytest tests/test_core.py -v
"""
import pytest
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from messenger_insights.processor import MessageProcessor
from messenger_insights.analytics import MessageAnalytics


# --- FIXTURES ---

@pytest.fixture
def sample_messages():
    """Sample message data for testing."""
    return [
        {"sender_name": "Alice", "timestamp_ms": 1672531200000, "content": "Hello 😀", "type": "Generic"},
        {"sender_name": "Bob", "timestamp_ms": 1672531260000, "content": "Hi there! 👋", "type": "Generic"},
        {"sender_name": "Alice", "timestamp_ms": 1672531320000, "content": "How are you?", "type": "Generic"},
        {"sender_name": "Bob", "timestamp_ms": 1672531380000, "content": "Great! 😂😂", "type": "Generic"},
    ]

@pytest.fixture
def sample_df(sample_messages):
    """Pre-processed DataFrame from sample messages."""
    proc = MessageProcessor()
    return proc.process_messages(sample_messages)


# --- PROCESSOR TESTS ---

class TestMessageProcessor:
    
    def test_process_messages_returns_dataframe(self, sample_messages):
        """Processor should return a pandas DataFrame."""
        proc = MessageProcessor()
        result = proc.process_messages(sample_messages)
        assert isinstance(result, pd.DataFrame)
    
    def test_process_messages_has_required_columns(self, sample_df):
        """DataFrame should have core columns."""
        required = ['timestamp', 'sender', 'content', 'word_count', 'date', 'hour']
        for col in required:
            assert col in sample_df.columns, f"Missing column: {col}"
    
    def test_process_messages_correct_count(self, sample_messages, sample_df):
        """DataFrame should have same row count as input."""
        assert len(sample_df) == len(sample_messages)
    
    def test_word_count_calculated(self, sample_df):
        """Word count should be calculated for each message."""
        # "Hello 😀" = 2 words
        assert sample_df['word_count'].iloc[0] == 2
        # "How are you?" = 3 words
        assert sample_df['word_count'].iloc[2] == 3
    
    def test_empty_input_returns_empty_df(self):
        """Empty input should return empty DataFrame."""
        proc = MessageProcessor()
        result = proc.process_messages([])
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


# --- ANALYTICS TESTS ---

class TestMessageAnalytics:
    
    def test_extract_emojis(self, sample_df):
        """Should extract emojis per sender."""
        analytics = MessageAnalytics()
        emoji_counts = analytics.extract_top_emojis(sample_df)
        
        assert 'Alice' in emoji_counts
        assert 'Bob' in emoji_counts
        # Bob has more emojis (👋, 😂, 😂)
        assert len(emoji_counts['Bob']) > 0
    
    def test_response_times_does_not_mutate(self, sample_df):
        """calculate_response_times should not mutate caller's DataFrame."""
        analytics = MessageAnalytics()
        original_cols = set(sample_df.columns)
        
        analytics.calculate_response_times(sample_df, my_name="Alice")
        
        # Original DataFrame should be unchanged
        assert set(sample_df.columns) == original_cols
        assert 'prev_sender' not in sample_df.columns
    
    def test_initiation_rate_does_not_mutate(self, sample_df):
        """calculate_initiation_rate should not mutate caller's DataFrame."""
        analytics = MessageAnalytics()
        original_cols = set(sample_df.columns)
        
        analytics.calculate_initiation_rate(sample_df, my_name="Alice")
        
        # Original DataFrame should be unchanged
        assert set(sample_df.columns) == original_cols
        assert 'time_diff_hours' not in sample_df.columns
    
    def test_analyze_reactions(self):
        """Should parse reaction data correctly."""
        analytics = MessageAnalytics()
        messages = [
            {"sender_name": "Alice", "reactions": [{"actor": "Bob", "reaction": "❤️"}]},
            {"sender_name": "Bob", "reactions": [{"actor": "Alice", "reaction": "😂"}]},
        ]
        result = analytics.analyze_reactions(messages)
        
        assert 'Bob' in result
        assert 'Alice' in result['Bob']
        assert result['Bob']['Alice'] == 1


# --- EDGE CASES ---

class TestEdgeCases:
    
    def test_empty_content(self):
        """Messages without content should not crash."""
        proc = MessageProcessor()
        messages = [
            {"sender_name": "Alice", "timestamp_ms": 1672531200000, "type": "Generic"},
        ]
        result = proc.process_messages(messages)
        assert len(result) == 1
        assert result['word_count'].iloc[0] == 0
    
    def test_unicode_content(self):
        """Unicode content should be handled correctly."""
        proc = MessageProcessor()
        messages = [
            {"sender_name": "Alice", "timestamp_ms": 1672531200000, "content": "مرحبا 你好 🌍", "type": "Generic"},
        ]
        result = proc.process_messages(messages)
        assert len(result) == 1
        assert result['content'].iloc[0] == "مرحبا 你好 🌍"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
