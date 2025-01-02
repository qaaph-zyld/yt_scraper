# Deployment Guide

## Overview

This guide covers deploying the YouTube Scraper in various environments, from development to production. Follow these instructions to ensure a secure and efficient deployment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Monitoring Setup](#monitoring-setup)
6. [Security Considerations](#security-considerations)

## Prerequisites

### System Requirements

- Python 3.8+
- Docker (optional)
- 2GB RAM minimum
- 1GB disk space

### Dependencies

1. Install Python packages:
```bash
pip install -r requirements.txt
```

2. Required environment variables:
```
YOUTUBE_API_KEY=your_api_key
METRICS_DIR=path/to/metrics
LOG_LEVEL=INFO
```

## Local Development

1. Set up environment:
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Run tests:
```bash
pytest
```

4. Start development server:
```bash
python run_dashboard.py
```

## Docker Deployment

1. Build image:
```bash
docker build -t youtube-scraper .
```

2. Run container:
```bash
docker run -d \
  --name youtube-scraper \
  -p 8050:8050 \
  -v $(pwd)/metrics:/app/metrics \
  -e YOUTUBE_API_KEY=your_api_key \
  youtube-scraper
```

3. Docker Compose:
```yaml
version: '3'
services:
  analyzer:
    build: .
    ports:
      - "8050:8050"
    volumes:
      - ./metrics:/app/metrics
    environment:
      - YOUTUBE_API_KEY=your_api_key
      - LOG_LEVEL=INFO
```

## Production Deployment

### Security Setup

1. Enable rate limiting:
```python
# config.py
RATE_LIMITS = {
    'analyze_content': {'capacity': 100, 'refill_rate': 10},
    'extract_phrases': {'capacity': 200, 'refill_rate': 20},
    'identify_topics': {'capacity': 150, 'refill_rate': 15}
}
```

2. Configure input validation:
```python
# config.py
VALIDATION_RULES = {
    'content_max_size': 1000000,  # 1MB
    'title_max_length': 1000,
    'description_max_length': 5000
}
```

### Performance Optimization

1. Cache configuration:
```python
# config.py
CACHE_CONFIG = {
    'default_size': 128,
    'ttl': 3600,  # 1 hour
    'metrics_enabled': True
}
```

2. Resource limits:
```bash
# systemd service file
[Service]
LimitNOFILE=65535
LimitNPROC=4096
MemoryLimit=2G
```

### Monitoring Setup

1. Configure metrics:
```python
# config.py
METRICS_CONFIG = {
    'enabled': True,
    'retention_days': 7,
    'dashboard_port': 8050
}
```

2. Set up logging:
```python
# config.py
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> | <level>{message}</level>',
    'rotation': '1 day',
    'retention': '7 days'
}
```

## Monitoring Setup

### Dashboard Configuration

1. Basic setup:
```python
from src.ui.dashboard import MetricsDashboard

dashboard = MetricsDashboard(
    metrics_dir="/path/to/metrics",
    refresh_interval=5000  # 5 seconds
)
```

2. Advanced options:
```python
# config.py
DASHBOARD_CONFIG = {
    'host': '0.0.0.0',
    'port': 8050,
    'debug': False,
    'ssl_context': 'adhoc'  # Enable HTTPS
}
```

### Metric Collection

1. Configure collectors:
```python
from src.monitoring.metrics_collector import MetricsCollector

collector = MetricsCollector(
    metrics_dir="/path/to/metrics",
    retention_days=7
)
```

2. Set up cleanup:
```bash
# crontab
0 0 * * * python -c 'from src.monitoring.metrics_collector import MetricsCollector; MetricsCollector().clear_old_metrics()'
```

## Security Considerations

### API Security

1. Rate limiting configuration:
```python
from src.security.rate_limiter import RateLimiter

limiter = RateLimiter()
limiter.create_limit("api", capacity=1000, refill_rate=100)
```

2. Input validation:
```python
from src.security.input_validator import InputValidator, ValidationRule

validator = InputValidator()
validator.add_rule("api_key", ValidationRule(
    field_type=str,
    pattern=r'^[A-Za-z0-9-_]{39}$'
))
```

### Network Security

1. Enable HTTPS:
```python
from ssl import create_default_context

ssl_context = create_default_context()
ssl_context.load_cert_chain('cert.pem', 'key.pem')

dashboard.run(ssl_context=ssl_context)
```

2. Configure firewall:
```bash
# Allow only necessary ports
sudo ufw allow 8050/tcp
sudo ufw enable
```

### Monitoring Security

1. Dashboard authentication:
```python
# config.py
AUTH_CONFIG = {
    'enabled': True,
    'username': 'admin',
    'password_hash': 'secure_hash'
}
```

2. Secure metrics storage:
```bash
# Set proper permissions
chmod 600 /path/to/metrics/*
chown app_user:app_group /path/to/metrics
```
