import os
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Union
from loguru import logger
import json

from .scraper import YouTubeAPI
from .storage import DataManager
from .analytics import YouTubeAnalyzer
from .visualization import YouTubeVisualizer

class YouTubeDataApp:
    """Main application class for YouTube data scraping and analysis."""
    
    def __init__(self, data_dir: str = "data", visualizations_dir: str = "visualizations"):
        """
        Initialize the application.
        
        Args:
            data_dir: Directory for storing scraped data
            visualizations_dir: Directory for storing visualizations
        """
        # Initialize components
        self.api = YouTubeAPI(data_dir)
        self.data_manager = DataManager(data_dir)
        self.analyzer = YouTubeAnalyzer()
        self.visualizer = YouTubeVisualizer(visualizations_dir)
        
        # Create directories
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(visualizations_dir, exist_ok=True)
        
        logger.info("YouTube Data Application initialized")
    
    def analyze_video(self, video_id: str, save_visualizations: bool = True) -> Dict:
        """
        Perform comprehensive analysis of a video.
        
        Args:
            video_id: YouTube video ID
            save_visualizations: Whether to save visualization plots
            
        Returns:
            dict: Analysis results and visualization paths
        """
        try:
            # Fetch video data
            metadata = self.api.get_video_metadata(video_id)
            if not metadata:
                raise ValueError(f"Could not fetch metadata for video: {video_id}")
            
            comments = self.api.get_video_comments(video_id)
            
            # Perform analysis
            performance_metrics = self.analyzer.analyze_video_performance(metadata)
            sentiment_analysis = self.analyzer.analyze_comments_sentiment(comments)
            
            # Create visualizations if requested
            visualization_paths = {}
            if save_visualizations:
                viz_paths = {
                    'engagement': self.visualizer.plot_engagement_metrics(metadata),
                    'sentiment': self.visualizer.plot_sentiment_distribution(sentiment_analysis),
                    'comments': self.visualizer.plot_comment_activity(comments),
                    'dashboard': self.visualizer.create_dashboard(
                        metadata, comments, sentiment_analysis,
                        {'title_trends': [], 'description_trends': []}  # Empty trends for single video
                    )
                }
                visualization_paths = {k: v for k, v in viz_paths.items() if v}  # Remove empty paths
            
            # Compile results
            analysis = {
                'video_id': video_id,
                'title': metadata['title'],
                'analysis_timestamp': datetime.now().isoformat(),
                'performance_metrics': performance_metrics,
                'sentiment_analysis': sentiment_analysis,
                'total_comments': len(comments),
                'visualization_paths': visualization_paths
            }
            
            # Save analysis results
            self.data_manager.save_analysis(video_id, analysis)
            
            logger.info(f"Completed analysis for video: {video_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing video {video_id}: {str(e)}")
            return {}
    
    def analyze_channel(self, channel_id: str, max_videos: int = 10,
                       save_visualizations: bool = True) -> Dict:
        """
        Analyze multiple videos from a channel.
        
        Args:
            channel_id: YouTube channel ID
            max_videos: Maximum number of videos to analyze
            save_visualizations: Whether to save visualization plots
            
        Returns:
            dict: Channel analysis results
        """
        # TODO: Implement channel analysis
        pass
    
    def analyze_topic(self, search_query: str, max_videos: int = 10,
                     save_visualizations: bool = True) -> Dict:
        """
        Analyze videos related to a specific topic or search query.
        
        Args:
            search_query: Search query or topic
            max_videos: Maximum number of videos to analyze
            save_visualizations: Whether to save visualization plots
            
        Returns:
            dict: Topic analysis results
        """
        try:
            # Search for videos
            videos = self.api.search_videos(search_query, max_videos)
            if not videos:
                raise ValueError(f"No videos found for query: {search_query}")
            
            # Analyze each video
            video_analyses = []
            for video in videos:
                analysis = self.analyze_video(video['id'], save_visualizations=False)
                if analysis:
                    video_analyses.append(analysis)
            
            # Aggregate video metadata for trend analysis
            keyword_trends = self.analyzer.analyze_keyword_trends(videos)
            
            # Create topic-level visualizations
            visualization_paths = {}
            if save_visualizations and video_analyses:
                viz_paths = {
                    'keyword_trends': self.visualizer.plot_keyword_trends(keyword_trends)
                }
                visualization_paths = {k: v for k, v in viz_paths.items() if v}
            
            # Compile results
            analysis = {
                'search_query': search_query,
                'analysis_timestamp': datetime.now().isoformat(),
                'videos_analyzed': len(video_analyses),
                'keyword_trends': keyword_trends,
                'video_analyses': video_analyses,
                'visualization_paths': visualization_paths
            }
            
            # Save analysis results
            self.data_manager.save_topic_analysis(search_query, analysis)
            
            logger.info(f"Completed topic analysis for: {search_query}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing topic {search_query}: {str(e)}")
            return {}
    
    def get_quota_status(self) -> Dict:
        """Get current API quota status."""
        return self.api.get_quota_status()

def main():
    """Command-line interface for the application."""
    parser = argparse.ArgumentParser(description="YouTube Data Scraper and Analyzer")
    
    parser.add_argument('--mode', choices=['video', 'channel', 'topic'],
                       required=True, help='Analysis mode')
    parser.add_argument('--id', help='Video ID or Channel ID')
    parser.add_argument('--query', help='Search query for topic analysis')
    parser.add_argument('--max-videos', type=int, default=10,
                       help='Maximum number of videos to analyze')
    parser.add_argument('--no-viz', action='store_true',
                       help='Disable visualization generation')
    parser.add_argument('--data-dir', default='data',
                       help='Directory for storing data')
    parser.add_argument('--viz-dir', default='visualizations',
                       help='Directory for storing visualizations')
    
    args = parser.parse_args()
    
    # Initialize application
    app = YouTubeDataApp(args.data_dir, args.viz_dir)
    
    try:
        if args.mode == 'video':
            if not args.id:
                raise ValueError("Video ID is required for video analysis mode")
            result = app.analyze_video(args.id, not args.no_viz)
            
        elif args.mode == 'channel':
            if not args.id:
                raise ValueError("Channel ID is required for channel analysis mode")
            result = app.analyze_channel(args.id, args.max_videos, not args.no_viz)
            
        elif args.mode == 'topic':
            if not args.query:
                raise ValueError("Search query is required for topic analysis mode")
            result = app.analyze_topic(args.query, args.max_videos, not args.no_viz)
        
        # Print results
        if result:
            print(json.dumps(result, indent=2))
        else:
            logger.error("Analysis failed")
            
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
