import discord
from discord.ext import tasks, commands
import string
import json
import requests
import sys
import traceback
sys.path.append("..")
from config_vars import *

# All commands relating to server specific CTF data
# Credentials provided for pulling challenges from the CTFd platform are NOT stored in the database.
    # they are stored in a pinned message in the discord channel.

def in_ctf_channel():
    async def tocheck(ctx):
        # A check for ctf context specific commands
        if teamdb[str(ctx.guild.id)].find_one({'name': str(ctx.message.channel)}):
            return True
        else:
            await ctx.send("You must be in a created ctf channel to use ctf commands!")
            return False
    return commands.check(tocheck)

def strip_string(tostrip, whitelist):
    # A string validator to correspond with a provided whitelist.
    stripped = ''.join([ch for ch in tostrip if ch in whitelist])
    return stripped.strip()

class InvalidProvider(Exception):
    pass
class InvalidCredentials(Exception):
    pass
class CredentialsNotFound(Exception):
    pass
class NonceNotFound(Exception):
    pass

def getChallenges(url, username, password):
    # Pull challenges from a ctf hosted with the commonly used CTFd platform using provided credentials
    whitelist = set(string.ascii_letters+string.digits+' '+'-'+'!'+'#'+'_'+'['+']'+'('+')'+'?'+'@'+'+'+'<'+'>')
    fingerprint = "Powered by CTFd"
    s = requests.session()
    if url[-1] == "/": url = url[:-1]
    r = s.get(f"{url}/login")
    if fingerprint not in r.text:
        raise InvalidProvider("CTF is not based on CTFd, cannot pull challenges.")
    else:
        # Get the nonce from the login page.
        try:
            nonce = r.text.split("csrfNonce': \"")[1].split('"')[0]
        except: # sometimes errors happen here, my theory is that it is different versions of CTFd
            try:
                nonce = r.text.split("name=\"nonce\" value=\"")[1].split('">')[0]
            except:
                raise NonceNotFound("Was not able to find the nonce token from login, please >report this along with the ctf url.")
        # Login with the username, password, and nonce
        r = s.post(f"{url}/login", data={"name": username, "password": password, "nonce": nonce})
        if "Your username or password is incorrect" in r.text:
            raise InvalidCredentials("Invalid login credentials")
        r_chals = s.get(f"{url}/api/v1/challenges")
        all_challenges = r_chals.json()
        r_solves = s.get(f"{url}/api/v1/teams/me/solves")
        team_solves = r_solves.json()
        if 'success' not in team_solves:
            # ctf is user based.  There is a flag on CTFd for this (userMode), but it is not present in all versions, this way seems to be.
            r_solves = s.get(f"{url}/api/v1/users/me/solves")
            team_solves = r_solves.json()
        
        solves = []
        if team_solves['success'] == True:
            for solve in team_solves['data']:
                cat = solve['challenge']['category']
                challname = solve['challenge']['name']
                solves.append(f"<{cat}> {challname}")
        challenges = {}
        if all_challenges['success'] == True:
            for chal in all_challenges['data']:
                cat = chal['category']
                challname = chal['name']
                name = f"<{cat}> {challname}"
                # print(name)
                # print(strip_string(name, whitelist))
                if name not in solves:
                    challenges.update({strip_string(name, whitelist): 'Unsolved'})
                else:
                    challenges.update({strip_string(name, whitelist): 'Solved'})
        else:
            raise Exception("Error making request")
        # Returns all the new challenges and their corresponding statuses in a dictionary compatible with the structure that would happen with 'normal' useage.
        return challenges



