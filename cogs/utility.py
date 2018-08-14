import base64
import binascii
import collections
import string
import urllib.parse
import json
import random

import discord
from discord.ext import commands

class Utility:
   def __init__(self, bot):
      self.bot = bot

   # Clear the amount of messages you supply
   # Usage: clear amount
   @commands.command(pass_context = True, aliases = ['purge'])
   async def clear(self, ctx, amount):
      amount = int(amount)
      await self.bot.delete_message(ctx.message)
      
      try:
         for amount in range(amount, 0, -100):
            await self.bot.purge_from(ctx.message.channel, limit=amount)
      
      except discord.errors.HTTPException:
         await self.bot.say("Can't delete messages more than 14 days old!  Try a lower number.")

   # Evaluate a math expression
   # Usage: calc expression
   @commands.command(pass_context = True)
   async def calc(self, ctx, expression):
      value = eval(expression)
      await self.bot.say(value)

   # Count the characters in the string you supply
   # Usage: characters [string]
   @commands.command(pass_context=True, aliases = ['char', 'c'])
   async def characters(self, ctx, string):
      await self.bot.say(len(string))

   # Count the words in the phrase you supply
   # Usage: worcount [this is a phrase]
   @commands.command(pass_context=True, aliases = ['wc', 'w'])
   async def wordcount(self, ctx, *args):
      await self.bot.say(len(args))

   # Reverse the supplied string - if message has spaces use quotations
   # Usage: reverse [message]
   @commands.command(pass_context = True, aliases = ['rev'])
   async def reverse(self, ctx, message):
      await self.bot.say(message[::-1])

   # Count the occurences of characters in a supplied message - if message has spaces use quotations
   # Usage: counteach [message]
   @commands.command(pass_context = True)
   async def counteach(self, ctx, message):
      count = {}

      for char in message:
         if char in count.keys():
            count[char] += 1
         
         else:
            count[char] = 1
      
      await self.bot.say(str(count))

   # Returns the magicbytes/file header of a supplied filetype
   # Json data edited (with permission) from https://gist.githubusercontent.com/qti3e/6341245314bf3513abb080677cd1c93b/raw/3ef94c55bc55ea82a3deb55373ddb7dcd2ed9deb/extensions.json
   # Usage: magicb file-extension
   @commands.command(pass_context = True, aliases = ['head'])
   async def magicb(self, ctx, filetype):
      file = open("magic.json").read()
      alldata = json.loads(file)
      messy_signs = str(alldata[filetype]['signs'])
      signs = messy_signs.split("[")[1].split(",")[0].split("]")[0].replace("'", "")
      filetype = alldata[filetype]['mime']
      await self.bot.say(f"{filetype}: {signs}")

   # Show a direct link to a twitter user you supply
   # Usage: twitter user
   @commands.command(pass_context = True)
   async def twitter(self, ctx, twituser):
      await self.bot.say('https://twitter.com/' + (twituser))

   # Show a direct link to a github user you supply
   # Usage: $github user
   @commands.command(pass_context = True)
   async def github(self, ctx, gituser):
      await self.bot.say('https://github.com/' + (gituser))

   # Get a 5050 choice of heads or tails
   # Usage: cointoss
   @commands.command(pass_context=True, aliases = ['5050', 'flip'])
   async def cointoss(self, ctx):
      choice = random.randint(1, 2)
      if (choice == 1):
         await self.bot.say('heads')
      if (choice == 2):
         await self.bot.say('tails')

   # Randomly says one of the arguments you pass through this command
   # Could be used for questions you want to hear at random to study
   # Usage: randread "questions 1" "question 2" "question 3"
   @commands.command(pass_context = True)
   async def randread(self, ctx, *args):
      choice = random.choice(args)
      await self.bot.send_message(ctx.message.channel, (choice), tts = True)

def setup(bot):
   bot.add_cog(Utility(bot))