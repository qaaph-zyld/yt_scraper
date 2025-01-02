# YouTube Analytics Module Documentation

## Overview
The analytics module provides advanced content analysis capabilities for YouTube videos, including topic extraction, sentiment analysis, and visualization features.

## Components

### 1. Topic Analyzer
The `TopicAnalyzer` class provides methods for extracting topics and key phrases from video content.

```python
from src.analytics.topic_analyzer import TopicAnalyzer

analyzer = TopicAnalyzer()
results = analyzer.analyze_content_themes(video_data)
```

#### Features:
- Key phrase extraction using NLTK
- Topic clustering with TF-IDF and KMeans
- Content theme analysis combining metadata and transcript
- Comprehensive error handling

### 2. Topic Visualizer
The `TopicVisualizer` class creates visual representations of analysis results.

```python
from src.visualization.topic_visualizer import TopicVisualizer

visualizer = TopicVisualizer(output_dir="output/visualizations")
plots = visualizer.create_topic_summary_report(analysis_results)
```

#### Visualization Types:
- Topic distribution bar plots
- Key phrase frequency charts
- Interactive visualization options

## Integration Example

```python
# 1. Initialize components
analyzer = TopicAnalyzer()
visualizer = TopicVisualizer()

# 2. Analyze video content
video_data = {
    'video_id': 'video123',
    'title': 'Example Video',
    'description': 'Video description',
    'transcript': 'Video transcript...'
}
analysis_results = analyzer.analyze_content_themes(video_data)

# 3. Create visualizations
plots = visualizer.create_topic_summary_report(analysis_results)

# 4. Access results
topic_plot = plots['topic_distribution']  # Path to topic distribution plot
phrases_plot = plots['key_phrases']       # Path to key phrases plot
```

## Performance Considerations
- Memory efficient processing for large transcripts
- Automatic plot cleanup
- Configurable visualization parameters

## Error Handling
The module includes comprehensive error handling:
- Input validation
- Graceful degradation
- Detailed error logging
- Recovery mechanisms

## Dependencies
- nltk==3.8.1
- scikit-learn==1.3.2
- matplotlib==3.8.2
- seaborn==0.13.0

## Testing
The module includes both unit tests and integration tests:
```bash
# Run unit tests
pytest tests/test_topic_analyzer.py
pytest tests/test_topic_visualizer.py

# Run integration tests
pytest tests/integration/test_analytics_pipeline.py
```
