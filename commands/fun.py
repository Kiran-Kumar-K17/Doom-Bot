"""
Fun Commands - Discord commands for entertainment and light-hearted features
"""

import discord
from discord.ext import commands
from datetime import datetime
import random
import asyncio

class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='quote', help='Get an inspirational quote')
    async def inspirational_quote(self, ctx):
        """Get a random inspirational quote"""
        quotes = [
            ("The only way to do great work is to love what you do.", "Steve Jobs"),
            ("Innovation distinguishes between a leader and a follower.", "Steve Jobs"),
            ("Life is what happens to you while you're busy making other plans.", "John Lennon"),
            ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
            ("It is during our darkest moments that we must focus to see the light.", "Aristotle"),
            ("The only impossible journey is the one you never begin.", "Tony Robbins"),
            ("Success is not final, failure is not fatal: it is the courage to continue that counts.", "Winston Churchill"),
            ("The only person you are destined to become is the person you decide to be.", "Ralph Waldo Emerson"),
            ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
            ("The only limit to our realization of tomorrow will be our doubts of today.", "Franklin D. Roosevelt"),
            ("Code is like humor. When you have to explain it, it's bad.", "Cory House"),
            ("First, solve the problem. Then, write the code.", "John Johnson"),
            ("Programming isn't about what you know; it's about what you can figure out.", "Chris Pine"),
            ("The best error message is the one that never shows up.", "Thomas Fuchs"),
            ("Debugging is twice as hard as writing the code in the first place.", "Brian Kernighan")
        ]
        
        quote, author = random.choice(quotes)
        
        embed = discord.Embed(
            title="💫 Daily Inspiration",
            description=f"*\"{quote}\"*\n\n— {author}",
            color=0xf39c12,
            timestamp=datetime.utcnow()
        )
        
        await ctx.send(embed=embed)

    @commands.command(name='joke', help='Get a programming joke')
    async def programming_joke(self, ctx):
        """Get a random programming joke"""
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
            "How many programmers does it take to change a light bulb? None, that's a hardware problem! 💡",
            "Why do Java developers wear glasses? Because they can't C#! 👓",
            "What's a programmer's favorite hangout place? Foo Bar! 🍺",
            "Why did the programmer quit his job? He didn't get arrays! 📊",
            "How do you comfort a JavaScript bug? You console it! 🐞",
            "Why don't programmers like nature? It has too many bugs! 🌿",
            "What do you call a programmer from Finland? Nerdic! 🇫🇮",
            "Why did the developer go broke? Because he used up all his cache! 💸",
            "What's the object-oriented way to become wealthy? Inheritance! 💰",
            "Why do programmers always mix up Halloween and Christmas? Because Oct 31 equals Dec 25! 🎃🎄",
            "What did the Java code say to the C code? You've got no class! ☕"
        ]
        
        joke = random.choice(jokes)
        
        embed = discord.Embed(
            title="😄 Programming Humor",
            description=joke,
            color=0x3498db,
            timestamp=datetime.utcnow()
        )
        
        await ctx.send(embed=embed)

    @commands.command(name='fact', help='Get an interesting tech fact')
    async def tech_fact(self, ctx):
        """Get a random tech fact"""
        facts = [
            "🌐 The first website ever created is still online: info.cern.ch",
            "📧 The first email was sent in 1971 by Ray Tomlinson to himself",
            "🐍 Python was named after Monty Python's Flying Circus, not the snake",
            "🔍 Google processes over 8.5 billion searches per day",
            "💾 The first hard drive in 1956 could store 5MB and weighed over a ton",
            "🎮 The first computer bug was an actual bug found in a computer in 1947",
            "📱 There are more mobile phones than toothbrushes in the world",
            "🌍 90% of the world's data was created in the last 2 years",
            "⌨️ The QWERTY keyboard layout was designed to slow down typing to prevent typewriter jams",
            "🖥️ The first computer programmer was Ada Lovelace in the 1840s",
            "📺 More video is uploaded to YouTube in 60 days than the 3 major US networks created in 60 years",
            "🔐 The term 'bug' in programming came from Admiral Grace Hopper"
        ]
        
        fact = random.choice(facts)
        
        embed = discord.Embed(
            title="🤓 Tech Fact",
            description=fact,
            color=0x9b59b6,
            timestamp=datetime.utcnow()
        )
        
        await ctx.send(embed=embed)

    @commands.command(name='motivate', help='Get pumped up with motivation')
    async def motivation(self, ctx):
        """Send motivational message"""
        motivations = [
            "🚀 **You're destined for greatness!** Every line of code you write is a step toward mastery!",
            "💪 **Iron sharpens iron!** Your challenges today are building the strength you need for tomorrow!",
            "🎯 **Focus on progress, not perfection!** Every small step forward is a victory worth celebrating!",
            "🔥 **Your potential is unlimited!** The only ceiling is the one you accept in your mind!",
            "⚡ **You're not just learning to code, you're learning to think!** That's a superpower!",
            "🌟 **Consistency beats perfection every time!** Show up, do the work, trust the process!",
            "🛠️ **Every problem you solve makes you stronger!** Embrace the debugging journey!",
            "🎮 **Level up your skills daily!** Yesterday's impossible is today's warm-up!",
            "🧠 **Your brain is a muscle!** The more you challenge it, the stronger it becomes!",
            "🏆 **Champions are made in the moments when no one is watching!** Keep grinding!"
        ]
        
        motivation = random.choice(motivations)
        
        embed = discord.Embed(
            title="💪 Iron Doom Motivation",
            description=motivation,
            color=0xe74c3c,
            timestamp=datetime.utcnow()
        )
        
        embed.set_footer(text="You've got this! 🔥")
        
        await ctx.send(embed=embed)

    @commands.command(name='roll', help='Roll a dice')
    async def roll_dice(self, ctx, sides: int = 6):
        """Roll a dice with specified sides"""
        if sides < 2 or sides > 100:
            await ctx.send("❌ Dice must have between 2 and 100 sides!")
            return
        
        result = random.randint(1, sides)
        
        embed = discord.Embed(
            title="🎲 Dice Roll",
            description=f"Rolling a {sides}-sided dice...\n\n🎯 **Result: {result}**",
            color=0x3498db,
            timestamp=datetime.utcnow()
        )
        
        await ctx.send(embed=embed)

    @commands.command(name='coinflip', help='Flip a coin')
    async def flip_coin(self, ctx):
        """Flip a coin"""
        result = random.choice(['Heads', 'Tails'])
        emoji = '👤' if result == 'Heads' else '⚜️'
        
        embed = discord.Embed(
            title="🪙 Coin Flip",
            description=f"Flipping a coin...\n\n{emoji} **{result}!**",
            color=0xf1c40f,
            timestamp=datetime.utcnow()
        )
        
        await ctx.send(embed=embed)

    @commands.command(name='8ball', help='Ask the magic 8-ball')
    async def magic_8ball(self, ctx, *, question: str):
        """Magic 8-ball responses"""
        responses = [
            "It is certain 🔮",
            "Without a doubt ✨",
            "Yes definitely 👍",
            "You may rely on it 💯",
            "Most likely 📈",
            "Outlook good 🌟",
            "Signs point to yes ✅",
            "Reply hazy, try again 🌫️",
            "Ask again later ⏰",
            "Better not tell you now 🤫",
            "Cannot predict now 🔄",
            "Concentrate and ask again 🧘",
            "Don't count on it ❌",
            "Outlook not so good 📉",
            "My sources say no 🚫",
            "Very doubtful 🤔"
        ]
        
        response = random.choice(responses)
        
        embed = discord.Embed(
            title="🎱 Magic 8-Ball",
            color=0x2c3e50,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=response, inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name='choose', help='Choose between options')
    async def choose_option(self, ctx, *, options: str):
        """Choose between comma-separated options"""
        choices = [choice.strip() for choice in options.split(',')]
        
        if len(choices) < 2:
            await ctx.send("❌ Please provide at least 2 options separated by commas!")
            return
        
        if len(choices) > 10:
            await ctx.send("❌ Maximum 10 options allowed!")
            return
        
        chosen = random.choice(choices)
        
        embed = discord.Embed(
            title="🎯 Decision Made!",
            color=0xe67e22,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Options", value="\n".join([f"• {choice}" for choice in choices]), inline=False)
        embed.add_field(name="My Choice", value=f"🎲 **{chosen}**", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name='progress', help='Show a random progress bar')
    async def progress_bar(self, ctx, task: str = "Life"):
        """Show a fun progress bar"""
        progress = random.randint(10, 95)
        bar_length = 20
        filled_length = int(bar_length * progress / 100)
        
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        embed = discord.Embed(
            title="📊 Progress Tracker",
            color=0x1abc9c,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name=f"Loading {task}...",
            value=f"```\n[{bar}] {progress}%\n```",
            inline=False
        )
        
        if progress < 30:
            status = "🔴 Just getting started!"
        elif progress < 60:
            status = "🟡 Making good progress!"
        elif progress < 90:
            status = "🟢 Almost there!"
        else:
            status = "🌟 Nearly complete!"
        
        embed.add_field(name="Status", value=status, inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name='compliment', help='Get a programming compliment')
    async def compliment(self, ctx, user: discord.Member = None):
        """Give a programming-related compliment"""
        target = user or ctx.author
        
        compliments = [
            "writes code so clean it could be in a museum! 🎨",
            "debugs faster than Neo dodges bullets! 🕶️",
            "has algorithms that would make Dijkstra proud! 🏆",
            "refactors code like a master sculptor! ⚒️",
            "has commits so good they should be featured! ⭐",
            "writes documentation that actually makes sense! 📚",
            "handles edge cases like a superhero! 🦸",
            "optimizes code like a performance wizard! ⚡",
            "designs APIs that are pure poetry! 📝",
            "solves problems with the elegance of a chess grandmaster! ♟️"
        ]
        
        compliment = random.choice(compliments)
        
        embed = discord.Embed(
            title="💝 Coding Compliment",
            description=f"{target.mention} {compliment}",
            color=0xe91e63,
            timestamp=datetime.utcnow()
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(FunCommands(bot))