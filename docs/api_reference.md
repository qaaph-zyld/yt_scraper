# YouTube Scraper API Reference

## Core Components

### TopicAnalyzer

The `TopicAnalyzer` class provides advanced content analysis capabilities with built-in security and performance optimizations.

```python
from src.analytics.topic_analyzer import TopicAnalyzer

analyzer = TopicAnalyzer(cache_size=128)
```

#### Methods

##### analyze_content_themes
```python
def analyze_content_themes(self, video_data: Dict[str, Any]) -> Dict[str, Any]
```
Analyzes themes and topics in YouTube video content.

**Parameters:**
- `video_data`: Dictionary containing:
  - `video_id`: YouTube video ID (required)
  - `title`: Video title
  - `description`: Video description
  - `transcript`: Video transcript

**Returns:**
- Dictionary containing:
  - `key_phrases`: List of extracted key phrases
  - `topics`: List of identified topics with weights
  - `content_length`: Total content length
  - `sentence_count`: Number of sentences

**Rate Limits:**
- 5 tokens per request
- Token refill rate: 1 token per second

##### extract_key_phrases
```python
def extract_key_phrases(self, content: str) -> List[str]
```
Extracts key phrases from content using NLP techniques.

**Parameters:**
- `content`: Text content to analyze

**Returns:**
- List of key phrases

**Rate Limits:**
- 1 token per request
- Token refill rate: 1 token per second

##### identify_topics
```python
def identify_topics(self, content: str, num_topics: int = 5) -> List[Dict[str, Any]]
```
Identifies main topics in content using clustering.

**Parameters:**
- `content`: Text content to analyze
- `num_topics`: Number of topics to identify (default: 5)

**Returns:**
- List of topics with terms and weights

**Rate Limits:**
- 2 tokens per request
- Token refill rate: 1 token per second

### MetricsCollector

The `MetricsCollector` class handles performance monitoring and metric tracking.

```python
from src.monitoring.metrics_collector import MetricsCollector

collector = MetricsCollector(metrics_dir="metrics")
```

#### Methods

##### record_metric
```python
def record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None)
```
Records a metric value with optional labels.

**Parameters:**
- `name`: Metric name
- `value`: Metric value
- `labels`: Optional key-value labels

##### get_metric_stats
```python
def get_metric_stats(self, name: str, start_time: Optional[float] = None, end_time: Optional[float] = None) -> Dict[str, float]
```
Gets statistics for a metric within a time range.

**Parameters:**
- `name`: Metric name
- `start_time`: Start timestamp (optional)
- `end_time`: End timestamp (optional)

**Returns:**
- Dictionary with min, max, avg, and count

### MetricsDashboard

The `MetricsDashboard` class provides a real-time monitoring interface.

```python
from src.ui.dashboard import MetricsDashboard

dashboard = MetricsDashboard(metrics_dir="metrics")
dashboard.run(host="0.0.0.0", port=8050)
```

#### Features

- Real-time performance monitoring
- Interactive time range selection
- Performance metrics visualization
- Content analysis graphs
- Error tracking table

## Security Components

### RateLimiter

The `RateLimiter` class implements token bucket rate limiting.

```python
from src.security.rate_limiter import RateLimiter, rate_limit

@rate_limit("my_function", tokens=1)
def my_function():
    pass
```

### InputValidator

The `InputValidator` class provides input validation and sanitization.

```python
from src.security.input_validator import InputValidator, ValidationRule

validator = InputValidator()
validator.add_rule("field", ValidationRule(
    field_type=str,
    min_length=1,
    max_length=1000
))
```

## Error Handling

All components use structured error handling and logging:

```python
try:
    result = analyzer.analyze_content_themes(video_data)
except ValidationError as e:
    logger.error("Validation error: {}", str(e))
except RateLimitExceeded as e:
    logger.error("Rate limit exceeded: {}", str(e))
except Exception as e:
    logger.error("Unexpected error: {}", str(e))
```

## Best Practices

1. Always handle rate limits and validation errors
2. Use structured logging for debugging
3. Monitor performance metrics in dashboard
4. Regularly clear old metrics
5. Validate and sanitize all inputs
