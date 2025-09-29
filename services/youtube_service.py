"""
YouTube Service - Handles YouTube API interactions for video recommendations and learning content
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncio
import aiohttp
import json
from utils.helpers import safe_request, load_data, save_data

class YouTubeService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.preferences_file = "data/youtube_preferences.json"
        
        if not self.api_key:
            self.logger.warning("YouTube API key not found. YouTube features will be disabled.")

    async def fetch_personalized_content(self) -> List[Dict]:
        """Fetch personalized YouTube content based on user preferences"""
        if not self.api_key:
            return []
        
        try:
            preferences = load_data(self.preferences_file)
            search_terms = preferences.get('interests', ['python programming', 'productivity', 'machine learning'])
            
            all_videos = []
            
            for term in search_terms[:3]:  # Limit to top 3 interests
                videos = await self._search_videos(term, max_results=5)
                all_videos.extend(videos)
            
            # Remove duplicates and sort by relevance
            unique_videos = {v['video_id']: v for v in all_videos}.values()
            sorted_videos = sorted(unique_videos, key=lambda x: x['relevance_score'], reverse=True)
            
            return list(sorted_videos)[:10]  # Return top 10
            
        except Exception as e:
            self.logger.error(f"Failed to fetch personalized content: {e}")
            return []

    async def _search_videos(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for videos by query"""
        try:
            params = {
                'part': 'snippet,statistics',
                'q': query,
                'type': 'video',
                'order': 'relevance',
                'maxResults': max_results,
                'key': self.api_key,
                'publishedAfter': (datetime.now() - timedelta(days=30)).isoformat() + 'Z'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/search", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return await self._process_video_results(data['items'])
                    else:
                        self.logger.error(f"YouTube API error: {response.status}")
                        return []
            
        except Exception as e:
            self.logger.error(f"Video search failed: {e}")
            return []

    async def _process_video_results(self, items: List[Dict]) -> List[Dict]:
        """Process and format video search results"""
        videos = []
        
        for item in items:
            try:
                video = {
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'][:200] + "..." if len(item['snippet']['description']) > 200 else item['snippet']['description'],
                    'channel': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt'],
                    'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                    'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                    'relevance_score': self._calculate_relevance_score(item)
                }
                videos.append(video)
            except Exception as e:
                self.logger.error(f"Failed to process video item: {e}")
                continue
        
        return videos

    def _calculate_relevance_score(self, item: Dict) -> float:
        """Calculate relevance score based on various factors"""
        score = 0.0
        
        # Base score from YouTube relevance
        score += 1.0
        
        # Boost for recent videos
        published = datetime.fromisoformat(item['snippet']['publishedAt'].replace('Z', '+00:00'))
        days_old = (datetime.now(published.tzinfo) - published).days
        if days_old < 7:
            score += 0.5
        elif days_old < 30:
            score += 0.3
        
        # Boost for educational channels (simplified)
        channel = item['snippet']['channelTitle'].lower()
        educational_keywords = ['tutorial', 'course', 'learning', 'education', 'academy', 'university']
        if any(keyword in channel for keyword in educational_keywords):
            score += 0.4
        
        # Boost for programming content
        title_lower = item['snippet']['title'].lower()
        programming_keywords = ['python', 'javascript', 'programming', 'coding', 'development', 'tutorial']
        matching_keywords = sum(1 for keyword in programming_keywords if keyword in title_lower)
        score += matching_keywords * 0.2
        
        return score

    async def get_video_details(self, video_id: str) -> Optional[Dict]:
        """Get detailed information about a specific video"""
        if not self.api_key:
            return None
        
        try:
            params = {
                'part': 'snippet,statistics,contentDetails',
                'id': video_id,
                'key': self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/videos", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['items']:
                            return self._format_video_details(data['items'][0])
                    return None
            
        except Exception as e:
            self.logger.error(f"Failed to get video details: {e}")
            return None

    def _format_video_details(self, item: Dict) -> Dict:
        """Format video details"""
        return {
            'video_id': item['id'],
            'title': item['snippet']['title'],
            'description': item['snippet']['description'],
            'channel': item['snippet']['channelTitle'],
            'published_at': item['snippet']['publishedAt'],
            'duration': item['contentDetails']['duration'],
            'view_count': item['statistics'].get('viewCount', 0),
            'like_count': item['statistics'].get('likeCount', 0),
            'thumbnail': item['snippet']['thumbnails']['high']['url'],
            'url': f"https://www.youtube.com/watch?v={item['id']}"
        }

    async def track_watched_video(self, video_id: str, rating: int = 5):
        """Track a watched video to improve recommendations"""
        try:
            preferences = load_data(self.preferences_file)
            
            if 'watched_videos' not in preferences:
                preferences['watched_videos'] = []
            
            # Get video details for better tracking
            video_details = await self.get_video_details(video_id)
            
            watch_record = {
                'video_id': video_id,
                'watched_at': datetime.now().isoformat(),
                'rating': rating,
                'title': video_details['title'] if video_details else '',
                'channel': video_details['channel'] if video_details else ''
            }
            
            preferences['watched_videos'].append(watch_record)
            
            # Keep only last 100 watched videos
            preferences['watched_videos'] = preferences['watched_videos'][-100:]
            
            # Update interests based on watched content
            await self._update_interests_from_video(video_details, rating)
            
            save_data(self.preferences_file, preferences)
            
        except Exception as e:
            self.logger.error(f"Failed to track watched video: {e}")

    async def _update_interests_from_video(self, video_details: Optional[Dict], rating: int):
        """Update user interests based on watched video"""
        if not video_details or rating < 3:
            return
        
        try:
            preferences = load_data(self.preferences_file)
            
            # Extract keywords from title and description
            title_words = video_details['title'].lower().split()
            desc_words = video_details['description'].lower().split()[:50]  # First 50 words
            
            # Common programming and learning keywords
            keywords = [
                'python', 'javascript', 'react', 'node', 'programming', 'coding',
                'machine learning', 'ai', 'data science', 'web development',
                'productivity', 'tutorial', 'course', 'learning'
            ]
            
            # Find matching keywords
            found_keywords = []
            for keyword in keywords:
                if any(keyword in word for word in title_words + desc_words):
                    found_keywords.append(keyword)
            
            # Update interests
            if 'interests' not in preferences:
                preferences['interests'] = []
            
            for keyword in found_keywords:
                if keyword not in preferences['interests']:
                    preferences['interests'].append(keyword)
            
            # Keep only top 10 interests
            preferences['interests'] = preferences['interests'][:10]
            
            save_data(self.preferences_file, preferences)
            
        except Exception as e:
            self.logger.error(f"Failed to update interests: {e}")

    async def get_trending_programming_videos(self) -> List[Dict]:
        """Get trending programming videos"""
        if not self.api_key:
            return []
        
        try:
            programming_terms = ['python programming', 'web development', 'coding tutorial']
            all_videos = []
            
            for term in programming_terms:
                videos = await self._search_videos(term, max_results=5)
                all_videos.extend(videos)
            
            # Sort by relevance and recency
            sorted_videos = sorted(all_videos, key=lambda x: x['relevance_score'], reverse=True)
            
            return sorted_videos[:8]
            
        except Exception as e:
            self.logger.error(f"Failed to get trending programming videos: {e}")
            return []

    async def search_videos_by_topic(self, topic: str, max_results: int = 10) -> List[Dict]:
        """Search videos by specific topic"""
        return await self._search_videos(topic, max_results)

    def get_watch_history(self, limit: int = 20) -> List[Dict]:
        """Get user's watch history"""
        try:
            preferences = load_data(self.preferences_file)
            watched = preferences.get('watched_videos', [])
            return watched[-limit:] if watched else []
        except Exception as e:
            self.logger.error(f"Failed to get watch history: {e}")
            return []

    def get_user_interests(self) -> List[str]:
        """Get user's current interests"""
        try:
            preferences = load_data(self.preferences_file)
            return preferences.get('interests', [])
        except Exception as e:
            self.logger.error(f"Failed to get user interests: {e}")
            return []

    def update_user_interests(self, interests: List[str]) -> bool:
        """Update user interests manually"""
        try:
            preferences = load_data(self.preferences_file)
            preferences['interests'] = interests[:10]  # Keep top 10
            save_data(self.preferences_file, preferences)
            return True
        except Exception as e:
            self.logger.error(f"Failed to update user interests: {e}")
            return False