"""
Metrics collection and monitoring module.
"""
from typing import Dict, Any, Optional, List
import time
from dataclasses import dataclass, field
from datetime import datetime
import threading
import json
from pathlib import Path
import logging
from loguru import logger

@dataclass
class MetricPoint:
    """Data class for storing metric information."""
    timestamp: float
    value: float
    labels: Dict[str, str] = field(default_factory=dict)

class MetricsCollector:
    """Collects and manages application metrics."""
    
    def __init__(self, metrics_dir: str = "metrics"):
        """Initialize the metrics collector."""
        self.logger = logger.bind(module="metrics_collector")
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics: Dict[str, list] = {}
        self.lock = threading.Lock()
        
        # Create metric files
        self._initialize_metric_files()
        
        self.logger.info("Initialized MetricsCollector with metrics_dir={}", metrics_dir)
    
    def _initialize_metric_files(self):
        """Initialize metric storage files."""
        metric_types = [
            "analysis_duration",
            "content_length",
            "topic_count",
            "phrase_count",
            "memory_usage",
            "cache_hits",
            "error_count"
        ]
        
        for metric in metric_types:
            metric_file = self.metrics_dir / f"{metric}.json"
            if not metric_file.exists():
                with open(metric_file, 'w') as f:
                    json.dump([], f)
    
    def record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a metric value with optional labels."""
        try:
            with self.lock:
                metric_point = MetricPoint(
                    timestamp=time.time(),
                    value=value,
                    labels=labels or {}
                )
                
                # Store in memory
                if name not in self.metrics:
                    self.metrics[name] = []
                self.metrics[name].append(metric_point)
                
                # Write to file
                metric_file = self.metrics_dir / f"{name}.json"
                try:
                    with open(metric_file, 'r') as f:
                        data = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    data = []
                
                data.append({
                    'timestamp': metric_point.timestamp,
                    'value': metric_point.value,
                    'labels': metric_point.labels
                })
                
                # Keep only last 1000 points
                if len(data) > 1000:
                    data = data[-1000:]
                
                with open(metric_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                self.logger.debug("Recorded metric {} = {} with labels {}", 
                                name, value, labels)
                
        except Exception as e:
            self.logger.error("Error recording metric {}: {}", name, str(e))
    
    def get_metric_stats(self, name: str, 
                        start_time: Optional[float] = None,
                        end_time: Optional[float] = None) -> Dict[str, float]:
        """Get statistics for a metric within the specified time range."""
        try:
            metric_file = self.metrics_dir / f"{name}.json"
            if not metric_file.exists():
                return {}
            
            with open(metric_file, 'r') as f:
                data = json.load(f)
            
            # Filter by time range
            if start_time:
                data = [d for d in data if d['timestamp'] >= start_time]
            if end_time:
                data = [d for d in data if d['timestamp'] <= end_time]
            
            if not data:
                return {}
            
            values = [d['value'] for d in data]
            
            return {
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'count': len(values)
            }
            
        except Exception as e:
            self.logger.error("Error getting metric stats for {}: {}", name, str(e))
            return {}
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent error metrics."""
        try:
            metric_file = self.metrics_dir / "error_count.json"
            if not metric_file.exists():
                return []
            
            with open(metric_file, 'r') as f:
                data = json.load(f)
            
            # Sort by timestamp and get most recent
            data.sort(key=lambda x: x['timestamp'], reverse=True)
            return data[:limit]
            
        except Exception as e:
            self.logger.error("Error getting recent errors: {}", str(e))
            return []
    
    def clear_old_metrics(self, days: int = 7):
        """Clear metrics older than specified days."""
        try:
            cutoff_time = time.time() - (days * 24 * 60 * 60)
            
            for metric_file in self.metrics_dir.glob("*.json"):
                with open(metric_file, 'r') as f:
                    data = json.load(f)
                
                # Filter out old data
                new_data = [d for d in data if d['timestamp'] > cutoff_time]
                
                with open(metric_file, 'w') as f:
                    json.dump(new_data, f, indent=2)
            
            self.logger.info("Cleared metrics older than {} days", days)
            
        except Exception as e:
            self.logger.error("Error clearing old metrics: {}", str(e))
