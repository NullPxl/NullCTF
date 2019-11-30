import asyncio
import random
from colorama import Back, Fore, Style
import sys
import os
import discord
from discord.ext.commands import Bot
from discord.ext import commands
import help_info
import auth

#Auth is set up like so:
#auth_token = 'DISCORD TOKEN'
#conn = "mongodb+srv://MONGODBUSER:PASSWORD@YOURCLUSTER.mongodb.net"



client = discord.Client()
bot = commands.Bot(command_prefix='>')
extensions = ['encoding_decoding', 'cipher', 'ctfs', 'utility']
bot.remove_command('help')
blacklisted = []
cool_names = ['nullpxl', 'Yiggles', 'JohnHammond', 'voidUpdate', 'Michel Ney', 'theKidOfArcrania', 'l14ck3r0x01', 'hasu', 'KFBI'] 
# This is intended to be able to be circumvented.
# If you do something like report a bug with the report command (OR GITHUB), e.g, >report "a bug", you might be added to the list!


# TODO: ok so I was/am an idiot and kind of forgot that I was calling the updateDb function every time ctftime current, timeleft, and countdown are called...  so I should probably fix that.

# https://github.com/Rapptz/discord.py/blob/master/examples/background_task.py

@bot.event
async def on_ready():
    print(('<' + bot.user.name) + ' Online>')
    print(f"discord.py {discord.__version__}\n")
    await bot.change_presence(activity=discord.Game(name='>help / >report "issue"'))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Invalid command passed.  Use >help")
    else:
        await ctx.send(f"There was an error, sorry!\nIf you think this should be fixed, report it with >report \"what happened\"")
    
    print(Style.BRIGHT + Fore.RED + f"Error occured with: {ctx.command}\n{error}\n")
    print(Style.RESET_ALL)

@bot.event
async def on_message(message):
    if 'who should I subscribe to?' in message.content:
        choice = random.randint(1, 2)
        
        if choice == 1:
            await message.channel.send('https://youtube.com/nullpxl')
        
        if choice == 2:
            await message.channel.send('https://www.youtube.com/user/RootOfTheNull')
    
    await bot.process_commands(message)

# Sends the github link.
@bot.command()
async def source(ctx):
    await ctx.send(help_info.src)

@bot.command()
async def help(ctx, page=None):
    
    if page == 'ctftime':
        emb = discord.Embed(description=help_info.ctftime_help, colour=4387968)
        emb.set_author(name='CTFTime Help')
    elif page == 'ctf':
        emb = discord.Embed(description=help_info.ctf_help, colour=4387968)
        emb.set_author(name='CTF Help')
    elif page == 'utility':
        emb = discord.Embed(description=help_info.utility_help, colour=4387968)
        emb.set_author(name='Utilities Help')
    
    else:
        emb = discord.Embed(description=help_info.help_page, colour=4387968)
        emb.set_author(name='NullCTF Help')
    
    await ctx.channel.send(embed=emb)

# Bot sends a dm to creator with the name of the user and their request.
@bot.command()
async def request(ctx, feature):
    creator = await bot.fetch_user(230827776637272064)
    authors_name = str(ctx.author)
    await creator.send(f''':pencil: {authors_name}: {feature}''')
    await ctx.send(f''':pencil: Thanks, "{feature}" has been requested!''')

# Bot sends a dm to creator with the name of the user and their report.
@bot.command()
async def report(ctx, error_report):
    creator = await bot.fetch_user(230827776637272064)
    authors_name = str(ctx.author)
    await creator.send(f''':triangular_flag_on_post: {authors_name}: {error_report}''')
    await ctx.send(f''':triangular_flag_on_post: Thanks for the help, "{error_report}" has been reported!''')

# @bot.command()
# async def creator(ctx):
#     await ctx.send(creator_info)

@bot.command()
async def amicool(ctx):
    authors_name = str(ctx.author)
    
    if any((name in authors_name for name in cool_names)):
        await ctx.send('You are very cool')
    else:
        await ctx.send('lolno')
        await ctx.send('Psst, kid.  Want to be cool?  Find an issue and report it or request a feature you think would be cool.')

if __name__ == '__main__':
    sys.path.insert(1, os.getcwd() + '/cogs/')
    for extension in extensions:
        bot.load_extension(extension)
    bot.run(auth.auth_token)