import asyncio
import urllib
import requests
import re
import random
import json
import base64
import binascii
import collections
import string
import sys
import os
import urllib.parse
from urllib.request import urlopen
import io
from dateutil.parser import parse
import time
import datetime
from datetime import timezone
from datetime import datetime

import discord 
from discord.ext.commands import Bot
from discord.ext import commands
from colorthief import ColorThief

from help_info import *
from auth_token import *

client = discord.Client()
bot = commands.Bot(command_prefix='>')
extensions = [
   
   'encoding_decoding',
   'cipher',
   'ctfs',
   'utility',

]

bot.remove_command('help')
blacklisted = []
cool_names = ['nullpxl', 'Test_Monkey'] 
# This is intended to be able to be circumvented
# If you do something like report a bug with the report command, e.g, >report "a bug", you might be added to the list!

@bot.event
async def on_ready():
   print('<' + bot.user.name + ' Online>')
   print(discord.__version__)
   await bot.change_presence(game = discord.Game(name='>help | in development'))

@bot.event
async def on_message(message):
   if 'who should I subscribe to?' in message.content:
      choice = random.randint(1, 2)
      
      if (choice == 1):
         await bot.send_message(message.channel, 'https://youtube.com/nullpxl')
      
      if (choice == 2):
         await bot.send_message(message.channel, 'https://www.youtube.com/user/RootOfTheNull')

   await bot.process_commands(message)


# Shows code source
# Usage: source
@bot.command(pass_context=True)
async def source(ctx):
   await bot.say(src)

# Displays help message(s) 
# Usage: help <page number>
@bot.command(pass_context=True)
async def help(ctx, page=None):
   if not page or page == '1':
      page_num = '1'         
      emb = (discord.Embed(description=help_page, colour=0x42f480))
      emb.set_author(name='>request "x" - request a feature')
   
   if page == '2':
      emb = (discord.Embed(description=help_page_2, colour=0x42f480))
      emb.set_author(name='>request "x" - request a feature')
   
   await bot.send_message(ctx.message.channel, embed = emb)

# Allows anyone to request a feature, bot dm's me with your name and the request
# Usage: request "add this cool feature"
@bot.command(pass_context = True)
async def request(ctx, feature):
   creator = await bot.get_user_info('230827776637272064')
   authors_name = str(ctx.message.author)
   await bot.send_message(creator, f":pencil: {authors_name}: {feature}")
   await bot.say(f":pencil: Thanks, \"{feature}\" has been requested!")

# Allows anyone to report an error
# Usage: report "the error"
@bot.command(pass_context = True)
async def report(ctx, error_report):
   creator = await bot.get_user_info('230827776637272064')
   authors_name = str(ctx.message.author)
   await bot.send_message(creator, f":triangular_flag_on_post: {authors_name}: {error_report}")
   await bot.say(f":triangular_flag_on_post: Thanks for the help, \"{error_report}\" has been reported!")

# Shows creator info
# Usage: $creator
@bot.command(pass_context = True)
async def creator(ctx):
   await bot.say(creator_info)

# Tells the truth
# Usage: amicool
@bot.command(pass_context = True)
async def amicool(ctx):
   authors_name = str(ctx.message.author)
   
   if any(name in authors_name for name in cool_names):
      await bot.say("You are very cool")
   
   else:
      await bot.say("lolno")


if __name__ == '__main__':
   sys.path.insert(1, os.getcwd() + "/cogs/")

   for extension in extensions:
      bot.load_extension(extension)

   bot.run(auth_token)
