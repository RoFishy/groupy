import discord
import os
from discord.ext import commands
import asyncio
from dotenv import dotenv_values

config = dotenv_values(".env")

TOKEN = config["TOKEN"]
Bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), help_command=None)

@Bot.event
async def on_ready():
    await Bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="RankBot"))
    print("Bot is connected to discord!")

async def load():
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            await Bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with Bot:
        await load()
        await Bot.start(TOKEN)

asyncio.run(main())