"""
Fitness Commands - Discord commands for fitness tracking and health
"""

import discord
from discord.ext import commands
from datetime import datetime, timedelta
import json
import os

class FitnessCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fitness_file = "data/fitness_data.json"

    def _load_fitness_data(self):
        """Load fitness data from file"""
        if os.path.exists(self.fitness_file):
            with open(self.fitness_file, 'r') as f:
                return json.load(f)
        return {"workouts": [], "goals": {}, "stats": {}}

    def _save_fitness_data(self, data):
        """Save fitness data to file"""
        os.makedirs(os.path.dirname(self.fitness_file), exist_ok=True)
        with open(self.fitness_file, 'w') as f:
            json.dump(data, f, indent=2)

    @commands.command(name='workout', help='Log a workout session')
    async def log_workout(self, ctx, workout_type: str, duration: int, *, notes: str = ""):
        """Log a workout session"""
        try:
            data = self._load_fitness_data()
            
            workout = {
                "type": workout_type.lower(),
                "duration": duration,
                "notes": notes,
                "date": datetime.now().isoformat(),
                "calories_estimated": self._estimate_calories(workout_type.lower(), duration)
            }
            
            data["workouts"].append(workout)
            self._save_fitness_data(data)
            
            embed = discord.Embed(
                title="💪 Workout Logged!",
                color=0xe74c3c,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(name="Type", value=workout_type.title(), inline=True)
            embed.add_field(name="Duration", value=f"{duration} minutes", inline=True)
            embed.add_field(name="Est. Calories", value=f"{workout['calories_estimated']}", inline=True)
            
            if notes:
                embed.add_field(name="Notes", value=notes, inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"Workout log failed: {e}")
            await ctx.send("❌ Failed to log workout. Please try again.")

    def _estimate_calories(self, workout_type: str, duration: int) -> int:
        """Estimate calories burned (rough estimates)"""
        calories_per_minute = {
            "running": 12,
            "cycling": 8,
            "swimming": 10,
            "weightlifting": 6,
            "yoga": 3,
            "walking": 4,
            "hiit": 15,
            "cardio": 10
        }
        
        rate = calories_per_minute.get(workout_type, 8)
        return duration * rate

    @commands.command(name='fitness', help='Show fitness statistics')
    async def fitness_stats(self, ctx):
        """Show fitness statistics"""
        try:
            data = self._load_fitness_data()
            workouts = data.get("workouts", [])
            
            if not workouts:
                await ctx.send("💪 No workouts logged yet. Use `!workout <type> <duration>` to get started!")
                return
            
            # Calculate stats
            total_workouts = len(workouts)
            total_duration = sum(w["duration"] for w in workouts)
            total_calories = sum(w["calories_estimated"] for w in workouts)
            
            # This week stats
            week_ago = datetime.now() - timedelta(days=7)
            this_week = [w for w in workouts if datetime.fromisoformat(w["date"]) > week_ago]
            week_workouts = len(this_week)
            week_duration = sum(w["duration"] for w in this_week)
            
            # Most common workout type
            workout_types = {}
            for w in workouts:
                workout_types[w["type"]] = workout_types.get(w["type"], 0) + 1
            most_common = max(workout_types.items(), key=lambda x: x[1]) if workout_types else ("None", 0)
            
            embed = discord.Embed(
                title="💪 Fitness Statistics",
                color=0xe74c3c,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="All Time",
                value=f"🏃 {total_workouts} workouts\n⏱️ {total_duration} minutes\n🔥 {total_calories} calories",
                inline=True
            )
            
            embed.add_field(
                name="This Week",
                value=f"🏃 {week_workouts} workouts\n⏱️ {week_duration} minutes\n📈 {week_workouts/7:.1f} avg/day",
                inline=True
            )
            
            embed.add_field(
                name="Favorite",
                value=f"🏆 {most_common[0].title()}\n📊 {most_common[1]} times",
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"Fitness stats failed: {e}")
            await ctx.send("❌ Failed to get fitness stats. Please try again.")

    @commands.command(name='workouts', help='Show recent workouts')
    async def recent_workouts(self, ctx, limit: int = 10):
        """Show recent workouts"""
        try:
            data = self._load_fitness_data()
            workouts = data.get("workouts", [])
            
            if not workouts:
                await ctx.send("💪 No workouts logged yet!")
                return
            
            recent = workouts[-limit:]
            recent.reverse()
            
            embed = discord.Embed(
                title=f"🏃 Last {len(recent)} Workouts",
                color=0xe74c3c,
                timestamp=datetime.utcnow()
            )
            
            for workout in recent:
                date = datetime.fromisoformat(workout["date"]).strftime("%m/%d")
                embed.add_field(
                    name=f"{workout['type'].title()} - {date}",
                    value=f"⏱️ {workout['duration']} min | 🔥 {workout['calories_estimated']} cal",
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"Recent workouts failed: {e}")
            await ctx.send("❌ Failed to get recent workouts. Please try again.")

async def setup(bot):
    await bot.add_cog(FitnessCommands(bot))