# YouTube Scraper User Guide

## Overview

The YouTube Scraper is a powerful tool for analyzing YouTube video content, extracting key themes, and monitoring performance metrics. This guide will help you get started and make the most of its features.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Content Analysis](#content-analysis)
4. [Performance Monitoring](#performance-monitoring)
5. [Security Features](#security-features)
6. [Troubleshooting](#troubleshooting)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/youtube_scraper.git
cd youtube_scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your YouTube API key
```

## Quick Start

1. Basic content analysis:
```python
from src.analytics.topic_analyzer import TopicAnalyzer

# Initialize analyzer
analyzer = TopicAnalyzer()

# Analyze video content
result = analyzer.analyze_content_themes({
    'video_id': 'YOUR_VIDEO_ID',
    'title': 'Video Title',
    'description': 'Video Description',
    'transcript': 'Video Transcript'
})

print(result['topics'])
print(result['key_phrases'])
```

2. Start the metrics dashboard:
```bash
python run_dashboard.py
```

Then open `http://localhost:8050` in your browser.

## Content Analysis

### Topic Analysis

The system uses advanced NLP techniques to identify key topics:

1. **Key Phrase Extraction**
   - Identifies important multi-word phrases
   - Filters out common stop words
   - Uses part-of-speech patterns

2. **Topic Identification**
   - Clusters content into topics
   - Assigns weights to topics
   - Provides representative terms

Example:
```python
# Get key phrases
phrases = analyzer.extract_key_phrases(content)

# Identify topics
topics = analyzer.identify_topics(content, num_topics=5)
```

### Performance Optimization

The system includes several optimizations:

1. **Caching**
   - LRU cache for frequent operations
   - Configurable cache size
   - Content-based cache keys

2. **Rate Limiting**
   - Token bucket algorithm
   - Configurable limits
   - Per-operation controls

## Performance Monitoring

### Metrics Dashboard

The dashboard provides real-time monitoring:

1. **Performance Metrics**
   - Analysis duration
   - Memory usage
   - Cache hit rates

2. **Content Analytics**
   - Topic distribution
   - Content length trends
   - Error tracking

3. **Time Range Selection**
   - Last hour
   - Last 24 hours
   - Last 7 days

### Metric Collection

Track custom metrics:
```python
from src.monitoring.metrics_collector import MetricsCollector

collector = MetricsCollector()
collector.record_metric("custom_metric", value=42.0, labels={
    "category": "test",
    "version": "1.0"
})
```

## Security Features

### Input Validation

All inputs are validated:

1. **Content Validation**
   - Size limits
   - Format checking
   - Pattern matching

2. **Video Data Validation**
   - Required fields
   - Format constraints
   - Length limits

Example:
```python
from src.security.input_validator import InputValidator, ValidationRule

validator = InputValidator()
validator.add_rule("content", ValidationRule(
    field_type=str,
    min_length=1,
    max_length=1000000
))
```

### Rate Limiting

Protect against overuse:

1. **Token Bucket**
   - Per-operation limits
   - Automatic refills
   - Configurable rates

2. **Decorator Usage**
```python
from src.security.rate_limiter import rate_limit

@rate_limit("my_operation", tokens=1)
def my_function():
    pass
```

## Troubleshooting

### Common Issues

1. **Rate Limit Exceeded**
   - Wait for token refill
   - Check rate limit configuration
   - Monitor usage patterns

2. **Validation Errors**
   - Check input formats
   - Verify content length
   - Review validation rules

3. **Performance Issues**
   - Monitor dashboard metrics
   - Check cache configuration
   - Review resource usage

### Logging

Enable detailed logging:
```python
from loguru import logger

logger.add("app.log", rotation="1 day")
```

### Support

For issues and feature requests:
1. Check the [API Reference](api_reference.md)
2. Open an issue on GitHub
3. Contact the maintainers
