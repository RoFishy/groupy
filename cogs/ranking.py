import discord
from discord.ext import commands
from discord import app_commands
from dotenv import dotenv_values
from discord.utils import get
from utils import config_data
from utils import api_data
from utils import group_data
import requests
import rblxopencloud

def getUserId(username : str) -> int:
    API_ENDPOINT = "https://users.roblox.com/v1/usernames/users"
    request_payload = {
        "usernames": [
            username
        ],

        "excludeBannedUsers": True
    }

    responseData = requests.post(API_ENDPOINT, json=request_payload)
    assert responseData.status_code == 200
    userId = responseData.json()["data"][0]["id"]
    return userId

def get_next_role_id(guild_id, current_role : int) -> int:
    group_id = group_data.fetch_id(guild_id)
    api_key = api_data.get_api_key(guild_id)
    group = rblxopencloud.Group(group_id, api_key)
    roles = []
    for role in group.list_roles():
        if role.rank > current_role:
            roles.append(role.rank)

    min_greater_than_target = min(roles) or None
    
    for role in group.list_roles():
        if role.rank == min_greater_than_target:
            role_id = role.id
    return role_id

class ranking(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} loaded successfully!")

    @app_commands.command(name="promote", description="Promotes the given user to the next rank")
    async def promote(self, interaction : discord.Interaction, username : str):
        await interaction.response.defer()
        if api_data.guild_already_setup(interaction.guild.id):
            if group_data.guild_already_setup(interaction.guild.id) == True:
                if config_data.guild_already_setup(interaction.guild.id) == True:
                    configs = config_data.fetch_configs(interaction.guild.id)
                    required_roles = configs["required_roles"]
                    if required_roles == {}:
                        await interaction.response.send_message("No ranking roles setup!")
                    else:
                        has_permission = False
                        for role in interaction.user.roles:
                            if role.name in required_roles:
                                has_permission = True
                        if has_permission == True:
                            group_id = group_data.fetch_id(interaction.guild.id)
                            api_key = api_data.get_api_key(interaction.guild.id)
                            user_id = getUserId(username)
                            group = rblxopencloud.Group(group_id, api_key)
                            try: 
                                member = group.fetch_member(user_id)
                            except Exception as e:
                                print(e)
                            next_rank = get_next_role_id(interaction.guild.id, member.fetch_role().rank)
                            if next_rank == None:
                                await interaction.followup.send("Unable to promote the user.")
                            try:
                                group.update_member(user_id, next_rank)
                                new_role = group.fetch_role(role_id=next_rank)
                                await interaction.followup.send(f"Successfully ranked **{username}** to **{new_role.name}**")
                            except Exception as e:
                                await interaction.followup.send("Something went wrong.")
                                print(e)
                        else:
                            await interaction.followup.send("You do not have permission to run this command!")
                else:
                    await interaction.followup.send("Please setup the configuration using the `/setup` commands, along with adding ranking roles using `/add-mod`.")
            else:
                await interaction.followup.send("Please setup the group ID using the `/setup group` command.")
        else:
            await interaction.followup.send("Please setup the API key using the `/setup ranking` command. Use the `/help ranking` command if you need assistance.")

async def setup(client):
    await client.add_cog(ranking(client))