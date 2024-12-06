import discord
from discord.ext import commands
from discord import app_commands
from dotenv import dotenv_values
from discord.utils import get
from utils import config_data
from utils import api_data
from utils import group_data

config = dotenv_values(".env")

class submit_key(discord.ui.Modal, title="Setup Ranking"):
    key = discord.ui.TextInput(
        label="API Key",
        placeholder="Your API key here...",
        required=True
    )

    async def on_submit(self, interaction : discord.Interaction):
        if api_data.guild_already_setup(interaction.guild.id) == True:
            api_data.update_info(interaction.guild.id,self.key.value)
        else:
            api_data.create_info(interaction.guild.id, self.key.value)
        await interaction.response.send_message("Ranking module has been setup.")
    
    async def on_error(self, interaction : discord.Interaction, error: Exception):
        await interaction.followup.send("Oops! Something went wrong.", ephemeral=True)

class setup_class(commands.Cog):
    def __init__(self, client):
        self.client = client

    setup_grp = app_commands.Group(
        name="setup",
        description="The basic bot setup commands."
    )

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} loaded successfully!")

    @setup_grp.command(name="ranking", description="Setup the ranking module.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_ranking(self, interaction : discord.Interaction):
        await interaction.response.send_modal(submit_key())

    @setup_grp.command(name="group", description="Setup the ROBLOX group module.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_group(self, interaction : discord.Interaction, group_id : str):
        groupId = int(group_id)
        await interaction.response.defer()
        if group_data.guild_already_setup(interaction.guild.id) == True:
            group_data.update_configs(interaction.guild.id, groupId)
        else:
            group_data.create_configs(interaction.guild.id, groupId)
        await interaction.followup.send("Group id successfully setup.")

    @setup_grp.command(name="logging", description="Setup the logging configurations.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_logging(self, interaction : discord.Interaction, logging_channel_id : str):
        logging_channel_id = int(logging_channel_id)
        await interaction.response.defer()
        if config_data.guild_already_setup(interaction.guild.id) == True:
            current_data = config_data.fetch_configs(interaction.guild.id)
            data = {
                "$set": {
                    "logging_channel_id": logging_channel_id,
                    "required_roles": current_data["required_roles"]
                }

            }
            config_data.update_configs(interaction.guild.id, data)
            await interaction.followup.send("Logging channel successfully set.")
        else:
            data = {
                "logging_channel_id": logging_channel_id,
                "required_roles": {}
            }
            config_data.create_configs(interaction.guild.id, data)
            await interaction.followup.send("Logging channel successfully set.")

    @app_commands.command(name="add-mod", description="Adds a role to the list of allowed roles for commands.")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_role(self, interaction : discord.Interaction, role : discord.Role):
        role_id = role.id
        await interaction.response.defer()
        if config_data.guild_already_setup(interaction.guild.id) == True:
            current_data = config_data.fetch_configs(interaction.guild.id)
            required_roles = current_data["required_roles"]
            if role.name in required_roles:
                await interaction.followup.send("Role has already been added.")
            else:
                required_roles[role.name] = role_id
                newData = {
                    "$set": {
                        "logging_channel_id": current_data["logging_channel_id"],
                        "required_roles": required_roles
                    }

                }
                config_data.update_configs(interaction.guild.id, newData)
                await interaction.followup.send("Added role successfully.")
        else:
            data = {
                "logging_channel_id": 0,
                "required_roles": {role.name : role.id}
            }
            config_data.create_configs(interaction.guild.id, data)
            await interaction.followup.send("Added role successfully.")

    @app_commands.command(name="remove-mod", description="Removes a role from the list of allowed roles for commands.")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_role(self, interaction : discord.Interaction, role : discord.Role):
        await interaction.response.defer()
        if config_data.guild_already_setup(interaction.guild.id) == True:
            current_data = config_data.fetch_configs(interaction.guild.id)
            required_roles = current_data["required_roles"]
            if role.name in required_roles:
                del required_roles[role.name]
                newData = {
                    "$set": {
                        "logging_channel_id": current_data["logging_channel_id"],
                        "required_roles": required_roles
                    }

                }
                config_data.update_configs(interaction.guild.id, newData)
            else:
                await interaction.followup.send("Role is not currently added.")
        else:
            await interaction.followup.send("No roles are currently setup as moderators")

async def setup(client):
    await client.add_cog(setup_class(client))