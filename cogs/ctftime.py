import re
import discord
from discord.ext import tasks, commands
from datetime import *
from dateutil.parser import parse # pip install python-dateutil
import requests
from colorama import Fore, Style
import sys
sys.path.append("..")
from config_vars import *


class CtfTime(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.upcoming_l = []
        self.updateDB.start() # pylint: disable=no-member

    async def cog_command_error(self, ctx, error):
        print(error)
    
    def cog_unload(self):
        self.updateDB.cancel() # pylint: disable=no-member

    @tasks.loop(minutes=30.0, reconnect=True)
    async def updateDB(self):
        # print("updateDB called")
        now = datetime.utcnow()
        unix_now = int(now.replace(tzinfo=timezone.utc).timestamp())
        headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0',
                }
        upcoming = 'https://ctftime.org/api/v1/events/'
        limit = '5' # Max amount I can grab the json data for
        response = requests.get(upcoming, headers=headers, params=limit)
        jdata = response.json()
        
        info = []
        for num, i in enumerate(jdata): # Generate list of dicts of upcoming ctfs
            ctf_title = jdata[num]['title']
            (ctf_start, ctf_end) = (parse(jdata[num]['start'].replace('T', ' ').split('+', 1)[0]), parse(jdata[num]['finish'].replace('T', ' ').split('+', 1)[0]))
            (unix_start, unix_end) = (int(ctf_start.replace(tzinfo=timezone.utc).timestamp()), int(ctf_end.replace(tzinfo=timezone.utc).timestamp()))
            dur_dict = jdata[num]['duration']
            (ctf_hours, ctf_days) = (str(dur_dict['hours']), str(dur_dict['days']))
            ctf_link = jdata[num]['url']
            ctf_image = jdata[num]['logo']
            ctf_format = jdata[num]['format']
            ctf_place = jdata[num]['onsite']
            if ctf_place == False:
              ctf_place = 'Online'
            else:
              ctf_place = 'Onsite'
            
            ctf = {
                'name': ctf_title,
                'start': unix_start,
                'end': unix_end,
                'dur': ctf_days+' days, '+ctf_hours+' hours',
                'url': ctf_link,
                'img': ctf_image,
                'format': ctf_place+' '+ctf_format
                 }
            info.append(ctf)
        
        got_ctfs = []
        for ctf in info: # If the document doesn't exist: add it, if it does: update it.
            query = ctf['name']
            ctfs.update({'name': query}, {"$set":ctf}, upsert=True)
            got_ctfs.append(ctf['name'])
        print(Fore.WHITE + f"{datetime.now()}: " + Fore.GREEN + f"Got and updated {got_ctfs}")
        print(Style.RESET_ALL)
        
        
        for ctf in ctfs.find(): # Delete ctfs that are over from the db
            if ctf['end'] < unix_now:
                ctfs.remove({'name': ctf['name']})

    @updateDB.before_loop
    async def before_updateDB(self):
        await self.bot.wait_until_ready()


    @commands.group()
    async def ctftime(self, ctx):

        if ctx.invoked_subcommand is None:
            # If the subcommand passed does not exist, its type is None
            ctftime_commands = list(set([c.qualified_name for c in CtfTime.walk_commands(self)][1:]))
            await ctx.send(f"Current ctftime commands are: {', '.join(ctftime_commands)}")

    @ctftime.command(aliases=['now', 'running'])
    async def current(self, ctx):
        now = datetime.utcnow()
        unix_now = int(now.replace(tzinfo=timezone.utc).timestamp())
        running = False
        
        for ctf in ctfs.find():
            if ctf['start'] < unix_now and ctf['end'] > unix_now: # Check if the ctf is running
                running = True
                embed = discord.Embed(title=':red_circle: ' + ctf['name']+' IS LIVE', description=ctf['url'], color=15874645)
                start = datetime.utcfromtimestamp(ctf['start']).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
                end = datetime.utcfromtimestamp(ctf['end']).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
                if ctf['img'] != '':
                    embed.set_thumbnail(url=ctf['img'])
                else:
                    embed.set_thumbnail(url="https://pbs.twimg.com/profile_images/2189766987/ctftime-logo-avatar_400x400.png")
                    
                embed.add_field(name='Duration', value=ctf['dur'], inline=True)
                embed.add_field(name='Format', value=ctf['format'], inline=True)
                embed.add_field(name='Timeframe', value=start+' -> '+end, inline=True)
                await ctx.channel.send(embed=embed)
        
        if running == False: # No ctfs were found to be running
            await ctx.send("No CTFs currently running! Check out >ctftime countdown, and >ctftime upcoming to see when ctfs will start!")

    @ctftime.command(aliases=["next"])
    async def upcoming(self, ctx, amount=None):
        if not amount:
            amount = '3'
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0',
        }
        upcoming_ep = "https://ctftime.org/api/v1/events/"
        default_image = "https://pbs.twimg.com/profile_images/2189766987/ctftime-logo-avatar_400x400.png"
        r = requests.get(upcoming_ep, headers=headers, params=amount)
        # print("made request")

        upcoming_data = r.json()
        # print("HERE")

        for ctf in range(0, int(amount)):
            ctf_title = upcoming_data[ctf]["title"]
            (ctf_start, ctf_end) = (upcoming_data[ctf]["start"].replace("T", " ").split("+", 1)[0] + " UTC", upcoming_data[ctf]["finish"].replace("T", " ").split("+", 1)[0] + " UTC")
            (ctf_start, ctf_end) = (re.sub(":00 ", " ", ctf_start), re.sub(":00 ", " ", ctf_end))
            dur_dict = upcoming_data[ctf]["duration"]
            (ctf_hours, ctf_days) = (str(dur_dict["hours"]), str(dur_dict["days"]))
            ctf_link = upcoming_data[ctf]["url"]
            ctf_image = upcoming_data[ctf]["logo"]
            ctf_format = upcoming_data[ctf]["format"]
            ctf_place = upcoming_data[ctf]["onsite"]
            if ctf_place == False:
                ctf_place = "Online"
            else:
                ctf_place = "Onsite"

            embed = discord.Embed(title=ctf_title, description=ctf_link, color=int("f23a55", 16))
            if ctf_image != '':
                embed.set_thumbnail(url=ctf_image)
            else:
                embed.set_thumbnail(url=default_image)

            embed.add_field(name="Duration", value=((ctf_days + " days, ") + ctf_hours) + " hours", inline=True)
            embed.add_field(name="Format", value=(ctf_place + " ") + ctf_format, inline=True)
            embed.add_field(name="Timeframe", value=(ctf_start + " -> ") + ctf_end, inline=True)
            await ctx.channel.send(embed=embed)
    
    @ctftime.command(aliases=["leaderboard"])
    async def top(self, ctx, year = None):
        
        if not year:
            # Default to current year
            year = str(datetime.today().year)
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0',
        }
        top_ep = f"https://ctftime.org/api/v1/top/{year}/"
        leaderboards = ""
        r = requests.get(top_ep, headers=headers)
        if r.status_code != 200:
            await ctx.send("Error retrieving data, please report this with `>report \"what happened\"`")
        else:
            try:
                top_data = (r.json())[year]
                for team in range(10):
                    # Leaderboard is always top 10 so we can just assume this for ease of formatting
                    rank = team + 1
                    teamname = top_data[team]['team_name']
                    score = str(round(top_data[team]['points'], 4))

                    if team != 9:
                        leaderboards += f"\n[{rank}]    {teamname}: {score}"
                    else:
                        leaderboards += f"\n[{rank}]   {teamname}: {score}\n"

                await ctx.send(f":triangular_flag_on_post:  **{year} CTFtime Leaderboards**```ini\n{leaderboards}```")
            except KeyError as e:
                await ctx.send("Please supply a valid year.")
                # LOG THIS
    @ctftime.command()
    async def timeleft(self, ctx):
        now = datetime.utcnow()
        unix_now = int(now.replace(tzinfo=timezone.utc).timestamp())
        running = False
        for ctf in ctfs.find():
            if ctf['start'] < unix_now and ctf['end'] > unix_now: # Check if the ctf is running
                running = True
                time = ctf['end'] - unix_now 
                days = time // (24 * 3600)
                time = time % (24 * 3600)
                hours = time // 3600
                time %= 3600
                minutes = time // 60
                time %= 60
                seconds = time
                await ctx.send(f"```ini\n{ctf['name']} ends in: [{days} days], [{hours} hours], [{minutes} minutes], [{seconds} seconds]```\n{ctf['url']}")
        
        if running == False:
            await ctx.send('No ctfs are running! Use >ctftime upcoming or >ctftime countdown to see upcoming ctfs')

    @ctftime.command()
    async def countdown(self, ctx, params=None):
        now = datetime.utcnow()
        unix_now = int(now.replace(tzinfo=timezone.utc).timestamp())
        
        if params == None:
            self.upcoming_l = []
            index = ""
            for ctf in ctfs.find():
                if ctf['start'] > unix_now:
                    self.upcoming_l.append(ctf)
            for i, c in enumerate(self.upcoming_l):
                index += f"\n[{i + 1}] {c['name']}\n"
            
            await ctx.send(f"Type >ctftime countdown <number> to select.\n```ini\n{index}```")
        else:
            if self.upcoming_l != []:
                x = int(params) - 1     
                start = datetime.utcfromtimestamp(self.upcoming_l[x]['start']).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
                end = datetime.utcfromtimestamp(self.upcoming_l[x]['end']).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
                    
                time = self.upcoming_l[x]['start'] - unix_now 
                days = time // (24 * 3600)
                time = time % (24 * 3600)
                hours = time // 3600
                time %= 3600
                minutes = time // 60
                time %= 60
                seconds = time
                
                await ctx.send(f"```ini\n{self.upcoming_l[x]['name']} starts in: [{days} days], [{hours} hours], [{minutes} minutes], [{seconds} seconds]```\n{self.upcoming_l[x]['url']}")
            else: # TODO: make this a function, too much repeated code here.
                for ctf in ctfs.find():
                    if ctf['start'] > unix_now:
                        self.upcoming_l.append(ctf)
                x = int(params) - 1     
                start = datetime.utcfromtimestamp(self.upcoming_l[x]['start']).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
                end = datetime.utcfromtimestamp(self.upcoming_l[x]['end']).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
                    
                time = self.upcoming_l[x]['start'] - unix_now 
                days = time // (24 * 3600)
                time = time % (24 * 3600)
                hours = time // 3600
                time %= 3600
                minutes = time // 60
                time %= 60
                seconds = time
                
                await ctx.send(f"```ini\n{self.upcoming_l[x]['name']} starts in: [{days} days], [{hours} hours], [{minutes} minutes], [{seconds} seconds]```\n{self.upcoming_l[x]['url']}")

def setup(bot):
    bot.add_cog(CtfTime(bot))
