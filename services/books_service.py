"""
Books Service - Handles book recommendations and reading tracking
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncio
import aiohttp
import json
from utils.helpers import safe_request, load_data, save_data

class BooksService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.google_books_api_key = os.getenv('GOOGLE_BOOKS_API_KEY')
        self.base_url = "https://www.googleapis.com/books/v1"
        self.preferences_file = "data/book_preferences.json"
        
        if not self.google_books_api_key:
            self.logger.warning("Google Books API key not found. Some book features may be limited.")

    async def fetch_personalized_recommendations(self) -> List[Dict]:
        """Fetch personalized book recommendations"""
        try:
            preferences = load_data(self.preferences_file)
            interests = preferences.get('genres', ['programming', 'productivity', 'technology'])
            
            all_books = []
            
            for interest in interests[:3]:  # Top 3 interests
                books = await self._search_books(interest, max_results=5)
                all_books.extend(books)
            
            # Remove duplicates and sort by rating
            unique_books = {b['id']: b for b in all_books}.values()
            sorted_books = sorted(unique_books, key=lambda x: x.get('rating', 0), reverse=True)
            
            return list(sorted_books)[:8]
            
        except Exception as e:
            self.logger.error(f"Failed to fetch book recommendations: {e}")
            return []

    async def _search_books(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for books by query"""
        try:
            params = {
                'q': query,
                'maxResults': max_results,
                'orderBy': 'relevance',
                'printType': 'books',
                'key': self.google_books_api_key
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/volumes"
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._process_book_results(data.get('items', []))
                    else:
                        self.logger.error(f"Google Books API error: {response.status}")
                        return []
            
        except Exception as e:
            self.logger.error(f"Book search failed: {e}")
            return []

    def _process_book_results(self, items: List[Dict]) -> List[Dict]:
        """Process and format book search results"""
        books = []
        
        for item in items:
            try:
                volume_info = item.get('volumeInfo', {})
                
                # Skip books without essential info
                if not volume_info.get('title') or not volume_info.get('authors'):
                    continue
                
                book = {
                    'id': item['id'],
                    'title': volume_info['title'],
                    'authors': volume_info.get('authors', []),
                    'description': volume_info.get('description', '')[:300] + "..." if volume_info.get('description', '') else '',
                    'published_date': volume_info.get('publishedDate', ''),
                    'page_count': volume_info.get('pageCount', 0),
                    'categories': volume_info.get('categories', []),
                    'rating': volume_info.get('averageRating', 0),
                    'rating_count': volume_info.get('ratingsCount', 0),
                    'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail', ''),
                    'preview_link': volume_info.get('previewLink', ''),
                    'info_link': volume_info.get('infoLink', ''),
                    'language': volume_info.get('language', 'en'),
                    'relevance_score': self._calculate_book_relevance(volume_info)
                }
                
                books.append(book)
                
            except Exception as e:
                self.logger.error(f"Failed to process book item: {e}")
                continue
        
        return books

    def _calculate_book_relevance(self, volume_info: Dict) -> float:
        """Calculate book relevance score"""
        score = 0.0
        
        # Base score
        score += 1.0
        
        # Boost for high ratings
        rating = volume_info.get('averageRating', 0)
        if rating >= 4.5:
            score += 1.0
        elif rating >= 4.0:
            score += 0.7
        elif rating >= 3.5:
            score += 0.4
        
        # Boost for many ratings (popular books)
        rating_count = volume_info.get('ratingsCount', 0)
        if rating_count > 1000:
            score += 0.5
        elif rating_count > 100:
            score += 0.3
        
        # Boost for technical/programming books
        categories = volume_info.get('categories', [])
        tech_keywords = ['computers', 'programming', 'technology', 'business', 'self-help']
        if any(keyword.lower() in ' '.join(categories).lower() for keyword in tech_keywords):
            score += 0.6
        
        # Boost for recent books
        published_date = volume_info.get('publishedDate', '')
        if published_date:
            try:
                year = int(published_date.split('-')[0])
                current_year = datetime.now().year
                if current_year - year <= 3:
                    score += 0.4
                elif current_year - year <= 7:
                    score += 0.2
            except:
                pass
        
        return score

    async def get_book_details(self, book_id: str) -> Optional[Dict]:
        """Get detailed information about a specific book"""
        try:
            params = {}
            if self.google_books_api_key:
                params['key'] = self.google_books_api_key
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/volumes/{book_id}"
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_book_details(data)
                    return None
            
        except Exception as e:
            self.logger.error(f"Failed to get book details: {e}")
            return None

    def _format_book_details(self, item: Dict) -> Dict:
        """Format detailed book information"""
        volume_info = item.get('volumeInfo', {})
        
        return {
            'id': item['id'],
            'title': volume_info.get('title', ''),
            'subtitle': volume_info.get('subtitle', ''),
            'authors': volume_info.get('authors', []),
            'publisher': volume_info.get('publisher', ''),
            'published_date': volume_info.get('publishedDate', ''),
            'description': volume_info.get('description', ''),
            'page_count': volume_info.get('pageCount', 0),
            'categories': volume_info.get('categories', []),
            'rating': volume_info.get('averageRating', 0),
            'rating_count': volume_info.get('ratingsCount', 0),
            'language': volume_info.get('language', 'en'),
            'preview_link': volume_info.get('previewLink', ''),
            'info_link': volume_info.get('infoLink', ''),
            'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail', ''),
            'large_thumbnail': volume_info.get('imageLinks', {}).get('large', ''),
        }

    async def track_read_book(self, book_id: str, status: str = 'completed', rating: int = 5):
        """Track a read book"""
        try:
            preferences = load_data(self.preferences_file)
            
            if 'reading_history' not in preferences:
                preferences['reading_history'] = []
            
            # Get book details
            book_details = await self.get_book_details(book_id)
            
            read_record = {
                'book_id': book_id,
                'status': status,  # 'completed', 'reading', 'want_to_read'
                'date_added': datetime.now().isoformat(),
                'rating': rating,
                'title': book_details['title'] if book_details else '',
                'authors': book_details['authors'] if book_details else []
            }
            
            # Remove existing record if present
            preferences['reading_history'] = [
                record for record in preferences['reading_history'] 
                if record['book_id'] != book_id
            ]
            
            preferences['reading_history'].append(read_record)
            
            # Update genres based on read book
            if book_details and rating >= 4:
                await self._update_genres_from_book(book_details)
            
            save_data(self.preferences_file, preferences)
            
        except Exception as e:
            self.logger.error(f"Failed to track read book: {e}")

    async def _update_genres_from_book(self, book_details: Dict):
        """Update user's genre preferences based on read book"""
        try:
            preferences = load_data(self.preferences_file)
            
            if 'genres' not in preferences:
                preferences['genres'] = []
            
            # Extract genres from book categories
            categories = book_details.get('categories', [])
            
            # Map common categories to simplified genres
            genre_mapping = {
                'computers': 'programming',
                'technology': 'technology',
                'business': 'business',
                'self-help': 'self-improvement',
                'science': 'science',
                'biography': 'biography',
                'fiction': 'fiction',
                'history': 'history',
                'psychology': 'psychology'
            }
            
            for category in categories:
                category_lower = category.lower()
                for key, genre in genre_mapping.items():
                    if key in category_lower and genre not in preferences['genres']:
                        preferences['genres'].append(genre)
            
            # Keep only top 8 genres
            preferences['genres'] = preferences['genres'][:8]
            
            save_data(self.preferences_file, preferences)
            
        except Exception as e:
            self.logger.error(f"Failed to update genres: {e}")

    async def get_programming_books(self) -> List[Dict]:
        """Get programming and technical books"""
        programming_topics = ['python programming', 'javascript', 'web development', 'software engineering']
        
        all_books = []
        for topic in programming_topics:
            books = await self._search_books(topic, max_results=3)
            all_books.extend(books)
        
        # Remove duplicates and sort by relevance
        unique_books = {b['id']: b for b in all_books}.values()
        sorted_books = sorted(unique_books, key=lambda x: x['relevance_score'], reverse=True)
        
        return list(sorted_books)[:6]

    async def get_productivity_books(self) -> List[Dict]:
        """Get productivity and self-improvement books"""
        return await self._search_books('productivity self improvement', max_results=8)

    async def search_books_by_topic(self, topic: str, max_results: int = 10) -> List[Dict]:
        """Search books by specific topic"""
        return await self._search_books(topic, max_results)

    def get_reading_history(self, limit: int = 20) -> List[Dict]:
        """Get user's reading history"""
        try:
            preferences = load_data(self.preferences_file)
            history = preferences.get('reading_history', [])
            return history[-limit:] if history else []
        except Exception as e:
            self.logger.error(f"Failed to get reading history: {e}")
            return []

    def get_reading_stats(self) -> Dict:
        """Get reading statistics"""
        try:
            preferences = load_data(self.preferences_file)
            history = preferences.get('reading_history', [])
            
            total_books = len(history)
            completed_books = len([book for book in history if book['status'] == 'completed'])
            currently_reading = len([book for book in history if book['status'] == 'reading'])
            average_rating = sum(book.get('rating', 0) for book in history) / total_books if total_books > 0 else 0
            
            # Calculate books read this year
            current_year = datetime.now().year
            books_this_year = len([
                book for book in history 
                if book['status'] == 'completed' and 
                datetime.fromisoformat(book['date_added']).year == current_year
            ])
            
            return {
                'total_books': total_books,
                'completed_books': completed_books,
                'currently_reading': currently_reading,
                'books_this_year': books_this_year,
                'average_rating': round(average_rating, 1)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get reading stats: {e}")
            return {}

    def get_user_genres(self) -> List[str]:
        """Get user's preferred genres"""
        try:
            preferences = load_data(self.preferences_file)
            return preferences.get('genres', ['programming', 'productivity', 'technology'])
        except Exception as e:
            self.logger.error(f"Failed to get user genres: {e}")
            return ['programming', 'productivity', 'technology']

    def update_user_genres(self, genres: List[str]) -> bool:
        """Update user's preferred genres"""
        try:
            preferences = load_data(self.preferences_file)
            preferences['genres'] = genres[:8]  # Keep top 8
            save_data(self.preferences_file, preferences)
            return True
        except Exception as e:
            self.logger.error(f"Failed to update user genres: {e}")
            return False