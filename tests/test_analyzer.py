import pytest
import os
import sys
from datetime import datetime, timezone

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analytics import YouTubeAnalyzer

@pytest.fixture
def analyzer():
    """Create YouTubeAnalyzer instance."""
    return YouTubeAnalyzer()

@pytest.fixture
def sample_metadata():
    """Create sample video metadata."""
    return {
        'id': 'dQw4w9WgXcQ',
        'title': 'Test Video Title',
        'description': 'This is a test video description with some keywords.',
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
            'text': 'This is a great video! Really enjoyed it.',
            'like_count': 10,
            'published_at': '2025-01-01T01:00:00Z',
            'replies': [
                {
                    'author': 'User2',
                    'text': 'Thanks, I agree!',
                    'like_count': 5,
                    'published_at': '2025-01-01T01:30:00Z'
                }
            ]
        },
        {
            'author': 'User3',
            'text': 'This content is terrible.',
            'like_count': 2,
            'published_at': '2025-01-01T02:00:00Z',
            'replies': []
        }
    ]

def test_analyze_video_performance(analyzer, sample_metadata):
    """Test video performance analysis."""
    result = analyzer.analyze_video_performance(sample_metadata)
    
    assert result['video_id'] == sample_metadata['id']
    assert result['total_engagement'] == 1150  # 1000 views + 100 likes + 50 comments
    assert result['engagement_rate'] > 0
    assert result['like_view_ratio'] == 10.0  # (100/1000) * 100
    assert result['comment_view_ratio'] == 5.0  # (50/1000) * 100
    assert result['views_per_day'] > 0
    assert result['video_age_days'] >= 0

def test_analyze_comments_sentiment(analyzer, sample_comments):
    """Test comment sentiment analysis."""
    result = analyzer.analyze_comments_sentiment(sample_comments)
    
    assert 'overall_sentiment' in result
    assert 'sentiment_stats' in result
    assert 'average_polarity' in result
    assert 'sentiment_distribution' in result
    
    # Check sentiment distributions
    assert 'comments' in result['sentiment_distribution']
    assert 'replies' in result['sentiment_distribution']
    
    # Verify sentiment stats sum to total number of texts
    total_texts = len(sample_comments) + sum(len(c['replies']) for c in sample_comments)
    assert sum(result['sentiment_stats'].values()) == total_texts

def test_keyword_trends_analysis(analyzer):
    """Test keyword trends analysis."""
    videos = [
        {
            'title': 'Python Programming Tutorial',
            'description': 'Learn Python programming basics'
        },
        {
            'title': 'Advanced Python Tips',
            'description': 'Advanced programming concepts in Python'
        }
    ]
    
    result = analyzer.analyze_keyword_trends(videos)
    
    assert 'title_trends' in result
    assert 'description_trends' in result
    assert len(result['title_trends']) <= 10
    assert len(result['description_trends']) <= 10
    
    # Check if 'python' appears in trends (should be common in both titles)
    title_words = [item['word'] for item in result['title_trends']]
    assert 'python' in title_words

def test_generate_video_report(analyzer, sample_metadata, sample_comments):
    """Test comprehensive video report generation."""
    report = analyzer.generate_video_report(sample_metadata, sample_comments)
    
    assert report['video_id'] == sample_metadata['id']
    assert report['title'] == sample_metadata['title']
    
    # Check all sections are present
    assert 'performance_metrics' in report
    assert 'sentiment_analysis' in report
    assert 'engagement_metrics' in report
    assert 'top_comments' in report
    
    # Check engagement metrics
    engagement = report['engagement_metrics']
    assert engagement['total_comments'] == len(sample_comments)
    assert engagement['total_replies'] == 1  # Only one reply in sample data
    assert engagement['avg_replies_per_comment'] == 0.5  # 1 reply / 2 comments
    assert engagement['avg_likes_per_comment'] == 6.0  # (10 + 2) / 2 comments

def test_sentiment_caching(analyzer):
    """Test sentiment analysis caching."""
    text = "This is a test message"
    
    # First call should cache the result
    result1 = analyzer._get_sentiment(text)
    
    # Second call should use cached result
    result2 = analyzer._get_sentiment(text)
    
    assert result1 == result2
    assert text in analyzer.sentiment_cache

def test_keyword_extraction(analyzer):
    """Test keyword extraction from text."""
    text = "The quick brown fox jumps over the lazy dog"
    keywords = analyzer._extract_keywords(text)
    
    # Check that stop words are removed
    assert 'the' not in keywords
    assert 'over' not in keywords
    
    # Check that meaningful words are kept
    assert 'quick' in keywords
    assert 'brown' in keywords
    assert 'fox' in keywords
    assert 'jumps' in keywords

def test_empty_inputs(analyzer):
    """Test analyzer behavior with empty inputs."""
    # Test empty metadata
    empty_metadata = {
        'id': '',
        'title': '',
        'description': '',
        'published_at': '2025-01-01T00:00:00Z',
        'view_count': 0,
        'like_count': 0,
        'comment_count': 0
    }
    performance = analyzer.analyze_video_performance(empty_metadata)
    assert performance['engagement_rate'] == 0
    assert performance['views_per_day'] == 0
    
    # Test empty comments
    sentiment = analyzer.analyze_comments_sentiment([])
    assert sentiment['overall_sentiment'] == 'neutral'
    assert sentiment['average_polarity'] == 0
    
    # Test empty videos for keyword trends
    trends = analyzer.analyze_keyword_trends([])
    assert len(trends['title_trends']) == 0
    assert len(trends['description_trends']) == 0
