import discord
import youtube_dl
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Create a Discord client instance
client = discord.Client()

# Spotify client credentials
spotify_client_id = 'YOUR_SPOTIFY_CLIENT_ID'
spotify_client_secret = 'YOUR_SPOTIFY_CLIENT_SECRET'

# Set up Spotify authentication
spotify_auth_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
spotify = spotipy.Spotify(auth_manager=spotify_auth_manager)

# Store the songs in a queue
song_queue = []

# Function to play YouTube audio
def play_youtube_audio(voice_channel, url):
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
        url2 = info['formats'][0]['url']
        voice_channel.play(discord.FFmpegPCMAudio(url2), after=lambda e: play_next_song(voice_channel))

# Function to play the next song in the queue
def play_next_song(voice_channel):
    if len(song_queue) > 0:
        url = song_queue.pop(0)
        play_youtube_audio(voice_channel, url)

# Function to search for a Spotify song
def search_spotify_song(query):
    results = spotify.search(q=query, type='track', limit=1)
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        return track['external_urls']['spotify']
    return None

# Function to search for a Spotify playlist
def search_spotify_playlist(query):
    results = spotify.search(q=query, type='playlist', limit=1)
    if results['playlists']['items']:
        playlist = results['playlists']['items'][0]
        return playlist['external_urls']['spotify']
    return None

# Event triggered when the bot is ready
@client.event
async def on_ready():
    print('Bot is ready.')

# Event triggered when a message is received
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!playyoutube'):
        voice_channel = message.author.voice.channel
        url = message.content.split(' ')[1]
        song_queue.append(url)
        if len(song_queue) == 1:
            play_youtube_audio(voice_channel, url)

    if message.content.startswith('!playspotifysong'):
        query = message.content.split(' ', 1)[1]
        song_url = search_spotify_song(query)
        if song_url:
            voice_channel = message.author.voice.channel
            song_queue.append(song_url)
            if len(song_queue) == 1:
                play_youtube_audio(voice_channel, song_url)
        else:
            await message.channel.send('No Spotify song found.')

    if message.content.startswith('!playspotifyplaylist'):
        query = message.content.split(' ', 1)[1]
        playlist_url = search_spotify_playlist(query)
        if playlist_url:
            # You can implement logic to extract the individual songs from the playlist and add them to the queue
            await message.channel.send('Playlist playback not implemented.')
        else:
            await message.channel.send('No Spotify playlist found.')

# Replace 'YOUR_DISCORD_BOT_TOKEN' with your actual Discord bot token
client.run('YOUR_DISCORD_BOT_TOKEN')
