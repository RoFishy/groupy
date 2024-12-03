import discord
from discord.ext import commands
from discord import app_commands
from dotenv import dotenv_values

config = dotenv_values(".env")
devs = config["DEVS"]

def dev_check(interaction : discord.Interaction):
    return interaction.user.id in devs

class maincmds(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} loaded successfully!")

    @app_commands.command(name="sync", description="Developer command.")
    @app_commands.check(dev_check)
    async def sync(self, interaction : discord.Interaction):
        await interaction.response.defer()
        fmt = await self.client.tree.sync()
        await interaction.followup.send(f"Synced {len(fmt)} commands.")