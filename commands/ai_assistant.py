"""
AI Assistant Commands - Discord commands for AI-powered assistance
"""

import discord
from discord.ext import commands
from datetime import datetime, timezone
import os
import asyncio

class AIAssistantCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.openai_api_key = os.getenv('OPENAI_API_KEY')

    @commands.command(name='list_models', help='List available Gemini models')
    async def list_models(self, ctx):
        """List available Gemini models"""
        try:
            async with ctx.typing():
                models = await self.bot.gemini.list_available_models()
                
                if isinstance(models, list):
                    model_list = '\n'.join([f"• {model}" for model in models[:10]])  # Show first 10
                    description = f"Available models:\n```{model_list}```"
                    color = 0x00ff00
                else:
                    description = str(models)
                    color = 0xff0000
                
                embed = discord.Embed(
                    title="🔧 Available Gemini Models",
                    description=description,
                    color=color,
                    timestamp=datetime.now(timezone.utc)
                )
                
                await ctx.send(embed=embed)
                
        except Exception as e:
            await ctx.send(f"❌ Failed to list models: {str(e)}")

    @commands.command(name='test_gemini', help='Test Gemini API connection')
    async def test_gemini(self, ctx):
        """Test the Gemini API connection"""
        try:
            async with ctx.typing():
                result = await self.bot.gemini.test_api_connection()
                
                embed = discord.Embed(
                    title="🔧 Gemini API Test",
                    description=result,
                    color=0x00ff00 if "✅" in result else 0xff0000,
                    timestamp=datetime.now(timezone.utc)
                )
                
                await ctx.send(embed=embed)
                
        except Exception as e:
            await ctx.send(f"❌ Test failed: {str(e)}")

    @commands.command(name='ask', help='Ask the AI assistant a question')
    async def ask_ai(self, ctx, *, question: str):
        """Ask AI assistant a question"""
        try:
            # Simple response system (can be enhanced with actual AI API)
            responses = self._get_smart_response(question.lower())
            
            embed = discord.Embed(
                title="🤖 AI Assistant",
                description=responses,
                color=0x3498db,
                timestamp=datetime.utcnow()
            )
            
            embed.set_footer(text="AI responses are generated suggestions")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"AI ask failed: {e}")
            await ctx.send("❌ Failed to process your question. Please try again.")

    def _get_smart_response(self, question: str) -> str:
        """Generate smart responses based on keywords (placeholder for actual AI)"""
        if 'productivity' in question or 'productive' in question:
            return ("🎯 **Productivity Tips:**\n"
                   "• Use the Pomodoro Technique (25min focus sessions)\n"
                   "• Prioritize your tasks using the Eisenhower Matrix\n"
                   "• Eliminate distractions during work hours\n"
                   "• Take regular breaks to maintain focus\n"
                   "• Use !focus 25 to start a focus session!")
        
        elif 'learn' in question or 'study' in question:
            return ("📚 **Learning Strategies:**\n"
                   "• Active recall: Test yourself regularly\n"
                   "• Spaced repetition: Review at intervals\n"
                   "• Teach others to reinforce your understanding\n"
                   "• Break complex topics into smaller chunks\n"
                   "• Use !learn <topic> for structured learning paths!")
        
        elif 'coding' in question or 'programming' in question:
            return ("💻 **Coding Best Practices:**\n"
                   "• Write clean, readable code with good comments\n"
                   "• Follow the DRY principle (Don't Repeat Yourself)\n"
                   "• Test your code regularly\n"
                   "• Use version control (Git) for all projects\n"
                   "• Practice coding challenges daily\n"
                   "• Check out !youtube programming for tutorials!")
        
        elif 'motivation' in question or 'motivated' in question:
            return ("🚀 **Motivation Boosters:**\n"
                   "• Set clear, achievable goals\n"
                   "• Celebrate small victories\n"
                   "• Track your progress daily\n"
                   "• Surround yourself with inspiring content\n"
                   "• Remember your 'why' - your purpose\n"
                   "• Use !stats to see your progress!")
        
        elif 'time management' in question or 'time' in question:
            return ("⏰ **Time Management:**\n"
                   "• Plan your day the night before\n"
                   "• Use time-blocking for important tasks\n"
                   "• Batch similar tasks together\n"
                   "• Learn to say no to non-essential activities\n"
                   "• Use !today to see your daily agenda!")
        
        elif 'career' in question or 'job' in question:
            return ("🎯 **Career Development:**\n"
                   "• Continuously update your skills\n"
                   "• Build a strong professional network\n"
                   "• Create a portfolio of your best work\n"
                   "• Seek feedback and act on it\n"
                   "• Stay updated with industry trends\n"
                   "• Use !news to stay informed!")
        
        else:
            return ("🤖 I'm here to help! Try asking about:\n"
                   "• **Productivity**: Tips for better focus and efficiency\n"
                   "• **Learning**: Study strategies and skill development\n"
                   "• **Coding**: Programming best practices\n"
                   "• **Motivation**: Ways to stay motivated\n"
                   "• **Time Management**: Better time usage\n"
                   "• **Career**: Professional development advice")

    @commands.command(name='suggest', help='Get suggestions based on your activity')
    async def get_suggestions(self, ctx):
        """Get AI-powered suggestions based on user activity"""
        try:
            # Get user insights from preference engine
            insights = self.bot.preference_engine.get_user_insights()
            
            suggestions = []
            
            # Analyze activity patterns
            total_interactions = insights.get('total_interactions', 0)
            content_dist = insights.get('content_type_distribution', {})
            
            if total_interactions < 10:
                suggestions.append("🎯 **Get Started**: Try exploring more content to get personalized recommendations!")
            
            # Content type suggestions
            if content_dist.get('youtube', 0) > content_dist.get('books', 0):
                suggestions.append("📚 **Balance Tip**: Consider adding more books to complement your video learning!")
            elif content_dist.get('books', 0) > content_dist.get('youtube', 0):
                suggestions.append("📹 **Visual Learning**: Try some video tutorials to reinforce your reading!")
            
            # Activity suggestions
            most_active_days = insights.get('most_active_days', [])
            if most_active_days:
                most_active_day = most_active_days[0][0]
                suggestions.append(f"📅 **Peak Day**: You're most active on {most_active_day}s - schedule important learning then!")
            
            # General suggestions
            suggestions.extend([
                "🎯 **Daily Habit**: Use !today each morning to plan your day",
                "🔥 **Stay Focused**: Try !focus sessions for better productivity",
                "📊 **Track Progress**: Check !stats regularly to monitor your growth"
            ])
            
            embed = discord.Embed(
                title="🤖 Personalized Suggestions",
                description="\n\n".join(suggestions[:5]),
                color=0x9b59b6,
                timestamp=datetime.utcnow()
            )
            
            embed.set_footer(text="Suggestions based on your activity patterns")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"Suggestions failed: {e}")
            await ctx.send("❌ Failed to generate suggestions. Please try again.")

    @commands.command(name='analyze', help='Analyze your learning patterns')
    async def analyze_patterns(self, ctx):
        """Analyze user's learning and productivity patterns"""
        try:
            insights = self.bot.preference_engine.get_user_insights()
            
            embed = discord.Embed(
                title="📊 Your Learning Analysis",
                color=0x1abc9c,
                timestamp=datetime.utcnow()
            )
            
            # Activity overview
            total_interactions = insights.get('total_interactions', 0)
            embed.add_field(
                name="📈 Activity Level",
                value=f"Total interactions: {total_interactions}\n" +
                      ("🌟 Very Active!" if total_interactions > 100 else
                       "👍 Good engagement!" if total_interactions > 30 else
                       "📚 Just getting started!"),
                inline=False
            )
            
            # Content preferences
            content_dist = insights.get('content_type_distribution', {})
            if content_dist:
                content_text = "\n".join([f"{k.title()}: {v}" for k, v in content_dist.items()])
                embed.add_field(
                    name="📊 Content Preferences",
                    value=content_text,
                    inline=True
                )
            
            # Activity patterns
            most_active_days = insights.get('most_active_days', [])[:3]
            if most_active_days:
                days_text = "\n".join([f"{day}: {count}" for day, count in most_active_days])
                embed.add_field(
                    name="📅 Most Active Days",
                    value=days_text,
                    inline=True
                )
            
            # Recommendations
            recommendations = [
                "🎯 Focus on consistency over intensity",
                "📚 Mix different types of content for better learning",
                "🔄 Regular review helps retention",
                "💡 Teaching others reinforces your knowledge"
            ]
            
            embed.add_field(
                name="💡 Recommendations",
                value="\n".join(recommendations),
                inline=False
            )
            
            embed.set_footer(text="Keep learning and growing! 🚀")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"Analysis failed: {e}")
            await ctx.send("❌ Failed to analyze patterns. Please try again.")

    @commands.command(name='brainstorm', help='Get creative ideas for a topic')
    async def brainstorm(self, ctx, *, topic: str):
        """Generate creative ideas around a topic"""
        try:
            ideas = self._generate_ideas(topic.lower())
            
            embed = discord.Embed(
                title=f"💡 Brainstorming: {topic.title()}",
                description="Here are some creative ideas to explore:",
                color=0xf39c12,
                timestamp=datetime.utcnow()
            )
            
            for i, idea in enumerate(ideas, 1):
                embed.add_field(
                    name=f"💡 Idea #{i}",
                    value=idea,
                    inline=False
                )
            
            embed.set_footer(text="Use these as starting points for your projects!")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"Brainstorm failed: {e}")
            await ctx.send("❌ Failed to generate ideas. Please try again.")

    def _generate_ideas(self, topic: str) -> list:
        """Generate ideas based on topic"""
        if 'app' in topic or 'application' in topic:
            return [
                "📱 Mobile app that solves a daily problem you face",
                "🤖 AI-powered tool that automates repetitive tasks",
                "🎮 Gamified learning app for a skill you want to teach",
                "📊 Dashboard that visualizes personal data meaningfully",
                "🌐 Web app that connects people with similar interests"
            ]
        
        elif 'project' in topic or 'coding' in topic:
            return [
                "🔧 Build a tool that improves your own workflow",
                "📈 Create an analytics dashboard for social media",
                "🤖 Develop a chatbot for a specific domain",
                "🎨 Generate art or music using code",
                "📚 Build a learning platform for a niche topic"
            ]
        
        elif 'business' in topic or 'startup' in topic:
            return [
                "🎯 Solve a problem you personally experience daily",
                "🌱 Create a sustainable alternative to existing products",
                "📱 Build a platform that connects communities",
                "🤝 Offer a service that saves people time",
                "📊 Help businesses make better data-driven decisions"
            ]
        
        else:
            return [
                f"🔍 Research current trends in {topic}",
                f"🎓 Create educational content about {topic}",
                f"🛠️ Build a tool related to {topic}",
                f"📝 Write comprehensive guides on {topic}",
                f"🤝 Connect with others interested in {topic}"
            ]

async def setup(bot):
    await bot.add_cog(AIAssistantCommands(bot))