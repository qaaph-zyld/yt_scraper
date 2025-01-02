from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from dotenv import load_dotenv
from loguru import logger
import json
from typing import Dict, List, Optional, Union
from datetime import datetime
from ..storage import DataManager
from ..utils import RateLimiter
from ..validation import DataValidator

load_dotenv()

class YouTubeAPI:
    # YouTube API quotas (as of 2024)
    DEFAULT_QUOTAS = {
        'queries_per_day': {'tokens': 10000, 'interval': 86400},  # 10k units per day
        'queries_per_second': {'tokens': 10, 'interval': 1},      # 10 queries per second
        'queries_per_100seconds': {'tokens': 100, 'interval': 100}  # 100 queries per 100s
    }
    
    # Cost in quota units for different operations
    QUOTA_COSTS = {
        'list_videos': 1,        # videos.list
        'list_comments': 1,      # commentThreads.list
        'search_videos': 100,    # search.list
    }
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the YouTube API client.
        
        Args:
            data_dir (str): Directory for storing scraped data
        """
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YouTube API key not found in environment variables")
        
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.data_manager = DataManager(data_dir)
        self.rate_limiter = RateLimiter(self.DEFAULT_QUOTAS)
        self.validator = DataValidator()
        logger.info("YouTube API client initialized successfully")

    def _check_quota(self, operation: str, timeout: Optional[float] = None) -> bool:
        """Check if we have enough quota for the operation."""
        cost = self.QUOTA_COSTS.get(operation, 1)
        return self.rate_limiter.acquire(tokens=cost, timeout=timeout)

    def get_video_metadata(self, video_id: str, save: bool = True) -> Optional[Dict]:
        """
        Fetch metadata for a specific video.
        
        Args:
            video_id (str): YouTube video ID
            save (bool): Whether to save the metadata to file
            
        Returns:
            dict: Video metadata including title, description, views, likes, etc.
        """
        # Validate video ID
        if not self.validator.validate_video_id(video_id):
            logger.error(f"Invalid video ID format: {video_id}")
            return None
            
        if not self._check_quota('list_videos'):
            logger.warning("Rate limit exceeded for video metadata retrieval")
            return None
            
        try:
            request = self.youtube.videos().list(
                part="snippet,statistics",
                id=video_id
            )
            response = request.execute()
            
            if not response['items']:
                logger.warning(f"No video found with ID: {video_id}")
                return None
                
            video = response['items'][0]
            metadata = {
                'id': video_id,
                'title': video['snippet']['title'],
                'description': video['snippet'].get('description', ''),
                'published_at': video['snippet']['publishedAt'],
                'view_count': int(video['statistics'].get('viewCount', 0)),
                'like_count': int(video['statistics'].get('likeCount', 0)),
                'comment_count': int(video['statistics'].get('commentCount', 0))
            }
            
            # Validate metadata
            if not self.validator.validate_metadata(metadata):
                logger.error("Invalid metadata structure")
                return None
            
            if save:
                self.data_manager.save_video_metadata(metadata)
            
            logger.info(f"Successfully fetched metadata for video: {video_id}")
            return metadata
            
        except HttpError as e:
            logger.error(f"Error fetching video metadata: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None

    def get_video_comments(self, video_id: str, max_results: int = 100, save: bool = True) -> List[Dict]:
        """
        Fetch comments for a specific video.
        
        Args:
            video_id (str): YouTube video ID
            max_results (int): Maximum number of comments to retrieve
            save (bool): Whether to save the comments to file
            
        Returns:
            list: List of comment dictionaries containing author, text, likes, etc.
        """
        # Validate video ID
        if not self.validator.validate_video_id(video_id):
            logger.error(f"Invalid video ID format: {video_id}")
            return []
            
        if not self._check_quota('list_comments'):
            logger.warning("Rate limit exceeded for comment retrieval")
            return []
            
        try:
            comments = []
            request = self.youtube.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=min(max_results, 100),  # API limit is 100 per request
                order="relevance"
            )
            
            while request and len(comments) < max_results:
                if not self._check_quota('list_comments'):
                    logger.warning("Rate limit exceeded during comment pagination")
                    break
                    
                response = request.execute()
                
                for item in response['items']:
                    comment = item['snippet']['topLevelComment']['snippet']
                    
                    # Extract reply count and replies if available
                    reply_count = item['snippet'].get('totalReplyCount', 0)
                    replies = []
                    
                    if reply_count > 0 and 'replies' in item:
                        for reply in item['replies']['comments']:
                            reply_snippet = reply['snippet']
                            reply_data = {
                                'author': reply_snippet['authorDisplayName'],
                                'text': reply_snippet['textDisplay'],
                                'like_count': int(reply_snippet.get('likeCount', 0)),
                                'published_at': reply_snippet['publishedAt']
                            }
                            
                            # Validate reply
                            if self.validator.validate_reply(reply_data):
                                replies.append(reply_data)
                    
                    comment_data = {
                        'author': comment['authorDisplayName'],
                        'text': comment['textDisplay'],
                        'like_count': int(comment.get('likeCount', 0)),
                        'published_at': comment['publishedAt'],
                        'reply_count': len(replies),
                        'replies': replies
                    }
                    
                    # Validate comment
                    if self.validator.validate_comment(comment_data):
                        comments.append(comment_data)
                    
                    if len(comments) >= max_results:
                        break
                
                # Get the next page of comments if available
                if 'nextPageToken' in response and len(comments) < max_results:
                    request = self.youtube.commentThreads().list(
                        part="snippet,replies",
                        videoId=video_id,
                        maxResults=min(max_results - len(comments), 100),
                        pageToken=response['nextPageToken'],
                        order="relevance"
                    )
                else:
                    break
            
            if save and comments:
                self.data_manager.save_comments(video_id, comments)
                    
            logger.info(f"Successfully fetched {len(comments)} comments for video: {video_id}")
            return comments
            
        except HttpError as e:
            if e.resp.status == 403:
                logger.warning(f"Comments are disabled for video: {video_id}")
            else:
                logger.error(f"Error fetching video comments: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching comments: {str(e)}")
            return []
        
    def search_videos(self, query: str, max_results: int = 50, save: bool = True) -> List[Dict]:
        """
        Search for videos based on a query.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            save (bool): Whether to save the video metadata to files
            
        Returns:
            list: List of video metadata dictionaries
        """
        if not query or not isinstance(query, str):
            logger.error("Invalid search query")
            return []
            
        if not self._check_quota('search_videos'):
            logger.warning("Rate limit exceeded for video search")
            return []
            
        try:
            request = self.youtube.search().list(
                part="id,snippet",
                q=query,
                type="video",
                maxResults=max_results
            )
            response = request.execute()
            
            videos = []
            for item in response['items']:
                video_id = item['id']['videoId']
                if self.validator.validate_video_id(video_id):
                    metadata = self.get_video_metadata(video_id, save=save)
                    if metadata:
                        videos.append(metadata)
                    
            logger.info(f"Found {len(videos)} videos for query: {query}")
            return videos
            
        except HttpError as e:
            logger.error(f"Error searching videos: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return []
            
    def get_quota_status(self) -> Dict[str, Dict[str, float]]:
        """Get current status of API quotas."""
        return self.rate_limiter.get_quota_status()
