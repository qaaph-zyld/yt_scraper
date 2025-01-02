import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Union, Optional
from loguru import logger

class DataManager:
    def __init__(self, base_dir: str = "data"):
        """
        Initialize the DataManager with a base directory for data storage.
        
        Args:
            base_dir (str): Base directory for storing data files
        """
        self.base_dir = Path(base_dir)
        self._ensure_directories()
        
    def _ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        directories = ['videos', 'comments', 'analytics']
        for dir_name in directories:
            dir_path = self.base_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            
    def _get_timestamp(self) -> str:
        """Get current timestamp in a file-friendly format."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def save_video_metadata(self, metadata: Dict, format: str = 'json') -> Path:
        """
        Save video metadata to file.
        
        Args:
            metadata (dict): Video metadata
            format (str): Output format ('json' or 'csv')
            
        Returns:
            Path: Path to the saved file
        """
        video_id = metadata['id']
        timestamp = self._get_timestamp()
        
        if format.lower() == 'json':
            file_path = self.base_dir / 'videos' / f"{video_id}_{timestamp}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        else:
            file_path = self.base_dir / 'videos' / f"{video_id}_{timestamp}.csv"
            df = pd.DataFrame([metadata])
            df.to_csv(file_path, index=False, encoding='utf-8')
            
        logger.info(f"Saved video metadata to {file_path}")
        return file_path
    
    def save_comments(self, video_id: str, comments: List[Dict], format: str = 'json') -> Path:
        """
        Save video comments to file.
        
        Args:
            video_id (str): YouTube video ID
            comments (list): List of comment dictionaries
            format (str): Output format ('json' or 'csv')
            
        Returns:
            Path: Path to the saved file
        """
        timestamp = self._get_timestamp()
        
        if format.lower() == 'json':
            file_path = self.base_dir / 'comments' / f"{video_id}_comments_{timestamp}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(comments, f, indent=2, ensure_ascii=False)
        else:
            file_path = self.base_dir / 'comments' / f"{video_id}_comments_{timestamp}.csv"
            # Flatten nested comments for CSV format
            flattened_comments = []
            for comment in comments:
                comment_data = {
                    'video_id': video_id,
                    'author': comment['author'],
                    'text': comment['text'],
                    'like_count': comment['like_count'],
                    'published_at': comment['published_at'],
                    'is_reply': False,
                    'parent_author': None
                }
                flattened_comments.append(comment_data)
                
                # Add replies
                for reply in comment.get('replies', []):
                    reply_data = {
                        'video_id': video_id,
                        'author': reply['author'],
                        'text': reply['text'],
                        'like_count': reply['like_count'],
                        'published_at': reply['published_at'],
                        'is_reply': True,
                        'parent_author': comment['author']
                    }
                    flattened_comments.append(reply_data)
            
            df = pd.DataFrame(flattened_comments)
            df.to_csv(file_path, index=False, encoding='utf-8')
            
        logger.info(f"Saved {len(comments)} comments to {file_path}")
        return file_path
    
    def load_video_metadata(self, file_path: Union[str, Path]) -> Optional[Dict]:
        """
        Load video metadata from file.
        
        Args:
            file_path (str or Path): Path to the metadata file
            
        Returns:
            dict: Video metadata or None if file doesn't exist
        """
        file_path = Path(file_path)
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return None
            
        try:
            if file_path.suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                df = pd.read_csv(file_path, encoding='utf-8')
                return df.to_dict('records')[0]
        except Exception as e:
            logger.error(f"Error loading metadata from {file_path}: {str(e)}")
            return None
    
    def load_comments(self, file_path: Union[str, Path]) -> Optional[List[Dict]]:
        """
        Load comments from file.
        
        Args:
            file_path (str or Path): Path to the comments file
            
        Returns:
            list: List of comments or None if file doesn't exist
        """
        file_path = Path(file_path)
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return None
            
        try:
            if file_path.suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                df = pd.read_csv(file_path, encoding='utf-8')
                # Reconstruct nested structure for CSV
                comments = []
                base_comments = df[~df['is_reply']].to_dict('records')
                replies = df[df['is_reply']].to_dict('records')
                
                for comment in base_comments:
                    comment_replies = [
                        {
                            'author': r['author'],
                            'text': r['text'],
                            'like_count': r['like_count'],
                            'published_at': r['published_at']
                        }
                        for r in replies
                        if r['parent_author'] == comment['author']
                    ]
                    
                    comments.append({
                        'author': comment['author'],
                        'text': comment['text'],
                        'like_count': comment['like_count'],
                        'published_at': comment['published_at'],
                        'reply_count': len(comment_replies),
                        'replies': comment_replies
                    })
                    
                return comments
        except Exception as e:
            logger.error(f"Error loading comments from {file_path}: {str(e)}")
            return None
