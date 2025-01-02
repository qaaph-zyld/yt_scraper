import pytest
import os
import sys
from pathlib import Path
import time

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper.youtube_api import YouTubeAPI

@pytest.fixture
def youtube_api(tmp_path):
    """Create a YouTubeAPI instance with a temporary data directory."""
    return YouTubeAPI(data_dir=str(tmp_path))

def test_api_initialization(youtube_api):
    """Test that the API client initializes correctly with valid credentials."""
    assert youtube_api.api_key is not None
    assert youtube_api.youtube is not None
    assert youtube_api.data_manager is not None
    assert youtube_api.rate_limiter is not None

def test_get_video_metadata_with_storage(youtube_api):
    """Test fetching and storing metadata for a known video."""
    video_id = "dQw4w9WgXcQ"  # Never Gonna Give You Up
    metadata = youtube_api.get_video_metadata(video_id)
    
    assert metadata is not None
    assert metadata['id'] == video_id
    assert 'title' in metadata
    assert 'view_count' in metadata
    assert 'like_count' in metadata
    assert 'comment_count' in metadata
    
    # Verify that the metadata was saved
    video_dir = Path(youtube_api.data_manager.base_dir) / 'videos'
    saved_files = list(video_dir.glob(f"{video_id}_*.json"))
    assert len(saved_files) > 0

def test_search_videos_with_storage(youtube_api):
    """Test searching for videos and storing their metadata."""
    query = "Python programming"
    videos = youtube_api.search_videos(query, max_results=2)
    
    assert isinstance(videos, list)
    assert len(videos) <= 2
    if videos:
        assert 'id' in videos[0]
        assert 'title' in videos[0]
        
        # Verify that the metadata was saved
        video_dir = Path(youtube_api.data_manager.base_dir) / 'videos'
        saved_files = list(video_dir.glob(f"{videos[0]['id']}_*.json"))
        assert len(saved_files) > 0

def test_get_comments_with_storage(youtube_api):
    """Test fetching and storing comments for a known video."""
    video_id = "dQw4w9WgXcQ"
    comments = youtube_api.get_video_comments(video_id, max_results=5)
    
    assert isinstance(comments, list)
    assert len(comments) <= 5
    
    if comments:
        # Verify comment structure
        comment = comments[0]
        assert 'author' in comment
        assert 'text' in comment
        assert 'like_count' in comment
        assert 'published_at' in comment
        assert 'replies' in comment
        
        # Verify that the comments were saved
        comments_dir = Path(youtube_api.data_manager.base_dir) / 'comments'
        saved_files = list(comments_dir.glob(f"{video_id}_comments_*.json"))
        assert len(saved_files) > 0

def test_rate_limiting(youtube_api):
    """Test that rate limiting is enforced."""
    video_id = "dQw4w9WgXcQ"
    
    # Get initial quota status
    initial_status = youtube_api.get_quota_status()
    assert 'queries_per_second' in initial_status
    
    # Make multiple requests quickly to trigger rate limiting
    responses = []
    for _ in range(15):  # More than our per-second quota
        response = youtube_api.get_video_metadata(video_id, save=False)
        responses.append(response is not None)
    
    # Some requests should have failed due to rate limiting
    assert False in responses
    
    # Wait for rate limit to reset
    time.sleep(1.1)
    
    # Should be able to make requests again
    assert youtube_api.get_video_metadata(video_id, save=False) is not None

def test_quota_costs(youtube_api):
    """Test that different operations have different quota costs."""
    # Search operation should use more quota than list operation
    initial_status = youtube_api.get_quota_status()
    
    # Perform a search (high cost)
    youtube_api.search_videos("test", max_results=1)
    after_search = youtube_api.get_quota_status()
    
    # Perform a list operation (low cost)
    youtube_api.get_video_metadata("dQw4w9WgXcQ")
    after_list = youtube_api.get_quota_status()
    
    # Search should use more quota than list
    search_cost = (initial_status['queries_per_day']['available_tokens'] - 
                  after_search['queries_per_day']['available_tokens'])
    list_cost = (after_search['queries_per_day']['available_tokens'] - 
                after_list['queries_per_day']['available_tokens'])
    assert search_cost > list_cost
