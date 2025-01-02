from datetime import datetime
from typing import Dict, List, Optional, Union
from loguru import logger
import re

class DataValidator:
    """Validator for YouTube data structures."""
    
    # Regular expressions for validation
    YOUTUBE_ID_PATTERN = r'^[a-zA-Z0-9_-]{11}$'
    URL_PATTERN = r'^https?://(?:www\.)?youtube\.com/watch\?v=[a-zA-Z0-9_-]{11}(?:&.*)?$'
    
    @staticmethod
    def validate_video_id(video_id: str) -> bool:
        """
        Validate YouTube video ID format.
        
        Args:
            video_id: YouTube video ID to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(video_id, str):
            return False
        return bool(re.match(DataValidator.YOUTUBE_ID_PATTERN, video_id))
    
    @staticmethod
    def validate_youtube_url(url: str) -> bool:
        """
        Validate YouTube video URL format.
        
        Args:
            url: YouTube URL to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(url, str):
            return False
        return bool(re.match(DataValidator.URL_PATTERN, url))
    
    @staticmethod
    def extract_video_id_from_url(url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL.
        
        Args:
            url: YouTube URL
            
        Returns:
            str: Video ID if valid URL, None otherwise
        """
        if not DataValidator.validate_youtube_url(url):
            return None
        
        try:
            # Extract v parameter from URL
            video_id = re.search(r'v=([a-zA-Z0-9_-]{11})', url).group(1)
            return video_id if DataValidator.validate_video_id(video_id) else None
        except (AttributeError, IndexError):
            return None
    
    @staticmethod
    def validate_metadata(metadata: Dict) -> bool:
        """
        Validate video metadata structure.
        
        Args:
            metadata: Video metadata dictionary
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = {
            'id': str,
            'title': str,
            'description': str,
            'published_at': str,
            'view_count': int,
            'like_count': int,
            'comment_count': int
        }
        
        try:
            # Check all required fields exist and have correct types
            for field, field_type in required_fields.items():
                if field not in metadata:
                    logger.warning(f"Missing required field: {field}")
                    return False
                if not isinstance(metadata[field], field_type):
                    logger.warning(f"Invalid type for field {field}: expected {field_type}, got {type(metadata[field])}")
                    return False
            
            # Validate video ID format
            if not DataValidator.validate_video_id(metadata['id']):
                logger.warning("Invalid video ID format")
                return False
            
            # Validate published_at datetime format
            try:
                datetime.fromisoformat(metadata['published_at'].replace('Z', '+00:00'))
            except ValueError:
                logger.warning("Invalid published_at datetime format")
                return False
            
            # Validate numeric fields are non-negative
            for field in ['view_count', 'like_count', 'comment_count']:
                if metadata[field] < 0:
                    logger.warning(f"Negative value for {field}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating metadata: {str(e)}")
            return False
    
    @staticmethod
    def validate_comment(comment: Dict) -> bool:
        """
        Validate comment structure.
        
        Args:
            comment: Comment dictionary
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = {
            'author': str,
            'text': str,
            'like_count': int,
            'published_at': str,
            'reply_count': int,
            'replies': list
        }
        
        try:
            # Check all required fields exist and have correct types
            for field, field_type in required_fields.items():
                if field not in comment:
                    logger.warning(f"Missing required field: {field}")
                    return False
                if not isinstance(comment[field], field_type):
                    logger.warning(f"Invalid type for field {field}: expected {field_type}, got {type(comment[field])}")
                    return False
            
            # Validate published_at datetime format
            try:
                datetime.fromisoformat(comment['published_at'].replace('Z', '+00:00'))
            except ValueError:
                logger.warning("Invalid published_at datetime format")
                return False
            
            # Validate numeric fields are non-negative
            if comment['like_count'] < 0 or comment['reply_count'] < 0:
                logger.warning("Negative value for like_count or reply_count")
                return False
            
            # Validate reply_count matches actual replies
            if comment['reply_count'] != len(comment['replies']):
                logger.warning("reply_count does not match number of replies")
                return False
            
            # Validate each reply
            for reply in comment['replies']:
                if not DataValidator.validate_reply(reply):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating comment: {str(e)}")
            return False
    
    @staticmethod
    def validate_reply(reply: Dict) -> bool:
        """
        Validate reply structure.
        
        Args:
            reply: Reply dictionary
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = {
            'author': str,
            'text': str,
            'like_count': int,
            'published_at': str
        }
        
        try:
            # Check all required fields exist and have correct types
            for field, field_type in required_fields.items():
                if field not in reply:
                    logger.warning(f"Missing required field in reply: {field}")
                    return False
                if not isinstance(reply[field], field_type):
                    logger.warning(f"Invalid type for field {field} in reply: expected {field_type}, got {type(reply[field])}")
                    return False
            
            # Validate published_at datetime format
            try:
                datetime.fromisoformat(reply['published_at'].replace('Z', '+00:00'))
            except ValueError:
                logger.warning("Invalid published_at datetime format in reply")
                return False
            
            # Validate like_count is non-negative
            if reply['like_count'] < 0:
                logger.warning("Negative value for like_count in reply")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating reply: {str(e)}")
            return False
