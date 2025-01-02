"""
Topic analysis module with caching and performance optimizations.
"""
from typing import Dict, List, Any, Optional
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
from functools import lru_cache
import hashlib
import logging
from loguru import logger
import time

class TopicAnalyzer:
    def __init__(self, cache_size: int = 128):
        """Initialize the topic analyzer with caching."""
        self.logger = logger.bind(module="topic_analyzer")
        self.logger.info("Initializing TopicAnalyzer with cache_size={}", cache_size)
        
        # Download required NLTK data if not already present
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('taggers/averaged_perceptron_tagger')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            self.logger.info("Downloading required NLTK data")
            nltk.download('punkt')
            nltk.download('averaged_perceptron_tagger')
            nltk.download('stopwords')
        
        self.stop_words = set(stopwords.words('english'))
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.kmeans = KMeans(n_clusters=5, random_state=42)
    
    @lru_cache(maxsize=128)
    def _generate_content_hash(self, content: str) -> str:
        """Generate a hash for content to use as cache key."""
        return hashlib.md5(content.encode()).hexdigest()
    
    @lru_cache(maxsize=128)
    def extract_key_phrases(self, content: str) -> List[str]:
        """Extract key phrases from content with caching."""
        start_time = time.time()
        self.logger.debug("Starting key phrase extraction for content length: {}", len(content))
        
        try:
            # Tokenize and tag parts of speech
            tokens = word_tokenize(content.lower())
            tagged = pos_tag(tokens)
            
            # Extract noun phrases
            phrases = []
            current_phrase = []
            
            for word, tag in tagged:
                if tag.startswith(('NN', 'JJ')):  # Nouns and adjectives
                    if word not in self.stop_words:
                        current_phrase.append(word)
                else:
                    if current_phrase:
                        phrase = ' '.join(current_phrase)
                        if len(phrase.split()) > 1:  # Only keep multi-word phrases
                            phrases.append(phrase)
                        current_phrase = []
            
            # Add the last phrase if exists
            if current_phrase:
                phrase = ' '.join(current_phrase)
                if len(phrase.split()) > 1:
                    phrases.append(phrase)
            
            elapsed_time = time.time() - start_time
            self.logger.info("Key phrase extraction completed in {:.2f}s. Found {} phrases", 
                           elapsed_time, len(phrases))
            
            return phrases
            
        except Exception as e:
            self.logger.error("Error in key phrase extraction: {}", str(e))
            return []
    
    @lru_cache(maxsize=128)
    def identify_topics(self, content: str, num_topics: int = 5) -> List[Dict[str, Any]]:
        """Identify topics in content with caching."""
        start_time = time.time()
        self.logger.debug("Starting topic identification with num_topics={}", num_topics)
        
        try:
            # Split into sentences for better topic modeling
            sentences = sent_tokenize(content)
            if not sentences:
                return []
            
            # Vectorize the text
            tfidf_matrix = self.vectorizer.fit_transform(sentences)
            
            # Adjust number of clusters based on content size
            actual_num_topics = min(num_topics, len(sentences))
            self.kmeans.n_clusters = actual_num_topics
            
            # Perform clustering
            clusters = self.kmeans.fit_predict(tfidf_matrix)
            
            # Extract topics
            topics = []
            feature_names = self.vectorizer.get_feature_names_out()
            
            for i in range(actual_num_topics):
                # Get top terms for this cluster
                center = self.kmeans.cluster_centers_[i]
                top_indices = center.argsort()[-5:][::-1]  # Top 5 terms
                terms = [feature_names[j] for j in top_indices]
                
                # Calculate cluster weight
                cluster_docs = [sent for j, sent in enumerate(sentences) if clusters[j] == i]
                weight = len(cluster_docs) / len(sentences)
                
                topics.append({
                    'id': i,
                    'terms': terms,
                    'weight': float(weight)
                })
            
            elapsed_time = time.time() - start_time
            self.logger.info("Topic identification completed in {:.2f}s. Found {} topics", 
                           elapsed_time, len(topics))
            
            return topics
            
        except Exception as e:
            self.logger.error("Error in topic identification: {}", str(e))
            return []
    
    def analyze_content_themes(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content themes with performance tracking."""
        start_time = time.time()
        self.logger.info("Starting content theme analysis for video_id: {}", 
                        video_data.get('video_id', 'unknown'))
        
        try:
            # Combine relevant text fields
            content = ' '.join(filter(None, [
                video_data.get('title', ''),
                video_data.get('description', ''),
                video_data.get('transcript', '')
            ]))
            
            if not content.strip():
                self.logger.warning("No content available for analysis")
                return {}
            
            # Generate content hash for cache key
            content_hash = self._generate_content_hash(content)
            
            # Extract key phrases and topics
            key_phrases = self.extract_key_phrases(content)
            topics = self.identify_topics(content)
            
            results = {
                'key_phrases': key_phrases,
                'topics': topics,
                'content_length': len(content),
                'sentence_count': len(sent_tokenize(content))
            }
            
            elapsed_time = time.time() - start_time
            self.logger.info("Content theme analysis completed in {:.2f}s", elapsed_time)
            
            return results
            
        except Exception as e:
            self.logger.error("Error in content theme analysis: {}", str(e))
            return {}
