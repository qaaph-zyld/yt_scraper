"""
Common test fixtures and configuration for pytest.
"""

import os
import sys
import pytest
from datetime import datetime, timedelta

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

@pytest.fixture
def sample_video_metadata():
    """Provide sample video metadata for testing."""
    return {
        'id': 'test_video_id',
        'title': 'Test Video Title',
        'description': 'This is a test video description with some keywords and content.',
        'published_at': (datetime.now() - timedelta(days=7)).isoformat() + 'Z',
        'view_count': '1000',
        'like_count': '100',
        'comment_count': '50',
        'duration': 'PT5M30S',
        'channel_id': 'test_channel_id',
        'channel_title': 'Test Channel',
        'tags': ['test', 'video', 'sample'],
        'category_id': '22'
    }

@pytest.fixture
def sample_comments():
    """Provide sample comments for testing."""
    return [
        {
            'id': 'comment1',
            'text': 'This video is amazing! Really helpful content.',
            'author': 'User1',
            'like_count': '10',
            'reply_count': '2',
            'published_at': datetime.now().isoformat()
        },
        {
            'id': 'comment2',
            'text': 'I did not like this video at all.',
            'author': 'User2',
            'like_count': '2',
            'reply_count': '0',
            'published_at': datetime.now().isoformat()
        },
        {
            'id': 'comment3',
            'text': 'The video was okay, nothing special.',
            'author': 'User3',
            'like_count': '5',
            'reply_count': '1',
            'published_at': datetime.now().isoformat()
        }
    ]

@pytest.fixture
def sample_channel_data():
    """Provide sample channel data for testing."""
    return {
        'id': 'test_channel_id',
        'title': 'Test Channel',
        'description': 'This is a test channel for development.',
        'published_at': (datetime.now() - timedelta(days=365)).isoformat() + 'Z',
        'subscriber_count': '10000',
        'video_count': '100',
        'view_count': '1000000'
    }

@pytest.fixture
def mock_api_response():
    """Provide mock API response data for testing."""
    return {
        'kind': 'youtube#videoListResponse',
        'etag': 'test_etag',
        'items': [{
            'kind': 'youtube#video',
            'etag': 'test_video_etag',
            'id': 'test_video_id',
            'snippet': {
                'title': 'Test Video Title',
                'description': 'Test Description',
                'publishedAt': datetime.now().isoformat() + 'Z'
            },
            'statistics': {
                'viewCount': '1000',
                'likeCount': '100',
                'commentCount': '50'
            }
        }]
    }

@pytest.fixture
def test_data_dir(tmp_path):
    """Create and return a temporary directory for test data."""
    data_dir = tmp_path / 'test_data'
    data_dir.mkdir()
    return data_dir

@pytest.fixture
def test_output_dir(tmp_path):
    """Create and return a temporary directory for test output."""
    output_dir = tmp_path / 'test_output'
    output_dir.mkdir()
    return output_dir
