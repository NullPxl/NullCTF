import collections
import string

import discord
from discord.ext import commands

class Ciphers:
   def __init__(self, bot):
      self.bot = bot

   # Returns all 25 possible caeser cipher (rot) combinations
   # Usage: rot string
   @commands.command(pass_context = True)
   async def rot(self, ctx, message, direction=None):
      allrot = ""
      
      for i in range(0, 26):
         upper = collections.deque(string.ascii_uppercase)
         lower = collections.deque(string.ascii_lowercase)
         
         if direction == None or direction == 'left':
            upper.rotate(-i)
            lower.rotate(-i)
         
         if direction == 'right':
            upper.rotate(i)
            lower.rotate(i)

         upper = ''.join(list(upper))
         lower = ''.join(list(lower))
         translated = message.translate(str.maketrans(string.ascii_uppercase, upper)).translate(str.maketrans(string.ascii_lowercase, lower))
         allrot += "{}: {}\n".format(i, translated)

      try:
         await self.bot.say("rotated " + message + " to the " + direction + "\n" + allrot)
      
      except:
         await self.bot.say("rotated " + message + " to the left\n" + allrot)

   # Returns your message with the atbash cipher (encode/decode would return the same thing so I'm not including the argument)
   # Usage: atbash decode/encode
   @commands.command(pass_context = True)
   async def atbash(self, ctx, message):
      normal   = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
      changed  = "zyxwvutsrqponmlkjihgfedcbaZYXWVUTSRQPONMLKJIHGFEDCBA"
      trans    = str.maketrans(normal, changed)
      atbashed = message.translate(trans)
      await self.bot.say(atbashed)


def setup(bot):
   bot.add_cog(Ciphers(bot))