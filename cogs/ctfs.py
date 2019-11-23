import urllib
import requests
import re
import json
import base64
import binascii
import collections
import string
import urllib.parse
from urllib.request import urlopen
import io
import time
import datetime
from pymongo import MongoClient
from pprint import pprint
from random import randint
from datetime import *
from dateutil.parser import parse
from mongo import *
from colorama import Fore, Style

from colorthief import ColorThief
import discord
from discord.ext import commands

class Ctfs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.challenges = {}
        self.ctfname = ""
        self.upcoming_l = []

    @staticmethod
    def updatedb():
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

    @commands.group()
    async def ctf(self, ctx):
        global guild
        global gid
        guild = ctx.guild
        gid = ctx.guild.id 

        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid command passed.  Use >help.')

    @commands.has_permissions(manage_channels=True)
    @ctf.command()
    async def create(self, ctx, params):
        try:
            sconf = serverdb[str(gid) + 'CONF']
            scat = sconf.find_one({'name': "category_name"})['ctfcategory'] # scat means server category
        except:
            scat = "CTF"
            
        category = discord.utils.get(ctx.guild.categories, name=scat)
        if category == None: # Checks if category exists, if it doesn't it will create it.
            await guild.create_category(name=scat)
            category = discord.utils.get(ctx.guild.categories, name=scat)

        await guild.create_text_channel(name=params, category=category)        
        server = teamdb[str(gid)]
        name = params.replace(' ', '-').replace("'", "").lower() # Discord does this when creating text channels. 
        await guild.create_role(name=name, mentionable=True)         
        ctf_info = {'name': name, "text_channel": name}
        server.update({'name': name}, {"$set": ctf_info}, upsert=True)

    @ctf.command()
    async def join(self, ctx):
        if teamdb[str(gid)].find_one({'name': str(ctx.message.channel)}):
            role = discord.utils.get(ctx.guild.roles, name=str(ctx.message.channel))
            user = ctx.message.author
            await user.add_roles(role)
            await ctx.send(f"{user} has joined the {str(ctx.message.channel)} team!")
        else:
            await ctx.send('You must be in a channel created using >ctf create to use this command!')

    @ctf.command()
    async def leave(self, ctx):
        if teamdb[str(gid)].find_one({'name': str(ctx.message.channel)}):
            role = discord.utils.get(ctx.guild.roles, name=str(ctx.message.channel))
            user = ctx.message.author
            await user.remove_roles(role)
            await ctx.send(f"{user} has left the {str(ctx.message.channel)} team.")
        else:
            await ctx.send('You must be in a channel created using >ctf create to use this command!')
    
    @commands.has_permissions(manage_channels=True)
    @ctf.command()
    async def end(self, ctx):
        if teamdb[str(gid)].find_one({'name': str(ctx.message.channel)}):
            #delete role from server, delete entry from db
            role = discord.utils.get(ctx.guild.roles, name=str(ctx.message.channel))
            await role.delete()
            await ctx.send(f"`{role.name}` role deleted")
            teamdb[str(gid)].remove({'name': str(ctx.message.channel)})
            await ctx.send(f"`{str(ctx.message.channel)}` deleted from db")
        else:
            await ctx.send('You must be in a channel created using >ctf create to use this command!')
    
    @ctf.command(aliases=['chal'])
    async def challenge(self, ctx, params, verbose=None):       
        # Testing if the command was sent in a ctf channel
        # This is how I will differenciate between different ctfs in the same server.
        server = teamdb[str(gid)]
        if teamdb[str(gid)].find_one({'name': str(ctx.message.channel)}):
            correct_channel = True
            
            def updatechallenge(status):
                challenge = {str(verbose): status}
                ctf = server.find_one({'name': str(ctx.message.channel)})
                try: # If there are existing challenges already...
                    challenges = ctf['challenges']
                    challenges.update(challenge)
                except:
                    challenges = challenge
                ctf_info = {'name': str(ctx.message.channel),
                'challenges': challenges
                }
                server.update({'name': str(ctx.message.channel)}, {"$set": ctf_info}, upsert=True)

        else:
            await ctx.send('You must be in a created ctf channel to use this command!')
            correct_channel = False

        if correct_channel == True:

            if params == 'add' or params == 'a': # Usage: ctf challenge add "challenge name"
                updatechallenge('Unsolved')
                await ctx.send(f"'{verbose}' has been added to the challenge list for {str(ctx.message.channel)}")

            
            if params == 'solved' or params == 's': # Usage: ctf challenge solved "challenge name"
                solve = f"Solved - {str(ctx.message.author)}"
                updatechallenge(solve)
                await ctx.send(f":triangular_flag_on_post: {verbose} has been solved by {str(ctx.message.author)}")
                           

            if params == 'working' or params == 'w': # Usage: ctf challenge working "challenge name"
                working = f"Working - {str(ctx.message.author)}"
                updatechallenge(working)
                await ctx.send(f"{str(ctx.message.author)} is working on {verbose}!")

            if params == 'list': # Usage: ctf challenge list
                ctf = server.find_one({'name': str(ctx.message.channel)})
                try:
                    challenges = str(ctf['challenges']).replace('"', '').replace("'", "").replace('{', '').replace('}', '').split(',')
                    formatted_chals = ""
                    for i, c in enumerate(challenges):
                        if i != 0:
                            pos = c.index(':') - 1
                        else:
                            pos = c.index(':')
                        c = c.lstrip(' ')
                        formatted_c = '[' + c[:pos] + ']' + c[pos:] + '\n'
                        formatted_chals += formatted_c
                    
                    await ctx.send(f"```ini\n{formatted_chals}```")
                except KeyError as e: # If nothing has been added to the challenges list
                    await ctx.send("Add some challenges with `>ctf challenge add \"challenge name\"`")
                    
                       


    # Returns upcoming ctfs, leaderboards, and currently running ctfs from ctftime.org (using their api)
    # Usage: ctftime <upcoming/top/current> <number of ctfs/year>
    @commands.command() 
    async def ctftime(self, ctx, status, params=None):
        current_ctftime_cmds = ['upcoming', 'top', 'current', 'countdown', 'timeleft']
        default_image = 'https://pbs.twimg.com/profile_images/2189766987/ctftime-logo-avatar_400x400.png'

        def rgb2hex(r, g, b):
            tohex = '#{:02x}{:02x}{:02x}'.format(r, g, b)
            return tohex
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0',
        }
        
        if status == 'upcoming':
            upcoming_url = 'https://ctftime.org/api/v1/events/'
            response = requests.get(upcoming_url, headers=headers, params=params)
            data = response.json()
            
            if params == None:
                params = '3'
            else:
                pass
            
            for num in range(0, int(params)):
                ctf_title = data[num]['title']
                (ctf_start, ctf_end) = (data[num]['start'].replace('T', ' ').split('+', 1)[0] + ' UTC', data[num]['finish'].replace('T', ' ').split('+', 1)[0] + ' UTC')
                (ctf_start, ctf_end) = (re.sub(':00 ', ' ', ctf_start), re.sub(':00 ', ' ', ctf_end))
                dur_dict = data[num]['duration']
                (ctf_hours, ctf_days) = (str(dur_dict['hours']), str(dur_dict['days']))
                ctf_link = data[num]['url']
                ctf_image = data[num]['logo']
                ctf_format = data[num]['format']
                ctf_place = data[num]['onsite']
                
                if ctf_place == False:
                    ctf_place = 'Online'
                else:
                    ctf_place = 'Onsite'
                
                # if ctf_image != '':
                #     fd = urlopen(ctf_image) # 403 is on this line, no longer able to access this?
                # else:
                #     fd = urlopen(default_image)
                fd = urlopen(default_image)
                f = io.BytesIO(fd.read())
                color_thief = ColorThief(f)
                rgb_color = color_thief.get_color(quality=49)
                hexed = str(rgb2hex(rgb_color[0], rgb_color[1], rgb_color[2])).replace('#', '')
                f_color = int(hexed, 16)
                embed = discord.Embed(title=ctf_title, description=ctf_link, color=f_color)
                
                if ctf_image != '':
                    embed.set_thumbnail(url=ctf_image)
                else:
                    embed.set_thumbnail(url=default_image)
                
                embed.add_field(name='Duration', value=((ctf_days + ' days, ') + ctf_hours) + ' hours', inline=True)
                embed.add_field(name='Format', value=(ctf_place + ' ') + ctf_format, inline=True)
                embed.add_field(name='─' * 23, value=(ctf_start + ' -> ') + ctf_end, inline=True)
                await ctx.channel.send(embed=embed)
        
        if status == 'top':
            if (not params):
                params = '2019'
            
            params = str(params)
            top_url = 'https://ctftime.org/api/v1/top/' + params + '/'
            response = requests.get(top_url, headers=headers)
            data = response.json()
            leaderboards = ''
            
            for team in range(10):
                rank = team + 1
                teamname = data[params][team]['team_name']
                score = data[params][team]['points']
                
                if team != 9:
                    leaderboards += f'''
[{rank}]    {teamname}: {score}
'''
                else:
                    leaderboards += f'''
[{rank}]   {teamname}: {score}
'''
            await ctx.send(f''':triangular_flag_on_post:  **{params} CTFtime Leaderboards**```ini
{leaderboards}```''')
        
        if status == 'current':
            Ctfs.updatedb()
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
                        embed.set_thumbnail(url=default_image)
                     
                    embed.add_field(name='Duration', value=ctf['dur'], inline=True)
                    embed.add_field(name='Format', value=ctf['format'], inline=True)
                    embed.add_field(name='─' * 23, value=start+' -> '+end, inline=True)
                    await ctx.channel.send(embed=embed)
            
            if running == False: # No ctfs were found to be running
                await ctx.send("No CTFs currently running! Check out >ctftime countdown, and >ctftime upcoming to see when ctfs will start!")

        if status == 'timeleft': # Return the timeleft in the ctf in days, hours, minutes, seconds
            Ctfs.updatedb()
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

        if status == 'countdown':
            Ctfs.updatedb()
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


        if status not in current_ctftime_cmds:
            await ctx.send('Current ctftime commands are: top [year], upcoming [amount up to 5], current, countdown, timeleft')

    @commands.command()
    async def htb(self, ctx):
        twitter_page = requests.get('https://twitter.com/hackthebox_eu')
        all_content = str(twitter_page.text.encode('utf-8'))
        tweet = re.search('\\w+ will go live \\d{2} \\w+ \\d{4} at \\d{2}:\\d{2}:\\d{2} UTC. \\w+ will be retired!', all_content)
        match = tweet.group(0)
        await ctx.send(match + '\nhttps://hackthebox.eu')

def setup(bot):
    bot.add_cog(Ctfs(bot))
