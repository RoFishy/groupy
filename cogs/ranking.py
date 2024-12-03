import discord
from discord.ext import commands
from discord import app_commands
from dotenv import dotenv_values
from discord.utils import get
from utils import config_data
from utils import api_data
import rblxopencloud

class ranking(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} loaded successfully!")

async def setup(client):
    await client.add_cog(ranking(client))