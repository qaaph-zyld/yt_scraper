import pytest
import os
import sys

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper.youtube_api import YouTubeAPI
from datetime import datetime

@pytest.fixture
def youtube_api():
    return YouTubeAPI()

def test_get_video_comments(youtube_api):
    """Test fetching comments for a known video."""
    video_id = "dQw4w9WgXcQ"  # Never Gonna Give You Up
    comments = youtube_api.get_video_comments(video_id, max_results=5)
    
    assert isinstance(comments, list)
    assert len(comments) <= 5
    
    if comments:
        comment = comments[0]
        assert 'author' in comment
        assert 'text' in comment
        assert 'like_count' in comment
        assert 'published_at' in comment
        assert 'reply_count' in comment
        assert 'replies' in comment
        assert isinstance(comment['replies'], list)

def test_comments_pagination(youtube_api):
    """Test comment pagination functionality."""
    video_id = "dQw4w9WgXcQ"
    max_results = 150
    comments = youtube_api.get_video_comments(video_id, max_results=max_results)
    
    assert isinstance(comments, list)
    assert len(comments) <= max_results

def test_disabled_comments(youtube_api):
    """Test handling of videos with disabled comments."""
    # Using a video ID that typically has comments disabled
    video_id = "invalid_video_id"
    comments = youtube_api.get_video_comments(video_id)
    
    assert isinstance(comments, list)
    assert len(comments) == 0
