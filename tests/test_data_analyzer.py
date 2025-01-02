"""
Tests for the YouTube data analyzer module.
"""

import pytest
from datetime import datetime, timedelta
from src.analytics.data_analyzer import YouTubeDataAnalyzer

@pytest.fixture
def analyzer():
    """Create a YouTubeDataAnalyzer instance."""
    return YouTubeDataAnalyzer()

@pytest.fixture
def sample_video_data():
    """Create sample video metadata."""
    return {
        'id': 'test123',
        'title': 'Test Video',
        'description': 'This is a test video description',
        'view_count': '1000',
        'like_count': '100',
        'comment_count': '50',
        'published_at': (datetime.now() - timedelta(days=7)).isoformat() + 'Z',
        'duration': 'PT5M30S',
        'channel_id': 'channel123',
        'channel_title': 'Test Channel'
    }

@pytest.fixture
def sample_comments():
    """Create sample comments data."""
    return [
        {
            'text': 'This video is amazing! Really helpful content.',
            'like_count': '10',
            'published_at': datetime.now().isoformat()
        },
        {
            'text': 'I did not like this video at all.',
            'like_count': '2',
            'published_at': datetime.now().isoformat()
        },
        {
            'text': 'The video was okay, nothing special.',
            'like_count': '5',
            'published_at': datetime.now().isoformat()
        }
    ]

def test_analyze_video_performance(analyzer, sample_video_data):
    """Test video performance analysis."""
    metrics = analyzer.analyze_video_performance(sample_video_data)
    
    assert isinstance(metrics, dict)
    assert metrics['total_engagement'] == 1000
    assert metrics['likes'] == 100
    assert metrics['comments'] == 50
    assert 'engagement_rate' in metrics
    assert 'avg_daily_views' in metrics
    assert metrics['engagement_rate'] > 0

def test_analyze_video_performance_empty_data(analyzer):
    """Test video performance analysis with empty data."""
    metrics = analyzer.analyze_video_performance({})
    expected = {
        'total_engagement': 0,
        'likes': 0,
        'comments': 0,
        'engagement_rate': 0.0,
        'avg_daily_views': 0.0
    }
    assert metrics == expected

def test_analyze_comments_sentiment(analyzer, sample_comments):
    """Test comment sentiment analysis."""
    sentiment = analyzer.analyze_comments_sentiment(sample_comments)
    
    assert isinstance(sentiment, dict)
    assert 'average_sentiment' in sentiment
    assert 'sentiment_distribution' in sentiment
    assert 'total_comments' in sentiment
    assert sentiment['total_comments'] == len(sample_comments)
    
    dist = sentiment['sentiment_distribution']
    assert 'positive' in dist
    assert 'neutral' in dist
    assert 'negative' in dist
    assert abs(sum(dist.values()) - 100) < 0.1  # Should sum to 100%

def test_analyze_comments_sentiment_empty_data(analyzer):
    """Test comment sentiment analysis with empty data."""
    sentiment = analyzer.analyze_comments_sentiment([])
    
    assert isinstance(sentiment, dict)
    assert sentiment['average_sentiment'] == 0
    assert sentiment['total_comments'] == 0
    assert all(v == 0 for v in sentiment['sentiment_distribution'].values())

def test_analyze_keyword_trends(analyzer):
    """Test keyword trend analysis."""
    videos = [
        {
            'title': 'Python Programming Tutorial',
            'description': 'Learn Python programming in this tutorial'
        },
        {
            'title': 'Advanced Python Tips',
            'description': 'Advanced programming tips for Python developers'
        }
    ]
    
    trends = analyzer.analyze_keyword_trends(videos)
    
    assert isinstance(trends, dict)
    assert 'title_trends' in trends
    assert 'description_trends' in trends
    assert 'total_videos_analyzed' in trends
    assert trends['total_videos_analyzed'] == len(videos)
    
    # Check if 'python' appears in trends
    title_words = [item['word'] for item in trends['title_trends']]
    desc_words = [item['word'] for item in trends['description_trends']]
    assert 'python' in title_words
    assert 'python' in desc_words

def test_analyze_keyword_trends_empty_data(analyzer):
    """Test keyword trend analysis with empty data."""
    trends = analyzer.analyze_keyword_trends([])
    expected = {
        'title_trends': [],
        'description_trends': [],
        'total_videos_analyzed': 0
    }
    assert trends == expected

def test_generate_video_report(analyzer, sample_video_data, sample_comments):
    """Test comprehensive video report generation."""
    report = analyzer.generate_video_report(sample_video_data, sample_comments)
    
    assert isinstance(report, dict)
    assert report['video_id'] == sample_video_data['id']
    assert report['title'] == sample_video_data['title']
    assert 'analysis_timestamp' in report
    assert 'performance_metrics' in report
    assert 'sentiment_analysis' in report
    assert 'metadata' in report
    
    metadata = report['metadata']
    assert metadata['duration'] == sample_video_data['duration']
    assert metadata['channel_id'] == sample_video_data['channel_id']
    assert metadata['channel_title'] == sample_video_data['channel_title']

def test_generate_video_report_empty_data(analyzer):
    """Test video report generation with empty data."""
    report = analyzer.generate_video_report({}, [])
    expected = {
        'video_id': '',
        'title': '',
        'analysis_timestamp': report['analysis_timestamp'],  # Use actual timestamp
        'performance_metrics': {
            'total_engagement': 0,
            'likes': 0,
            'comments': 0,
            'engagement_rate': 0.0,
            'avg_daily_views': 0.0
        },
        'sentiment_analysis': {
            'average_sentiment': 0,
            'sentiment_distribution': {
                'positive': 0,
                'neutral': 0,
                'negative': 0
            },
            'total_comments': 0
        },
        'metadata': {
            'duration': '',
            'published_at': '',
            'channel_id': '',
            'channel_title': ''
        }
    }
    assert report == expected
