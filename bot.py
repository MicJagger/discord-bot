import asyncio
from discord.ext import commands
import discord
from dotenv import load_dotenv
import os
import yt_dlp

try:
    import nacl
except ImportError:
    try:
        if os.name == "nt":
            os.system("py -m pip install pynacl")
        else:
            os.system("python3 -m install pynacl")
    except Exception as e:
        print("PyNaCl install error: ", e)
        exit()

intents=discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents) # , help_command=None
intents.message_content = True

# (url, title)
linkQueue = []


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
        await ctx.author.voice.channel.connect()
        await ctx.send("joined voice channel")
        return True
    else:
        await ctx.send("you gotta be in a voice channel first")
        return False

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("left voice channel")
        return True
    else:
        await ctx.send("didn't leave the voice channel I'm not in")
        return False

@bot.command()
async def next(ctx):
    await skip(ctx)

@bot.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("paused")
    else:
        await ctx.send("can't pause what isn't playing")

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
    
    if ("youtube.com" in query) or ("youtu.be" in query):
        info = getInfo(query)
    else:
        await ctx.send(f"searching: {query}")
        info = searchYoutube(query)
    
    if not info:
        await ctx.send("video not found")
        return
    
    url = info["url"]
    title = info["title"]

    if not ctx.voice_client.is_playing():
        await ctx.send(f"playing: {title}")
        playVideo(ctx.voice_client, url)
    else:
        linkQueue.append((url, title))
        await ctx.send(f"queued: {title}")

@bot.command()
async def queue(ctx):
    if linkQueue:
        queueText = "queue:\n"
        i = 1
        for video in linkQueue:
            queueText += str(i) + ". " + video[1] + "\n"
            i += 1
        await ctx.send(queueText)
    else:
        await ctx.send("queue empty")

@bot.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("resumed")
    else:
        await ctx.send("can't resume what isn't paused")

@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("skipping")
    else:
        await ctx.send("can't skip what isn't playing")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        linkQueue.clear()
        await ctx.send("stopped everything")
    else:
        await ctx.send("nothing to stop")

@bot.command()
async def unpause(ctx):
    await resume(ctx)


# helpers

def checkNext(voice_client):
    if linkQueue:
        song_url, song_title = linkQueue.pop(0)
        playVideo(voice_client, song_url)
        asyncio.run_coroutine_threadsafe(voice_client.channel.send(f"playing: {song_title}"), bot.loop)

def getInfo(url):
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return { "url": info["url"], "title": info.get("title", "unknown title") }
        except Exception as e:
            print(f"Error fetching song info: {e}")
            return None

def playVideo(voice_client, url):
    source = discord.FFmpegPCMAudio(url)
    voice_client.play(source, after=lambda e: checkNext(voice_client))

def searchYoutube(query):
    ydl_opts = {
        "default_search": "ytsearch",
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if "entries" in info and len(info["entries"]) > 0:
            top = info["entries"][0]
            return { "url": top["url"], "title": top.get("title", "unknown title") }
    
    return None


load_dotenv()
bot.run(os.getenv("TOKEN"))