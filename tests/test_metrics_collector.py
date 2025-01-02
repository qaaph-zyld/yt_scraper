"""
Tests for the metrics collection module.
"""
import pytest
from src.monitoring.metrics_collector import MetricsCollector
import tempfile
import shutil
import time
from pathlib import Path
import json

@pytest.fixture
def temp_metrics_dir():
    """Create a temporary directory for metrics."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def collector(temp_metrics_dir):
    """Create a MetricsCollector instance with temporary directory."""
    return MetricsCollector(metrics_dir=temp_metrics_dir)

def test_record_metric(collector, temp_metrics_dir):
    """Test recording a metric."""
    collector.record_metric("test_metric", 42.0, {"label": "test"})
    
    # Check file exists
    metric_file = Path(temp_metrics_dir) / "test_metric.json"
    assert metric_file.exists()
    
    # Check content
    with open(metric_file) as f:
        data = json.load(f)
    assert len(data) == 1
    assert data[0]["value"] == 42.0
    assert data[0]["labels"] == {"label": "test"}

def test_get_metric_stats(collector):
    """Test getting metric statistics."""
    # Record some test metrics
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    for v in values:
        collector.record_metric("test_stats", v)
    
    # Get stats
    stats = collector.get_metric_stats("test_stats")
    
    assert stats["min"] == 1.0
    assert stats["max"] == 5.0
    assert stats["avg"] == 3.0
    assert stats["count"] == 5

def test_time_range_filtering(collector):
    """Test filtering metrics by time range."""
    # Record metrics at different times
    collector.record_metric("time_test", 1.0)
    time.sleep(0.1)
    mid_time = time.time()
    time.sleep(0.1)
    collector.record_metric("time_test", 2.0)
    
    # Get stats for different time ranges
    early_stats = collector.get_metric_stats("time_test", end_time=mid_time)
    late_stats = collector.get_metric_stats("time_test", start_time=mid_time)
    
    assert early_stats["count"] == 1
    assert early_stats["avg"] == 1.0
    assert late_stats["count"] == 1
    assert late_stats["avg"] == 2.0

def test_error_tracking(collector):
    """Test error metric tracking."""
    # Record some errors
    for i in range(5):
        collector.record_metric("error_count", 1.0, {
            "error_type": f"error_{i}",
            "message": f"Test error {i}"
        })
    
    # Get recent errors
    errors = collector.get_recent_errors(limit=3)
    
    assert len(errors) == 3
    assert all("error_type" in e["labels"] for e in errors)

def test_metric_cleanup(collector):
    """Test cleaning up old metrics."""
    # Record some metrics
    collector.record_metric("cleanup_test", 1.0)
    
    # Simulate old data by modifying the timestamp
    metric_file = Path(collector.metrics_dir) / "cleanup_test.json"
    with open(metric_file) as f:
        data = json.load(f)
    
    data[0]["timestamp"] -= 8 * 24 * 60 * 60  # 8 days old
    
    with open(metric_file, "w") as f:
        json.dump(data, f)
    
    # Clear old metrics
    collector.clear_old_metrics(days=7)
    
    # Check that old data was removed
    with open(metric_file) as f:
        data = json.load(f)
    assert len(data) == 0

def test_concurrent_access(collector):
    """Test concurrent metric recording."""
    import threading
    
    def record_metrics():
        for i in range(100):
            collector.record_metric("concurrent_test", float(i))
    
    # Create multiple threads
    threads = [threading.Thread(target=record_metrics) for _ in range(5)]
    
    # Start all threads
    for t in threads:
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    # Check results
    stats = collector.get_metric_stats("concurrent_test")
    assert stats["count"] == 500  # 5 threads * 100 metrics each
