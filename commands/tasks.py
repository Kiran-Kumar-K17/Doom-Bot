"""
Tasks Commands - Discord commands for task management and productivity
"""

import discord
from discord.ext import commands
from datetime import datetime, timedelta
from typing import Optional
import asyncio

class TasksCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.notion = bot.notion

    @commands.command(name='today', help='Show today\'s tasks and agenda')
    async def show_today(self, ctx):
        """Show today's tasks and recommendations"""
        try:
            # Get today's tasks
            tasks = await self.notion.get_todays_tasks()
            
            # Get recommendations
            youtube_rec = self.bot.preference_engine.get_recommendation('youtube')
            book_rec = self.bot.preference_engine.get_recommendation('books')
            news_items = await self.bot.news.get_top_news(3)
            
            embed = discord.Embed(
                title="📅 Today's Agenda",
                color=0x3498db,
                timestamp=datetime.utcnow()
            )
            
            # Tasks section
            if tasks:
                task_text = ""
                for i, task in enumerate(tasks[:8], 1):
                    priority_emoji = "🔴" if task['priority'] == 'High' else "🟡" if task['priority'] == 'Medium' else "🟢"
                    task_text += f"{priority_emoji} **{task['title']}**\n"
                    if task.get('due_date'):
                        task_text += f"   📅 Due: {task['due_date']}\n"
                    task_text += "\n"
                
                embed.add_field(name="📋 Today's Tasks", value=task_text[:1000], inline=False)
            else:
                embed.add_field(name="📋 Today's Tasks", value="No tasks scheduled for today! 🎉", inline=False)
            
            # Learning recommendations
            learning_text = ""
            if youtube_rec:
                learning_text += f"📹 **Video**: [{youtube_rec['title'][:50]}...]({youtube_rec['url']})\n"
            if book_rec:
                learning_text += f"📚 **Book**: {book_rec['title'][:50]}...\n"
            
            if learning_text:
                embed.add_field(name="🧠 Learning Focus", value=learning_text, inline=False)
            
            # Top news
            if news_items:
                news_text = "\n".join([f"• {item['title'][:60]}..." for item in news_items])
                embed.add_field(name="📰 Tech News", value=news_text[:1000], inline=False)
            
            embed.set_footer(text="Use !tasks to manage tasks • !recommend for more suggestions")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"Today command failed: {e}")
            await ctx.send("❌ Failed to fetch today's agenda. Please try again later.")

    @commands.command(name='tasks', help='Show all pending tasks')
    async def show_tasks(self, ctx, filter_type: Optional[str] = 'all'):
        """Show tasks with optional filtering"""
        try:
            if filter_type.lower() == 'overdue':
                tasks = await self.notion.get_overdue_tasks()
                title = "⚠️ Overdue Tasks"
                color = 0xe74c3c
            elif filter_type.lower() == 'today':
                tasks = await self.notion.get_todays_tasks()
                title = "📅 Today's Tasks"
                color = 0x3498db
            else:
                tasks = await self.notion.get_todays_tasks()
                overdue = await self.notion.get_overdue_tasks()
                tasks.extend(overdue)
                title = "📋 All Pending Tasks"
                color = 0x2ecc71
            
            if not tasks:
                embed = discord.Embed(
                    title=title,
                    description="No tasks found! Great job! 🎉",
                    color=color
                )
                await ctx.send(embed=embed)
                return
            
            # Create paginated embeds if too many tasks
            tasks_per_page = 10
            pages = []
            
            for i in range(0, len(tasks), tasks_per_page):
                page_tasks = tasks[i:i+tasks_per_page]
                
                embed = discord.Embed(title=title, color=color)
                
                task_text = ""
                for j, task in enumerate(page_tasks, 1):
                    priority_emoji = "🔴" if task['priority'] == 'High' else "🟡" if task['priority'] == 'Medium' else "🟢"
                    status_emoji = "✅" if task['status'] == 'Done' else "🔄" if task['status'] == 'In Progress' else "⭕"
                    
                    task_text += f"{priority_emoji}{status_emoji} **{task['title']}**\n"
                    
                    if task.get('due_date'):
                        due_date = datetime.fromisoformat(task['due_date']).strftime('%m/%d')
                        task_text += f"   📅 Due: {due_date}"
                        
                        # Add overdue warning
                        if datetime.fromisoformat(task['due_date']).date() < datetime.now().date():
                            task_text += " ⚠️"
                        task_text += "\n"
                    
                    if task.get('description') and len(task['description']) > 0:
                        desc_preview = task['description'][:50] + "..." if len(task['description']) > 50 else task['description']
                        task_text += f"   💭 {desc_preview}\n"
                    
                    task_text += "\n"
                
                embed.description = task_text
                embed.set_footer(text=f"Page {len(pages)+1} • {len(tasks)} total tasks")
                pages.append(embed)
            
            # Send first page
            message = await ctx.send(embed=pages[0])
            
            # Add pagination reactions if multiple pages
            if len(pages) > 1:
                await message.add_reaction('◀️')
                await message.add_reaction('▶️')
                
                def check(reaction, user):
                    return (user == ctx.author and 
                           str(reaction.emoji) in ['◀️', '▶️'] and 
                           reaction.message.id == message.id)
                
                current_page = 0
                while True:
                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                        
                        if str(reaction.emoji) == '▶️' and current_page < len(pages) - 1:
                            current_page += 1
                            await message.edit(embed=pages[current_page])
                        elif str(reaction.emoji) == '◀️' and current_page > 0:
                            current_page -= 1
                            await message.edit(embed=pages[current_page])
                        
                        await message.remove_reaction(reaction, user)
                        
                    except asyncio.TimeoutError:
                        break
            
        except Exception as e:
            self.bot.logger.error(f"Tasks command failed: {e}")
            await ctx.send("❌ Failed to fetch tasks. Please try again later.")

    @commands.command(name='addtask', help='Add a new task')
    async def add_task(self, ctx, *, task_info):
        """Add a new task to Notion"""
        try:
            # Parse task info (simple format: title | description | priority | due_date)
            parts = [part.strip() for part in task_info.split('|')]
            
            title = parts[0] if parts else task_info
            description = parts[1] if len(parts) > 1 else ""
            priority = parts[2] if len(parts) > 2 and parts[2] in ['High', 'Medium', 'Low'] else 'Medium'
            due_date = parts[3] if len(parts) > 3 else None
            
            # Validate due_date format if provided
            if due_date:
                try:
                    # Try parsing different date formats
                    if '/' in due_date:
                        parsed_date = datetime.strptime(due_date, '%m/%d/%Y').date().isoformat()
                    elif '-' in due_date:
                        parsed_date = datetime.strptime(due_date, '%Y-%m-%d').date().isoformat()
                    else:
                        # Assume it's days from now
                        days = int(due_date)
                        parsed_date = (datetime.now().date() + timedelta(days=days)).isoformat()
                    due_date = parsed_date
                except:
                    due_date = None
            
            success = await self.notion.create_task(title, description, priority, due_date)
            
            if success:
                embed = discord.Embed(
                    title="✅ Task Created",
                    color=0x2ecc71
                )
                embed.add_field(name="Title", value=title, inline=False)
                if description:
                    embed.add_field(name="Description", value=description[:200], inline=False)
                embed.add_field(name="Priority", value=priority, inline=True)
                if due_date:
                    embed.add_field(name="Due Date", value=due_date, inline=True)
                
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Failed to create task. Please check your Notion configuration.")
            
        except Exception as e:
            self.bot.logger.error(f"Add task command failed: {e}")
            await ctx.send("❌ Failed to create task. Please try again with format: `!addtask Task Title | Description | Priority | Due Date`")

    @commands.command(name='stats', help='Show productivity statistics')
    async def show_stats(self, ctx):
        """Show productivity statistics"""
        try:
            stats = await self.notion.get_weekly_stats()
            
            embed = discord.Embed(
                title="📊 Productivity Stats",
                color=0x9b59b6,
                timestamp=datetime.utcnow()
            )
            
            # Weekly stats
            embed.add_field(
                name="This Week",
                value=f"✅ {stats.get('completed_tasks', 0)} completed\n📋 {stats.get('total_tasks', 0)} total\n📈 {stats.get('completion_rate', 0):.1f}% completion rate",
                inline=True
            )
            
            # Streak
            embed.add_field(
                name="Streak",
                value=f"🔥 {stats.get('streak', 0)} days",
                inline=True
            )
            
            # Performance indicator
            completion_rate = stats.get('completion_rate', 0)
            if completion_rate >= 80:
                performance = "🌟 Excellent!"
            elif completion_rate >= 60:
                performance = "👍 Good work!"
            elif completion_rate >= 40:
                performance = "📈 Keep pushing!"
            else:
                performance = "💪 Room for improvement!"
            
            embed.add_field(
                name="Performance",
                value=performance,
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"Stats command failed: {e}")
            await ctx.send("❌ Failed to fetch statistics. Please try again later.")

    @commands.command(name='remind', help='Set a reminder')
    async def set_reminder(self, ctx, time_str: str, *, message: str):
        """Set a reminder (simple implementation)"""
        try:
            # Parse time (supports formats like 30m, 2h, 1d)
            time_unit = time_str[-1].lower()
            time_value = int(time_str[:-1])
            
            if time_unit == 'm':
                delay = time_value * 60
            elif time_unit == 'h':
                delay = time_value * 3600
            elif time_unit == 'd':
                delay = time_value * 86400
            else:
                await ctx.send("❌ Invalid time format. Use: 30m, 2h, 1d")
                return
            
            if delay > 86400 * 7:  # Max 7 days
                await ctx.send("❌ Maximum reminder time is 7 days.")
                return
            
            embed = discord.Embed(
                title="⏰ Reminder Set",
                description=f"I'll remind you about: **{message}**",
                color=0xf39c12
            )
            embed.add_field(name="In", value=time_str, inline=True)
            embed.add_field(name="At", value=f"<t:{int(datetime.now().timestamp() + delay)}:F>", inline=True)
            
            await ctx.send(embed=embed)
            
            # Wait and send reminder
            await asyncio.sleep(delay)
            
            reminder_embed = discord.Embed(
                title="⏰ Reminder!",
                description=f"**{message}**",
                color=0xe67e22
            )
            reminder_embed.set_footer(text=f"Requested by {ctx.author.display_name}")
            
            await ctx.send(f"{ctx.author.mention}", embed=reminder_embed)
            
        except ValueError:
            await ctx.send("❌ Invalid time format. Use: 30m, 2h, 1d")
        except Exception as e:
            self.bot.logger.error(f"Reminder command failed: {e}")
            await ctx.send("❌ Failed to set reminder. Please try again.")

    @commands.command(name='focus', help='Start a focus session with Pomodoro timer')
    async def focus_session(self, ctx, duration: int = 25):
        """Start a focus session"""
        try:
            if duration > 120:
                await ctx.send("❌ Maximum focus session is 120 minutes.")
                return
            
            if duration < 5:
                await ctx.send("❌ Minimum focus session is 5 minutes.")
                return
            
            embed = discord.Embed(
                title="🍅 Focus Session Started",
                description=f"Focus time: **{duration} minutes**\nStay focused and avoid distractions!",
                color=0xe74c3c,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(name="Tips", value="• Turn off notifications\n• Close distracting tabs\n• Stay hydrated\n• Take breaks", inline=False)
            embed.set_footer(text="I'll notify you when the session ends!")
            
            await ctx.send(embed=embed)
            
            # Wait for focus session to complete
            await asyncio.sleep(duration * 60)
            
            # Send completion notification
            complete_embed = discord.Embed(
                title="🎉 Focus Session Complete!",
                description=f"Great job! You focused for **{duration} minutes**.\nTime for a well-deserved break!",
                color=0x2ecc71
            )
            
            complete_embed.add_field(name="Break Suggestions", value="• Stretch or walk around\n• Drink some water\n• Rest your eyes\n• Take deep breaths", inline=False)
            
            await ctx.send(f"{ctx.author.mention}", embed=complete_embed)
            
        except Exception as e:
            self.bot.logger.error(f"Focus command failed: {e}")
            await ctx.send("❌ Failed to start focus session. Please try again.")

async def setup(bot):
    await bot.add_cog(TasksCommands(bot))