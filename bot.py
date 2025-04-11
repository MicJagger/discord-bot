from discord.ext import commands
import discord
from dotenv import load_dotenv
import os
import yt_dlp

intents=discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents) # , help_command=None
intents.message_content = True


# commands

@bot.command()
async def clear(ctx):
    await ctx.send("clear")

# @bot.command()
# async def help(ctx):
#     await ctx.send("help")

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        await ctx.send("join")
        return True
    else:
        await ctx.send("not join")
        return False

@bot.command()
async def leave(ctx):
    await ctx.send("leave")

@bot.command()
async def pause(ctx):
    await ctx.send("pause")

@bot.command()
async def next(ctx):
    await skip(ctx)

@bot.command()
async def play(ctx, *, query="null"):
    inCall = ctx.voice_client
    if not inCall:
        inCall = await join(ctx)
    if not inCall:
        return
    if query == "null":
        await ctx.send("need query")
        return
    await ctx.send("play " + query)

@bot.command()
async def queue(ctx):
    await ctx.send("queue")

@bot.command()
async def resume(ctx):
    await ctx.send("resume")

@bot.command()
async def skip(ctx):
    await ctx.send("skip")

@bot.command()
async def stop(ctx):
    await ctx.send("stop")

@bot.command()
async def unpause(ctx):
    await resume(ctx)


# helpers




load_dotenv()
bot.run(os.getenv("TOKEN"))