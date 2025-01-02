import pytest
import os
import sys
from datetime import datetime, timezone
import matplotlib.pyplot as plt

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.visualization import YouTubeVisualizer

@pytest.fixture
def visualizer():
    """Create YouTubeVisualizer instance with test output directory."""
    test_output_dir = "test_visualizations"
    return YouTubeVisualizer(output_dir=test_output_dir)

@pytest.fixture
def sample_metadata():
    """Create sample video metadata."""
    return {
        'id': 'test123',
        'title': 'Test Video Title',
        'description': 'This is a test video description',
        'published_at': '2025-01-01T00:00:00Z',
        'view_count': 1000,
        'like_count': 100,
        'comment_count': 50
    }

@pytest.fixture
def sample_comments():
    """Create sample comments."""
    return [
        {
            'author': 'User1',
            'text': 'Great video!',
            'like_count': 10,
            'published_at': '2025-01-01T01:00:00Z',
            'replies': []
        },
        {
            'author': 'User2',
            'text': 'Not so good.',
            'like_count': 5,
            'published_at': '2025-01-01T02:00:00Z',
            'replies': []
        }
    ]

@pytest.fixture
def sample_sentiment_data():
    """Create sample sentiment analysis data."""
    return {
        'overall_sentiment': 'positive',
        'sentiment_stats': {
            'positive': 60,
            'neutral': 30,
            'negative': 10
        },
        'average_polarity': 0.3
    }

@pytest.fixture
def sample_trends():
    """Create sample keyword trends data."""
    return {
        'title_trends': [
            {'word': 'python', 'count': 5},
            {'word': 'tutorial', 'count': 3},
            {'word': 'programming', 'count': 2}
        ],
        'description_trends': [
            {'word': 'learn', 'count': 4},
            {'word': 'code', 'count': 3},
            {'word': 'basics', 'count': 2}
        ]
    }

def test_plot_engagement_metrics(visualizer, sample_metadata):
    """Test engagement metrics visualization."""
    filepath = visualizer.plot_engagement_metrics(sample_metadata)
    assert os.path.exists(filepath)
    assert filepath.endswith('.png')
    
    # Test without saving
    result = visualizer.plot_engagement_metrics(sample_metadata, save=False)
    assert result == ""

def test_plot_sentiment_distribution(visualizer, sample_sentiment_data):
    """Test sentiment distribution visualization."""
    filepath = visualizer.plot_sentiment_distribution(sample_sentiment_data)
    assert os.path.exists(filepath)
    assert filepath.endswith('.png')
    
    # Test without saving
    result = visualizer.plot_sentiment_distribution(sample_sentiment_data, save=False)
    assert result == ""

def test_plot_comment_activity(visualizer, sample_comments):
    """Test comment activity visualization."""
    filepath = visualizer.plot_comment_activity(sample_comments)
    assert os.path.exists(filepath)
    assert filepath.endswith('.png')
    
    # Test without saving
    result = visualizer.plot_comment_activity(sample_comments, save=False)
    assert result == ""

def test_plot_keyword_trends(visualizer, sample_trends):
    """Test keyword trends visualization."""
    filepath = visualizer.plot_keyword_trends(sample_trends)
    assert os.path.exists(filepath)
    assert filepath.endswith('.png')
    
    # Test without saving
    result = visualizer.plot_keyword_trends(sample_trends, save=False)
    assert result == ""

def test_create_dashboard(visualizer, sample_metadata, sample_comments,
                        sample_sentiment_data, sample_trends):
    """Test dashboard creation."""
    filepath = visualizer.create_dashboard(
        sample_metadata,
        sample_comments,
        sample_sentiment_data,
        sample_trends
    )
    assert os.path.exists(filepath)
    assert filepath.endswith('.png')

def test_invalid_data_handling(visualizer):
    """Test handling of invalid data."""
    # Test with empty metadata
    empty_metadata = {
        'id': '',
        'title': '',
        'description': '',
        'published_at': '2025-01-01T00:00:00Z',
        'view_count': 0,
        'like_count': 0,
        'comment_count': 0
    }
    result = visualizer.plot_engagement_metrics(empty_metadata)
    assert os.path.exists(result)
    
    # Test with empty comments
    result = visualizer.plot_comment_activity([])
    assert result == ""
    
    # Test with empty trends
    empty_trends = {'title_trends': [], 'description_trends': []}
    result = visualizer.plot_keyword_trends(empty_trends)
    assert result == ""

@pytest.fixture(autouse=True)
def cleanup():
    """Clean up test files after each test."""
    yield
    test_output_dir = "test_visualizations"
    if os.path.exists(test_output_dir):
        for file in os.listdir(test_output_dir):
            os.remove(os.path.join(test_output_dir, file))
        os.rmdir(test_output_dir)
