"""
Stats Commands - Discord commands for analytics and progress tracking
"""

import discord
from discord.ext import commands
from datetime import datetime, timedelta
import json
import os

class StatsCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='mystats', help='Show comprehensive user statistics')
    async def show_user_stats(self, ctx):
        """Show comprehensive user statistics"""
        try:
            # Get insights from preference engine
            insights = self.bot.preference_engine.get_user_insights()
            
            # Get task stats
            task_stats = await self.bot.notion.get_weekly_stats()
            
            # Get GitHub stats if available
            github_stats = await self.bot.github.get_user_stats()
            
            embed = discord.Embed(
                title="📊 Your Complete Stats Dashboard",
                color=0x1abc9c,
                timestamp=datetime.utcnow()
            )
            
            # Activity Overview
            total_interactions = insights.get('total_interactions', 0)
            embed.add_field(
                name="🔥 Activity Level",
                value=f"**{total_interactions}** total interactions\n" +
                      self._get_activity_badge(total_interactions),
                inline=True
            )
            
            # Task Performance
            completion_rate = task_stats.get('completion_rate', 0)
            embed.add_field(
                name="📋 Task Performance",
                value=f"**{completion_rate:.1f}%** completion rate\n" +
                      f"🔥 **{task_stats.get('streak', 0)}** day streak",
                inline=True
            )
            
            # Content Distribution
            content_dist = insights.get('content_type_distribution', {})
            if content_dist:
                most_used = max(content_dist.items(), key=lambda x: x[1])
                embed.add_field(
                    name="📚 Learning Focus",
                    value=f"Primary: **{most_used[0].title()}**\nUsage: **{most_used[1]}** times",
                    inline=True
                )
            
            # GitHub Activity (if available)
            if github_stats and github_stats.get('public_repos', 0) > 0:
                embed.add_field(
                    name="💻 Coding Stats",
                    value=f"**{github_stats.get('public_repos', 0)}** repositories\n" +
                          f"⭐ **{github_stats.get('total_stars', 0)}** total stars",
                    inline=True
                )
            
            # Weekly Activity Pattern
            most_active_days = insights.get('most_active_days', [])[:3]
            if most_active_days:
                days_text = " → ".join([day for day, _ in most_active_days])
                embed.add_field(
                    name="📅 Most Active Days",
                    value=days_text,
                    inline=True
                )
            
            # Overall Performance Badge
            performance_score = self._calculate_performance_score(
                completion_rate, total_interactions, task_stats.get('streak', 0)
            )
            embed.add_field(
                name="🏆 Performance Level",
                value=self._get_performance_badge(performance_score),
                inline=True
            )
            
            embed.set_footer(text="Keep up the great work! 🚀")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"User stats failed: {e}")
            await ctx.send("❌ Failed to generate stats. Please try again.")

    def _get_activity_badge(self, interactions: int) -> str:
        """Get activity level badge"""
        if interactions >= 200:
            return "🌟 **Superstar User**"
        elif interactions >= 100:
            return "🔥 **Power User**"
        elif interactions >= 50:
            return "⚡ **Active User**"
        elif interactions >= 20:
            return "👍 **Regular User**"
        elif interactions >= 5:
            return "🌱 **Growing User**"
        else:
            return "👋 **New User**"

    def _calculate_performance_score(self, completion_rate: float, interactions: int, streak: int) -> int:
        """Calculate overall performance score"""
        score = 0
        score += min(completion_rate / 10, 10)  # Max 10 points from completion rate
        score += min(interactions / 10, 5)     # Max 5 points from interactions
        score += min(streak, 5)                # Max 5 points from streak
        return int(score)

    def _get_performance_badge(self, score: int) -> str:
        """Get performance badge based on score"""
        if score >= 18:
            return "🏆 **Iron Doom Legend**"
        elif score >= 15:
            return "🥇 **Productivity Master**"
        elif score >= 12:
            return "🥈 **High Achiever**"
        elif score >= 9:
            return "🥉 **Solid Performer**"
        elif score >= 6:
            return "📈 **On the Rise**"
        else:
            return "🌱 **Just Starting**"

    @commands.command(name='leaderboard', help='Show productivity leaderboard')
    async def show_leaderboard(self, ctx):
        """Show productivity leaderboard (simplified version)"""
        try:
            embed = discord.Embed(
                title="🏆 Iron Doom Leaderboard",
                description="Top performers this week:",
                color=0xf39c12,
                timestamp=datetime.utcnow()
            )
            
            # This is a simplified version - in a real implementation,
            # you'd track multiple users' stats
            embed.add_field(
                name="🥇 This Week's Champion",
                value=f"{ctx.author.mention}\n🔥 Keep up the amazing work!",
                inline=False
            )
            
            embed.add_field(
                name="📊 Categories",
                value="🎯 **Most Tasks Completed**\n📚 **Most Content Consumed**\n⚡ **Longest Streak**\n💻 **Most Code Commits**",
                inline=False
            )
            
            embed.set_footer(text="Compete with yourself and become the best version of you!")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"Leaderboard failed: {e}")
            await ctx.send("❌ Failed to show leaderboard. Please try again.")

    @commands.command(name='trends', help='Show your activity trends')
    async def show_trends(self, ctx):
        """Show activity trends over time"""
        try:
            insights = self.bot.preference_engine.get_user_insights()
            
            embed = discord.Embed(
                title="📈 Your Activity Trends",
                color=0x3498db,
                timestamp=datetime.utcnow()
            )
            
            # Weekly activity pattern
            most_active_days = insights.get('most_active_days', [])
            if most_active_days:
                trend_text = ""
                for day, count in most_active_days[:7]:
                    bar_length = int((count / most_active_days[0][1]) * 10) if most_active_days[0][1] > 0 else 0
                    bar = "█" * bar_length + "░" * (10 - bar_length)
                    trend_text += f"{day[:3]}: [{bar}] {count}\n"
                
                embed.add_field(name="📅 Weekly Pattern", value=f"```\n{trend_text}```", inline=False)
            
            # Content type trends
            content_dist = insights.get('content_type_distribution', {})
            if content_dist:
                total = sum(content_dist.values())
                content_text = ""
                for content_type, count in content_dist.items():
                    percentage = (count / total * 100) if total > 0 else 0
                    content_text += f"{content_type.title()}: {percentage:.1f}% ({count})\n"
                
                embed.add_field(name="📊 Content Distribution", value=content_text, inline=False)
            
            # Growth insights
            embed.add_field(
                name="🚀 Growth Insights",
                value="• You're most productive on weekdays\n• Keep up the consistent learning\n• Try diversifying your content mix",
                inline=False
            )
            
            embed.set_footer(text="Trends help you optimize your learning patterns!")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"Trends failed: {e}")
            await ctx.send("❌ Failed to show trends. Please try again.")

    @commands.command(name='compare', help='Compare different time periods')
    async def compare_periods(self, ctx, period: str = "week"):
        """Compare performance across time periods"""
        try:
            embed = discord.Embed(
                title=f"📊 Performance Comparison - {period.title()}",
                color=0x9b59b6,
                timestamp=datetime.utcnow()
            )
            
            # This is a simplified comparison - in a real implementation,
            # you'd store historical data for actual comparisons
            
            if period.lower() == "week":
                embed.add_field(
                    name="This Week vs Last Week",
                    value="📈 **Tasks**: 15 (+3)\n🎯 **Completion**: 85% (+10%)\n🔥 **Streak**: 5 days (+2)",
                    inline=True
                )
                
                embed.add_field(
                    name="Learning Activity",
                    value="📹 **Videos**: 8 (+2)\n📚 **Books**: 3 (+1)\n📰 **Articles**: 12 (+4)",
                    inline=True
                )
                
                trend = "📈 **Improving!**"
            
            elif period.lower() == "month":
                embed.add_field(
                    name="This Month vs Last Month",
                    value="📈 **Tasks**: 60 (+12)\n🎯 **Completion**: 82% (+5%)\n🔥 **Best Streak**: 7 days (+3)",
                    inline=True
                )
                
                embed.add_field(
                    name="Learning Growth",
                    value="📹 **Videos**: 32 (+8)\n📚 **Books**: 8 (+2)\n📰 **Articles**: 48 (+15)",
                    inline=True
                )
                
                trend = "🚀 **Great Progress!**"
            
            else:
                await ctx.send("❌ Supported periods: `week`, `month`")
                return
            
            embed.add_field(name="Overall Trend", value=trend, inline=False)
            embed.add_field(
                name="💡 Insights",
                value="• Consistency is your strength\n• Learning engagement is increasing\n• Task completion rate improving",
                inline=False
            )
            
            embed.set_footer(text="Keep building on this positive momentum!")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"Compare failed: {e}")
            await ctx.send("❌ Failed to compare periods. Please try again.")

    @commands.command(name='goals', help='Manage your goals and targets')
    async def manage_goals(self, ctx, action: str = "show", *, goal: str = ""):
        """Manage personal goals"""
        try:
            goals_file = "data/user_goals.json"
            
            # Load existing goals
            if os.path.exists(goals_file):
                with open(goals_file, 'r') as f:
                    goals_data = json.load(f)
            else:
                goals_data = {"goals": [], "completed": []}
            
            if action.lower() == "show":
                embed = discord.Embed(
                    title="🎯 Your Goals",
                    color=0xe74c3c,
                    timestamp=datetime.utcnow()
                )
                
                active_goals = goals_data.get("goals", [])
                if active_goals:
                    goals_text = "\n".join([f"• {goal}" for goal in active_goals])
                    embed.add_field(name="Active Goals", value=goals_text, inline=False)
                else:
                    embed.add_field(name="Active Goals", value="No goals set. Use `!goals add <goal>`", inline=False)
                
                completed_goals = goals_data.get("completed", [])
                if completed_goals:
                    completed_text = "\n".join([f"✅ {goal}" for goal in completed_goals[-5:]])
                    embed.add_field(name="Recently Completed", value=completed_text, inline=False)
                
            elif action.lower() == "add":
                if not goal:
                    await ctx.send("❌ Please specify a goal to add.")
                    return
                
                goals_data["goals"].append(goal)
                with open(goals_file, 'w') as f:
                    json.dump(goals_data, f, indent=2)
                
                embed = discord.Embed(
                    title="✅ Goal Added!",
                    description=f"Added: **{goal}**",
                    color=0x2ecc71
                )
                
            elif action.lower() == "complete":
                if not goal:
                    await ctx.send("❌ Please specify which goal to complete.")
                    return
                
                if goal in goals_data["goals"]:
                    goals_data["goals"].remove(goal)
                    goals_data["completed"].append(goal)
                    
                    with open(goals_file, 'w') as f:
                        json.dump(goals_data, f, indent=2)
                    
                    embed = discord.Embed(
                        title="🎉 Goal Completed!",
                        description=f"Completed: **{goal}**\n\nCongratulations! 🎊",
                        color=0xf39c12
                    )
                else:
                    await ctx.send("❌ Goal not found in your active goals.")
                    return
                    
            else:
                await ctx.send("❌ Valid actions: `show`, `add`, `complete`")
                return
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"Goals failed: {e}")
            await ctx.send("❌ Failed to manage goals. Please try again.")

async def setup(bot):
    await bot.add_cog(StatsCommands(bot))