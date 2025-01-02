from typing import Dict, List, Optional, Union, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from collections import Counter
from textblob import TextBlob
import re
from loguru import logger

class YouTubeAnalyzer:
    """Analyzer for YouTube video data and comments."""
    
    def __init__(self):
        """Initialize the analyzer."""
        self.sentiment_cache = {}
    
    def analyze_video_performance(self, metadata: Dict) -> Dict:
        """
        Analyze video performance metrics.
        
        Args:
            metadata: Video metadata dictionary
            
        Returns:
            dict: Performance metrics and insights
        """
        try:
            # Calculate engagement metrics
            total_engagement = metadata['view_count'] + metadata['like_count'] + metadata['comment_count']
            engagement_rate = (total_engagement / metadata['view_count']) * 100 if metadata['view_count'] > 0 else 0
            
            # Calculate like-to-view ratio
            like_view_ratio = (metadata['like_count'] / metadata['view_count']) * 100 if metadata['view_count'] > 0 else 0
            
            # Calculate comment-to-view ratio
            comment_view_ratio = (metadata['comment_count'] / metadata['view_count']) * 100 if metadata['view_count'] > 0 else 0
            
            # Calculate video age
            published_at = datetime.fromisoformat(metadata['published_at'].replace('Z', '+00:00'))
            video_age = datetime.now(published_at.tzinfo) - published_at
            
            # Calculate views per day
            views_per_day = metadata['view_count'] / max(video_age.days, 1)
            
            return {
                'video_id': metadata['id'],
                'title': metadata['title'],
                'total_engagement': total_engagement,
                'engagement_rate': round(engagement_rate, 2),
                'like_view_ratio': round(like_view_ratio, 2),
                'comment_view_ratio': round(comment_view_ratio, 2),
                'views_per_day': round(views_per_day, 2),
                'video_age_days': video_age.days
            }
        except Exception as e:
            logger.error(f"Error analyzing video performance: {str(e)}")
            return {}
    
    def analyze_comments_sentiment(self, comments: List[Dict]) -> Dict:
        """
        Analyze sentiment in video comments.
        
        Args:
            comments: List of comment dictionaries
            
        Returns:
            dict: Sentiment analysis results
        """
        try:
            sentiments = []
            reply_sentiments = []
            
            for comment in comments:
                # Analyze main comment
                comment_sentiment = self._get_sentiment(comment['text'])
                sentiments.append(comment_sentiment)
                
                # Analyze replies
                for reply in comment['replies']:
                    reply_sentiment = self._get_sentiment(reply['text'])
                    reply_sentiments.append(reply_sentiment)
            
            all_sentiments = sentiments + reply_sentiments
            
            if not all_sentiments:
                return {
                    'overall_sentiment': 'neutral',
                    'sentiment_stats': {'positive': 0, 'neutral': 0, 'negative': 0},
                    'average_polarity': 0,
                    'sentiment_distribution': {'comments': {}, 'replies': {}}
                }
            
            # Calculate sentiment distribution
            comment_distribution = self._calculate_sentiment_distribution(sentiments)
            reply_distribution = self._calculate_sentiment_distribution(reply_sentiments)
            
            # Calculate overall metrics
            avg_polarity = sum(s['polarity'] for s in all_sentiments) / len(all_sentiments)
            sentiment_counts = Counter(s['sentiment'] for s in all_sentiments)
            
            return {
                'overall_sentiment': max(sentiment_counts, key=sentiment_counts.get),
                'sentiment_stats': dict(sentiment_counts),
                'average_polarity': round(avg_polarity, 2),
                'sentiment_distribution': {
                    'comments': comment_distribution,
                    'replies': reply_distribution
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing comment sentiment: {str(e)}")
            return {}
    
    def _get_sentiment(self, text: str) -> Dict:
        """Get sentiment for a piece of text."""
        # Check cache first
        if text in self.sentiment_cache:
            return self.sentiment_cache[text]
        
        # Clean text
        cleaned_text = re.sub(r'[^\w\s]', '', text)
        
        # Get sentiment
        blob = TextBlob(cleaned_text)
        polarity = blob.sentiment.polarity
        
        # Determine sentiment category
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        result = {
            'polarity': polarity,
            'sentiment': sentiment
        }
        
        # Cache result
        self.sentiment_cache[text] = result
        return result
    
    def _calculate_sentiment_distribution(self, sentiments: List[Dict]) -> Dict:
        """Calculate distribution of sentiments."""
        if not sentiments:
            return {'positive': 0, 'neutral': 0, 'negative': 0}
            
        counts = Counter(s['sentiment'] for s in sentiments)
        total = len(sentiments)
        
        return {
            sentiment: round((count / total) * 100, 2)
            for sentiment, count in counts.items()
        }
    
    def analyze_keyword_trends(self, videos: List[Dict]) -> Dict:
        """
        Analyze keyword trends across videos.
        
        Args:
            videos: List of video metadata dictionaries
            
        Returns:
            dict: Keyword trend analysis
        """
        try:
            # Extract words from titles and descriptions
            title_words = []
            desc_words = []
            
            for video in videos:
                # Process title
                title_words.extend(self._extract_keywords(video['title']))
                
                # Process description
                desc_words.extend(self._extract_keywords(video['description']))
            
            # Get top keywords
            title_trends = Counter(title_words).most_common(10)
            desc_trends = Counter(desc_words).most_common(10)
            
            return {
                'title_trends': [{'word': word, 'count': count} for word, count in title_trends],
                'description_trends': [{'word': word, 'count': count} for word, count in desc_trends]
            }
        except Exception as e:
            logger.error(f"Error analyzing keyword trends: {str(e)}")
            return {}
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        # Common English stop words to filter out
        stop_words = {'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have',
                     'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you',
                     'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they',
                     'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one',
                     'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out',
                     'if', 'about', 'who', 'get', 'which', 'go', 'me'}
        
        # Clean and tokenize text
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out stop words and short words
        return [word for word in words if word not in stop_words and len(word) > 2]
    
    def generate_video_report(self, metadata: Dict, comments: List[Dict]) -> Dict:
        """
        Generate a comprehensive report for a video.
        
        Args:
            metadata: Video metadata
            comments: Video comments
            
        Returns:
            dict: Comprehensive video analysis report
        """
        try:
            # Get performance metrics
            performance = self.analyze_video_performance(metadata)
            
            # Get sentiment analysis
            sentiment = self.analyze_comments_sentiment(comments)
            
            # Analyze comment engagement
            comment_engagement = {
                'total_comments': len(comments),
                'total_replies': sum(len(c['replies']) for c in comments),
                'avg_replies_per_comment': round(sum(len(c['replies']) for c in comments) / max(len(comments), 1), 2),
                'avg_likes_per_comment': round(sum(c['like_count'] for c in comments) / max(len(comments), 1), 2)
            }
            
            # Get top comments
            top_comments = sorted(comments, key=lambda x: x['like_count'], reverse=True)[:5]
            
            return {
                'video_id': metadata['id'],
                'title': metadata['title'],
                'performance_metrics': performance,
                'sentiment_analysis': sentiment,
                'engagement_metrics': comment_engagement,
                'top_comments': [
                    {
                        'text': c['text'],
                        'likes': c['like_count'],
                        'replies': len(c['replies'])
                    }
                    for c in top_comments
                ]
            }
        except Exception as e:
            logger.error(f"Error generating video report: {str(e)}")
            return {}
