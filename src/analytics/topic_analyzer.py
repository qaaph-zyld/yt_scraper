"""
Topic extraction and analysis module for YouTube video content.
"""

import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from typing import List, Dict, Any, Optional
import numpy as np
import logging

class TopicAnalyzer:
    """Analyzes topics and themes in YouTube video content."""
    
    def __init__(self):
        """Initialize the topic analyzer with necessary models and configurations."""
        self.logger = logging.getLogger(__name__)
        self.stop_words = set(stopwords.words('english'))
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
    def extract_key_phrases(self, text: Optional[str]) -> List[str]:
        """Extract key phrases from text using NLTK."""
        if not text:
            return []
            
        try:
            # Tokenize and tag parts of speech
            tokens = word_tokenize(text.lower())
            tagged = pos_tag(tokens)
            
            # Extract noun phrases and important words
            key_phrases = []
            current_phrase = []
            
            for word, tag in tagged:
                if word not in self.stop_words and len(word) > 2:
                    if tag.startswith(('NN', 'JJ')):  # Nouns and adjectives
                        current_phrase.append(word)
                    else:
                        if current_phrase:
                            key_phrases.append(' '.join(current_phrase))
                            current_phrase = []
            
            if current_phrase:
                key_phrases.append(' '.join(current_phrase))
                
            return list(set(key_phrases))  # Remove duplicates
            
        except Exception as e:
            self.logger.error(f"Error extracting key phrases: {str(e)}")
            return []
    
    def identify_topics(self, texts: Optional[List[str]], num_topics: int = 5) -> List[Dict[str, Any]]:
        """Identify main topics using TF-IDF and KMeans clustering."""
        if not texts:
            return []
            
        try:
            # Create TF-IDF matrix
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Perform clustering
            kmeans = KMeans(n_clusters=min(num_topics, len(texts)), random_state=42)
            kmeans.fit(tfidf_matrix)
            
            # Get top terms per cluster
            order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
            terms = self.vectorizer.get_feature_names_out()
            
            topics = []
            for i in range(kmeans.n_clusters):
                top_terms = [terms[ind] for ind in order_centroids[i, :10]]
                topics.append({
                    'id': i,
                    'terms': top_terms,
                    'weight': float(np.sum(kmeans.cluster_centers_[i]))
                })
                
            return topics
            
        except Exception as e:
            self.logger.error(f"Error identifying topics: {str(e)}")
            return []
    
    def analyze_content_themes(self, video_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content themes combining video metadata and transcript."""
        if not video_data:
            return {}
            
        try:
            # Combine title, description, and transcript
            text_content = ' '.join(filter(None, [
                video_data.get('title', ''),
                video_data.get('description', ''),
                video_data.get('transcript', '')
            ]))
            
            # Extract key phrases
            key_phrases = self.extract_key_phrases(text_content)
            
            # Analyze sentiment and themes
            sentences = sent_tokenize(text_content)
            
            # Get topics from sentences
            topics = self.identify_topics(sentences)
            
            return {
                'key_phrases': key_phrases,
                'topics': topics,
                'content_length': len(text_content),
                'sentence_count': len(sentences)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing content themes: {str(e)}")
            return {}
