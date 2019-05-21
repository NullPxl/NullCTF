# from pymongo import MongoClient
# from mongo import *
# import discord
# from discord.ext import commands

# class Settings():
    
#     def __init__(self, bot):
#         self.bot = bot

#     @commands.group()
#     async def configure(self, ctx):
#         global guild
#         global gid
#         guild = ctx.guild
#         gid = ctx.guild.id

#     @commands.has_permissions(manage_channels=True)
#     @configure.command()
#     async def ctfcategory(self, ctx, category_name):
#         category = discord.utils.get(ctx.guild.categories, name=category_name)
        
#         if category == None: # Checks if category exists, if it doesn't it will create it.
#             await guild.create_category(name=category_name)
#             category = discord.utils.get(ctx.guild.categories, name=category_name)
        
#         sconf = serverdb[str(gid) + 'CONF'] # sconf means server configuration
#         info = {"ctfcategory": category_name}
#         sconf.update({"name": 'category_name'}, {"$set": info}, upsert=True)
#         categoryset = sconf.find_one({'name': "category_name"})['ctfcategory']
#         await ctx.send(f"CTF category set as {categoryset}")


# def setup(bot):
#     bot.add_cog(Settings(bot))


