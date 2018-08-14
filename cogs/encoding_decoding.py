import base64
import binascii
import collections
import string
import urllib.parse

import discord
from discord.ext import commands

class EncodingDecoding:
   def __init__(self, bot):
      self.bot = bot

   # Encode or decode base64
   # Usage: b64 encode/decode <message> - if message has spaces use quotations
   @commands.command(pass_context = True)
   async def b64(self, ctx, encode_or_decode, string):
      byted_str = str.encode(string)

      if encode_or_decode == 'decode':
         decoded = base64.b64decode(byted_str).decode('utf-8')
         await self.bot.say(decoded)

      if encode_or_decode == 'encode':
         encoded = base64.b64encode(byted_str).decode('utf-8').replace('\n', '')
         await self.bot.say(encoded)

   # Encode or decode binary
   # Usage: binary encode/decode <message> - if message has spaces use quotations
   @commands.command(pass_context = True)
   async def binary(self, ctx, encode_or_decode, string):
      if encode_or_decode == 'decode':
         data = int(string, 2)
         decoded = data.to_bytes((data.bit_length() + 7) // 8, 'big').decode()
         await self.bot.say(decoded)

      if encode_or_decode == 'encode':
         encoded = bin(int.from_bytes(string.encode(), 'big')).replace('b', '')
         await self.bot.say(encoded)

   # Encode or decode hex
   # Usage: hex encode/decode <message> - if message has spaces use quotations
   @commands.command(pass_context = True)
   async def hex(self, ctx, encode_or_decode, string):
      if encode_or_decode == 'decode':
         decoded = binascii.unhexlify(string).decode('ascii')
         await self.bot.say(decoded)
       
      if encode_or_decode == 'encode':
         byted = string.encode()
         encoded = binascii.hexlify(byted).decode('ascii')
         await self.bot.say(encoded)

   # Encode or decode in url
   # Usage: url encode/decode <message> - if message has spaces use quotations
   @commands.command(pass_context=True)
   async def url(self, ctx, encode_or_decode, message):
      if encode_or_decode == 'decode':
         
         if "%20" in message:
            message = message.replace('%20', '(space)')
            await self.bot.say(urllib.parse.unquote(message))
         
         else:
            await self.bot.say(urllib.parse.unquote(message))
       
      if encode_or_decode == 'encode':
         await self.bot.say(urllib.parse.quote(message))      


def setup(bot):
   bot.add_cog(EncodingDecoding(bot))