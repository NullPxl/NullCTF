import collections
import string
import discord
from discord.ext import commands

class Ciphers():

    def __init__(self, bot):
        self.bot = bot

    @commands.command()  # Returns all 25 possible caeser cipher (rot) combinations
    async def rot(self, ctx, message, direction=None):  # Usage: rot string direction
        allrot = ''
        for i in range(0, 26):
            upper = collections.deque(string.ascii_uppercase)
            lower = collections.deque(string.ascii_lowercase)
            if (direction == None) or (direction == 'left'):
                upper.rotate((- i))
                lower.rotate((- i))
            if direction == 'right':
                upper.rotate(i)
                lower.rotate(i)
            upper = ''.join(list(upper))
            lower = ''.join(list(lower))
            translated = message.translate(str.maketrans(string.ascii_uppercase, upper)).translate(str.maketrans(string.ascii_lowercase, lower))
            allrot += '{}: {}\n'.format(i, translated)
        try:
            await ctx.send((((('rotated ' + message) + ' to the ') + direction) + '\n') + allrot)
        except:
            await ctx.send((('rotated ' + message) + ' to the left\n') + allrot)

    @commands.command()
    async def atbash(self, ctx, message):
        normal = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        changed = 'zyxwvutsrqponmlkjihgfedcbaZYXWVUTSRQPONMLKJIHGFEDCBA'
        trans = str.maketrans(normal, changed)
        atbashed = message.translate(trans)
        await ctx.send(atbashed)

def setup(bot):  # Returns your message with the atbash cipher (encode/decode would return the same thing so I'm not including the argument)
    bot.add_cog(Ciphers(bot))  # Usage: atbash decode/encode