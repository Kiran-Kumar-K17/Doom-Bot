"""
Notion Service - Handles all Notion API interactions for tasks, notes, and databases
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncio
import aiohttp
from notion_client import AsyncClient
from utils.helpers import safe_request

class NotionService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = None
        self.task_database_id = os.getenv('NOTION_TASK_DATABASE_ID')
        self.notes_database_id = os.getenv('NOTION_NOTES_DATABASE_ID')
        
        if os.getenv('NOTION_TOKEN'):
            self.client = AsyncClient(auth=os.getenv('NOTION_TOKEN'))
        else:
            self.logger.warning("Notion token not found. Notion features will be disabled.")

    async def get_todays_tasks(self) -> List[Dict]:
        """Get tasks for today"""
        if not self.client or not self.task_database_id:
            return []
        
        try:
            today = datetime.now().date().isoformat()
            
            response = await self.client.databases.query(
                database_id=self.task_database_id,
                filter={
                    "and": [
                        {
                            "property": "Due Date",
                            "date": {"on_or_before": today}
                        },
                        {
                            "property": "Status",
                            "select": {"does_not_equal": "Done"}
                        }
                    ]
                },
                sorts=[
                    {
                        "property": "Priority",
                        "direction": "descending"
                    }
                ]
            )
            
            tasks = []
            for page in response['results']:
                task = self._parse_task_page(page)
                if task:
                    tasks.append(task)
            
            return tasks
            
        except Exception as e:
            self.logger.error(f"Failed to fetch today's tasks: {e}")
            return []

    async def get_overdue_tasks(self) -> List[Dict]:
        """Get overdue tasks"""
        if not self.client or not self.task_database_id:
            return []
        
        try:
            yesterday = (datetime.now().date() - timedelta(days=1)).isoformat()
            
            response = await self.client.databases.query(
                database_id=self.task_database_id,
                filter={
                    "and": [
                        {
                            "property": "Due Date",
                            "date": {"before": yesterday}
                        },
                        {
                            "property": "Status",
                            "select": {"does_not_equal": "Done"}
                        }
                    ]
                },
                sorts=[
                    {
                        "property": "Due Date",
                        "direction": "ascending"
                    }
                ]
            )
            
            tasks = []
            for page in response['results']:
                task = self._parse_task_page(page)
                if task:
                    tasks.append(task)
            
            return tasks
            
        except Exception as e:
            self.logger.error(f"Failed to fetch overdue tasks: {e}")
            return []

    async def get_tomorrows_priority_tasks(self) -> List[Dict]:
        """Get priority tasks for tomorrow"""
        if not self.client or not self.task_database_id:
            return []
        
        try:
            tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()
            
            response = await self.client.databases.query(
                database_id=self.task_database_id,
                filter={
                    "and": [
                        {
                            "property": "Due Date",
                            "date": {"equals": tomorrow}
                        },
                        {
                            "property": "Priority",
                            "select": {"equals": "High"}
                        }
                    ]
                },
                sorts=[
                    {
                        "property": "Priority",
                        "direction": "descending"
                    }
                ]
            )
            
            tasks = []
            for page in response['results']:
                task = self._parse_task_page(page)
                if task:
                    tasks.append(task)
            
            return tasks
            
        except Exception as e:
            self.logger.error(f"Failed to fetch tomorrow's tasks: {e}")
            return []

    async def get_completed_tasks_today(self) -> List[Dict]:
        """Get tasks completed today"""
        if not self.client or not self.task_database_id:
            return []
        
        try:
            today = datetime.now().date().isoformat()
            
            response = await self.client.databases.query(
                database_id=self.task_database_id,
                filter={
                    "and": [
                        {
                            "property": "Status",
                            "select": {"equals": "Done"}
                        },
                        {
                            "property": "Completed Date",
                            "date": {"equals": today}
                        }
                    ]
                }
            )
            
            tasks = []
            for page in response['results']:
                task = self._parse_task_page(page)
                if task:
                    tasks.append(task)
            
            return tasks
            
        except Exception as e:
            self.logger.error(f"Failed to fetch completed tasks: {e}")
            return []

    async def get_weekly_stats(self) -> Dict:
        """Get weekly statistics"""
        if not self.client or not self.task_database_id:
            return {}
        
        try:
            week_ago = (datetime.now().date() - timedelta(days=7)).isoformat()
            today = datetime.now().date().isoformat()
            
            # Get all tasks from the past week
            response = await self.client.databases.query(
                database_id=self.task_database_id,
                filter={
                    "property": "Created",
                    "date": {"on_or_after": week_ago}
                }
            )
            
            total_tasks = len(response['results'])
            completed_tasks = 0
            
            for page in response['results']:
                status = self._get_property_value(page, 'Status')
                if status == 'Done':
                    completed_tasks += 1
            
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Calculate streak (simplified)
            streak = await self._calculate_completion_streak()
            
            return {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'completion_rate': completion_rate,
                'streak': streak
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get weekly stats: {e}")
            return {}

    async def create_task(self, title: str, description: str = "", priority: str = "Medium", 
                         due_date: Optional[str] = None) -> bool:
        """Create a new task in Notion"""
        if not self.client or not self.task_database_id:
            return False
        
        try:
            properties = {
                "Title": {
                    "title": [{"text": {"content": title}}]
                },
                "Status": {
                    "select": {"name": "Not Started"}
                },
                "Priority": {
                    "select": {"name": priority}
                }
            }
            
            if description:
                properties["Description"] = {
                    "rich_text": [{"text": {"content": description}}]
                }
            
            if due_date:
                properties["Due Date"] = {
                    "date": {"start": due_date}
                }
            
            await self.client.pages.create(
                parent={"database_id": self.task_database_id},
                properties=properties
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create task: {e}")
            return False

    async def update_task_priorities(self):
        """Update task priorities based on completion history and deadlines"""
        if not self.client or not self.task_database_id:
            return
        
        try:
            # Get all incomplete tasks
            response = await self.client.databases.query(
                database_id=self.task_database_id,
                filter={
                    "property": "Status",
                    "select": {"does_not_equal": "Done"}
                }
            )
            
            for page in response['results']:
                # Simple priority adjustment logic
                due_date = self._get_property_value(page, 'Due Date')
                if due_date:
                    due_datetime = datetime.fromisoformat(due_date)
                    days_until_due = (due_datetime.date() - datetime.now().date()).days
                    
                    # Increase priority if due soon
                    if days_until_due <= 1:
                        await self._update_task_priority(page['id'], 'High')
                    elif days_until_due <= 3:
                        await self._update_task_priority(page['id'], 'Medium')
            
        except Exception as e:
            self.logger.error(f"Failed to update task priorities: {e}")

    def _parse_task_page(self, page: Dict) -> Optional[Dict]:
        """Parse a Notion page into a task dictionary"""
        try:
            return {
                'id': page['id'],
                'title': self._get_property_value(page, 'Title'),
                'status': self._get_property_value(page, 'Status'),
                'priority': self._get_property_value(page, 'Priority'),
                'due_date': self._get_property_value(page, 'Due Date'),
                'description': self._get_property_value(page, 'Description'),
                'url': page['url']
            }
        except Exception as e:
            self.logger.error(f"Failed to parse task page: {e}")
            return None

    def _get_property_value(self, page: Dict, property_name: str):
        """Get property value from Notion page"""
        try:
            prop = page['properties'].get(property_name)
            if not prop:
                return None
            
            prop_type = prop['type']
            
            if prop_type == 'title':
                return prop['title'][0]['text']['content'] if prop['title'] else ""
            elif prop_type == 'rich_text':
                return prop['rich_text'][0]['text']['content'] if prop['rich_text'] else ""
            elif prop_type == 'select':
                return prop['select']['name'] if prop['select'] else None
            elif prop_type == 'date':
                return prop['date']['start'] if prop['date'] else None
            else:
                return str(prop.get(prop_type, ""))
        except:
            return None

    async def _update_task_priority(self, page_id: str, priority: str):
        """Update task priority"""
        try:
            await self.client.pages.update(
                page_id=page_id,
                properties={
                    "Priority": {
                        "select": {"name": priority}
                    }
                }
            )
        except Exception as e:
            self.logger.error(f"Failed to update task priority: {e}")

    async def _calculate_completion_streak(self) -> int:
        """Calculate current completion streak (simplified)"""
        # This is a simplified implementation
        # In a real scenario, you'd want to track daily completions more precisely
        try:
            streak = 0
            current_date = datetime.now().date()
            
            for i in range(30):  # Check last 30 days
                check_date = current_date - timedelta(days=i)
                
                response = await self.client.databases.query(
                    database_id=self.task_database_id,
                    filter={
                        "and": [
                            {
                                "property": "Status",
                                "select": {"equals": "Done"}
                            },
                            {
                                "property": "Completed Date",
                                "date": {"equals": check_date.isoformat()}
                            }
                        ]
                    }
                )
                
                if response['results']:
                    streak += 1
                else:
                    break
            
            return streak
            
        except Exception as e:
            self.logger.error(f"Failed to calculate streak: {e}")
            return 0