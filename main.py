# WaLLE
import requests
import json
import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
import os
from cogs.Music import Music


load_dotenv()
# Get the API token from the .env file.
DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='n!', intents=intents)

bot.remove_command('help')


@bot.command(name='help', description="sends a help message")
async def help_(ctx):
    """Help message"""

    embed = discord.Embed(
        title="Help", description="List of available commands:", color=discord.Color.green())

    embed.add_field(
        name="join", value="Connects to a voice channel (if no channel is passed, it will connect to the voice channel you are connected to)\n`Example: n!join`", inline=False)
    embed.add_field(
        name="play", value="Queue the provided song (only works with urls for now)\n`Example: n!play https://www.youtube.com/watch?v=dQw4w9WgXcQ`", inline=False)
    embed.add_field(name="pause", value="Pauses music\n`Example: n!pause`", inline=False)
    embed.add_field(name="resume", value="Resumes music\n`Example: n!resume`", inline=False)
    embed.add_field(
        name="skip", value="Skips to the next song in queue\n`Example: n!skip`", inline=False)
    embed.add_field(
        name="remove", value="Removes a specified song from the queue\n`Example: n!remove 1`", inline=False)
    embed.add_field(
        name="clear", value="Clears the entire queue\n`Example: n!clear`", inline=False)
    embed.add_field(
        name="queue", value="Shows the queue of upcoming songs\n`Example: n!queue`", inline=False)
    embed.add_field(
        name="np", value="Shows song currently playing\n`Example: n!np`", inline=False)

    await ctx.send(embed=embed)


@bot.event
async def on_ready():
    await bot.load_extension("cogs.Music")

    for guild in bot.guilds:
        print('Active in {}\n Member Count : {}'.format(
            guild.name, guild.member_count))


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
