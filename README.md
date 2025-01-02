# YouTube Data Scraper and Analyzer

A comprehensive Python application for scraping, analyzing, and visualizing YouTube video data. This tool helps content creators and researchers gain insights from YouTube videos through data analysis and visualization.

## Features

- **Data Collection**
  - Video metadata retrieval
  - Comment scraping with replies
  - Channel analysis
  - Topic-based video search
  - Rate limiting and quota management

- **Data Analysis**
  - Performance metrics calculation
  - Sentiment analysis of comments
  - Keyword trend analysis
  - Engagement metrics

- **Data Visualization**
  - Engagement metrics plots
  - Sentiment distribution charts
  - Comment activity timelines
  - Keyword trend visualizations
  - Comprehensive dashboards

- **Data Storage**
  - Structured data storage
  - Analysis results persistence
  - Visualization export

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/youtube_scraper.git
cd youtube_scraper
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your YouTube API key:
Create a `.env` file in the project root and add your YouTube Data API key:
```
YOUTUBE_API_KEY=your_api_key_here
```

## Usage

### Command Line Interface

The application can be run in three modes:

1. **Video Analysis**
```bash
python -m src.app --mode video --id VIDEO_ID
```

2. **Channel Analysis**
```bash
python -m src.app --mode channel --id CHANNEL_ID --max-videos 10
```

3. **Topic Analysis**
```bash
python -m src.app --mode topic --query "your search query" --max-videos 10
```

Additional options:
- `--no-viz`: Disable visualization generation
- `--data-dir`: Specify data storage directory
- `--viz-dir`: Specify visualization output directory

### Python API

```python
from src.app import YouTubeDataApp

# Initialize the application
app = YouTubeDataApp()

# Analyze a single video
analysis = app.analyze_video("VIDEO_ID")

# Analyze videos by topic
topic_analysis = app.analyze_topic("search query", max_videos=10)

# Check API quota status
quota_status = app.get_quota_status()
```

## Project Structure

```
youtube_scraper/
├── src/
│   ├── scraper/         # YouTube API interaction
│   ├── storage/         # Data persistence
│   ├── analytics/       # Data analysis
│   ├── visualization/   # Data visualization
│   └── app.py          # Main application
├── tests/              # Test suite
├── data/              # Data storage
├── visualizations/    # Generated plots
├── requirements.txt   # Dependencies
└── README.md         # Documentation
```

## Development

### Running Tests

```bash
pytest -v
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Dependencies

- google-api-python-client
- python-dotenv
- pandas
- numpy
- matplotlib
- seaborn
- textblob
- loguru
- pytest

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- YouTube Data API v3
- Python Data Science Community
- Open Source Contributors
