
import requests
import urllib
import discord
import json
from discord.ext import commands

class Writeups(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='writeups', usage='<query>')
    async def writeups(self, ctx, *, query=None):
        if query is None:
            await ctx.send("Query not provided: `>writeups <query>` For an exact match, enclose your search query between double quotes. To exclude a search term, prepend a '-' character.") 
        else:
            writeupapi = "http://ctf-api.hfz-1337.ninja/?q="
            url = writeupapi + urllib.parse.quote_plus(query, safe="")
            r = requests.get(url)
            data = json.loads(r.content)
            i = 0

            while i <= 4:
                try:
                    embed = discord.Embed(title=data[i]['name'], color=0xFF5733)
                    embed.add_field(name="Event", value=data[i]['ctf'], inline=False)
                    embed.add_field(name="Author", value=data[i]['author'], inline=True)
                    embed.add_field(name="Team", value=data[i]['team'], inline=True)
                    embed.add_field(name="CTF Time URL", value=data[i]['ctftime'], inline=False)
                    await ctx.send(embed=embed)
                    i += 1
                except Exception as err:
                    await ctx.send("Error fetching additional results.")
                    break

def setup(bot):
    bot.add_cog(Writeups(bot))
