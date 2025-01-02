import pytest
import os
import sys
import shutil
from unittest.mock import Mock, patch
from datetime import datetime

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import YouTubeDataApp

@pytest.fixture
def app():
    """Create YouTubeDataApp instance with test directories."""
    test_data_dir = "test_data"
    test_viz_dir = "test_visualizations"
    
    # Create test instance
    app = YouTubeDataApp(test_data_dir, test_viz_dir)
    
    yield app
    
    # Cleanup test directories
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    if os.path.exists(test_viz_dir):
        shutil.rmtree(test_viz_dir)

@pytest.fixture
def mock_video_data():
    """Create mock video data."""
    return {
        'id': 'test123',
        'title': 'Test Video',
        'description': 'Test Description',
        'published_at': '2025-01-01T00:00:00Z',
        'view_count': 1000,
        'like_count': 100,
        'comment_count': 50
    }

@pytest.fixture
def mock_comments():
    """Create mock comments."""
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

def test_app_initialization(app):
    """Test application initialization."""
    assert os.path.exists(app.data_manager.data_dir)
    assert os.path.exists(app.visualizer.output_dir)

@patch('src.scraper.YouTubeAPI.get_video_metadata')
@patch('src.scraper.YouTubeAPI.get_video_comments')
def test_analyze_video(mock_get_comments, mock_get_metadata, app, mock_video_data, mock_comments):
    """Test video analysis functionality."""
    # Setup mocks
    mock_get_metadata.return_value = mock_video_data
    mock_get_comments.return_value = mock_comments
    
    # Perform analysis
    result = app.analyze_video('test123', save_visualizations=True)
    
    # Verify analysis results
    assert result['video_id'] == 'test123'
    assert result['title'] == 'Test Video'
    assert 'analysis_timestamp' in result
    assert 'performance_metrics' in result
    assert 'sentiment_analysis' in result
    assert result['total_comments'] == len(mock_comments)
    assert 'visualization_paths' in result
    
    # Verify visualization files were created
    viz_paths = result['visualization_paths']
    for path in viz_paths.values():
        assert os.path.exists(path)

@patch('src.scraper.YouTubeAPI.search_videos')
def test_analyze_topic(mock_search_videos, app, mock_video_data):
    """Test topic analysis functionality."""
    # Setup mock
    mock_search_videos.return_value = [mock_video_data]
    
    # Mock analyze_video method
    original_analyze_video = app.analyze_video
    app.analyze_video = Mock(return_value={
        'video_id': 'test123',
        'title': 'Test Video',
        'analysis_timestamp': datetime.now().isoformat(),
        'performance_metrics': {},
        'sentiment_analysis': {},
        'total_comments': 2
    })
    
    # Perform analysis
    result = app.analyze_topic('test query', max_videos=1)
    
    # Restore original method
    app.analyze_video = original_analyze_video
    
    # Verify analysis results
    assert result['search_query'] == 'test query'
    assert 'analysis_timestamp' in result
    assert result['videos_analyzed'] == 1
    assert 'keyword_trends' in result
    assert 'video_analyses' in result
    assert len(result['video_analyses']) == 1

def test_invalid_video_id(app):
    """Test handling of invalid video ID."""
    result = app.analyze_video('')
    assert result == {}

@patch('src.scraper.YouTubeAPI.search_videos')
def test_empty_search_results(mock_search_videos, app):
    """Test handling of empty search results."""
    mock_search_videos.return_value = []
    result = app.analyze_topic('nonexistent topic')
    assert result == {}

def test_get_quota_status(app):
    """Test quota status retrieval."""
    status = app.get_quota_status()
    assert isinstance(status, dict)

@pytest.mark.parametrize("test_input,expected", [
    ({'mode': 'video', 'id': 'test123'}, True),
    ({'mode': 'topic', 'query': 'test'}, True),
    ({'mode': 'video'}, False),  # Missing ID
    ({'mode': 'topic'}, False),  # Missing query
])
def test_command_line_args(test_input, expected, app, capsys):
    """Test command line argument handling."""
    with patch('sys.argv', ['script'] + [f'--{k}={v}' for k, v in test_input.items()]):
        try:
            from src.app import main
            main()
            captured = capsys.readouterr()
            assert (len(captured.out) > 0) == expected
        except SystemExit as e:
            assert (e.code == 0) == expected
