import discord
from discord.ext import tasks, commands
import sys
sys.path.append("..")
from config_vars import *

class Configuration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def config(self, ctx):
        if ctx.invoked_subcommand is None:
            # If the subcommand passed does not exist, its type is None
            config_commands = list(set([c.qualified_name for c in Configuration.walk_commands(self)][1:]))
            await ctx.send(f"Current config commands are: {', '.join(config_commands)}")
        
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    @config.command()
    async def ctf_category(self, ctx, category_name):
        category = discord.utils.get(ctx.guild.categories, name=category_name)
        
        if category == None: # Checks if category exists, if it doesn't it will create it.
            await ctx.guild.create_category(name=category_name)
            category = discord.utils.get(ctx.guild.categories, name=category_name)
        
        sconf = serverdb[str(ctx.guild.id) + '-CONF'] # sconf means server configuration
        info = {"ctf_category": category_name}
        sconf.update({"name": 'category_name'}, {"$set": info}, upsert=True)
        categoryset = sconf.find_one({'name': "category_name"})['ctf_category']
        await ctx.send(f"CTF category set as `{categoryset}`")
    
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    @config.command()
    async def archive_category(self, ctx, category_name):
        category = discord.utils.get(ctx.guild.categories, name=category_name)
        
        if category == None: # Checks if category exists, if it doesn't it will create it.
            await ctx.guild.create_category(name=category_name)
            category = discord.utils.get(ctx.guild.categories, name=category_name)
        
        sconf = serverdb[str(ctx.guild.id) + '-CONF'] # sconf means server configuration
        info = {"archive_category": category_name}
        sconf.update({"name": 'archive_category_name'}, {"$set": info}, upsert=True)
        categoryset = sconf.find_one({'name': "archive_category_name"})['archive_category']
        await ctx.send(f"Archive category set as `{categoryset}`")


def setup(bot):
    bot.add_cog(Configuration(bot))