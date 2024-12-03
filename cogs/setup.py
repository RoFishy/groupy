import discord
from discord.ext import commands
from discord import app_commands
from dotenv import dotenv_values
from discord.utils import get
from ..utils import config_data
from ..utils import api_data

config = dotenv_values(".env")

class submit_key(discord.ui.Modal, title="Setup Ranking"):
    global key
    key = discord.ui.TextInput(
        label="API Key",
        placeholder="Your API key here...",
        required=True
    )

    async def on_submit(self, interaction : discord.Interaction):
        await interaction.response.defer()
        api_data.create_info(interaction.guild.id, key)
        await interaction.followup.send("Ranking module has been setup.", ephemeral=True)
    
    async def on_error(self, interaction : discord.Interaction, error: Exception):
        await interaction.response.send_message("Oops! Something went wrong.", ephemeral=True)

class setup(commands.Cog):
    def __init__(self, client):
        self.client = client

    setup = app_commands.Group(
        name="setup",
        description="The basic bot setup commands."
    )

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} loaded successfully!")

    @setup.command(name="ranking", description="Setup the ranking module.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_ranking(self, interaction : discord.Interaction):
        await interaction.response.send_modal(submit_key())

    @setup.command(name="logging", description="Setup the logging configurations.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_logging(self, interaction : discord.Interaction, logging_channel_id : int):
        await interaction.response.defer()
        current_data = config_data.fetch_configs(interaction.guild.id)
        data = {
            "logging_channel_id": logging_channel_id,
            "required_roles": current_data["required_roles"]
        }
        config_data.create_configs(interaction.guild.id, data)
        await interaction.followup.send("Logging channel successfully set.")

    @app_commands.command(name="add-mod", description="Adds a role to the list of allowed roles for commands.")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_role(self, interaction : discord.Interaction, role_id : int):
        await interaction.response.defer()
        current_data = config_data.fetch_configs(interaction.guild.id)
        required_roles = current_data["required_roles"]
        global role
        try:
            role = get(interaction.guild.roles, id=role_id)
        except Exception as e:
            await interaction.followup.send("Error executing command.")
        if role.name in required_roles:
            await interaction.followup.send("Role has already been added.")
        else:
            required_roles[role.name] = role_id
            newData = {
                "logging_channel_id": current_data["logging_channel_id"],
                "required_roles": required_roles
            }
            config_data.update_configs(interaction.guild.id, newData)
            await interaction.followup.send("Added role successfully.")

    @app_commands.command(name="remove-mod", description="Removes a role from the list of allowed roles for commands.")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_role(self, interaction : discord.Interaction, role_id : int):
        await interaction.response.defer()
        current_data = config_data.fetch_configs(interaction.guild.id)
        required_roles = current_data["required_roles"]
        global role
        try:
            role = get(interaction.guild.roles, id=role_id)
        except Exception as e:
            await interaction.followup.send("Error executing command.")
        if role.name in required_roles:
            del required_roles[role.name]
            newData = {
                "logging_channel_id": current_data["logging_channel_id"],
                "required_roles": required_roles
            }
            config_data.update_configs(interaction.guild.id, newData)
        else:
            await interaction.response.send_message("Role is not currently added.")

async def setup(client):
    await client.add_cog(setup(client))