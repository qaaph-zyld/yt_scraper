"""
Example script demonstrating basic usage of the YouTube Data Scraper.
"""

import os
import sys
from datetime import datetime
import json

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import YouTubeDataApp

def main():
    """Run example analysis."""
    # Initialize application
    app = YouTubeDataApp()
    
    # Example 1: Analyze a single video
    print("\n=== Example 1: Single Video Analysis ===")
    video_id = "dQw4w9WgXcQ"  # Replace with your video ID
    result = app.analyze_video(video_id)
    
    if result:
        print(f"\nAnalysis results for video: {result['title']}")
        print(f"Total views: {result['performance_metrics']['total_engagement']:,}")
        print(f"Engagement rate: {result['performance_metrics']['engagement_rate']}%")
        print(f"Total comments analyzed: {result['total_comments']}")
        
        if 'visualization_paths' in result:
            print("\nVisualization files created:")
            for viz_type, path in result['visualization_paths'].items():
                print(f"- {viz_type}: {path}")
    
    # Example 2: Topic Analysis
    print("\n=== Example 2: Topic Analysis ===")
    search_query = "Python programming tutorial"
    topic_result = app.analyze_topic(search_query, max_videos=3)
    
    if topic_result:
        print(f"\nAnalysis results for topic: {search_query}")
        print(f"Videos analyzed: {topic_result['videos_analyzed']}")
        
        print("\nTop keywords in titles:")
        for keyword in topic_result['keyword_trends']['title_trends'][:5]:
            print(f"- {keyword['word']}: {keyword['count']} occurrences")
    
    # Example 3: Check API Quota Status
    print("\n=== Example 3: API Quota Status ===")
    quota_status = app.get_quota_status()
    print("\nCurrent API quota status:")
    print(json.dumps(quota_status, indent=2))

if __name__ == '__main__':
    main()
