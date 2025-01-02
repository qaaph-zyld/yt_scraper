import pytest
import os
import sys
from datetime import datetime, timezone

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.validation import DataValidator

@pytest.fixture
def valid_metadata():
    """Create valid video metadata."""
    return {
        'id': 'dQw4w9WgXcQ',
        'title': 'Test Video',
        'description': 'Test Description',
        'published_at': '2025-01-02T00:00:00Z',
        'view_count': 1000,
        'like_count': 100,
        'comment_count': 50
    }

@pytest.fixture
def valid_comment():
    """Create valid comment data."""
    return {
        'author': 'TestUser',
        'text': 'Great video!',
        'like_count': 10,
        'published_at': '2025-01-02T01:00:00Z',
        'reply_count': 2,
        'replies': [
            {
                'author': 'User1',
                'text': 'Thanks!',
                'like_count': 5,
                'published_at': '2025-01-02T01:30:00Z'
            },
            {
                'author': 'User2',
                'text': 'Agreed!',
                'like_count': 3,
                'published_at': '2025-01-02T02:00:00Z'
            }
        ]
    }

def test_validate_video_id():
    """Test video ID validation."""
    assert DataValidator.validate_video_id('dQw4w9WgXcQ')  # Valid ID
    assert not DataValidator.validate_video_id('invalid')   # Too short
    assert not DataValidator.validate_video_id('dQw4w9WgXcQ!')  # Invalid character
    assert not DataValidator.validate_video_id('')  # Empty string
    assert not DataValidator.validate_video_id(123)  # Wrong type

def test_validate_youtube_url():
    """Test YouTube URL validation."""
    valid_urls = [
        'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'http://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'https://youtube.com/watch?v=dQw4w9WgXcQ',
        'https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=123'
    ]
    invalid_urls = [
        'https://youtu.be/dQw4w9WgXcQ',  # Short URL not supported
        'https://www.youtube.com/channel/123',  # Channel URL
        'https://www.youtube.com/watch',  # Missing video ID
        'https://www.youtube.com/watch?v=invalid',  # Invalid video ID
        'not a url',
        ''
    ]
    
    for url in valid_urls:
        assert DataValidator.validate_youtube_url(url)
    
    for url in invalid_urls:
        assert not DataValidator.validate_youtube_url(url)

def test_extract_video_id_from_url():
    """Test video ID extraction from URL."""
    url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=123'
    assert DataValidator.extract_video_id_from_url(url) == 'dQw4w9WgXcQ'
    
    invalid_urls = [
        'https://youtube.com/watch',
        'https://youtube.com/watch?v=invalid',
        'not a url',
        ''
    ]
    for url in invalid_urls:
        assert DataValidator.extract_video_id_from_url(url) is None

def test_validate_metadata(valid_metadata):
    """Test metadata validation."""
    assert DataValidator.validate_metadata(valid_metadata)
    
    # Test invalid cases
    invalid_cases = [
        {k: v for k, v in valid_metadata.items() if k != 'id'},  # Missing field
        {**valid_metadata, 'id': 'invalid'},  # Invalid video ID
        {**valid_metadata, 'view_count': -1},  # Negative count
        {**valid_metadata, 'published_at': 'invalid-date'},  # Invalid date
        {**valid_metadata, 'title': 123}  # Wrong type
    ]
    
    for case in invalid_cases:
        assert not DataValidator.validate_metadata(case)

def test_validate_comment(valid_comment):
    """Test comment validation."""
    assert DataValidator.validate_comment(valid_comment)
    
    # Test invalid cases
    invalid_cases = [
        {k: v for k, v in valid_comment.items() if k != 'author'},  # Missing field
        {**valid_comment, 'like_count': -1},  # Negative count
        {**valid_comment, 'published_at': 'invalid-date'},  # Invalid date
        {**valid_comment, 'reply_count': 3},  # Mismatched reply count
        {**valid_comment, 'replies': []}  # Empty replies with non-zero count
    ]
    
    for case in invalid_cases:
        assert not DataValidator.validate_comment(case)

def test_validate_reply(valid_comment):
    """Test reply validation."""
    reply = valid_comment['replies'][0]
    assert DataValidator.validate_reply(reply)
    
    # Test invalid cases
    invalid_cases = [
        {k: v for k, v in reply.items() if k != 'author'},  # Missing field
        {**reply, 'like_count': -1},  # Negative count
        {**reply, 'published_at': 'invalid-date'},  # Invalid date
        {**reply, 'text': 123}  # Wrong type
    ]
    
    for case in invalid_cases:
        assert not DataValidator.validate_reply(case)
