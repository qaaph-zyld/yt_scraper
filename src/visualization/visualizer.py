import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Tuple
from datetime import datetime, timedelta
import os
from loguru import logger

class YouTubeVisualizer:
    """Visualizer for YouTube data analysis."""
    
    def __init__(self, output_dir: str = "visualizations"):
        """
        Initialize the visualizer.
        
        Args:
            output_dir: Directory to save visualizations
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn')
        sns.set_palette("husl")
    
    def plot_engagement_metrics(self, metadata: Dict, save: bool = True) -> str:
        """
        Create engagement metrics visualization.
        
        Args:
            metadata: Video metadata dictionary
            save: Whether to save the plot
            
        Returns:
            str: Path to saved plot if save=True, else empty string
        """
        try:
            # Prepare data
            metrics = {
                'Views': metadata['view_count'],
                'Likes': metadata['like_count'],
                'Comments': metadata['comment_count']
            }
            
            # Create figure
            plt.figure(figsize=(10, 6))
            
            # Create bar plot
            bars = plt.bar(metrics.keys(), metrics.values())
            
            # Customize plot
            plt.title(f"Engagement Metrics for Video: {metadata['title'][:50]}...")
            plt.ylabel('Count')
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:,.0f}',
                        ha='center', va='bottom')
            
            # Save or show plot
            if save:
                filename = f"engagement_metrics_{metadata['id']}.png"
                filepath = os.path.join(self.output_dir, filename)
                plt.savefig(filepath, bbox_inches='tight', dpi=300)
                plt.close()
                return filepath
            else:
                plt.show()
                plt.close()
                return ""
                
        except Exception as e:
            logger.error(f"Error creating engagement metrics plot: {str(e)}")
            return ""
    
    def plot_sentiment_distribution(self, sentiment_data: Dict, save: bool = True) -> str:
        """
        Create sentiment distribution visualization.
        
        Args:
            sentiment_data: Sentiment analysis results
            save: Whether to save the plot
            
        Returns:
            str: Path to saved plot if save=True, else empty string
        """
        try:
            # Prepare data
            sentiments = sentiment_data['sentiment_stats']
            
            # Create figure
            plt.figure(figsize=(10, 6))
            
            # Create pie chart
            plt.pie(sentiments.values(), labels=sentiments.keys(), autopct='%1.1f%%',
                   colors=sns.color_palette("husl", n_colors=len(sentiments)))
            
            # Customize plot
            plt.title("Sentiment Distribution in Comments")
            
            # Save or show plot
            if save:
                filename = "sentiment_distribution.png"
                filepath = os.path.join(self.output_dir, filename)
                plt.savefig(filepath, bbox_inches='tight', dpi=300)
                plt.close()
                return filepath
            else:
                plt.show()
                plt.close()
                return ""
                
        except Exception as e:
            logger.error(f"Error creating sentiment distribution plot: {str(e)}")
            return ""
    
    def plot_comment_activity(self, comments: List[Dict], save: bool = True) -> str:
        """
        Create comment activity timeline visualization.
        
        Args:
            comments: List of comment dictionaries
            save: Whether to save the plot
            
        Returns:
            str: Path to saved plot if save=True, else empty string
        """
        try:
            # Extract timestamps and convert to datetime
            timestamps = [datetime.fromisoformat(c['published_at'].replace('Z', '+00:00'))
                        for c in comments]
            
            # Create figure
            plt.figure(figsize=(12, 6))
            
            # Create histogram
            plt.hist(timestamps, bins=20, alpha=0.7)
            
            # Customize plot
            plt.title("Comment Activity Timeline")
            plt.xlabel("Time")
            plt.ylabel("Number of Comments")
            plt.xticks(rotation=45)
            
            # Save or show plot
            if save:
                filename = "comment_activity.png"
                filepath = os.path.join(self.output_dir, filename)
                plt.savefig(filepath, bbox_inches='tight', dpi=300)
                plt.close()
                return filepath
            else:
                plt.show()
                plt.close()
                return ""
                
        except Exception as e:
            logger.error(f"Error creating comment activity plot: {str(e)}")
            return ""
    
    def plot_keyword_trends(self, trends: Dict, save: bool = True) -> str:
        """
        Create keyword trends visualization.
        
        Args:
            trends: Keyword trend analysis results
            save: Whether to save the plot
            
        Returns:
            str: Path to saved plot if save=True, else empty string
        """
        try:
            # Create figure with two subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # Plot title trends
            title_words = [item['word'] for item in trends['title_trends']]
            title_counts = [item['count'] for item in trends['title_trends']]
            
            sns.barplot(x=title_counts, y=title_words, ax=ax1)
            ax1.set_title("Top Keywords in Titles")
            ax1.set_xlabel("Frequency")
            
            # Plot description trends
            desc_words = [item['word'] for item in trends['description_trends']]
            desc_counts = [item['count'] for item in trends['description_trends']]
            
            sns.barplot(x=desc_counts, y=desc_words, ax=ax2)
            ax2.set_title("Top Keywords in Descriptions")
            ax2.set_xlabel("Frequency")
            
            # Adjust layout
            plt.tight_layout()
            
            # Save or show plot
            if save:
                filename = "keyword_trends.png"
                filepath = os.path.join(self.output_dir, filename)
                plt.savefig(filepath, bbox_inches='tight', dpi=300)
                plt.close()
                return filepath
            else:
                plt.show()
                plt.close()
                return ""
                
        except Exception as e:
            logger.error(f"Error creating keyword trends plot: {str(e)}")
            return ""
    
    def create_dashboard(self, metadata: Dict, comments: List[Dict], 
                        sentiment_data: Dict, trends: Dict) -> str:
        """
        Create a comprehensive dashboard with all visualizations.
        
        Args:
            metadata: Video metadata
            comments: Video comments
            sentiment_data: Sentiment analysis results
            trends: Keyword trend analysis
            
        Returns:
            str: Path to saved dashboard
        """
        try:
            # Create figure with subplots
            fig = plt.figure(figsize=(20, 15))
            gs = fig.add_gridspec(3, 2)
            
            # Engagement metrics (top left)
            ax1 = fig.add_subplot(gs[0, 0])
            metrics = {
                'Views': metadata['view_count'],
                'Likes': metadata['like_count'],
                'Comments': metadata['comment_count']
            }
            bars = ax1.bar(metrics.keys(), metrics.values())
            ax1.set_title("Engagement Metrics")
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:,.0f}', ha='center', va='bottom')
            
            # Sentiment distribution (top right)
            ax2 = fig.add_subplot(gs[0, 1])
            sentiments = sentiment_data['sentiment_stats']
            ax2.pie(sentiments.values(), labels=sentiments.keys(), autopct='%1.1f%%',
                   colors=sns.color_palette("husl", n_colors=len(sentiments)))
            ax2.set_title("Sentiment Distribution")
            
            # Comment activity (middle)
            ax3 = fig.add_subplot(gs[1, :])
            timestamps = [datetime.fromisoformat(c['published_at'].replace('Z', '+00:00'))
                        for c in comments]
            ax3.hist(timestamps, bins=20, alpha=0.7)
            ax3.set_title("Comment Activity Timeline")
            ax3.set_xlabel("Time")
            ax3.set_ylabel("Number of Comments")
            plt.setp(ax3.get_xticklabels(), rotation=45)
            
            # Keywords in titles (bottom left)
            ax4 = fig.add_subplot(gs[2, 0])
            title_words = [item['word'] for item in trends['title_trends'][:5]]
            title_counts = [item['count'] for item in trends['title_trends'][:5]]
            sns.barplot(x=title_counts, y=title_words, ax=ax4)
            ax4.set_title("Top Keywords in Titles")
            
            # Keywords in descriptions (bottom right)
            ax5 = fig.add_subplot(gs[2, 1])
            desc_words = [item['word'] for item in trends['description_trends'][:5]]
            desc_counts = [item['count'] for item in trends['description_trends'][:5]]
            sns.barplot(x=desc_counts, y=desc_words, ax=ax5)
            ax5.set_title("Top Keywords in Descriptions")
            
            # Add title and adjust layout
            fig.suptitle(f"YouTube Video Analysis Dashboard\n{metadata['title'][:50]}...",
                        fontsize=16, y=1.02)
            plt.tight_layout()
            
            # Save dashboard
            filename = f"dashboard_{metadata['id']}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, bbox_inches='tight', dpi=300)
            plt.close()
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {str(e)}")
            return ""
