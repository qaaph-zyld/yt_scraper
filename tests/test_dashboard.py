"""
Tests for the metrics dashboard.
"""
import pytest
from pathlib import Path
import tempfile
import shutil
import json
import time
from src.ui.dashboard import MetricsDashboard

@pytest.fixture
def temp_metrics_dir():
    """Create a temporary directory for metrics."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_metrics(temp_metrics_dir):
    """Create sample metrics data."""
    metrics_dir = Path(temp_metrics_dir)
    
    # Analysis duration data
    duration_data = [
        {
            "timestamp": time.time() - i * 3600,
            "value": float(i + 1),
            "labels": {}
        }
        for i in range(24)
    ]
    
    with open(metrics_dir / "analysis_duration.json", "w") as f:
        json.dump(duration_data, f)
    
    # Memory usage data
    memory_data = [
        {
            "timestamp": time.time() - i * 3600,
            "value": float(100 + i * 10),
            "labels": {}
        }
        for i in range(24)
    ]
    
    with open(metrics_dir / "memory_usage.json", "w") as f:
        json.dump(memory_data, f)
    
    # Topic count data
    topic_data = [
        {
            "timestamp": time.time() - i * 3600,
            "value": float(5 + (i % 3)),
            "labels": {}
        }
        for i in range(24)
    ]
    
    with open(metrics_dir / "topic_count.json", "w") as f:
        json.dump(topic_data, f)
    
    # Content length data
    content_data = [
        {
            "timestamp": time.time() - i * 3600,
            "value": float(1000 + i * 100),
            "labels": {}
        }
        for i in range(24)
    ]
    
    with open(metrics_dir / "content_length.json", "w") as f:
        json.dump(content_data, f)
    
    # Error data
    error_data = [
        {
            "timestamp": time.time() - i * 3600,
            "value": 1.0,
            "labels": {
                "error_type": f"Error_{i}",
                "message": f"Test error message {i}"
            }
        }
        for i in range(5)
    ]
    
    with open(metrics_dir / "error_count.json", "w") as f:
        json.dump(error_data, f)
    
    return metrics_dir

def test_dashboard_initialization(temp_metrics_dir):
    """Test dashboard initialization."""
    dashboard = MetricsDashboard(metrics_dir=temp_metrics_dir)
    assert dashboard.app is not None
    assert dashboard.metrics_dir == Path(temp_metrics_dir)

def test_metrics_loading(sample_metrics):
    """Test metrics data loading."""
    dashboard = MetricsDashboard(metrics_dir=sample_metrics)
    metrics = dashboard._load_metrics(time.time() - 86400)  # Last 24 hours
    
    assert "analysis_duration" in metrics
    assert "memory_usage" in metrics
    assert "topic_count" in metrics
    assert "content_length" in metrics
    assert "error_count" in metrics
    
    # Check data frames
    for df in metrics.values():
        assert not df.empty
        assert "datetime" in df.columns
        assert "value" in df.columns
        assert "labels" in df.columns

def test_graph_creation(sample_metrics):
    """Test graph creation functions."""
    dashboard = MetricsDashboard(metrics_dir=sample_metrics)
    metrics = dashboard._load_metrics(time.time() - 86400)
    
    # Test duration graph
    duration_fig = dashboard._create_duration_graph(metrics)
    assert duration_fig is not None
    
    # Test memory graph
    memory_fig = dashboard._create_memory_graph(metrics)
    assert memory_fig is not None
    
    # Test topic graph
    topic_fig = dashboard._create_topic_graph(metrics)
    assert topic_fig is not None
    
    # Test content graph
    content_fig = dashboard._create_content_graph(metrics)
    assert content_fig is not None

def test_error_table_creation(sample_metrics):
    """Test error table creation."""
    dashboard = MetricsDashboard(metrics_dir=sample_metrics)
    metrics = dashboard._load_metrics(time.time() - 86400)
    
    error_table = dashboard._create_error_table(metrics)
    assert error_table is not None

def test_empty_metrics(temp_metrics_dir):
    """Test handling of empty metrics."""
    dashboard = MetricsDashboard(metrics_dir=temp_metrics_dir)
    metrics = dashboard._load_metrics(time.time() - 86400)
    
    # Test empty graphs
    duration_fig = dashboard._create_duration_graph(metrics)
    assert "No Analysis Duration Data" in str(duration_fig.to_dict())
    
    memory_fig = dashboard._create_memory_graph(metrics)
    assert "No Memory Usage Data" in str(memory_fig.to_dict())
    
    topic_fig = dashboard._create_topic_graph(metrics)
    assert "No Topic Data" in str(topic_fig.to_dict())
    
    content_fig = dashboard._create_content_graph(metrics)
    assert "No Content Length Data" in str(content_fig.to_dict())
    
    # Test empty error table
    error_table = dashboard._create_error_table(metrics)
    assert "No Errors Recorded" in str(error_table)
