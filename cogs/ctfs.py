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
from dateutil.parser import parse
import time
import datetime
from datetime import timezone
from datetime import datetime, timedelta

from colorthief import ColorThief
import discord
from discord.ext import commands

class Ctfs():

    def __init__(self, bot):
        self.bot = bot
        self.challenges = {}
        self.ctfname = ""
        self.upcoming_l = []

    @staticmethod
    def updatedb():
        headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0',
                }
        upcoming = 'https://ctftime.org/api/v1/events/'
        limit = '5'
        response = requests.get(upcoming, headers=headers, params=limit)
        json_data = response.json()
        data = []
        with open("db.json", 'r') as local:
            db_data = json.load(local)
        
        def update(name, entry):
            with open("db.json", mode='a', encoding='utf-8') as db:
                json.dump(data, db, indent=3)

        with open("db.json", 'w') as db:
            if len(db_data) > len(json_data):
                diff = int(len(db_data)) - int(len(json_data))
                
                for each in range (0, diff):
                    ctf_info = {
                        'name': db_data[each]['name'],
                        'start': db_data[each]['start'],
                        'end': db_data[each]['end'],
                        'dur': db_data[each]['dur'],
                        'url': db_data[each]['url'],
                        'img': db_data[each]['img'],
                        'format': db_data[each]['format']
                        }
                    data.append(ctf_info)



            for num in range(0, int(limit)):
                ctf_title = json_data[num]['title']
                now = datetime.utcnow()
                unix_now = int(now.replace(tzinfo=timezone.utc).timestamp())
                ctf_format = json_data[num]['format']
                ctf_place = json_data[num]['onsite']
                
                if ctf_place == False:
                    ctf_place = 'Online'
                else:
                    ctf_place = 'Onsite'
                
                dur_dict = json_data[num]['duration']
                (ctf_hours, ctf_days) = (str(dur_dict['hours']), str(dur_dict['days']))
                (ctf_start, ctf_end) = (parse(json_data[num]['start'].replace('T', ' ').split('+', 1)[0]), parse(json_data[num]['finish'].replace('T', ' ').split('+', 1)[0]))
                (unix_start, unix_end) = (int(ctf_start.replace(tzinfo=timezone.utc).timestamp()), int(ctf_end.replace(tzinfo=timezone.utc).timestamp()))
                dur_dict = json_data[num]['duration']
                (ctf_hours, ctf_days) = (str(dur_dict['hours']), str(dur_dict['days']))
                ctf_link = json_data[num]['url']
                ctf_image = json_data[num]['logo']
                ctf_info = {
                    'name': ctf_title,
                    'start': unix_start,
                    'end': unix_end,
                    'dur': ctf_days+' days, '+ctf_hours+' hours',
                    'url': ctf_link,
                    'img': ctf_image,
                    'format': ctf_place+' '+ctf_format
                    }
                data.append(ctf_info)
                
        update('db.json', data)
    @commands.command()
    async def ctf(self, ctx, cmd, params=None, verbose=None):
    # I understand how terrible this all this, I will make an actual fix using tinydb, but for now this should sort of work.
        guild = ctx.guild
        gid = ctx.guild.id
        category = discord.utils.get(ctx.guild.categories, name="CTF")
        data = []
        def update(name, entry):
            with open('ctf.json', mode='a', encoding='utf-8') as g_ctfs:
                json.dump(data, g_ctfs, indent=3)        

        with open('ctf.json', 'r') as json_ctf:
            try:
                ctf_data = json.load(json_ctf)
                for ctf in ctf_data:
                    try:
                        g_ctfname = ctf[str(gid)]["ctf_name"]
                        g_challenges = ctf[str(gid)]["challenges"]
                    except:
                        print(f"server {gid} is not in ctf.json")
            except:
                print('error loading json file (might just be empty)')


        with open('ctf.json', 'w') as g_ctfs: #FIX THIS!
        
            if cmd == 'create': #todo, make this append onto the ctf.json file, not replace it.
                if ctx.message.author.id ==  ctx.guild.owner.id or ctx.message.author.id == 230827776637272064:
                    await guild.create_text_channel(name=params, category=category)
                    await guild.create_role(name=params)
                    self.ctfname = params
                    self.challenges = {}
                    ctf_info = {str(ctx.guild.id):{
                        "ctf_name": self.ctfname,
                        "challenges": self.challenges
                        }}
                    print(ctf_info)
                    data.append(ctf_info)
                    update('ctf.json', data)
                else:
                    await ctx.send('You must be owner to use this command! Please tag the owner to create the ctf.') 
            
            if cmd == 'challenge':

                if params == 'add': # Usage: ctf challenge add challengename
                    self.challenges[verbose] = 'Incomplete'

                    g_challenges.update(self.challenges)
                    ctf_info = {str(ctx.guild.id):{
                        "ctf_name": g_ctfname,
                        "challenges": g_challenges
                        }}
                
                if params == 'solved': # Usage: ctf challenge solved challengename
                    self.challenges[verbose] = g_challenges[verbose].replace('Incomplete', 'Completed!')
                    await ctx.send(':triangular_flag_on_post:')
                    
                    g_challenges.update(self.challenges)
                    ctf_info = {str(ctx.guild.id):{
                        "ctf_name": g_ctfname,
                        "challenges": g_challenges
                        }}             

                if params == 'working': # Usage: ctf challenge working challengename
                    author = str(ctx.message.author)
                    author = re.sub(r'#(\d{4})', '', author)
                    try:
                        self.challenges[verbose] += ' - '+author
                    except:
                        self.challenges[verbose] = 'Incomplete'
                        self.challenges[verbose] += ' - '+author

                    g_challenges.update(self.challenges)
                    
                    ctf_info = {str(ctx.guild.id):{
                        "ctf_name": g_ctfname,
                        "challenges": g_challenges
                        }}

                if params == 'list': # Usage: ctf challenge list
                    try:
                        pretty_g_chal = str(g_challenges).replace(', ', '\n').replace('{', '').replace('}', '').replace("'", '')
                        await ctx.send(f"```ini\n{pretty_g_chal}```")
                    except:
                        await ctx.send("Steps:  Create a ctf with >ctf create \"ctf\", Add a challenge with >ctf challenge add <challengename>")

                    g_challenges.update(self.challenges)
                    ctf_info = {str(ctx.guild.id):{
                        "ctf_name": g_ctfname,
                        "challenges": g_challenges
                        }}

                else:
                    pass

                    #CTF.JSON GETS CLEARED WHEN THIS ANY OTHER CTF COMMANDS ARE CALLED! FIX
                print(ctf_info)
                data.append(ctf_info)
                update('ctf.json', data)

        if cmd == 'timeleft': # Return the timeleft in the ctf in days, hours, minutes, seconds
            Ctfs.updatedb()
            guild = ctx.guild
            gid = ctx.guild.id
            with open('ctf.json', 'r') as json_ctf:
                try:
                    ctf_data = json.load(json_ctf)
                    for ctf in ctf_data:
                        try:
                            g_ctfname = ctf[str(gid)]["ctf_name"]
                        except:
                            print(f"server {gid} is not in ctf.json")
                except:
                    print('error loading json file (might just be empty)')            

            with open("db.json") as db:
                time_data = json.load(db)
                running = False
                
                for ctf in time_data:
                    now = datetime.utcnow()
                    unix_now = int(now.replace(tzinfo=timezone.utc).timestamp())
                    start = datetime.utcfromtimestamp(ctf['start']).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
                    end = datetime.utcfromtimestamp(ctf['end']).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
                  
                    if ctf['start'] < unix_now and ctf['end'] > unix_now: #check if ctf is currently running
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
                    await ctx.send('No ctfs are running! Use >ctftime upcoming to see upcoming ctfs')


            ctf_info = {str(ctx.guild.id):{
                "ctf_name": g_ctfname,
                "challenges": g_challenges
                }}
            print(ctf_info)
            data.append(ctf_info)
            update('ctf.json', data)

        if cmd == 'countdown':
            Ctfs.updatedb()
            guild = ctx.guild
            gid = ctx.guild.id
            with open('ctf.json', 'r') as json_ctf:
                try:
                    ctf_data = json.load(json_ctf)
                    for ctf in ctf_data:
                        try:
                            g_ctfname = ctf[str(gid)]["ctf_name"]
                        except:
                            print(f"server {gid} is not in ctf.json")
                except:
                    print('error loading json file (might just be empty)')
            
            with open("db.json") as db:
                time_data = json.load(db)
                i = 0
                numbers = ""
                now = datetime.utcnow()
                unix_now = int(now.replace(tzinfo=timezone.utc).timestamp())

                if params == None:
                    self.upcoming_l = []                    
                    for ctf in time_data:
                        
                        if ctf['start'] > unix_now:
                            self.upcoming_l.append(ctf)
                        else:
                            pass

                    for entry in self.upcoming_l:
                        numbers += f"\n[{i + 1}] {entry['name']}\n"
                        i += 1
                    
                    await ctx.send(f"Type >ctf countdown <number> to select.```ini\n{numbers}```")
                
                else:
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
        
            ctf_info = {str(ctx.guild.id):{
                "ctf_name": g_ctfname,
                "challenges": g_challenges
                }}
            print(ctf_info)
            data.append(ctf_info)
            update('ctf.json', data)

        if cmd == 'join':
            guild = ctx.guild
            gid = ctx.guild.id
            with open('ctf.json', 'r') as json_ctf:
                try:
                    ctf_data = json.load(json_ctf)
                    for ctf in ctf_data:
                        try:
                            g_ctfname = ctf[str(gid)]["ctf_name"]
                        except:
                            print(f"server {gid} is not in ctf.json")
                except:
                    print('error loading json file (might just be empty)')
            
            role = discord.utils.get(ctx.guild.roles, name=g_ctfname)
            user = ctx.message.author
            await user.add_roles(role)
            await ctx.send(f"{user} has joined the {g_ctfname} team!")

            ctf_info = {str(ctx.guild.id):{
                "ctf_name": g_ctfname,
                "challenges": g_challenges
                }}
            print(ctf_info)
            data.append(ctf_info)
            update('ctf.json', data)

        if cmd == 'leave':
            guild = ctx.guild
            gid = ctx.guild.id
            with open('ctf.json', 'r') as json_ctf:
                try:
                    ctf_data = json.load(json_ctf)
                    for ctf in ctf_data:
                        try:
                            g_ctfname = ctf[str(gid)]["ctf_name"]
                        except:
                            print(f"server {gid} is not in ctf.json")
                except:
                    print('error loading json file (might just be empty)')
            role = discord.utils.get(ctx.guild.roles, name=g_ctfname)
            user = ctx.message.author
            await user.remove_roles(role)
            await ctx.send(f"{user} has left the {g_ctfname} team.")

            ctf_info = {str(ctx.guild.id):{
                "ctf_name": g_ctfname,
                "challenges": g_challenges
                }}
            print(ctf_info)
            data.append(ctf_info)
            update('ctf.json', data)

    # Returns upcoming ctfs, leaderboards, and currently running ctfs from ctftime.org (using their api)
    # Usage: ctftime <upcoming/top/current> <number of ctfs/year>
    @commands.command() 
    async def ctftime(self, ctx, status, params=None):
        current_ctftime_cmds = ['upcoming', 'top', 'current']
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
                
                if ctf_image != '':
                    fd = urlopen(ctf_image)
                else:
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
            top_url = 'https://ctftime.org/api/v1/top/'
            response = requests.get(top_url, headers=headers, params=params)
            data = response.json()
            leaderboards = ''
            
            if (not params):
                params = '2018'
            
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
            running = False
            #read from file and check if ctf is running
            with open("db.json") as db:
                data = json.load(db) #data, ctf['name'], ctf['start'], ctf['end'], ctf['dur'], ctf['url'], ctf['img'], ctf['format']
                
                for ctf in data:
                    now = datetime.utcnow()
                    unix_now = int(now.replace(tzinfo=timezone.utc).timestamp())
                    start = datetime.utcfromtimestamp(ctf['start']).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
                    end = datetime.utcfromtimestamp(ctf['end']).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
                  
                    if ctf['start'] < unix_now and ctf['end'] > unix_now: #check if ctf is currently running
                        running = True
                        embed = discord.Embed(title=':red_circle: ' + ctf['name']+' IS LIVE', description=ctf['url'], color=15874645)
                     
                        if ctf['img'] != '':
                            embed.set_thumbnail(url=ctf['img'])
                        else:
                            embed.set_thumbnail(url=default_image)
                         
                        embed.add_field(name='Duration', value=ctf['dur'], inline=True)
                        embed.add_field(name='Format', value=ctf['format'], inline=True)
                        embed.add_field(name='─' * 23, value=start+' -> '+end, inline=True)
                        await ctx.channel.send(embed=embed)
                        
            if running == False:
                await ctx.send("No CTFs currently running! Check out >ctf countdown, and >ctftime upcoming to see when ctfs will start!")
 
        
        if status not in current_ctftime_cmds:
            await ctx.send('Current ctftime commands are: top [year], upcoming [amount up to 5], current')

    @commands.command()
    async def htb(self, ctx):
        twitter_page = requests.get('https://twitter.com/hackthebox_eu')
        all_content = str(twitter_page.text.encode('utf-8'))
        tweet = re.search('\\w+ will go live \\d{2}/\\d{2}/\\d{4} at \\d{2}:\\d{2}:\\d{2} UTC', all_content)
        match = tweet.group(0)
        await ctx.send(match + '\nhttps://hackthebox.eu')

def setup(bot):
    bot.add_cog(Ctfs(bot))