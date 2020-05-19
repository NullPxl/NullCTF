import discord
from discord.ext.commands import Bot
from discord.ext import commands

import help_info
import config_vars

client = discord.Client()
bot = commands.Bot(command_prefix=">")
bot.remove_command('help')

extensions = ['ctf', 'ctftime', 'configuration', 'encoding', 'cipher', 'utility']
cool_names = ['nullpxl', 'Yiggles', 'JohnHammond', 'voidUpdate', 'Michel Ney', 'theKidOfArcrania', 'l14ck3r0x01', 'hasu', 'KFBI', 'mrFu', 'warlock_rootx', 'd347h4ck'] 

@bot.event
async def on_ready():
    print(f"{bot.user.name} - Online")
    print(f"discord.py {discord.__version__}\n")
    print("-------------------------------")

    await bot.change_presence(activity=discord.Game(name=">help | >report \"x\""))

@bot.command()
async def help(ctx, page=None):
    
    if page == 'ctftime':
        emb = discord.Embed(description=help_info.ctftime_help, colour=4387968)
        emb.set_author(name='CTFTime Help')
    elif page == 'ctf':
        emb = discord.Embed(description=help_info.ctf_help, colour=4387968)
        emb.set_author(name='CTF Help')
    elif page == 'config':
        emb = discord.Embed(description=help_info.config_help, colour=4387968)
        emb.set_author(name='Configuration Help')
    elif page == 'utility':
        emb = discord.Embed(description=help_info.utility_help, colour=4387968)
        emb.set_author(name='Utilities Help')
    
    else:
        emb = discord.Embed(description=help_info.help_page, colour=4387968)
        emb.set_author(name='NullCTF Help')
    
    await ctx.channel.send(embed=emb)

@bot.command()
async def source(ctx):
    await ctx.send(help_info.src)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing a required argument.  Do >help")
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the appropriate permissions to run this command.")
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send("I don't have sufficient permissions!")
    else:
        print("error not caught")
        print(error)

@bot.command()
async def request(ctx, feature):
    # Bot sends a dm to creator with the name of the user and their request.
    creator = await bot.fetch_user(230827776637272064)
    authors_name = str(ctx.author)
    await creator.send(f''':pencil: {authors_name}: {feature}''')
    await ctx.send(f''':pencil: Thanks, "{feature}" has been requested!''')

@bot.command()
async def report(ctx, error_report):
    # Bot sends a dm to creator with the name of the user and their report.
    creator = await bot.fetch_user(230827776637272064)
    authors_name = str(ctx.author)
    await creator.send(f''':triangular_flag_on_post: {authors_name}: {error_report}''')
    await ctx.send(f''':triangular_flag_on_post: Thanks for the help, "{error_report}" has been reported!''')

@bot.command()
async def amicool(ctx):
    authors_name = str(ctx.author).split("#")[0]
    if authors_name in cool_names:
        await ctx.send('You are very cool :]')
    else:
        await ctx.send('lolno')
        await ctx.send('Psst, kid.  Want to be cool?  Find an issue and report it or request a feature!')

if __name__ == '__main__':
    for extension in extensions:
        bot.load_extension('cogs.' + extension)
    bot.run(config_vars.discord_token)