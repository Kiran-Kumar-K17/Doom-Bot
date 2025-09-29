"""
GitHub Service - Handles GitHub API interactions for repository tracking and coding insights
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncio
import aiohttp
from utils.helpers import safe_request, load_data, save_data

class GitHubService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.base_url = "https://api.github.com"
        self.username = os.getenv('GITHUB_USERNAME')
        self.preferences_file = "data/github_preferences.json"
        
        if not self.github_token:
            self.logger.warning("GitHub token not found. GitHub features will be limited.")

    async def get_user_activity(self, username: str = None) -> List[Dict]:
        """Get user's recent GitHub activity"""
        if not self.github_token:
            return []
        
        username = username or self.username
        if not username:
            return []
        
        try:
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/users/{username}/events/public"
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        events = await response.json()
                        return self._process_user_events(events)
                    else:
                        self.logger.error(f"GitHub API error: {response.status}")
                        return []
            
        except Exception as e:
            self.logger.error(f"Failed to get user activity: {e}")
            return []

    def _process_user_events(self, events: List[Dict]) -> List[Dict]:
        """Process and format user events"""
        processed_events = []
        
        for event in events[:20]:  # Process last 20 events
            try:
                event_type = event.get('type')
                created_at = event.get('created_at')
                repo = event.get('repo', {}).get('name', '')
                
                processed_event = {
                    'type': event_type,
                    'repository': repo,
                    'created_at': created_at,
                    'description': self._get_event_description(event),
                    'url': f"https://github.com/{repo}"
                }
                
                processed_events.append(processed_event)
                
            except Exception as e:
                self.logger.error(f"Failed to process event: {e}")
                continue
        
        return processed_events

    def _get_event_description(self, event: Dict) -> str:
        """Generate human-readable description for GitHub event"""
        event_type = event.get('type')
        repo_name = event.get('repo', {}).get('name', 'repository')
        
        if event_type == 'PushEvent':
            commits_count = len(event.get('payload', {}).get('commits', []))
            return f"Pushed {commits_count} commit{'s' if commits_count != 1 else ''} to {repo_name}"
        
        elif event_type == 'CreateEvent':
            ref_type = event.get('payload', {}).get('ref_type', 'repository')
            return f"Created {ref_type} in {repo_name}"
        
        elif event_type == 'IssuesEvent':
            action = event.get('payload', {}).get('action', 'updated')
            issue_title = event.get('payload', {}).get('issue', {}).get('title', '')
            return f"{action.capitalize()} issue: {issue_title[:50]}..." if issue_title else f"{action.capitalize()} issue in {repo_name}"
        
        elif event_type == 'PullRequestEvent':
            action = event.get('payload', {}).get('action', 'updated')
            pr_title = event.get('payload', {}).get('pull_request', {}).get('title', '')
            return f"{action.capitalize()} pull request: {pr_title[:50]}..." if pr_title else f"{action.capitalize()} pull request in {repo_name}"
        
        elif event_type == 'StarEvent':
            return f"Starred {repo_name}"
        
        elif event_type == 'WatchEvent':
            return f"Started watching {repo_name}"
        
        elif event_type == 'ForkEvent':
            return f"Forked {repo_name}"
        
        else:
            return f"{event_type.replace('Event', '')} activity in {repo_name}"

    async def get_repositories(self, username: str = None, sort: str = 'updated') -> List[Dict]:
        """Get user's repositories"""
        if not self.github_token:
            return []
        
        username = username or self.username
        if not username:
            return []
        
        try:
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            params = {
                'sort': sort,
                'per_page': 20
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/users/{username}/repos"
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        repos = await response.json()
                        return self._process_repositories(repos)
                    else:
                        self.logger.error(f"GitHub repos API error: {response.status}")
                        return []
            
        except Exception as e:
            self.logger.error(f"Failed to get repositories: {e}")
            return []

    def _process_repositories(self, repos: List[Dict]) -> List[Dict]:
        """Process and format repository data"""
        processed_repos = []
        
        for repo in repos:
            try:
                processed_repo = {
                    'name': repo.get('name', ''),
                    'full_name': repo.get('full_name', ''),
                    'description': repo.get('description', ''),
                    'language': repo.get('language', 'Unknown'),
                    'stars': repo.get('stargazers_count', 0),
                    'forks': repo.get('forks_count', 0),
                    'updated_at': repo.get('updated_at'),
                    'created_at': repo.get('created_at'),
                    'url': repo.get('html_url'),
                    'private': repo.get('private', False),
                    'size': repo.get('size', 0)
                }
                
                processed_repos.append(processed_repo)
                
            except Exception as e:
                self.logger.error(f"Failed to process repository: {e}")
                continue
        
        return processed_repos

    async def get_repository_stats(self, repo_full_name: str) -> Optional[Dict]:
        """Get detailed statistics for a repository"""
        if not self.github_token:
            return None
        
        try:
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            async with aiohttp.ClientSession() as session:
                # Get repository info
                repo_url = f"{self.base_url}/repos/{repo_full_name}"
                async with session.get(repo_url, headers=headers) as response:
                    if response.status != 200:
                        return None
                    
                    repo_data = await response.json()
                
                # Get commit activity
                activity_url = f"{self.base_url}/repos/{repo_full_name}/stats/commit_activity"
                async with session.get(activity_url, headers=headers) as response:
                    commit_activity = await response.json() if response.status == 200 else []
                
                # Get language stats
                languages_url = f"{self.base_url}/repos/{repo_full_name}/languages"
                async with session.get(languages_url, headers=headers) as response:
                    languages = await response.json() if response.status == 200 else {}
                
                return {
                    'name': repo_data.get('name'),
                    'description': repo_data.get('description'),
                    'language': repo_data.get('language'),
                    'stars': repo_data.get('stargazers_count', 0),
                    'forks': repo_data.get('forks_count', 0),
                    'open_issues': repo_data.get('open_issues_count', 0),
                    'size': repo_data.get('size', 0),
                    'created_at': repo_data.get('created_at'),
                    'updated_at': repo_data.get('updated_at'),
                    'languages': languages,
                    'commit_activity': commit_activity,
                    'url': repo_data.get('html_url')
                }
            
        except Exception as e:
            self.logger.error(f"Failed to get repository stats: {e}")
            return None

    async def get_trending_repositories(self, language: str = None, time_range: str = 'daily') -> List[Dict]:
        """Get trending repositories"""
        try:
            # GitHub doesn't have a trending API, so we'll search for recently created popular repos
            query = f"created:>{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')}"
            
            if language:
                query += f" language:{language}"
            
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': 10
            }
            
            headers = {}
            if self.github_token:
                headers['Authorization'] = f'token {self.github_token}'
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/search/repositories"
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._process_repositories(data.get('items', []))
                    else:
                        self.logger.error(f"GitHub trending API error: {response.status}")
                        return []
            
        except Exception as e:
            self.logger.error(f"Failed to get trending repositories: {e}")
            return []

    async def search_repositories(self, query: str, language: str = None) -> List[Dict]:
        """Search repositories"""
        try:
            search_query = query
            if language:
                search_query += f" language:{language}"
            
            params = {
                'q': search_query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': 10
            }
            
            headers = {}
            if self.github_token:
                headers['Authorization'] = f'token {self.github_token}'
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/search/repositories"
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._process_repositories(data.get('items', []))
                    else:
                        self.logger.error(f"GitHub search API error: {response.status}")
                        return []
            
        except Exception as e:
            self.logger.error(f"Failed to search repositories: {e}")
            return []

    async def get_user_stats(self, username: str = None) -> Dict:
        """Get comprehensive user statistics"""
        if not self.github_token:
            return {}
        
        username = username or self.username
        if not username:
            return {}
        
        try:
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            async with aiohttp.ClientSession() as session:
                # Get user profile
                user_url = f"{self.base_url}/users/{username}"
                async with session.get(user_url, headers=headers) as response:
                    if response.status != 200:
                        return {}
                    
                    user_data = await response.json()
                
                # Get repositories
                repos = await self.get_repositories(username)
                
                # Calculate stats
                total_stars = sum(repo.get('stars', 0) for repo in repos)
                total_forks = sum(repo.get('forks', 0) for repo in repos)
                languages = {}
                
                for repo in repos:
                    lang = repo.get('language')
                    if lang:
                        languages[lang] = languages.get(lang, 0) + 1
                
                # Get most popular language
                most_popular_language = max(languages.items(), key=lambda x: x[1])[0] if languages else "Unknown"
                
                return {
                    'username': username,
                    'name': user_data.get('name', ''),
                    'bio': user_data.get('bio', ''),
                    'location': user_data.get('location', ''),
                    'company': user_data.get('company', ''),
                    'public_repos': user_data.get('public_repos', 0),
                    'followers': user_data.get('followers', 0),
                    'following': user_data.get('following', 0),
                    'created_at': user_data.get('created_at'),
                    'total_stars': total_stars,
                    'total_forks': total_forks,
                    'most_popular_language': most_popular_language,
                    'languages_used': dict(sorted(languages.items(), key=lambda x: x[1], reverse=True)),
                    'profile_url': user_data.get('html_url')
                }
            
        except Exception as e:
            self.logger.error(f"Failed to get user stats: {e}")
            return {}

    async def get_commit_streak(self, username: str = None) -> Dict:
        """Get user's commit streak information"""
        username = username or self.username
        if not username or not self.github_token:
            return {}
        
        try:
            # Get recent activity
            activity = await self.get_user_activity(username)
            
            # Count commits by date
            commit_dates = []
            for event in activity:
                if event.get('type') == 'PushEvent':
                    date = event.get('created_at', '')[:10]  # Get date part
                    if date:
                        commit_dates.append(date)
            
            # Calculate streak
            unique_dates = sorted(set(commit_dates), reverse=True)
            current_streak = 0
            today = datetime.now().date()
            
            for i, date_str in enumerate(unique_dates):
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                expected_date = today - timedelta(days=i)
                
                if date == expected_date:
                    current_streak += 1
                else:
                    break
            
            return {
                'current_streak': current_streak,
                'total_commit_days': len(unique_dates),
                'recent_activity': len(commit_dates)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get commit streak: {e}")
            return {}

    def get_github_preferences(self) -> Dict:
        """Get GitHub tracking preferences"""
        try:
            return load_data(self.preferences_file)
        except Exception as e:
            self.logger.error(f"Failed to get GitHub preferences: {e}")
            return {
                'tracked_languages': ['python', 'javascript', 'typescript'],
                'notifications_enabled': True
            }

    def update_github_preferences(self, **kwargs) -> bool:
        """Update GitHub preferences"""
        try:
            preferences = self.get_github_preferences()
            preferences.update(kwargs)
            save_data(self.preferences_file, preferences)
            return True
        except Exception as e:
            self.logger.error(f"Failed to update GitHub preferences: {e}")
            return False