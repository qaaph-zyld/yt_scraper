"""
Integration tests for the YouTube analytics pipeline.
Tests the interaction between data collection, analysis, and visualization components.
"""
import pytest
from src.analytics.topic_analyzer import TopicAnalyzer
from src.visualization.topic_visualizer import TopicVisualizer
from pathlib import Path
import json
import tempfile
import shutil
import os

@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_video_data():
    """Load sample video data from test fixtures."""
    return {
        'video_id': 'test123',
        'title': 'Machine Learning Tutorial',
        'description': 'Learn about artificial intelligence and neural networks',
        'transcript': '''
        Welcome to this comprehensive tutorial on machine learning.
        Today we'll explore neural networks and deep learning concepts.
        We'll start with basic principles and move to advanced topics.
        Understanding AI requires knowledge of mathematics and programming.
        Let's dive into the fascinating world of artificial intelligence.
        ''',
        'metadata': {
            'view_count': 1000,
            'like_count': 100,
            'comment_count': 50,
            'published_at': '2025-01-01T00:00:00Z'
        }
    }

@pytest.fixture
def analyzer():
    """Create TopicAnalyzer instance."""
    return TopicAnalyzer()

@pytest.fixture
def visualizer(temp_output_dir):
    """Create TopicVisualizer instance with temporary output directory."""
    return TopicVisualizer(output_dir=temp_output_dir)

def test_end_to_end_analysis(analyzer, visualizer, sample_video_data, temp_output_dir):
    """Test the complete analysis pipeline from raw data to visualization."""
    # 1. Analyze topics
    analysis_results = analyzer.analyze_content_themes(sample_video_data)
    
    # Verify analysis results
    assert isinstance(analysis_results, dict)
    assert 'key_phrases' in analysis_results
    assert 'topics' in analysis_results
    assert len(analysis_results['key_phrases']) > 0
    assert len(analysis_results['topics']) > 0
    
    # 2. Create visualizations
    plots = visualizer.create_topic_summary_report(analysis_results)
    
    # Verify visualization outputs
    assert isinstance(plots, dict)
    assert 'topic_distribution' in plots
    assert 'key_phrases' in plots
    
    # Check if plot files exist
    for plot_path in plots.values():
        assert Path(plot_path).exists()
        assert Path(plot_path).is_file()
        assert Path(plot_path).stat().st_size > 0
    
    # 3. Save analysis results
    results_file = Path(temp_output_dir) / 'analysis_results.json'
    with open(results_file, 'w') as f:
        json.dump({
            'video_id': sample_video_data['video_id'],
            'analysis': analysis_results,
            'visualizations': {k: str(Path(v).name) for k, v in plots.items()}
        }, f, indent=2)
    
    # Verify results file
    assert results_file.exists()
    assert results_file.stat().st_size > 0

def test_pipeline_error_handling(analyzer, visualizer, temp_output_dir):
    """Test error handling in the analysis pipeline."""
    # Test with invalid input
    analysis_results = analyzer.analyze_content_themes(None)
    assert analysis_results == {}
    
    # Test with empty input
    analysis_results = analyzer.analyze_content_themes({})
    assert analysis_results == {}
    
    # Test visualization with invalid input
    plots = visualizer.create_topic_summary_report(None)
    assert plots == {}
    
    # Test visualization with empty input
    plots = visualizer.create_topic_summary_report({})
    assert plots == {}

def test_large_dataset_handling(analyzer, visualizer, temp_output_dir):
    """Test pipeline performance with larger datasets."""
    # Create a larger dataset
    large_transcript = " ".join(["artificial intelligence machine learning"] * 1000)
    large_data = {
        'video_id': 'large_test',
        'title': 'Large Test Video',
        'description': 'Testing with large dataset',
        'transcript': large_transcript
    }
    
    # Run analysis
    analysis_results = analyzer.analyze_content_themes(large_data)
    
    # Verify analysis completed successfully
    assert isinstance(analysis_results, dict)
    assert 'key_phrases' in analysis_results
    assert 'topics' in analysis_results
    
    # Create visualizations
    plots = visualizer.create_topic_summary_report(analysis_results)
    
    # Verify visualization completed successfully
    assert isinstance(plots, dict)
    assert len(plots) > 0
    
    # Check memory usage (files should be cleaned up)
    for plot_path in plots.values():
        assert Path(plot_path).stat().st_size < 10 * 1024 * 1024  # Less than 10MB
