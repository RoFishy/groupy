import discord
from discord.ext import commands
from discord import app_commands

class help(commands.Cog):
    def __init__(self, client):
        self.client = client

    help = app_commands.Group(
        name="help",
        description="The basic bot setup commands."
    )

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} loaded successfully!")

    @help.command(name="ranking", description="Get help setting up the ranking module!")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_ranking(self, interaction : discord.Interaction):
        embed = discord.Embed(title="Command Help", description="To setup the ranking module and start using ranking commands, you can use the `/setup ranking command` and input your Group API key. You can get your API key here: https://create.roblox.com/.\n\n**Instructions:**\n1. In the top left corner, switch to the group you want to create the API key for.\n2. In the bottom left, open the 'Open Cloud' menu and click on 'API Keys'.\n3. Click the 'Create API Key' Button.\n4. Fill out the General Information setting.\n5. Under the `Access Permissions` setting, set the API System to `groups`.\n6. (optional) Under the security section, if you don't want to set a specific IP address, you can just enter `0.0.0.0/0` in the IP address bar.\n\nAfter setting your API key up, run the `/add-mod` command to give certain roles ranking/group moderation permissions.")
        embed.set_footer(text="This bot was created by RoFishy")
        await interaction.response.send_message(embed=embed)

async def setup(client):
    await client.add_cog(help(client))