"""
News Service - Handles news fetching and filtering
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncio
import aiohttp
import json
from utils.helpers import safe_request, load_data, save_data

class NewsService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.base_url = "https://newsapi.org/v2"
        self.preferences_file = "data/news_preferences.json"
        self.cache_file = "data/news_cache.json"
        
        if not self.news_api_key:
            self.logger.warning("News API key not found. News features will be disabled.")

    async def fetch_daily_news(self) -> List[Dict]:
        """Fetch daily news based on user preferences"""
        if not self.news_api_key:
            return []
        
        try:
            preferences = load_data(self.preferences_file)
            categories = preferences.get('categories', ['technology', 'business', 'science'])
            
            all_articles = []
            
            # Fetch news for each category
            for category in categories[:3]:  # Limit to 3 categories
                articles = await self._fetch_category_news(category)
                all_articles.extend(articles)
            
            # Also fetch tech news from specific sources
            tech_articles = await self._fetch_tech_news()
            all_articles.extend(tech_articles)
            
            # Remove duplicates and filter
            unique_articles = self._remove_duplicates(all_articles)
            filtered_articles = self._filter_articles(unique_articles)
            
            # Cache the results
            self._cache_articles(filtered_articles)
            
            return filtered_articles[:15]  # Top 15 articles
            
        except Exception as e:
            self.logger.error(f"Failed to fetch daily news: {e}")
            return []

    async def _fetch_category_news(self, category: str, page_size: int = 10) -> List[Dict]:
        """Fetch news for a specific category"""
        try:
            params = {
                'category': category,
                'country': 'us',  # Can be made configurable
                'pageSize': page_size,
                'apiKey': self.news_api_key
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/top-headlines"
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._process_articles(data.get('articles', []), category)
                    else:
                        self.logger.error(f"News API error for {category}: {response.status}")
                        return []
            
        except Exception as e:
            self.logger.error(f"Failed to fetch {category} news: {e}")
            return []

    async def _fetch_tech_news(self) -> List[Dict]:
        """Fetch tech news from specific sources"""
        try:
            tech_sources = [
                'techcrunch', 'the-verge', 'wired', 'ars-technica',
                'hacker-news', 'engadget'
            ]
            
            params = {
                'sources': ','.join(tech_sources[:3]),  # Use top 3 sources
                'pageSize': 15,
                'apiKey': self.news_api_key
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/top-headlines"
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._process_articles(data.get('articles', []), 'technology')
                    else:
                        self.logger.error(f"Tech news API error: {response.status}")
                        return []
            
        except Exception as e:
            self.logger.error(f"Failed to fetch tech news: {e}")
            return []

    def _process_articles(self, articles: List[Dict], category: str) -> List[Dict]:
        """Process and format news articles"""
        processed = []
        
        for article in articles:
            try:
                # Skip articles without essential info
                if not article.get('title') or not article.get('url'):
                    continue
                
                # Skip articles with [Removed] content
                if '[Removed]' in article.get('title', '') or '[Removed]' in article.get('description', ''):
                    continue
                
                processed_article = {
                    'title': article['title'],
                    'description': article.get('description', '')[:200] + "..." if article.get('description') else '',
                    'url': article['url'],
                    'source': article['source']['name'],
                    'author': article.get('author', ''),
                    'published_at': article['publishedAt'],
                    'url_to_image': article.get('urlToImage', ''),
                    'category': category,
                    'relevance_score': self._calculate_news_relevance(article, category),
                    'fetched_at': datetime.now().isoformat()
                }
                
                processed.append(processed_article)
                
            except Exception as e:
                self.logger.error(f"Failed to process article: {e}")
                continue
        
        return processed

    def _calculate_news_relevance(self, article: Dict, category: str) -> float:
        """Calculate news article relevance score"""
        score = 0.0
        
        # Base score
        score += 1.0
        
        # Boost for recent articles
        try:
            published = datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))
            hours_old = (datetime.now(published.tzinfo) - published).total_seconds() / 3600
            
            if hours_old <= 6:
                score += 1.0
            elif hours_old <= 24:
                score += 0.7
            elif hours_old <= 48:
                score += 0.4
        except:
            pass
        
        # Boost for tech-related content
        title_lower = article.get('title', '').lower()
        desc_lower = article.get('description', '').lower()
        
        tech_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'programming',
            'software', 'technology', 'startup', 'developer', 'coding',
            'python', 'javascript', 'github', 'tech', 'innovation'
        ]
        
        matching_keywords = 0
        for keyword in tech_keywords:
            if keyword in title_lower or keyword in desc_lower:
                matching_keywords += 1
        
        score += matching_keywords * 0.3
        
        # Boost for reputable tech sources
        source = article.get('source', {}).get('name', '').lower()
        reputable_sources = [
            'techcrunch', 'the verge', 'wired', 'ars technica',
            'hacker news', 'engadget', 'tech radar', 'zdnet'
        ]
        
        if any(rep_source in source for rep_source in reputable_sources):
            score += 0.5
        
        return score

    def _remove_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title similarity"""
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            title_key = article['title'].lower().replace(' ', '').replace('-', '')[:50]
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)
        
        return unique_articles

    def _filter_articles(self, articles: List[Dict]) -> List[Dict]:
        """Filter articles based on preferences and quality"""
        preferences = load_data(self.preferences_file)
        blocked_sources = preferences.get('blocked_sources', [])
        
        filtered = []
        for article in articles:
            # Skip blocked sources
            if article['source'].lower() in [source.lower() for source in blocked_sources]:
                continue
            
            # Skip articles with poor quality indicators
            if len(article['title']) < 10 or not article['description']:
                continue
            
            # Skip promotional content
            title_lower = article['title'].lower()
            if any(word in title_lower for word in ['sponsored', 'advertisement', 'promo']):
                continue
            
            filtered.append(article)
        
        # Sort by relevance score
        filtered.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return filtered

    def _cache_articles(self, articles: List[Dict]):
        """Cache articles for offline access"""
        try:
            cache_data = {
                'articles': articles,
                'cached_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=6)).isoformat()
            }
            save_data(self.cache_file, cache_data)
        except Exception as e:
            self.logger.error(f"Failed to cache articles: {e}")

    async def get_top_news(self, limit: int = 10) -> List[Dict]:
        """Get top news articles"""
        # Try to get from cache first
        try:
            cache = load_data(self.cache_file)
            expires_at = datetime.fromisoformat(cache['expires_at'])
            
            if datetime.now() < expires_at:
                return cache['articles'][:limit]
        except:
            pass
        
        # Fetch fresh news
        articles = await self.fetch_daily_news()
        return articles[:limit]

    async def search_news(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for news articles by query"""
        if not self.news_api_key:
            return []
        
        try:
            params = {
                'q': query,
                'sortBy': 'relevancy',
                'pageSize': limit,
                'apiKey': self.news_api_key
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/everything"
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._process_articles(data.get('articles', []), 'search')
                    else:
                        self.logger.error(f"News search API error: {response.status}")
                        return []
            
        except Exception as e:
            self.logger.error(f"Failed to search news: {e}")
            return []

    def get_news_preferences(self) -> Dict:
        """Get user's news preferences"""
        try:
            return load_data(self.preferences_file)
        except Exception as e:
            self.logger.error(f"Failed to get news preferences: {e}")
            return {
                'categories': ['technology', 'business', 'science'],
                'blocked_sources': []
            }

    def update_news_preferences(self, categories: List[str] = None, blocked_sources: List[str] = None) -> bool:
        """Update user's news preferences"""
        try:
            preferences = load_data(self.preferences_file)
            
            if categories is not None:
                preferences['categories'] = categories[:5]  # Max 5 categories
            
            if blocked_sources is not None:
                preferences['blocked_sources'] = blocked_sources
            
            save_data(self.preferences_file, preferences)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update news preferences: {e}")
            return False

    def mark_article_read(self, article_url: str):
        """Mark an article as read"""
        try:
            preferences = load_data(self.preferences_file)
            
            if 'read_articles' not in preferences:
                preferences['read_articles'] = []
            
            if article_url not in preferences['read_articles']:
                preferences['read_articles'].append(article_url)
            
            # Keep only last 1000 read articles
            preferences['read_articles'] = preferences['read_articles'][-1000:]
            
            save_data(self.preferences_file, preferences)
            
        except Exception as e:
            self.logger.error(f"Failed to mark article as read: {e}")

    def get_unread_articles(self, articles: List[Dict]) -> List[Dict]:
        """Filter out already read articles"""
        try:
            preferences = load_data(self.preferences_file)
            read_articles = preferences.get('read_articles', [])
            
            return [article for article in articles if article['url'] not in read_articles]
            
        except Exception as e:
            self.logger.error(f"Failed to filter unread articles: {e}")
            return articles

    async def get_programming_news(self) -> List[Dict]:
        """Get programming and development related news"""
        programming_queries = [
            'programming', 'software development', 'coding',
            'python', 'javascript', 'github', 'developer'
        ]
        
        all_articles = []
        for query in programming_queries[:2]:  # Limit queries
            articles = await self.search_news(query, limit=5)
            all_articles.extend(articles)
        
        # Remove duplicates and sort
        unique_articles = self._remove_duplicates(all_articles)
        unique_articles.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return unique_articles[:8]