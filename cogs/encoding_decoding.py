import base64
import binascii
import collections
import string
import urllib.parse
import discord
from discord.ext import commands

#TODO: l14ck3r0x01: ROT47 , base32 encoding

class EncodingDecoding(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def b64(self, ctx, encode_or_decode, string):
        byted_str = str.encode(string)
        
        if encode_or_decode == 'decode':
            decoded = base64.b64decode(byted_str).decode('utf-8')
            await ctx.send(decoded)
        
        if encode_or_decode == 'encode':
            encoded = base64.b64encode(byted_str).decode('utf-8').replace('\n', '')
            await ctx.send(encoded)

    @commands.command()
    async def binary(self, ctx, encode_or_decode, string):
        if encode_or_decode == 'decode':
            string = string.replace(" ", "")
            data = int(string, 2)
            decoded = data.to_bytes((data.bit_length() + 7) // 8, 'big').decode()
            await ctx.send(decoded)
        
        if encode_or_decode == 'encode':
            encoded = bin(int.from_bytes(string.encode(), 'big')).replace('b', '')
            await ctx.send(encoded)

    @commands.command()
    async def hex(self, ctx, encode_or_decode, string):
        if encode_or_decode == 'decode':
            string = string.replace(" ", "")
            decoded = binascii.unhexlify(string).decode('ascii')
            await ctx.send(decoded)
        
        if encode_or_decode == 'encode':
            byted = string.encode()
            encoded = binascii.hexlify(byted).decode('ascii')
            await ctx.send(encoded)

    @commands.command()
    async def url(self, ctx, encode_or_decode, message):
        if encode_or_decode == 'decode':
            
            if '%20' in message:
                message = message.replace('%20', '(space)')
                await ctx.send(urllib.parse.unquote(message))
            else:
                await ctx.send(urllib.parse.unquote(message))
        
        if encode_or_decode == 'encode':
            await ctx.send(urllib.parse.quote(message))

def setup(bot):
    bot.add_cog(EncodingDecoding(bot))