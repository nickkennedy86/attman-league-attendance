from discord.ext import commands
from datetime import datetime
from include.config import *
import discord

class Registration(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.slash_command(name='register')
    async def register(self,ctx):
        server_exists = server_check(ctx.guild.id)
        if server_exists:
            message = f'{ctx.guild.name} already exists in the configuration!'
        else:
            add_server(serverId=ctx.guild.id,serverName=ctx.guild.name,registeredBy=ctx.user.global_name,dateRegistered=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            message = f'{ctx.guild.name} added to the configuration!'
        await ctx.interaction.response.send_message(content=message,ephemeral=True)

    @commands.slash_command(name='deregister')
    async def deregister(self,ctx):
        server_exists = server_check(ctx.guild.id)
        if server_exists:
            message = f'{ctx.guild.name} has been removed from the configuration!'
            remove_server(serverId=ctx.guild.id)
        else:
            message = f'{ctx.guild.name} does not exist in the configuration!'
        await ctx.interaction.response.send_message(content=message,ephemeral=True)

def setup(bot):
    bot.add_cog(Registration(bot))