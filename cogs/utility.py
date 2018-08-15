import base64
import binascii
import collections
import string
import urllib.parse
import json
import random
import discord
from discord.ext import commands

class Utility():

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['purge'])  # Clear the amount of messages you supply
    async def clear(self, ctx, amount):  # Usage: clear amount
        amount = int(amount)
        await ctx.message.delete()
        try:
            for amount in range(amount, 0, (- 100)):
                await ctx.channel.purge(limit=amount)
        except discord.errors.HTTPException:
            await ctx.send("Can't delete messages more than 14 days old!  Try a lower number.")

    @commands.command()
    async def calc(self, ctx, expression):
        value = eval(expression)
        await ctx.send(value)
  # Evaluate a math expression
    @commands.command(aliases=['char', 'c'])  # Usage: calc expression
    async def characters(self, ctx, string):
        await ctx.send(len(string))

    @commands.command(aliases=['wc', 'w'])
    async def wordcount(self, ctx, *args):
        await ctx.send(len(args))  # Count the characters in the string you supply
  # Usage: characters [string]
    @commands.command(aliases=['rev'])
    async def reverse(self, ctx, message):
        await ctx.send(message[::(- 1)])

    @commands.command()  # Count the words in the phrase you supply
    async def counteach(self, ctx, message):  # Usage: worcount [this is a phrase]
        count = {
            
        }
        for char in message:
            if char in count.keys():  # Reverse the supplied string - if message has spaces use quotations
                count[char] += 1  # Usage: reverse [message]
            else:
                count[char] = 1
        await ctx.send(str(count))

    @commands.command(aliases=['head'])  # Count the occurences of characters in a supplied message - if message has spaces use quotations
    async def magicb(self, ctx, filetype):  # Usage: counteach [message]
        file = open('magic.json').read()
        alldata = json.loads(file)
        messy_signs = str(alldata[filetype]['signs'])
        signs = messy_signs.split('[')[1].split(',')[0].split(']')[0].replace("'", '')
        filetype = alldata[filetype]['mime']
        await ctx.send(f'''{filetype}: {signs}''')

    @commands.command()
    async def twitter(self, ctx, twituser):
        await ctx.send('https://twitter.com/' + twituser)

    @commands.command()
    async def github(self, ctx, gituser):
        await ctx.send('https://github.com/' + gituser)  # Returns the magicbytes/file header of a supplied filetype
  # Json data edited (with permission) from https://gist.githubusercontent.com/qti3e/6341245314bf3513abb080677cd1c93b/raw/3ef94c55bc55ea82a3deb55373ddb7dcd2ed9deb/extensions.json
    @commands.command(aliases=['5050', 'flip'])  # Usage: magicb file-extension
    async def cointoss(self, ctx):
        choice = random.randint(1, 2)
        if choice == 1:
            await ctx.send('heads')
        if choice == 2:
            await ctx.send('tails')

    @commands.command()
    async def randread(self, ctx, *args):
        choice = random.choice(args)  # Show a direct link to a twitter user you supply
        await ctx.channel.send(choice, tts=True)  # Usage: twitter user

def setup(bot):
    bot.add_cog(Utility(bot))