#!/usr/bin/env python3
"""
Iron Doom Jarvis - Autonomous AI Assistant Bot
A self-updating, continuously learning Discord bot for productivity, learning, and entertainment.
"""

import os
import asyncio
import logging
from datetime import datetime, timezone
import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

# Import custom modules
from utils.logger import setup_logger
from utils.helpers import load_config, ensure_data_files
from services.notion_service import NotionService
from services.youtube_service import YouTubeService
from services.books_service import BooksService
from services.news_service import NewsService
from services.github_service import GitHubService
from services.gemini_service import GeminiService
from models.preference_model import PreferenceEngine

class IronDoomJarvis(commands.Bot):
    def __init__(self):
        # Bot configuration
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            description="Iron Doom Jarvis - Your Autonomous AI Assistant"
        )
        
        # Initialize logger
        self.logger = setup_logger()
        
        # Initialize scheduler
        self.scheduler = AsyncIOScheduler(timezone=pytz.timezone('UTC'))
        
        # Initialize services
        self.notion = NotionService()
        self.youtube = YouTubeService()
        self.books = BooksService()
        self.news = NewsService()
        self.github = GitHubService()
        self.gemini = GeminiService()
        self.preference_engine = PreferenceEngine()
        
        # Bot state
        self.is_ready = False
        self.daily_tasks_sent = False
        
        self.logger.info("Iron Doom Jarvis initialized")

    async def setup_hook(self):
        """Setup hook called when bot is starting"""
        self.logger.info("Setting up Iron Doom Jarvis...")
        
        # Ensure data files exist
        ensure_data_files()
        
        # Load command modules
        await self.load_extensions()
        
        # Setup scheduler
        self.setup_scheduler()
        
        # Start background services
        self.scheduler.start()
        self.logger.info("Scheduler started")

    async def load_extensions(self):
        """Load all command modules"""
        extensions = [
            'commands.tasks',
            'commands.learning', 
            'commands.fitness',
            'commands.ai_assistant',
            'commands.fun',
            'commands.stats'
        ]
        
        for extension in extensions:
            try:
                await self.load_extension(extension)
                self.logger.info(f"Loaded extension: {extension}")
            except Exception as e:
                self.logger.error(f"Failed to load extension {extension}: {e}")

    def setup_scheduler(self):
        """Setup all scheduled tasks"""
        timezone = pytz.timezone('UTC')
        
        # Morning routine - 6:00 AM UTC
        self.scheduler.add_job(
            self.morning_routine,
            CronTrigger(hour=6, minute=0, timezone=timezone),
            id='morning_routine'
        )
        
        # Fetch YouTube videos - 7:00 AM UTC
        self.scheduler.add_job(
            self.fetch_youtube_content,
            CronTrigger(hour=7, minute=0, timezone=timezone),
            id='fetch_youtube'
        )
        
        # Update book recommendations - 8:00 AM UTC  
        self.scheduler.add_job(
            self.update_book_recommendations,
            CronTrigger(hour=8, minute=0, timezone=timezone),
            id='update_books'
        )
        
        # Evening summary - 8:00 PM UTC
        self.scheduler.add_job(
            self.evening_summary,
            CronTrigger(hour=20, minute=0, timezone=timezone),
            id='evening_summary'
        )
        
        # Hourly task reminders during work hours (9 AM - 6 PM UTC)
        self.scheduler.add_job(
            self.check_task_reminders,
            CronTrigger(hour='9-18', minute=0, timezone=timezone),
            id='task_reminders'
        )
        
        # Weekly stats - Sunday 9:00 AM UTC
        self.scheduler.add_job(
            self.weekly_stats,
            CronTrigger(day_of_week=6, hour=9, minute=0, timezone=timezone),
            id='weekly_stats'
        )

    async def on_ready(self):
        """Called when bot is ready"""
        self.logger.info(f'{self.user} has connected to Discord!')
        self.logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for your productivity 🤖"
            )
        )
        
        self.is_ready = True
        
        # Send startup message to primary channel (if configured)
        primary_channel_id = os.getenv('PRIMARY_CHANNEL_ID')
        if primary_channel_id:
            channel = self.get_channel(int(primary_channel_id))
            if channel:
                embed = discord.Embed(
                    title="🤖 Iron Doom Jarvis Online",
                    description="Your autonomous AI assistant is ready to serve!",
                    color=0x00ff00,
                    timestamp=datetime.now(timezone.utc)
                )
                embed.add_field(
                    name="Status", 
                    value="✅ All systems operational", 
                    inline=False
                )
                embed.add_field(
                    name="Features Active",
                    value="📋 Task Management\n📚 Learning Assistant\n💪 Fitness Tracking\n🤖 AI Assistant\n🎮 Entertainment",
                    inline=False
                )
                await channel.send(embed=embed)

    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("❌ Command not found. Use `!help` to see available commands.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: {error.param}")
        else:
            self.logger.error(f"Command error: {error}")
            await ctx.send("❌ An error occurred while processing your command.")

    async def on_message(self, message):
        """Handle all messages for conversational AI"""
        # Ignore messages from the bot itself
        if message.author == self.user:
            return
            
        # Process commands first
        await self.process_commands(message)
        
        # If the message was a command, don't process as conversation
        if message.content.startswith('!'):
            return
            
        # Get primary channel ID from environment
        primary_channel_id = os.getenv('PRIMARY_CHANNEL_ID')
        
        # Respond to messages in primary channel or DMs
        should_respond = (
            isinstance(message.channel, discord.DMChannel) or  # DMs
            (primary_channel_id and str(message.channel.id) == primary_channel_id) or  # Primary channel
            self.user.mentioned_in(message)  # Direct mentions anywhere
        )
        
        if should_respond:
            # Remove mention from message content if present
            content = message.content.replace(f'<@{self.user.id}>', '').strip()
            
            if not content:
                content = "Hi"
            
            try:
                # Show typing indicator
                async with message.channel.typing():
                    # Get AI response using Gemini
                    response = await self.gemini.chat(
                        content, 
                        str(message.author.id),
                        context={
                            'channel': message.channel.name if hasattr(message.channel, 'name') else 'DM',
                            'guild': message.guild.name if message.guild else 'Direct Message'
                        }
                    )
                    
                    if response:
                        # Split long responses if needed
                        if len(response) > 2000:
                            chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                            for chunk in chunks:
                                await message.channel.send(chunk)
                        else:
                            await message.channel.send(response)
                            
                        # Add reaction to indicate processing
                        await message.add_reaction('🤖')
                        
            except Exception as e:
                self.logger.error(f"Conversation error: {str(e)}")
                await message.channel.send("I'm having trouble processing that right now. Try using a specific command like `!help` instead.")

    # Scheduled Tasks
    
    async def morning_routine(self):
        """Morning routine - fetch news and prepare daily summary"""
        self.logger.info("Running morning routine...")
        
        try:
            # Fetch fresh news
            await self.news.fetch_daily_news()
            
            # Update task priorities based on completion history
            await self.notion.update_task_priorities()
            
            # Generate and send morning summary
            await self.send_morning_summary()
            
        except Exception as e:
            self.logger.error(f"Morning routine failed: {e}")

    async def fetch_youtube_content(self):
        """Fetch new YouTube content based on preferences"""
        self.logger.info("Fetching YouTube content...")
        
        try:
            # Get personalized recommendations
            recommendations = await self.youtube.fetch_personalized_content()
            
            # Store recommendations for later commands
            self.preference_engine.update_content_pool('youtube', recommendations)
            
        except Exception as e:
            self.logger.error(f"YouTube content fetch failed: {e}")

    async def update_book_recommendations(self):
        """Update book recommendations"""
        self.logger.info("Updating book recommendations...")
        
        try:
            recommendations = await self.books.fetch_personalized_recommendations()
            self.preference_engine.update_content_pool('books', recommendations)
            
        except Exception as e:
            self.logger.error(f"Book recommendations update failed: {e}")

    async def check_task_reminders(self):
        """Check for overdue tasks and send reminders"""
        try:
            overdue_tasks = await self.notion.get_overdue_tasks()
            
            if overdue_tasks:
                await self.send_task_reminders(overdue_tasks)
                
        except Exception as e:
            self.logger.error(f"Task reminder check failed: {e}")

    async def evening_summary(self):
        """Send evening summary with accomplishments and tomorrow's focus"""
        self.logger.info("Generating evening summary...")
        
        try:
            await self.send_evening_summary()
        except Exception as e:
            self.logger.error(f"Evening summary failed: {e}")

    async def weekly_stats(self):
        """Send weekly statistics and insights"""
        self.logger.info("Generating weekly stats...")
        
        try:
            await self.send_weekly_stats()
        except Exception as e:
            self.logger.error(f"Weekly stats failed: {e}")

    # Helper methods for scheduled tasks
    
    async def send_morning_summary(self):
        """Send morning summary to primary channel"""
        primary_channel_id = os.getenv('PRIMARY_CHANNEL_ID')
        if not primary_channel_id:
            return
            
        channel = self.get_channel(int(primary_channel_id))
        if not channel:
            return
        
        # Get today's tasks
        tasks = await self.notion.get_todays_tasks()
        
        # Get recommended content
        youtube_rec = self.preference_engine.get_recommendation('youtube')
        book_rec = self.preference_engine.get_recommendation('books')
        news_items = await self.news.get_top_news(5)
        
        embed = discord.Embed(
            title="🌅 Good Morning! Your Daily Brief",
            color=0xffd700,
            timestamp=datetime.utcnow()
        )
        
        # Tasks section
        if tasks:
            task_text = '\n'.join([f"• {task['title']}" for task in tasks[:5]])
            embed.add_field(name="📋 Today's Priority Tasks", value=task_text, inline=False)
        
        # Learning recommendations
        learning_text = ""
        if youtube_rec:
            learning_text += f"📹 **Video**: {youtube_rec['title']}\n"
        if book_rec:
            learning_text += f"📚 **Book**: {book_rec['title']}\n"
        
        if learning_text:
            embed.add_field(name="🧠 Learning Recommendations", value=learning_text, inline=False)
        
        # News headlines
        if news_items:
            news_text = '\n'.join([f"• {item['title']}" for item in news_items[:3]])
            embed.add_field(name="📰 Top News", value=news_text, inline=False)
        
        embed.set_footer(text="Use !today for more details • !recommend for personalized suggestions")
        
        await channel.send(embed=embed)

    async def send_task_reminders(self, overdue_tasks):
        """Send task reminders"""
        primary_channel_id = os.getenv('PRIMARY_CHANNEL_ID')
        if not primary_channel_id:
            return
            
        channel = self.get_channel(int(primary_channel_id))
        if not channel:
            return
        
        embed = discord.Embed(
            title="⚠️ Task Reminder",
            description="You have overdue tasks that need attention:",
            color=0xff6b6b
        )
        
        for task in overdue_tasks[:5]:
            embed.add_field(
                name=task['title'],
                value=f"Due: {task['due_date']}",
                inline=False
            )
        
        await channel.send(embed=embed)

    async def send_evening_summary(self):
        """Send evening summary"""
        primary_channel_id = os.getenv('PRIMARY_CHANNEL_ID')
        if not primary_channel_id:
            return
            
        channel = self.get_channel(int(primary_channel_id))
        if not channel:
            return
        
        # Get today's completed tasks
        completed_tasks = await self.notion.get_completed_tasks_today()
        
        embed = discord.Embed(
            title="🌙 Evening Summary",
            description="Here's what you accomplished today:",
            color=0x6c5ce7,
            timestamp=datetime.utcnow()
        )
        
        if completed_tasks:
            completed_text = '\n'.join([f"✅ {task['title']}" for task in completed_tasks[:5]])
            embed.add_field(name="Completed Tasks", value=completed_text, inline=False)
        else:
            embed.add_field(name="Completed Tasks", value="No tasks completed today", inline=False)
        
        # Tomorrow's focus
        tomorrow_tasks = await self.notion.get_tomorrows_priority_tasks()
        if tomorrow_tasks:
            tomorrow_text = '\n'.join([f"• {task['title']}" for task in tomorrow_tasks[:3]])
            embed.add_field(name="Tomorrow's Focus", value=tomorrow_text, inline=False)
        
        embed.set_footer(text="Rest well! Tomorrow is a new opportunity to excel.")
        
        await channel.send(embed=embed)

    async def send_weekly_stats(self):
        """Send weekly statistics"""
        primary_channel_id = os.getenv('PRIMARY_CHANNEL_ID')
        if not primary_channel_id:
            return
            
        channel = self.get_channel(int(primary_channel_id))
        if not channel:
            return
        
        # Get weekly stats
        stats = await self.notion.get_weekly_stats()
        
        embed = discord.Embed(
            title="📊 Weekly Performance Report",
            color=0x00cec9,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="Task Completion",
            value=f"✅ {stats.get('completed_tasks', 0)} completed\n📋 {stats.get('total_tasks', 0)} total",
            inline=True
        )
        
        embed.add_field(
            name="Completion Rate",
            value=f"{stats.get('completion_rate', 0):.1f}%",
            inline=True
        )
        
        embed.add_field(
            name="Streak",
            value=f"🔥 {stats.get('streak', 0)} days",
            inline=True
        )
        
        await channel.send(embed=embed)

async def main():
    """Main function to run the bot"""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check for required environment variables
    required_vars = ['DISCORD_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        return
    
    # Initialize and run bot
    bot = IronDoomJarvis()
    
    try:
        await bot.start(os.getenv('DISCORD_TOKEN'))
    except KeyboardInterrupt:
        print("\n⚡ Shutting down Iron Doom Jarvis...")
        await bot.close()
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())