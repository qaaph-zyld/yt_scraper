"""
Tests for the topic analyzer module.
"""

import pytest
from datetime import datetime
from src.analytics.topic_analyzer import TopicAnalyzer

@pytest.fixture
def analyzer():
    """Create a TopicAnalyzer instance."""
    return TopicAnalyzer()

@pytest.fixture
def sample_text():
    """Create sample text."""
    return """
    Machine learning is a fascinating field of artificial intelligence.
    Deep learning models have revolutionized natural language processing.
    Neural networks can solve complex pattern recognition problems.
    """

@pytest.fixture
def sample_video_data():
    """Create sample video data."""
    return {
        'title': 'Introduction to Machine Learning',
        'description': 'Learn about artificial intelligence and neural networks',
        'transcript': 'Today we will discuss machine learning concepts and deep learning applications',
        'analysis_timestamp': datetime.now().isoformat()
    }

def test_extract_key_phrases(analyzer, sample_text):
    """Test key phrase extraction."""
    phrases = analyzer.extract_key_phrases(sample_text)
    assert isinstance(phrases, list)
    assert len(phrases) > 0
    for phrase in phrases:
        assert isinstance(phrase, str)
        assert len(phrase) > 0

def test_extract_key_phrases_empty_text(analyzer):
    """Test key phrase extraction with empty text."""
    phrases = analyzer.extract_key_phrases('')
    assert phrases == []

def test_identify_topics(analyzer, sample_text):
    """Test topic identification."""
    # Split text into sentences for topic analysis
    sentences = sample_text.split('.')
    topics = analyzer.identify_topics(sentences)
    
    assert isinstance(topics, list)
    if topics:  # Topics might be empty for very short texts
        assert isinstance(topics[0], dict)
        assert 'id' in topics[0]
        assert 'terms' in topics[0]
        assert 'weight' in topics[0]

def test_identify_topics_empty_texts(analyzer):
    """Test topic identification with empty input."""
    topics = analyzer.identify_topics([])
    assert topics == []

def test_analyze_content_themes(analyzer, sample_video_data):
    """Test content theme analysis."""
    results = analyzer.analyze_content_themes(sample_video_data)
    
    assert isinstance(results, dict)
    assert 'key_phrases' in results
    assert 'topics' in results
    assert 'content_length' in results
    assert 'sentence_count' in results

def test_analyze_content_themes_empty_data(analyzer):
    """Test content theme analysis with empty data."""
    results = analyzer.analyze_content_themes({})
    assert results == {}

def test_empty_input_handling(analyzer):
    """Test empty input handling."""
    assert analyzer.extract_key_phrases('') == []
    assert analyzer.identify_topics([]) == []
    assert analyzer.analyze_content_themes({}) == {}

def test_invalid_input_handling(analyzer):
    """Test invalid input handling."""
    # Test with None values
    assert analyzer.extract_key_phrases(None) == []
    assert analyzer.identify_topics(None) == []
    assert analyzer.analyze_content_themes(None) == {}
