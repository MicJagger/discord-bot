from discord.ext import commands
import discord
import os

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

@bot.event
async def on_message(message):
    if message.author != bot.user:
        await message.channel.send("no")

bot.run(os.getenv("DISCORD_KEY"))