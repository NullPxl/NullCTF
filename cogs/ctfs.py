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
from datetime import datetime
from colorthief import ColorThief

import discord
from discord.ext import commands

class Ctfs:
   def __init__(self, bot):
      self.bot = bot
   
   # Returns upcoming ctfs, leaderboards, and currently running ctfs from ctftime.org (using their api)
   # Usage: ctftime <upcoming/top/current> <number of ctfs/year>
   @commands.command(pass_context = True)
   async def ctftime(self, ctx, status, params=None):
      current_ctftime_cmds = ['upcoming', 'top', 'current']
      default_image = "https://pbs.twimg.com/profile_images/2189766987/ctftime-logo-avatar_400x400.png"

      def rgb2hex(r,g,b):
         tohex = "#{:02x}{:02x}{:02x}".format(r,g,b)
         return tohex

      headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}
      
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
            ctf_start, ctf_end = data[num]['start'].replace('T', ' ').split('+', 1)[0] + ' UTC', data[num]['finish'].replace('T', ' ').split('+', 1)[0] + ' UTC'
            ctf_start, ctf_end = re.sub(':00 ', ' ', ctf_start), re.sub(':00 ', ' ', ctf_end)
            dur_dict  = data[num]['duration']
            ctf_hours, ctf_days = str(dur_dict['hours']), str(dur_dict['days'])
            ctf_link  = data[num]['url']
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
            
            # Get the dominant color in image (ctf logo must be available to the api)
            f = io.BytesIO(fd.read())
            color_thief = ColorThief(f)
            rgb_color = color_thief.get_color(quality=49)
            hexed = str(rgb2hex(rgb_color[0], rgb_color[1], rgb_color[2])).replace('#', '')
            f_color = int(hexed, 16)   

            # Set up embed
            embed = discord.Embed(title=ctf_title, description=ctf_link, color=f_color) #0x42f480
            
            if ctf_image != '':
               embed.set_thumbnail(url=ctf_image)
            
            else:
               embed.set_thumbnail(url=default_image)
            
            embed.add_field(name="Duration", value=ctf_days+" days, "+ctf_hours+" hours", inline=True)
            embed.add_field(name="Format", value=ctf_place+' '+ctf_format, inline=True)
            embed.add_field(name="─"*23, value=ctf_start+" -> "+ctf_end, inline=True)
            
            await self.bot.send_message(ctx.message.channel, embed=embed)


      if status == 'top':      
         top_url = 'https://ctftime.org/api/v1/top/'
         response = requests.get(top_url, headers=headers, params=params)
         data = response.json()
         leaderboards = ""
         
         if not params:
            params = '2018'
         
         for team in range (10):
            rank = team + 1
            teamname = data[params][team]['team_name']
            score    = data[params][team]['points']
            
            if team != 9:
               leaderboards += (f"\n[{rank}]    {teamname}: {score}\n")
            
            else:
               leaderboards += (f"\n[{rank}]   {teamname}: {score}\n")
         
         await self.bot.say(f":triangular_flag_on_post:  **{params} CTFtime Leaderboards**```ini\n{leaderboards}```")


      if status == "current":
         def updateDb():
            upcoming = 'https://ctftime.org/api/v1/events/'
            limit = '5'
            response = requests.get(upcoming, headers=headers, params=limit)
            json_data = response.json()

            with open('db.txt', 'r+') as db:
               data=db.read()

               for num in range(0, int(limit)):
                  ctf_title = json_data[num]['title']
                  ctf_check = f"{ctf_title}"
                  
                  if ctf_check in data:
                     continue
                  
                  else:

                     now = datetime.utcnow()
                     unix_now = int(now.replace(tzinfo=timezone.utc).timestamp())
                     ctf_format = json_data[num]['format']
                     ctf_place = json_data[num]['onsite']
                     
                     if ctf_place == False:
                        ctf_place = 'Online'
                     
                     else:
                        ctf_place = 'Onsite'
                     
                     dur_dict  = json_data[num]['duration']
                     ctf_hours, ctf_days = str(dur_dict['hours']), str(dur_dict['days'])
                     ctf_start, ctf_end = parse(json_data[num]['start'].replace('T', ' ').split('+', 1)[0]), parse(json_data[num]['finish'].replace('T', ' ').split('+', 1)[0])
                     unix_start, unix_end = int(ctf_start.replace(tzinfo=timezone.utc).timestamp()), int(ctf_end.replace(tzinfo=timezone.utc).timestamp())
                     dur_dict  = json_data[num]['duration']
                     ctf_hours, ctf_days = str(dur_dict['hours']), str(dur_dict['days'])
                     ctf_link  = json_data[num]['url']
                     ctf_image = json_data[num]['logo']
                     db.write(f"\n\"{ctf_title}\" \"{unix_start}\" \"{unix_end}\" <link>{ctf_link}<link> <image>{ctf_image}<image> <format>{ctf_place} {ctf_format}<format> <duration>{ctf_days} days, {ctf_hours} hours<duration>")

         updateDb()

         running = False
         
         with open('db.txt', 'r+') as db:
            data=db.readlines()
            times_pat = r"\"(\d+)\""
            ctf_pat   = r".*(?=\s\"\d+\"\s\"\d+\")"
            ctf_url_pat = r"<link>(.*)<link>"
            ctf_img_pat = r"<image>(.*)<image>"
            ctf_format_pat = r"<format>(.*)<format>"
            ctf_dur_pat = r"<duration>(.*)<duration>"
            
            for line in data:
               now = datetime.utcnow()
               unix_now = int(now.replace(tzinfo=timezone.utc).timestamp())
               
               try:
                  ctf_name = re.search(ctf_pat, line)
                  ctf_url = re.search(ctf_url_pat, line)
                  ctf_img = re.search(ctf_img_pat, line)
                  ctf_format = re.search(ctf_format_pat, line)
                  ctf_dur = re.search(ctf_dur_pat, line)       
                  times = re.findall(times_pat, line)
                  u_start = int(times[0].replace('"', ''))
                  u_end   = int(times[1].replace('"', ''))
                  start   = datetime.utcfromtimestamp(u_start).strftime('%Y-%m-%d %H:%M:%S')
                  end     = datetime.utcfromtimestamp(u_end).strftime('%Y-%m-%d %H:%M:%S')
                  url = ctf_url.group(0).replace("<link>", '')
                  img = ctf_img.group(0).replace("<image>", '')
                  format_c = ctf_format.group(0).replace("<format>", '')
                  dur = ctf_dur.group(0).replace("<duration>", '')
                  ctf   = ctf_name.group(0).replace('"', '')
               
               except:
                  continue
               
               if u_start < unix_now and u_end > unix_now:               
                  running = True
                  embed = discord.Embed(title=":red_circle: "+ctf+" IS LIVE", description=url, color=0xf23a55)
                  
                  if img != '':
                     embed.set_thumbnail(url=img)
                  
                  else:
                     embed.set_thumbnail(url=default_image)
                  
                  embed.add_field(name="Duration", value=dur, inline=True)
                  embed.add_field(name="Format", value=format_c, inline=True)
                  embed.add_field(name="─"*23, value=start+" UTC -> "+end+" UTC", inline=True)
                  await self.bot.send_message(ctx.message.channel, embed=embed)
         
         if running == False:
            await self.bot.say("There are currently no running ctfs on ctftime.org :neutral_face: .  Check out '>ctftime upcoming' to see upcoming ctfs")
         
         else:
            pass

      if status not in current_ctftime_cmds:
         await self.bot.say("Current ctftime commands are: top [year], upcoming [amount up to 5], current")

   # Returns the latest tweet from @hackthebox_eu that says when the next box will go live.
   # Usage: htb
   @commands.command(pass_context = True)
   async def htb(self, ctx):
      # Define page and encode into str format from bytes
      twitter_page = requests.get("https://twitter.com/hackthebox_eu")
      all_content = str(twitter_page.text.encode("utf-8"))
       
      # Set up regex and get the most recent tweet that matches
      tweet = re.search(r"\w+ will go live \d{2}/\d{2}/\d{4} at \d{2}:\d{2}:\d{2} UTC", all_content)
      match = tweet.group(0)
      await self.bot.say(match + "\nhttps://hackthebox.eu")

def setup(bot):
   bot.add_cog(Ctfs(bot))