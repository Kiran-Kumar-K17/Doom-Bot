"""
Preference Engine - Handles machine learning for recommendations and user preference learning
"""

import logging
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from utils.helpers import load_data, save_data
from collections import defaultdict, Counter
import math

class PreferenceEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.history_file = "data/history.json"
        self.preferences_file = "data/user_preferences.json"
        self.content_pools = {
            'youtube': [],
            'books': [],
            'news': []
        }

    def update_content_pool(self, content_type: str, content: List[Dict]):
        """Update content pool with new recommendations"""
        if content_type in self.content_pools:
            self.content_pools[content_type] = content
            self.logger.debug(f"Updated {content_type} content pool with {len(content)} items")

    def get_recommendation(self, content_type: str) -> Optional[Dict]:
        """Get a personalized recommendation"""
        try:
            if content_type not in self.content_pools or not self.content_pools[content_type]:
                return None

            content_pool = self.content_pools[content_type]
            
            # Get user preferences and history
            preferences = self._get_user_preferences()
            interaction_history = self._get_interaction_history(content_type)
            
            # Score all content items
            scored_content = []
            for item in content_pool:
                score = self._calculate_recommendation_score(item, content_type, preferences, interaction_history)
                scored_content.append((item, score))
            
            # Sort by score and add some randomness to avoid always recommending the same thing
            scored_content.sort(key=lambda x: x[1], reverse=True)
            
            # Use weighted random selection from top 5 items
            top_items = scored_content[:5]
            if not top_items:
                return None
            
            # Weighted selection (higher scores more likely to be picked)
            weights = [score for _, score in top_items]
            selected_item = self._weighted_random_choice(top_items, weights)
            
            return selected_item[0] if selected_item else None
            
        except Exception as e:
            self.logger.error(f"Failed to get {content_type} recommendation: {e}")
            return None

    def _calculate_recommendation_score(self, item: Dict, content_type: str, 
                                       preferences: Dict, history: List[Dict]) -> float:
        """Calculate recommendation score for an item"""
        base_score = item.get('relevance_score', 1.0)
        
        # Preference matching score
        preference_score = self._calculate_preference_match(item, content_type, preferences)
        
        # Novelty score (prefer unseen content)
        novelty_score = self._calculate_novelty_score(item, content_type, history)
        
        # Diversity score (prefer varied content)
        diversity_score = self._calculate_diversity_score(item, content_type, history)
        
        # Time decay score (prefer recent content)
        time_score = self._calculate_time_score(item, content_type)
        
        # Combine scores with weights
        final_score = (
            base_score * 0.3 +
            preference_score * 0.35 +
            novelty_score * 0.15 +
            diversity_score * 0.10 +
            time_score * 0.10
        )
        
        return final_score

    def _calculate_preference_match(self, item: Dict, content_type: str, preferences: Dict) -> float:
        """Calculate how well item matches user preferences"""
        if content_type == 'youtube':
            return self._match_youtube_preferences(item, preferences)
        elif content_type == 'books':
            return self._match_book_preferences(item, preferences)
        elif content_type == 'news':
            return self._match_news_preferences(item, preferences)
        return 1.0

    def _match_youtube_preferences(self, video: Dict, preferences: Dict) -> float:
        """Match YouTube video to user preferences"""
        score = 0.0
        interests = preferences.get('youtube_interests', [])
        
        title_lower = video.get('title', '').lower()
        description_lower = video.get('description', '').lower()
        channel_lower = video.get('channel', '').lower()
        
        for interest in interests:
            interest_lower = interest.lower()
            if interest_lower in title_lower:
                score += 1.0
            elif interest_lower in description_lower:
                score += 0.6
            elif interest_lower in channel_lower:
                score += 0.4
        
        # Normalize by number of interests
        return min(score / max(len(interests), 1), 2.0)

    def _match_book_preferences(self, book: Dict, preferences: Dict) -> float:
        """Match book to user preferences"""
        score = 0.0
        preferred_genres = preferences.get('book_genres', [])
        preferred_authors = preferences.get('book_authors', [])
        
        # Genre matching
        book_categories = [cat.lower() for cat in book.get('categories', [])]
        for genre in preferred_genres:
            if any(genre.lower() in cat for cat in book_categories):
                score += 1.0
        
        # Author matching
        book_authors = [author.lower() for author in book.get('authors', [])]
        for pref_author in preferred_authors:
            if any(pref_author.lower() in author for author in book_authors):
                score += 2.0  # Author preference is stronger
        
        # Rating boost
        rating = book.get('rating', 0)
        if rating >= 4.0:
            score += 0.5
        
        return min(score, 3.0)

    def _match_news_preferences(self, article: Dict, preferences: Dict) -> float:
        """Match news article to user preferences"""
        score = 0.0
        preferred_categories = preferences.get('news_categories', [])
        preferred_sources = preferences.get('news_sources', [])
        
        # Category matching
        article_category = article.get('category', '').lower()
        if article_category in [cat.lower() for cat in preferred_categories]:
            score += 1.0
        
        # Source matching
        article_source = article.get('source', '').lower()
        if article_source in [source.lower() for source in preferred_sources]:
            score += 0.8
        
        return min(score, 2.0)

    def _calculate_novelty_score(self, item: Dict, content_type: str, history: List[Dict]) -> float:
        """Calculate novelty score (penalize already seen content)"""
        item_id = self._get_item_id(item, content_type)
        
        # Check if item was already interacted with
        for interaction in history:
            if interaction.get('item_id') == item_id:
                days_ago = (datetime.now() - datetime.fromisoformat(interaction['timestamp'])).days
                # Reduce penalty over time
                penalty = max(0.1, 1.0 - (0.1 * days_ago))
                return 1.0 - penalty
        
        return 1.0  # Full novelty score for unseen content

    def _calculate_diversity_score(self, item: Dict, content_type: str, history: List[Dict]) -> float:
        """Calculate diversity score to promote varied content"""
        if not history:
            return 1.0
        
        # Get recent items (last 10)
        recent_items = history[-10:]
        
        if content_type == 'youtube':
            return self._youtube_diversity_score(item, recent_items)
        elif content_type == 'books':
            return self._book_diversity_score(item, recent_items)
        elif content_type == 'news':
            return self._news_diversity_score(item, recent_items)
        
        return 1.0

    def _youtube_diversity_score(self, video: Dict, recent_items: List[Dict]) -> float:
        """Calculate YouTube diversity score"""
        video_channel = video.get('channel', '').lower()
        recent_channels = [item.get('channel', '').lower() for item in recent_items 
                          if item.get('channel')]
        
        # Penalize if same channel appears frequently in recent history
        channel_count = recent_channels.count(video_channel)
        if channel_count > 0:
            return max(0.3, 1.0 - (channel_count * 0.2))
        
        return 1.0

    def _book_diversity_score(self, book: Dict, recent_items: List[Dict]) -> float:
        """Calculate book diversity score"""
        book_categories = set(cat.lower() for cat in book.get('categories', []))
        
        recent_categories = []
        for item in recent_items:
            recent_categories.extend([cat.lower() for cat in item.get('categories', [])])
        
        category_overlap = len(book_categories.intersection(set(recent_categories)))
        
        if category_overlap > 0:
            return max(0.4, 1.0 - (category_overlap * 0.15))
        
        return 1.0

    def _news_diversity_score(self, article: Dict, recent_items: List[Dict]) -> float:
        """Calculate news diversity score"""
        article_category = article.get('category', '').lower()
        recent_categories = [item.get('category', '').lower() for item in recent_items]
        
        category_count = recent_categories.count(article_category)
        if category_count > 0:
            return max(0.5, 1.0 - (category_count * 0.1))
        
        return 1.0

    def _calculate_time_score(self, item: Dict, content_type: str) -> float:
        """Calculate time-based score (prefer recent content)"""
        try:
            if content_type == 'youtube':
                published_at = item.get('published_at')
            elif content_type == 'news':
                published_at = item.get('published_at')
            elif content_type == 'books':
                published_at = item.get('published_date')
            else:
                return 1.0
            
            if not published_at:
                return 0.8
            
            # Parse date
            if 'T' in published_at:
                pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            else:
                pub_date = datetime.strptime(published_at[:10], '%Y-%m-%d')
            
            days_old = (datetime.now(pub_date.tzinfo if pub_date.tzinfo else None) - pub_date).days
            
            # Higher score for more recent content
            if days_old <= 7:
                return 1.0
            elif days_old <= 30:
                return 0.8
            elif days_old <= 90:
                return 0.6
            elif days_old <= 365:
                return 0.4
            else:
                return 0.2
                
        except Exception as e:
            self.logger.debug(f"Failed to calculate time score: {e}")
            return 0.8

    def record_interaction(self, content_type: str, item: Dict, interaction_type: str, 
                          rating: Optional[int] = None, feedback: str = ""):
        """Record user interaction with content"""
        try:
            history = load_data(self.history_file)
            
            if 'user_interactions' not in history:
                history['user_interactions'] = []
            
            interaction_record = {
                'timestamp': datetime.now().isoformat(),
                'content_type': content_type,
                'item_id': self._get_item_id(item, content_type),
                'interaction_type': interaction_type,  # 'viewed', 'liked', 'completed', etc.
                'rating': rating,
                'feedback': feedback,
                'item_data': {
                    'title': item.get('title', ''),
                    'channel': item.get('channel', item.get('source', '')),
                    'category': item.get('category', ''),
                    'categories': item.get('categories', []),
                    'authors': item.get('authors', [])
                }
            }
            
            history['user_interactions'].append(interaction_record)
            
            # Keep only last 1000 interactions
            history['user_interactions'] = history['user_interactions'][-1000:]
            
            save_data(self.history_file, history)
            
            # Update preferences based on positive interactions
            if interaction_type in ['liked', 'completed'] or (rating and rating >= 4):
                self._update_preferences_from_interaction(content_type, item, rating or 5)
            
        except Exception as e:
            self.logger.error(f"Failed to record interaction: {e}")

    def _get_item_id(self, item: Dict, content_type: str) -> str:
        """Get unique identifier for an item"""
        if content_type == 'youtube':
            return item.get('video_id', item.get('url', ''))
        elif content_type == 'books':
            return item.get('id', '')
        elif content_type == 'news':
            return item.get('url', '')
        return str(hash(str(item)))

    def _get_user_preferences(self) -> Dict:
        """Get current user preferences"""
        try:
            preferences = load_data(self.preferences_file)
            
            # Set defaults if empty
            if not preferences:
                preferences = {
                    'youtube_interests': ['python programming', 'productivity', 'machine learning'],
                    'book_genres': ['programming', 'technology', 'productivity'],
                    'book_authors': [],
                    'news_categories': ['technology', 'business', 'science'],
                    'news_sources': []
                }
                save_data(self.preferences_file, preferences)
            
            return preferences
            
        except Exception as e:
            self.logger.error(f"Failed to get user preferences: {e}")
            return {}

    def _get_interaction_history(self, content_type: str, limit: int = 50) -> List[Dict]:
        """Get interaction history for specific content type"""
        try:
            history = load_data(self.history_file)
            all_interactions = history.get('user_interactions', [])
            
            # Filter by content type and get recent interactions
            filtered_interactions = [
                interaction for interaction in all_interactions
                if interaction.get('content_type') == content_type
            ]
            
            return filtered_interactions[-limit:] if filtered_interactions else []
            
        except Exception as e:
            self.logger.error(f"Failed to get interaction history: {e}")
            return []

    def _update_preferences_from_interaction(self, content_type: str, item: Dict, rating: int):
        """Update user preferences based on positive interaction"""
        try:
            preferences = self._get_user_preferences()
            
            if content_type == 'youtube' and rating >= 4:
                self._update_youtube_preferences(preferences, item)
            elif content_type == 'books' and rating >= 4:
                self._update_book_preferences(preferences, item)
            elif content_type == 'news' and rating >= 4:
                self._update_news_preferences(preferences, item)
            
            save_data(self.preferences_file, preferences)
            
        except Exception as e:
            self.logger.error(f"Failed to update preferences: {e}")

    def _update_youtube_preferences(self, preferences: Dict, video: Dict):
        """Update YouTube preferences based on liked video"""
        # Extract keywords from title and description
        title_words = video.get('title', '').lower().split()
        desc_words = video.get('description', '').lower().split()[:20]
        
        # Common tech keywords
        tech_keywords = [
            'python', 'javascript', 'programming', 'coding', 'tutorial',
            'machine learning', 'ai', 'development', 'software', 'tech'
        ]
        
        found_keywords = []
        for keyword in tech_keywords:
            if any(keyword in word for word in title_words + desc_words):
                found_keywords.append(keyword)
        
        # Add new interests
        current_interests = preferences.get('youtube_interests', [])
        for keyword in found_keywords:
            if keyword not in current_interests:
                current_interests.append(keyword)
        
        preferences['youtube_interests'] = current_interests[:10]  # Keep top 10

    def _update_book_preferences(self, preferences: Dict, book: Dict):
        """Update book preferences based on liked book"""
        # Add categories
        categories = book.get('categories', [])
        current_genres = preferences.get('book_genres', [])
        
        for category in categories:
            simplified_genre = category.lower().replace(' ', '')
            if simplified_genre not in current_genres:
                current_genres.append(simplified_genre)
        
        preferences['book_genres'] = current_genres[:8]
        
        # Add authors
        authors = book.get('authors', [])
        current_authors = preferences.get('book_authors', [])
        
        for author in authors:
            if author not in current_authors:
                current_authors.append(author)
        
        preferences['book_authors'] = current_authors[:15]

    def _update_news_preferences(self, preferences: Dict, article: Dict):
        """Update news preferences based on liked article"""
        # Add category
        category = article.get('category')
        if category:
            current_categories = preferences.get('news_categories', [])
            if category not in current_categories:
                current_categories.append(category)
            preferences['news_categories'] = current_categories[:6]
        
        # Add source
        source = article.get('source')
        if source:
            current_sources = preferences.get('news_sources', [])
            if source not in current_sources:
                current_sources.append(source)
            preferences['news_sources'] = current_sources[:10]

    def _weighted_random_choice(self, items: List, weights: List[float]):
        """Select item using weighted random selection"""
        if not items or not weights:
            return None
        
        total_weight = sum(weights)
        if total_weight <= 0:
            return random.choice(items)
        
        r = random.uniform(0, total_weight)
        cumulative_weight = 0
        
        for item, weight in zip(items, weights):
            cumulative_weight += weight
            if r <= cumulative_weight:
                return item
        
        return items[-1]  # Fallback to last item

    def get_user_insights(self) -> Dict:
        """Get insights about user preferences and behavior"""
        try:
            history = load_data(self.history_file)
            interactions = history.get('user_interactions', [])
            preferences = self._get_user_preferences()
            
            insights = {
                'total_interactions': len(interactions),
                'content_type_distribution': {},
                'most_active_days': [],
                'preferred_content': {},
                'engagement_trends': {}
            }
            
            # Analyze content type distribution
            content_counts = Counter(interaction.get('content_type') for interaction in interactions)
            insights['content_type_distribution'] = dict(content_counts)
            
            # Analyze engagement by day of week
            day_counts = defaultdict(int)
            for interaction in interactions:
                try:
                    timestamp = datetime.fromisoformat(interaction['timestamp'])
                    day_name = timestamp.strftime('%A')
                    day_counts[day_name] += 1
                except:
                    continue
            
            insights['most_active_days'] = sorted(day_counts.items(), key=lambda x: x[1], reverse=True)
            
            # Get current preferences
            insights['preferred_content'] = {
                'youtube_interests': preferences.get('youtube_interests', [])[:5],
                'book_genres': preferences.get('book_genres', [])[:5],
                'news_categories': preferences.get('news_categories', [])[:5]
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Failed to get user insights: {e}")
            return {}

    def reset_preferences(self):
        """Reset user preferences to defaults"""
        try:
            default_preferences = {
                'youtube_interests': ['python programming', 'productivity', 'machine learning'],
                'book_genres': ['programming', 'technology', 'productivity'],
                'book_authors': [],
                'news_categories': ['technology', 'business', 'science'],
                'news_sources': []
            }
            
            save_data(self.preferences_file, default_preferences)
            self.logger.info("User preferences reset to defaults")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reset preferences: {e}")
            return False