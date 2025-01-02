"""
Data analysis module for YouTube video data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from textblob import TextBlob
import logging
from collections import Counter

class YouTubeDataAnalyzer:
    """Analyzes YouTube video data to extract insights and trends."""
    
    def __init__(self):
        """Initialize the analyzer with necessary configurations."""
        self.logger = logging.getLogger(__name__)
    
    def analyze_video_performance(self, video_data: Dict) -> Dict:
        """
        Analyze video performance metrics.
        
        Args:
            video_data: Dictionary containing video metadata
            
        Returns:
            Dictionary containing performance metrics
        """
        try:
            metrics = {
                'total_engagement': int(video_data.get('view_count', 0)),
                'likes': int(video_data.get('like_count', 0)),
                'comments': int(video_data.get('comment_count', 0))
            }
            
            # Calculate engagement rate (likes + comments / views)
            if metrics['total_engagement'] > 0:
                metrics['engagement_rate'] = round(
                    ((metrics['likes'] + metrics['comments']) / 
                     metrics['total_engagement']) * 100, 2
                )
            else:
                metrics['engagement_rate'] = 0.0
            
            # Calculate average engagement per day since publication
            published_at = video_data.get('published_at', '')
            if published_at:
                try:
                    # Convert to UTC datetime object
                    published_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    now = datetime.now(published_date.tzinfo)  # Use same timezone as published_date
                    days_since_published = (now - published_date).days or 1
                    
                    metrics['avg_daily_views'] = round(
                        metrics['total_engagement'] / days_since_published, 2
                    )
                except (ValueError, AttributeError) as e:
                    self.logger.warning(f"Error parsing published_at date: {str(e)}")
                    metrics['avg_daily_views'] = metrics['total_engagement']
            else:
                metrics['avg_daily_views'] = metrics['total_engagement']
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error analyzing video performance: {str(e)}")
            return {
                'total_engagement': 0,
                'likes': 0,
                'comments': 0,
                'engagement_rate': 0.0,
                'avg_daily_views': 0.0
            }
    
    def analyze_comments_sentiment(self, comments: List[Dict]) -> Dict:
        """
        Perform sentiment analysis on video comments.
        
        Args:
            comments: List of comment dictionaries
            
        Returns:
            Dictionary containing sentiment metrics
        """
        try:
            if not comments:
                return {
                    'average_sentiment': 0,
                    'sentiment_distribution': {
                        'positive': 0,
                        'neutral': 0,
                        'negative': 0
                    },
                    'total_comments': 0
                }
            
            sentiments = []
            sentiment_dist = {'positive': 0, 'neutral': 0, 'negative': 0}
            
            for comment in comments:
                text = comment.get('text', '')
                if not text:
                    continue
                    
                # Analyze sentiment using TextBlob
                sentiment = TextBlob(text).sentiment.polarity
                sentiments.append(sentiment)
                
                # Categorize sentiment
                if sentiment > 0.1:
                    sentiment_dist['positive'] += 1
                elif sentiment < -0.1:
                    sentiment_dist['negative'] += 1
                else:
                    sentiment_dist['neutral'] += 1
            
            # Calculate metrics
            total_analyzed = len(sentiments) or 1
            sentiment_dist = {
                k: round((v / total_analyzed) * 100, 2)
                for k, v in sentiment_dist.items()
            }
            
            return {
                'average_sentiment': round(sum(sentiments) / len(sentiments), 2) if sentiments else 0,
                'sentiment_distribution': sentiment_dist,
                'total_comments': len(comments)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing comment sentiment: {str(e)}")
            return {
                'average_sentiment': 0,
                'sentiment_distribution': {
                    'positive': 0,
                    'neutral': 0,
                    'negative': 0
                },
                'total_comments': 0
            }
    
    def analyze_keyword_trends(self, videos: List[Dict]) -> Dict:
        """
        Analyze keyword trends across multiple videos.
        
        Args:
            videos: List of video metadata dictionaries
            
        Returns:
            Dictionary containing keyword trend analysis
        """
        try:
            # Extract words from titles and descriptions
            title_words = []
            desc_words = []
            
            for video in videos:
                # Process title
                if title := video.get('title', ''):
                    words = title.lower().split()
                    title_words.extend(words)
                
                # Process description
                if desc := video.get('description', ''):
                    words = desc.lower().split()
                    desc_words.extend(words)
            
            # Count word frequencies
            title_freq = Counter(title_words)
            desc_freq = Counter(desc_words)
            
            # Convert to sorted lists of dictionaries
            title_trends = [
                {'word': word, 'count': count}
                for word, count in title_freq.most_common(20)
            ]
            
            desc_trends = [
                {'word': word, 'count': count}
                for word, count in desc_freq.most_common(20)
            ]
            
            return {
                'title_trends': title_trends,
                'description_trends': desc_trends,
                'total_videos_analyzed': len(videos)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing keyword trends: {str(e)}")
            return {
                'title_trends': [],
                'description_trends': [],
                'total_videos_analyzed': 0
            }
    
    def generate_video_report(self, video_data: Dict, comments: List[Dict]) -> Dict:
        """
        Generate a comprehensive report for a video.
        
        Args:
            video_data: Dictionary containing video metadata
            comments: List of comment dictionaries
            
        Returns:
            Dictionary containing the complete analysis report
        """
        try:
            # Get performance metrics
            performance = self.analyze_video_performance(video_data)
            
            # Get sentiment analysis
            sentiment = self.analyze_comments_sentiment(comments)
            
            # Generate report
            report = {
                'video_id': video_data.get('id', ''),
                'title': video_data.get('title', ''),
                'analysis_timestamp': datetime.now().isoformat(),
                'performance_metrics': performance,
                'sentiment_analysis': sentiment,
                'metadata': {
                    'duration': video_data.get('duration', ''),
                    'published_at': video_data.get('published_at', ''),
                    'channel_id': video_data.get('channel_id', ''),
                    'channel_title': video_data.get('channel_title', '')
                }
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating video report: {str(e)}")
            return {}
