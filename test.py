import discord
from discord.ext import commands
import youtube_dl
import asyncio
from functools import partial
import re
import requests
import os
from dotenv import load_dotenv

load_dotenv()

bot = commands.Bot(command_prefix='n!', intents=discord.Intents.all())

# Global variables
queue = []
is_playing = False


def check_queue(ctx):
    if len(queue) > 0:
        is_playing = True
        song = queue[0]
        song_url = song['url']
        voice_client = ctx.voice_client
        player = discord.FFmpegPCMAudio(
            song_url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")
        player = discord.PCMVolumeTransformer(
            player, volume=0.5)  # Adjust volume here
        voice_client.play(player, after=partial(play_next, ctx))


def play_next(ctx, error=None):
    if error:
        print(f'Error: {error}')

    if len(queue) > 0:
        del queue[0]

    if len(queue) == 0:
        is_playing = False
        return

    voice_client = ctx.voice_client
    song = queue[0]
    song_url = song['url']
    player = discord.FFmpegPCMAudio(
        song_url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")
    player = discord.PCMVolumeTransformer(
        player, volume=0.5)  # Adjust volume here
    voice_client.play(player, after=partial(play_next, ctx))


def get_youtube_playlist_videos(playlist_id):
    API_KEY = os.getenv('YOUTUBE_API_KEY')
    url = f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId={playlist_id}&key={API_KEY}'
    response = requests.get(url)
    json_data = response.json()
    videos = []
    for item in json_data['items']:
        video_id = item['snippet']['resourceId']['videoId']
        video_title = item['snippet']['title']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        videos.append({'title': video_title, 'url': video_url})
    return videos


@bot.event
async def on_ready():
    print(f'Bot is ready! Logged in as {bot.user}')


@bot.command()
async def play(ctx, url: str):
    voice_channel = ctx.author.voice.channel
    voice_client = ctx.voice_client

    if voice_client is None:
        voice_client = await voice_channel.connect()
    else:
        if voice_client.channel != voice_channel:
            await voice_client.move_to(voice_channel)

    if 'youtube.com/playlist' in url:
        playlist_id = re.findall(r'list=([a-zA-Z0-9_-]+)', url)[0]
        videos = get_youtube_playlist_videos(playlist_id)
        for video in videos:
            queue.append(video)

        if not voice_client.is_playing():
            await play_song(ctx)

        await ctx.send(f'Added playlist to queue: {len(videos)} songs')
    else:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            song_url = info['formats'][0]['url']
            song_title = info['title']

        song = {'title': song_title, 'url': song_url}
        queue.append(song)

        if not voice_client.is_playing():
            await play_song(ctx)

        await ctx.send(f'Added to queue: {song_title}')


async def play_song(ctx):
    voice_client = ctx.voice_client
    if len(queue) > 0:
        is_playing = True
        song = queue[0]
        song_url = song['url']
        player = discord.FFmpegPCMAudio(
            song_url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")
        player = discord.PCMVolumeTransformer(
            player, volume=0.5)  # Adjust volume here
        voice_client.play(player, after=lambda error: asyncio.run_coroutine_threadsafe(
            play_next(ctx, error), bot.loop))
        await ctx.send(f'Now playing: {song["title"]}')
    else:
        is_playing = False


async def play_next(ctx, error):
    voice_client = ctx.voice_client
    if error:
        print(f'Player error: {error}')

    if len(queue) > 0:
        queue.pop(0)

    if len(queue) > 0:
        await asyncio.sleep(1)  # Add a delay before playing the next song
        await play_song(ctx)
    else:
        await asyncio.sleep(1)  # Add a delay before disconnecting
        if not voice_client.is_playing():
            await voice_client.disconnect()


@bot.command()
async def stop(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client.is_playing():
        voice_client.stop()
        queue.clear()
        is_playing = False

bot.run(os.getenv('DISCORD_BOT_TOKEN'))