class CTF(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.group()
    async def ctf(self, ctx):
        if ctx.invoked_subcommand is None:
            # If the subcommand passed does not exist, its type is None
            ctf_commands = list(set([c.qualified_name for c in CTF.walk_commands(self)][1:]))
            await ctx.send(f"Current ctf commands are: {', '.join(ctf_commands)}") # update this to include params

    @commands.bot_has_permissions(manage_channels=True, manage_roles=True)
    @commands.has_permissions(manage_channels=True)
    @ctf.command(aliases=["new"])
    async def create(self, ctx, name):
        # Create a new channel in the CTF category (default='CTF' or configured with the configuration extension)
        try:
            sconf = serverdb[str(ctx.guild.id) + '-CONF']
            servcat = sconf.find_one({'name': "category_name"})['ctf_category']
        except:
            servcat = "CTF"
        
        category = discord.utils.get(ctx.guild.categories, name=servcat)
        if category == None: # Checks if category exists, if it doesn't it will create it.
            await ctx.guild.create_category(name=servcat)
            category = discord.utils.get(ctx.guild.categories, name=servcat)
        
        ctf_name = strip_string(name, set(string.ascii_letters + string.digits + ' ' + '-')).replace(' ', '-').lower()
        if ctf_name[0] == '-': ctf_name = ctf_name[1:] # edge case where channel names can't start with a space (but can end in one)
        # There cannot be 2 spaces (which are converted to '-') in a row when creating a channel.  This makes sure these are taken out.
        new_ctf_name = ctf_name
        prev = ''
        while '--' in ctf_name:
            for i, c in enumerate(ctf_name):
                if c == prev and c == '-':
                    new_ctf_name = ctf_name[:i] + ctf_name[i+1:]
                prev = c
            ctf_name = new_ctf_name
        
        await ctx.guild.create_text_channel(name=ctf_name, category=category)
        server = teamdb[str(ctx.guild.id)]
        await ctx.guild.create_role(name=ctf_name, mentionable=True)         
        ctf_info = {'name': ctf_name, "text_channel": ctf_name}
        server.update({'name': ctf_name}, {"$set": ctf_info}, upsert=True)
        # Give a visual confirmation of completion.
        await ctx.message.add_reaction("✅")
    
    @commands.bot_has_permissions(manage_channels=True, manage_roles=True)
    @commands.has_permissions(manage_channels=True)
    @ctf.command()
    @in_ctf_channel()
    async def delete(self, ctx):
        # Delete role from server, delete entry from db
        try:
            role = discord.utils.get(ctx.guild.roles, name=str(ctx.message.channel))
            await role.delete()
            await ctx.send(f"`{role.name}` role deleted")
        except: # role most likely already deleted with archive
            pass
        teamdb[str(ctx.guild.id)].remove({'name': str(ctx.message.channel)})
        await ctx.send(f"`{str(ctx.message.channel)}` deleted from db")
    
    @commands.bot_has_permissions(manage_channels=True, manage_roles=True)
    @commands.has_permissions(manage_channels=True)
    @ctf.command(aliases=["over"])
    @in_ctf_channel()
    async def archive(self, ctx):
        # Delete the role, and move the ctf channel to either the default category (Archive) or whatever has been configured.
        role = discord.utils.get(ctx.guild.roles, name=str(ctx.message.channel))
        await role.delete()
        await ctx.send(f"`{role.name}` role deleted, archiving channel.")
        try:
            sconf = serverdb[str(ctx.guild.id) + '-CONF']
            servarchive = sconf.find_one({'name': "archive_category_name"})['archive_category']
        except:
            servarchive = "ARCHIVE" # default

        category = discord.utils.get(ctx.guild.categories, name=servarchive)
        if category == None: # Checks if category exists, if it doesn't it will create it.
            await ctx.guild.create_category(name=servarchive)
            category = discord.utils.get(ctx.guild.categories, name=servarchive)
        await ctx.message.channel.edit(syncpermissoins=True, category=category)
        
    @ctf.command()
    @in_ctf_channel()
    async def end(self, ctx):
        # This command is deprecated, but due to getting so many DMs from people who didn't use >help, I've decided to just have this as my solution.
        await ctx.send("You can now use either `>ctf delete` (which will delete all data), or `>ctf archive/over` \
which will move the channel and delete the role, but retain challenge info(`>config archive_category \
\"archive category\"` to specify where to archive.")
    
    @commands.bot_has_permissions(manage_roles=True)
    @ctf.command()
    @in_ctf_channel()
    async def join(self, ctx):
        # Give the user the role of whatever ctf channel they're currently in.
        role = discord.utils.get(ctx.guild.roles, name=str(ctx.message.channel))
        user = ctx.message.author
        await user.add_roles(role)
        await ctx.send(f"{user} has joined the {str(ctx.message.channel)} team!")
    
    @commands.bot_has_permissions(manage_roles=True)
    @ctf.command()
    @in_ctf_channel()
    async def leave(self, ctx):
        # Remove from the user the role of the ctf channel they're currently in.
        role = discord.utils.get(ctx.guild.roles, name=str(ctx.message.channel))
        user = ctx.message.author
        await user.remove_roles(role)
        await ctx.send(f"{user} has left the {str(ctx.message.channel)} team.")
    
    @ctf.group(aliases=["chal", "chall", "challenges"])
    @in_ctf_channel()
    async def challenge(self, ctx):
        pass
    
    @staticmethod
    def updateChallenge(ctx, name, status):
        # Update the db with a new challenge and its status
        server = teamdb[str(ctx.guild.id)]
        whitelist = set(string.ascii_letters+string.digits+' '+'-'+'!'+'#'+'_'+'['+']'+'('+')'+'?'+'@'+'+'+'<'+'>')
        challenge = {strip_string(str(name), whitelist): status}
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

    
    @challenge.command(aliases=["a"])
    @in_ctf_channel()
    async def add(self, ctx, name):
        CTF.updateChallenge(ctx, name, 'Unsolved')
        await ctx.send(f"`{name}` has been added to the challenge list for `{str(ctx.message.channel)}`")
    
    @challenge.command(aliases=['s', 'solve'])
    @in_ctf_channel()
    async def solved(self, ctx, name):
        solve = f"Solved - {str(ctx.message.author)}"
        CTF.updateChallenge(ctx, name, solve)
        await ctx.send(f":triangular_flag_on_post: `{name}` has been solved by `{str(ctx.message.author)}`")
    
    @challenge.command(aliases=['w'])
    @in_ctf_channel()
    async def working(self, ctx, name):
        work = f"Working - {str(ctx.message.author)}"
        CTF.updateChallenge(ctx, name, work)
        await ctx.send(f"`{str(ctx.message.author)}` is working on `{name}`!")
    
    @challenge.command(aliases=['r', 'delete', 'd'])
    @in_ctf_channel()
    async def remove(self, ctx, name):
        # Typos can happen (remove a ctf challenge from the list)
        ctf = teamdb[str(ctx.guild.id)].find_one({'name': str(ctx.message.channel)})
        challenges = ctf['challenges']
        whitelist = set(string.ascii_letters+string.digits+' '+'-'+'!'+'#'+'_'+'['+']'+'('+')'+'?'+'@'+'+'+'<'+'>')
        name = strip_string(name, whitelist)
        challenges.pop(name, None)
        ctf_info = {'name': str(ctx.message.channel),
        'challenges': challenges
        }
        teamdb[str(ctx.guild.id)].update({'name': str(ctx.message.channel)}, {"$set": ctf_info}, upsert=True)
        await ctx.send(f"Removed `{name}`")
    
    @challenge.command(aliases=['get', 'ctfd'])
    @in_ctf_channel()
    async def pull(self, ctx, url):
        # Pull challenges from a ctf hosted on the CTFd platform
        try:
            try:
                # Get the credentials from the pinned message
                pinned = await ctx.message.channel.pins()
                user_pass = CTF.get_creds(pinned)
            except CredentialsNotFound as cnfm:
                await ctx.send(cnfm)
            ctfd_challs = getChallenges(url, user_pass[0], user_pass[1])
            ctf = teamdb[str(ctx.guild.id)].find_one({'name': str(ctx.message.channel)})
            try: # If there are existing challenges already...
                challenges = ctf['challenges']
                challenges.update(ctfd_challs)
            except:
                challenges = ctfd_challs
            ctf_info = {'name': str(ctx.message.channel),
            'challenges': challenges
            }
            teamdb[str(ctx.guild.id)].update({'name': str(ctx.message.channel)}, {"$set": ctf_info}, upsert=True)
            await ctx.message.add_reaction("✅")
        except InvalidProvider as ipm:
            await ctx.send(ipm)
        except InvalidCredentials as icm:
            await ctx.send(icm)
        except NonceNotFound as nnfm:
            await ctx.send(nnfm)
        except requests.exceptions.MissingSchema:
            await ctx.send("Supply a valid url in the form: `http(s)://ctfd.url`")
        except:
            traceback.print_exc()

    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @ctf.command(aliases=['login'])
    @in_ctf_channel()
    async def setcreds(self, ctx, username, password):
        # Creates a pinned message with the credntials supplied by the user
        pinned = await ctx.message.channel.pins()
        for pin in pinned:
            if "CTF credentials set." in pin.content:
                # Look for previously pinned credntials, and remove them if they exist.
                await pin.unpin()
        msg = await ctx.send(f"CTF credentials set. name:{username} password:{password}")
        await msg.pin()
    
    @commands.bot_has_permissions(manage_messages=True)
    @ctf.command(aliases=['getcreds'])
    @in_ctf_channel()
    async def creds(self, ctx):
        # Send a message with the credntials
        pinned = await ctx.message.channel.pins()
        try:
            user_pass = CTF.get_creds(pinned)
            await ctx.send(f"name:`{user_pass[0]}` password:`{user_pass[1]}`")
        except CredentialsNotFound as cnfm:
            await ctx.send(cnfm)

    @staticmethod
    def get_creds(pinned):
        for pin in pinned:
            if "CTF credentials set." in pin.content:
                user_pass = pin.content.split("name:")[1].split(" password:")
                return user_pass
        raise CredentialsNotFound("Set credentials with `>ctf setcreds \"username\" \"password\"`")

    @staticmethod
    def gen_page(challengelist):
        # Function for generating each page (message) for the list of challenges in a ctf.
        challenge_page = ""
        challenge_pages = []
        for c in challengelist:
            # Discord message sizes cannot exceed 2000 characters.
            # This will create a new message every 2k characters.
            if not len(challenge_page + c) >= 1989:
                challenge_page += c
                if c == challengelist[-1]: # if it is the last item
                    challenge_pages.append(challenge_page)
            
            elif len(challenge_page + c) >= 1989:
                challenge_pages.append(challenge_page)
                challenge_page = ""
                challenge_page += c

        # print(challenge_pages)
        return challenge_pages

    @challenge.command(aliases=['ls', 'l'])
    @in_ctf_channel()
    async def list(self, ctx):
        # list the challenges in the current ctf.
        ctf_challenge_list = []
        server = teamdb[str(ctx.guild.id)]
        ctf = server.find_one({'name': str(ctx.message.channel)})
        try:
            ctf_challenge_list = []
            for k, v in ctf['challenges'].items():
                challenge = f"[{k}]: {v}\n"
                ctf_challenge_list.append(challenge)
            
            for page in CTF.gen_page(ctf_challenge_list):
                await ctx.send(f"```ini\n{page}```")
                # ```ini``` makes things in '[]' blue which looks nice :)
        except KeyError as e: # If nothing has been added to the challenges list
            await ctx.send("Add some challenges with `>ctf challenge add \"challenge name\"`")
        except:
            traceback.print_exc()

def setup(bot):
    bot.add_cog(CTF(bot))