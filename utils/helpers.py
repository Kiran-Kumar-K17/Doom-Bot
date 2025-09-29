"""
Helper utilities for Iron Doom Jarvis
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import asyncio
import aiohttp

def setup_config():
    """Setup basic configuration and directories"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Create default preference files if they don't exist
    default_files = {
        "data/youtube_preferences.json": {
            "interests": ["python programming", "productivity", "machine learning"],
            "watched_videos": []
        },
        "data/book_preferences.json": {
            "genres": ["programming", "productivity", "technology"],
            "reading_history": []
        },
        "data/news_preferences.json": {
            "categories": ["technology", "business", "science"],
            "blocked_sources": [],
            "read_articles": []
        },
        "data/history.json": {
            "user_interactions": [],
            "recommendations": [],
            "feedback": []
        }
    }
    
    for file_path, default_content in default_files.items():
        if not os.path.exists(file_path):
            save_data(file_path, default_content)

def load_data(file_path: str, default: Any = None) -> Any:
    """Load data from JSON file"""
    if default is None:
        default = {}
    
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return default
    except Exception as e:
        logging.error(f"Failed to load data from {file_path}: {e}")
        return default

def save_data(file_path: str, data: Any) -> bool:
    """Save data to JSON file"""
    try:
        # Ensure directory exists
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logging.error(f"Failed to save data to {file_path}: {e}")
        return False

def load_config() -> Dict:
    """Load configuration from environment and files"""
    config = {
        'discord_token': os.getenv('DISCORD_TOKEN'),
        'primary_channel_id': os.getenv('PRIMARY_CHANNEL_ID'),
        'notion_token': os.getenv('NOTION_TOKEN'),
        'notion_task_database_id': os.getenv('NOTION_TASK_DATABASE_ID'),
        'youtube_api_key': os.getenv('YOUTUBE_API_KEY'),
        'google_books_api_key': os.getenv('GOOGLE_BOOKS_API_KEY'),
        'news_api_key': os.getenv('NEWS_API_KEY'),
        'github_token': os.getenv('GITHUB_TOKEN'),
        'openai_api_key': os.getenv('OPENAI_API_KEY')
    }
    
    return config

def ensure_data_files():
    """Ensure all necessary data files exist"""
    setup_config()

async def safe_request(session: aiohttp.ClientSession, method: str, url: str, 
                      max_retries: int = 3, **kwargs) -> Optional[Dict]:
    """Make a safe HTTP request with retries"""
    for attempt in range(max_retries):
        try:
            async with session.request(method, url, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:  # Rate limited
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logging.warning(f"HTTP {response.status} for {url}")
                    return None
        except asyncio.TimeoutError:
            logging.warning(f"Timeout for {url}, attempt {attempt + 1}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
            continue
        except Exception as e:
            logging.error(f"Request failed for {url}: {e}")
            break
    
    return None

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s" if secs > 0 else f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def parse_youtube_duration(duration: str) -> int:
    """Parse YouTube duration format (PT4M13S) to seconds"""
    import re
    
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration)
    
    if not match:
        return 0
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    return hours * 3600 + minutes * 60 + seconds

def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """Extract keywords from text"""
    import re
    
    # Remove special characters and split
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    # Filter out common stop words and short words
    stop_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
        'after', 'above', 'below', 'between', 'among', 'this', 'that', 'these',
        'those', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could',
        'can', 'may', 'might', 'must', 'shall'
    }
    
    keywords = [word for word in words 
                if len(word) >= min_length and word not in stop_words]
    
    return list(set(keywords))  # Remove duplicates

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate simple similarity between two texts"""
    words1 = set(extract_keywords(text1))
    words2 = set(extract_keywords(text2))
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0

def format_date(date_string: str, format_type: str = 'relative') -> str:
    """Format date string to human readable format"""
    try:
        # Parse ISO format date
        if 'T' in date_string:
            date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        else:
            date_obj = datetime.strptime(date_string, '%Y-%m-%d')
        
        if format_type == 'relative':
            now = datetime.now(date_obj.tzinfo) if date_obj.tzinfo else datetime.now()
            diff = now - date_obj
            
            if diff.days == 0:
                return "Today"
            elif diff.days == 1:
                return "Yesterday"
            elif diff.days < 7:
                return f"{diff.days} days ago"
            elif diff.days < 30:
                weeks = diff.days // 7
                return f"{weeks} week{'s' if weeks > 1 else ''} ago"
            elif diff.days < 365:
                months = diff.days // 30
                return f"{months} month{'s' if months > 1 else ''} ago"
            else:
                years = diff.days // 365
                return f"{years} year{'s' if years > 1 else ''} ago"
        else:
            return date_obj.strftime('%Y-%m-%d')
    
    except Exception:
        return date_string

def validate_url(url: str) -> bool:
    """Validate if URL is properly formatted"""
    import re
    
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None

def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters"""
    import re
    
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Truncate if too long
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename.strip()

class RateLimiter:
    """Simple rate limiter for API requests"""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = datetime.now().timestamp()
        
        # Remove old requests outside time window
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.time_window]
        
        # If we're at the limit, wait
        if len(self.requests) >= self.max_requests:
            sleep_time = self.time_window - (now - self.requests[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
                # Clean up again after waiting
                now = datetime.now().timestamp()
                self.requests = [req_time for req_time in self.requests 
                               if now - req_time < self.time_window]
        
        # Record this request
        self.requests.append(now)

def create_progress_bar(current: int, total: int, length: int = 20) -> str:
    """Create a text progress bar"""
    if total <= 0:
        return "[" + "█" * length + "]"
    
    progress = current / total
    filled_length = int(length * progress)
    
    bar = "█" * filled_length + "░" * (length - filled_length)
    percentage = int(progress * 100)
    
    return f"[{bar}] {percentage}%"

def get_file_size(file_path: str) -> str:
    """Get human readable file size"""
    try:
        size = os.path.getsize(file_path)
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        
        return f"{size:.1f} TB"
    except:
        return "Unknown"