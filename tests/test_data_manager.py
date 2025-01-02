import pytest
import os
import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage.data_manager import DataManager

@pytest.fixture
def data_manager(tmp_path):
    """Create a DataManager instance with a temporary directory."""
    return DataManager(base_dir=str(tmp_path))

@pytest.fixture
def sample_metadata():
    """Create sample video metadata."""
    return {
        'id': 'test123',
        'title': 'Test Video',
        'description': 'Test Description',
        'published_at': '2025-01-02T00:00:00Z',
        'view_count': 1000,
        'like_count': 100,
        'comment_count': 50
    }

@pytest.fixture
def sample_comments():
    """Create sample video comments."""
    return [
        {
            'author': 'User1',
            'text': 'Great video!',
            'like_count': 10,
            'published_at': '2025-01-02T01:00:00Z',
            'reply_count': 2,
            'replies': [
                {
                    'author': 'User2',
                    'text': 'Thanks!',
                    'like_count': 5,
                    'published_at': '2025-01-02T01:30:00Z'
                },
                {
                    'author': 'User3',
                    'text': 'Agreed!',
                    'like_count': 3,
                    'published_at': '2025-01-02T02:00:00Z'
                }
            ]
        }
    ]

def test_directory_creation(data_manager):
    """Test that necessary directories are created."""
    for dir_name in ['videos', 'comments', 'analytics']:
        assert (Path(data_manager.base_dir) / dir_name).exists()

def test_save_load_metadata_json(data_manager, sample_metadata):
    """Test saving and loading video metadata in JSON format."""
    # Save metadata
    file_path = data_manager.save_video_metadata(sample_metadata, format='json')
    assert file_path.exists()
    
    # Load metadata
    loaded_metadata = data_manager.load_video_metadata(file_path)
    assert loaded_metadata == sample_metadata

def test_save_load_metadata_csv(data_manager, sample_metadata):
    """Test saving and loading video metadata in CSV format."""
    # Save metadata
    file_path = data_manager.save_video_metadata(sample_metadata, format='csv')
    assert file_path.exists()
    
    # Load metadata
    loaded_metadata = data_manager.load_video_metadata(file_path)
    assert loaded_metadata['id'] == sample_metadata['id']
    assert loaded_metadata['title'] == sample_metadata['title']

def test_save_load_comments_json(data_manager, sample_comments):
    """Test saving and loading comments in JSON format."""
    # Save comments
    file_path = data_manager.save_comments('test123', sample_comments, format='json')
    assert file_path.exists()
    
    # Load comments
    loaded_comments = data_manager.load_comments(file_path)
    assert loaded_comments == sample_comments

def test_save_load_comments_csv(data_manager, sample_comments):
    """Test saving and loading comments in CSV format."""
    # Save comments
    file_path = data_manager.save_comments('test123', sample_comments, format='csv')
    assert file_path.exists()
    
    # Load comments
    loaded_comments = data_manager.load_comments(file_path)
    assert len(loaded_comments) == len(sample_comments)
    assert loaded_comments[0]['author'] == sample_comments[0]['author']
    assert len(loaded_comments[0]['replies']) == len(sample_comments[0]['replies'])

def test_error_handling(data_manager):
    """Test error handling for non-existent files."""
    assert data_manager.load_video_metadata('nonexistent.json') is None
    assert data_manager.load_comments('nonexistent.json') is None
