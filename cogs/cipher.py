import collections
import string
import discord
from discord.ext import commands

class Ciphers(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def rot(self, ctx, message, direction=None):
        allrot = ''
        
        for i in range(0, 26):
            upper = collections.deque(string.ascii_uppercase)
            lower = collections.deque(string.ascii_lowercase)
            
            upper.rotate((- i))
            lower.rotate((- i))
            
            upper = ''.join(list(upper))
            lower = ''.join(list(lower))
            translated = message.translate(str.maketrans(string.ascii_uppercase, upper)).translate(str.maketrans(string.ascii_lowercase, lower))
            allrot += '{}: {}\n'.format(i, translated)
        
        await ctx.send(f"```{allrot}```")

    @commands.command()
    async def atbash(self, ctx, message):
        normal = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        changed = 'zyxwvutsrqponmlkjihgfedcbaZYXWVUTSRQPONMLKJIHGFEDCBA'
        trans = str.maketrans(normal, changed)
        atbashed = message.translate(trans)
        await ctx.send(atbashed)

def setup(bot):
    bot.add_cog(Ciphers(bot))