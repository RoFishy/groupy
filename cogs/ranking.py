import discord
from discord.ext import commands
from discord import app_commands
from utils.data import config_data
from utils.data import api_data
from utils.data import group_data
from utils import json_handler
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

def log_rank_change(user_id, amount):
    data = {"amount" : amount}
    if json_handler.check_user_in_file("ranking", user_id) == True:
        json_handler.add_data_to_user("ranking", user_id, data)
    else:
        json_handler.add_user_to_json("ranking", user_id)
        json_handler.add_data_to_user("ranking", user_id, data)

def authenticate(guild_id) -> rblxopencloud.Group:
    print('starting auth')
    group_id = group_data.fetch_id(guild_id)
    print('fetched id')
    api_key = api_data.get_api_key(guild_id)
    print('fetched api')
    group = rblxopencloud.Group(group_id, api_key)
    print('done')
    return group

def get_id_from_role(guild_id, role : int) -> int:
    group = authenticate(guild_id)
    for grp_role in group.list_roles():
        if grp_role.rank == role:
            role_id = grp_role.id

    return role_id

def get_next_role_id(guild_id, current_role : int) -> int:
    group = authenticate(guild_id)
    roles = []
    for role in group.list_roles():
        if role.rank > current_role:
            roles.append(role.rank)

    min_greater_than_target = min(roles) or None
    role_id = get_id_from_role(guild_id, min_greater_than_target)
    return role_id

def get_prev_role_id(guild_id, current_role : int) -> int:
    group = authenticate(guild_id)
    roles = []
    for role in group.list_roles():
        if role.rank < current_role:
            roles.append(role.rank)
    max_lower_than_target = max(roles) or None
    role_id = get_id_from_role(guild_id, max_lower_than_target)
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
                            user_id = getUserId(username)
                            try:
                                group = authenticate(interaction.guild.id)
                            except Exception as e:
                                print(e)

                            try: 
                                member = group.fetch_member(user_id)
                            except Exception as e:
                                print(e)
                            next_rank = get_next_role_id(interaction.guild.id, member.fetch_role().rank)
                            if next_rank == None or next_rank == 255:
                                await interaction.followup.send("Unable to promote the user.")
                            try:
                                group.update_member(user_id, next_rank)
                                new_role = group.fetch_role(role_id=next_rank)
                                await interaction.followup.send(f"Successfully promoted **{username}** to **{new_role.name}**")
                                log_rank_change(interaction.user.id, 1)
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

    @app_commands.command(name="demote", description="Demotes the given user to the previous rank.")
    async def demote(self, interaction :discord.Interaction, username : str):
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
                            print("has perms")
                            user_id = getUserId(username)
                            group = authenticate(interaction.guild.id)
                            print("authed")
                            try: 
                                member = group.fetch_member(user_id)
                            except Exception as e:
                                print(e)

                            print("done some stuffs")
                            next_rank = get_prev_role_id(interaction.guild.id, member.fetch_role().rank)
                            print(next_rank)
                            if next_rank == None:
                                await interaction.followup.send("Unable to demote the user.")
                            try:
                                group.update_member(user_id, next_rank)
                                new_role = group.fetch_role(role_id=next_rank)
                                await interaction.followup.send(f"Successfully demoted **{username}** to **{new_role.name}**")
                                log_rank_change(interaction.user.id, 1)
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