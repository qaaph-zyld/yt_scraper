"""
Visualization module for topic analysis results.
"""
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any
import numpy as np
from pathlib import Path
import logging

class TopicVisualizer:
    def __init__(self, output_dir: str = "output/visualizations"):
        """Initialize the topic visualizer."""
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style
        sns.set_theme(style="whitegrid")
    
    def plot_topic_distribution(self, topics: List[Dict[str, Any]], title: str = "Topic Distribution") -> str:
        """Create a bar plot showing topic distribution and weights."""
        try:
            if not topics:
                self.logger.warning("No topics provided for visualization")
                return ""
                
            # Extract data
            weights = [topic['weight'] for topic in topics]
            labels = [f"Topic {topic['id']}" for topic in topics]
            
            # Create plot
            plt.figure(figsize=(12, 6))
            sns.barplot(x=labels, y=weights)
            plt.title(title)
            plt.xlabel("Topics")
            plt.ylabel("Weight")
            plt.xticks(rotation=45)
            
            # Save plot
            output_path = self.output_dir / f"{title.lower().replace(' ', '_')}.png"
            plt.savefig(output_path, bbox_inches='tight')
            plt.close()
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error creating topic distribution plot: {str(e)}")
            return ""
    
    def plot_key_phrases_cloud(self, key_phrases: List[str], title: str = "Key Phrases") -> str:
        """Create a word cloud visualization of key phrases."""
        try:
            if not key_phrases:
                self.logger.warning("No key phrases provided for visualization")
                return ""
            
            # Create frequency distribution
            phrase_freq = {}
            for phrase in key_phrases:
                phrase_freq[phrase] = phrase_freq.get(phrase, 0) + 1
            
            # Create horizontal bar plot for top phrases
            plt.figure(figsize=(12, 8))
            phrases = list(phrase_freq.keys())[:10]  # Top 10 phrases
            freqs = [phrase_freq[p] for p in phrases]
            
            sns.barplot(y=phrases, x=freqs, orient='h')
            plt.title(title)
            plt.xlabel("Frequency")
            plt.ylabel("Phrases")
            
            # Save plot
            output_path = self.output_dir / f"{title.lower().replace(' ', '_')}.png"
            plt.savefig(output_path, bbox_inches='tight')
            plt.close()
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error creating key phrases cloud: {str(e)}")
            return ""
    
    def create_topic_summary_report(self, analysis_results: Dict[str, Any]) -> Dict[str, str]:
        """Create a comprehensive visualization report of topic analysis results."""
        try:
            plots = {}
            
            # Plot topic distribution
            if 'topics' in analysis_results:
                plot_path = self.plot_topic_distribution(analysis_results['topics'])
                if plot_path:
                    plots['topic_distribution'] = plot_path
            
            # Plot key phrases
            if 'key_phrases' in analysis_results:
                plot_path = self.plot_key_phrases_cloud(analysis_results['key_phrases'])
                if plot_path:
                    plots['key_phrases'] = plot_path
            
            return plots
            
        except Exception as e:
            self.logger.error(f"Error creating topic summary report: {str(e)}")
            return {}
