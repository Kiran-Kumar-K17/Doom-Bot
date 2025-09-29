"""
Learning Commands - Discord commands for YouTube, books, and educational content
"""

import discord
from discord.ext import commands
from datetime import datetime
from typing import Optional
import asyncio

class LearningCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.youtube = bot.youtube
        self.books = bot.books
        self.news = bot.news

    @commands.command(name='recommend', help='Get personalized recommendations')
    async def get_recommendations(self, ctx, content_type: Optional[str] = 'all'):
        """Get personalized recommendations"""
        try:
            embed = discord.Embed(
                title="🤖 Personalized Recommendations",
                color=0x3498db,
                timestamp=datetime.utcnow()
            )
            
            if content_type.lower() in ['all', 'video', 'youtube']:
                youtube_rec = self.bot.preference_engine.get_recommendation('youtube')
                if youtube_rec:
                    embed.add_field(
                        name="📹 Recommended Video",
                        value=f"**[{youtube_rec['title'][:60]}...]({youtube_rec['url']})**\n"
                              f"👤 {youtube_rec['channel']}\n"
                              f"📅 {youtube_rec.get('published_at', 'Unknown date')[:10]}",
                        inline=False
                    )
            
            if content_type.lower() in ['all', 'book', 'books']:
                book_rec = self.bot.preference_engine.get_recommendation('books')
                if book_rec:
                    authors = ', '.join(book_rec.get('authors', [])[:2])
                    embed.add_field(
                        name="📚 Recommended Book",
                        value=f"**{book_rec['title'][:60]}...**\n"
                              f"✍️ {authors}\n"
                              f"⭐ {book_rec.get('rating', 'N/A')} rating\n"
                              f"🔗 [More Info]({book_rec.get('info_link', '#')})",
                        inline=False
                    )
            
            if content_type.lower() in ['all', 'news']:
                news_items = await self.news.get_top_news(3)
                if news_items:
                    news_text = "\n".join([
                        f"• **[{item['title'][:50]}...]({item['url']})**\n  📰 {item['source']}"
                        for item in news_items
                    ])
                    embed.add_field(name="📰 Latest Tech News", value=news_text[:1000], inline=False)
            
            if not embed.fields:
                embed.description = "No recommendations available right now. Check back later!"
            else:
                embed.set_footer(text="👍 React with 👍 if you like these recommendations!")
            
            message = await ctx.send(embed=embed)
            
            # Add reaction for feedback
            if embed.fields:
                await message.add_reaction('👍')
                await message.add_reaction('👎')
            
        except Exception as e:
            self.bot.logger.error(f"Recommend command failed: {e}")
            await ctx.send("❌ Failed to get recommendations. Please try again later.")

    @commands.command(name='youtube', aliases=['yt'], help='Search YouTube videos')
    async def search_youtube(self, ctx, *, query):
        """Search YouTube videos"""
        try:
            videos = await self.youtube.search_videos_by_topic(query, max_results=5)
            
            if not videos:
                await ctx.send(f"❌ No videos found for: {query}")
                return
            
            embed = discord.Embed(
                title=f"📹 YouTube Search: {query}",
                color=0xff0000,
                timestamp=datetime.utcnow()
            )
            
            for i, video in enumerate(videos[:5], 1):
                embed.add_field(
                    name=f"{i}. {video['title'][:50]}...",
                    value=f"👤 {video['channel']}\n"
                          f"📅 {video.get('published_at', 'Unknown')[:10]}\n"
                          f"🔗 [Watch Video]({video['url']})",
                    inline=False
                )
            
            embed.set_footer(text="React with numbers to track a video as watched!")
            
            message = await ctx.send(embed=embed)
            
            # Add number reactions for tracking
            number_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
            for i in range(min(len(videos), 5)):
                await message.add_reaction(number_emojis[i])
            
            # Handle reactions for tracking
            def check(reaction, user):
                return (user == ctx.author and 
                       str(reaction.emoji) in number_emojis[:len(videos)] and 
                       reaction.message.id == message.id)
            
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                video_index = number_emojis.index(str(reaction.emoji))
                selected_video = videos[video_index]
                
                # Track the video
                await self.youtube.track_watched_video(selected_video['video_id'], 5)
                
                track_embed = discord.Embed(
                    title="✅ Video Tracked",
                    description=f"Marked **{selected_video['title'][:50]}...** as watched!",
                    color=0x2ecc71
                )
                await ctx.send(embed=track_embed)
                
            except asyncio.TimeoutError:
                pass
            
        except Exception as e:
            self.bot.logger.error(f"YouTube search failed: {e}")
            await ctx.send("❌ Failed to search YouTube. Please try again later.")

    @commands.command(name='books', help='Search for books')
    async def search_books(self, ctx, *, query):
        """Search for books"""
        try:
            books = await self.books.search_books_by_topic(query, max_results=5)
            
            if not books:
                await ctx.send(f"❌ No books found for: {query}")
                return
            
            embed = discord.Embed(
                title=f"📚 Book Search: {query}",
                color=0x8b4513,
                timestamp=datetime.utcnow()
            )
            
            for i, book in enumerate(books[:5], 1):
                authors = ', '.join(book.get('authors', [])[:2])
                rating_text = f"⭐ {book.get('rating', 'N/A')}" if book.get('rating') else ""
                
                embed.add_field(
                    name=f"{i}. {book['title'][:50]}...",
                    value=f"✍️ {authors}\n"
                          f"{rating_text}\n"
                          f"📄 {book.get('page_count', 'Unknown')} pages\n"
                          f"🔗 [More Info]({book.get('info_link', '#')})",
                    inline=False
                )
            
            embed.set_footer(text="React with numbers to add a book to your reading list!")
            
            message = await ctx.send(embed=embed)
            
            # Add reactions
            number_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
            for i in range(min(len(books), 5)):
                await message.add_reaction(number_emojis[i])
            
            # Handle reactions
            def check(reaction, user):
                return (user == ctx.author and 
                       str(reaction.emoji) in number_emojis[:len(books)] and 
                       reaction.message.id == message.id)
            
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                book_index = number_emojis.index(str(reaction.emoji))
                selected_book = books[book_index]
                
                # Track the book
                await self.books.track_read_book(selected_book['id'], 'want_to_read', 4)
                
                track_embed = discord.Embed(
                    title="✅ Book Added",
                    description=f"Added **{selected_book['title'][:50]}...** to your reading list!",
                    color=0x2ecc71
                )
                await ctx.send(embed=track_embed)
                
            except asyncio.TimeoutError:
                pass
            
        except Exception as e:
            self.bot.logger.error(f"Book search failed: {e}")
            await ctx.send("❌ Failed to search books. Please try again later.")

    @commands.command(name='news', help='Get latest tech news')
    async def get_news(self, ctx, category: Optional[str] = 'technology'):
        """Get latest news"""
        try:
            if category.lower() == 'programming':
                news_items = await self.news.get_programming_news()
            else:
                news_items = await self.news.get_top_news(8)
            
            if not news_items:
                await ctx.send("❌ No news available right now.")
                return
            
            embed = discord.Embed(
                title=f"📰 Latest {category.title()} News",
                color=0x1f77b4,
                timestamp=datetime.utcnow()
            )
            
            for i, item in enumerate(news_items[:6], 1):
                published_date = item.get('published_at', '')[:10]
                embed.add_field(
                    name=f"{i}. {item['title'][:50]}...",
                    value=f"📰 {item['source']}\n"
                          f"📅 {published_date}\n"
                          f"🔗 [Read Article]({item['url']})",
                    inline=False
                )
            
            embed.set_footer(text="Click links to read full articles")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"News command failed: {e}")
            await ctx.send("❌ Failed to fetch news. Please try again later.")

    @commands.command(name='interests', help='Manage your learning interests')
    async def manage_interests(self, ctx, action: Optional[str] = 'show', *, interests: str = ""):
        """Manage learning interests"""
        try:
            if action.lower() == 'show':
                youtube_interests = self.youtube.get_user_interests()
                book_genres = self.books.get_user_genres()
                
                embed = discord.Embed(
                    title="🎯 Your Learning Interests",
                    color=0x9b59b6,
                    timestamp=datetime.utcnow()
                )
                
                if youtube_interests:
                    embed.add_field(
                        name="📹 YouTube Topics",
                        value="• " + "\n• ".join(youtube_interests[:8]),
                        inline=False
                    )
                
                if book_genres:
                    embed.add_field(
                        name="📚 Book Genres",
                        value="• " + "\n• ".join(book_genres[:8]),
                        inline=False
                    )
                
                embed.set_footer(text="Use !interests add <topics> to add new interests")
                
            elif action.lower() == 'add':
                if not interests:
                    await ctx.send("❌ Please specify interests to add. Example: `!interests add python, machine learning`")
                    return
                
                new_interests = [interest.strip() for interest in interests.split(',')]
                
                # Update YouTube interests
                current_youtube = self.youtube.get_user_interests()
                updated_youtube = list(set(current_youtube + new_interests))
                self.youtube.update_user_interests(updated_youtube[:10])
                
                # Update book genres  
                current_books = self.books.get_user_genres()
                updated_books = list(set(current_books + new_interests))
                self.books.update_user_genres(updated_books[:8])
                
                embed = discord.Embed(
                    title="✅ Interests Updated",
                    description=f"Added: {', '.join(new_interests)}",
                    color=0x2ecc71
                )
            
            else:
                await ctx.send("❌ Invalid action. Use: `!interests show` or `!interests add <topics>`")
                return
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"Interests command failed: {e}")
            await ctx.send("❌ Failed to manage interests. Please try again later.")

    @commands.command(name='learn', help='Get a structured learning path')
    async def learning_path(self, ctx, *, topic: str):
        """Generate a learning path for a topic"""
        try:
            # Get diverse content for the topic
            videos = await self.youtube.search_videos_by_topic(f"{topic} tutorial", max_results=3)
            books = await self.books.search_books_by_topic(topic, max_results=2)
            
            embed = discord.Embed(
                title=f"🎓 Learning Path: {topic.title()}",
                description=f"Here's a structured approach to learn {topic}:",
                color=0x3498db,
                timestamp=datetime.utcnow()
            )
            
            # Step 1: Fundamentals
            if videos:
                video_text = f"**[{videos[0]['title'][:40]}...]({videos[0]['url']})**\n👤 {videos[0]['channel']}"
                embed.add_field(name="📹 Step 1: Watch Introduction", value=video_text, inline=False)
            
            # Step 2: Deep Learning
            if books:
                book_text = f"**{books[0]['title'][:40]}...**\n✍️ {', '.join(books[0].get('authors', [])[:2])}"
                embed.add_field(name="📚 Step 2: Read Fundamentals", value=book_text, inline=False)
            
            # Step 3: Practice
            if len(videos) > 1:
                practice_video = f"**[{videos[1]['title'][:40]}...]({videos[1]['url']})**\n👤 {videos[1]['channel']}"
                embed.add_field(name="💻 Step 3: Hands-on Practice", value=practice_video, inline=False)
            
            # Step 4: Advanced
            if len(videos) > 2:
                advanced_video = f"**[{videos[2]['title'][:40]}...]({videos[2]['url']})**\n👤 {videos[2]['channel']}"
                embed.add_field(name="🚀 Step 4: Advanced Concepts", value=advanced_video, inline=False)
            
            embed.add_field(
                name="💡 Learning Tips",
                value="• Take notes while learning\n• Practice with real projects\n• Join communities\n• Ask questions",
                inline=False
            )
            
            embed.set_footer(text="Use !focus 25 to start a focused study session!")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"Learning path command failed: {e}")
            await ctx.send("❌ Failed to generate learning path. Please try again later.")

async def setup(bot):
    await bot.add_cog(LearningCommands(bot))