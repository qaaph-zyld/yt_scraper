"""
Tests for the topic visualization module.
"""
import pytest
from src.visualization.topic_visualizer import TopicVisualizer
from pathlib import Path
import tempfile
import shutil

@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def visualizer(temp_output_dir):
    """Create a TopicVisualizer instance with temporary output directory."""
    return TopicVisualizer(output_dir=temp_output_dir)

@pytest.fixture
def sample_topics():
    """Create sample topic analysis results."""
    return [
        {'id': 0, 'terms': ['machine', 'learning', 'ai'], 'weight': 0.8},
        {'id': 1, 'terms': ['data', 'analysis', 'processing'], 'weight': 0.6},
        {'id': 2, 'terms': ['neural', 'networks', 'deep'], 'weight': 0.7}
    ]

@pytest.fixture
def sample_key_phrases():
    """Create sample key phrases."""
    return [
        'machine learning',
        'artificial intelligence',
        'deep learning',
        'neural networks',
        'data science'
    ]

@pytest.fixture
def sample_analysis_results(sample_topics, sample_key_phrases):
    """Create sample complete analysis results."""
    return {
        'topics': sample_topics,
        'key_phrases': sample_key_phrases,
        'content_length': 1000,
        'sentence_count': 50
    }

def test_plot_topic_distribution(visualizer, sample_topics):
    """Test topic distribution plot creation."""
    output_path = visualizer.plot_topic_distribution(sample_topics)
    assert output_path
    assert Path(output_path).exists()
    assert Path(output_path).is_file()

def test_plot_key_phrases_cloud(visualizer, sample_key_phrases):
    """Test key phrases visualization creation."""
    output_path = visualizer.plot_key_phrases_cloud(sample_key_phrases)
    assert output_path
    assert Path(output_path).exists()
    assert Path(output_path).is_file()

def test_create_topic_summary_report(visualizer, sample_analysis_results):
    """Test complete topic summary report creation."""
    plots = visualizer.create_topic_summary_report(sample_analysis_results)
    assert isinstance(plots, dict)
    assert 'topic_distribution' in plots
    assert 'key_phrases' in plots
    for path in plots.values():
        assert Path(path).exists()
        assert Path(path).is_file()

def test_empty_input_handling(visualizer):
    """Test handling of empty inputs."""
    assert visualizer.plot_topic_distribution([]) == ""
    assert visualizer.plot_key_phrases_cloud([]) == ""
    assert visualizer.create_topic_summary_report({}) == {}

def test_invalid_input_handling(visualizer):
    """Test handling of invalid inputs."""
    assert visualizer.plot_topic_distribution(None) == ""
    assert visualizer.plot_key_phrases_cloud(None) == ""
    assert visualizer.create_topic_summary_report(None) == {}
