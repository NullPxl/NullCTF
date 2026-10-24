import os
import subprocess
import traceback
from time import time

import discord
from colorama import Fore, Style
from discord.ext import commands

import cogs
import config_vars
from common import Context

intents = discord.Intents.none()
intents.guilds = True
intents.guild_messages = True
intents.guild_reactions = True
intents.message_content = True
intents.dm_messages = True

bot = commands.Bot(
    command_prefix=config_vars.COMMAND_PREFIX,
    allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False),
    intents=intents,
)
# The default help command is removed so a custom one can be added.

# List of names reserved for those who gave cool ideas or reported something interesting.
# please don't spam me asking to be added.  if you send something interesting to me i will add you to the list.
# If your name is in the list and you use the command '>amicool' you'll get a nice message.
cool_names = [
    "thefireskull",
    "Seadyot",
    "iHeyHey",
    "Inryatt"
]
# This is intended to be circumvented; the idea being that people will change their names to people in this list just so >amicool works for them, and I think that's funny.


def get_git_hash() -> str:
    # Captured at startup so the version command reports the commit the bot is
    # actually running, even if the repo on disk is pulled forward afterwards.
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        return "unknown"  # not running from a git checkout (e.g. Docker)


RUNNING_COMMIT = get_git_hash()


@bot.command()
async def prefix(ctx: Context | None, prefix: str):
    """
    Change the command prefix of the bot.

    Parameters
    ----------
    prefix : str
        The new command prefix.
    """
    bot.command_prefix = prefix

    if ctx:
        await ctx.send(f"Prefix set to `{prefix}`!")

    await bot.change_presence(
        activity=discord.Game(name=f"")
    )

@bot.command()
async def amicool(ctx: Context):
    """
    For the truth.
    """
    authors_name = str(ctx.author).split("#")[0]
    if authors_name in cool_names:
        await ctx.send("You are very cool :]")
    else:
        await ctx.send("lolno")


@bot.command()
async def version(ctx: Context):
    """
    Show the git commit the bot is currently running.
    """
    authors_name = str(ctx.author).split("#")[0]
    if authors_name not in cool_names:
        await ctx.send("lolno")
        return
    await ctx.send(f"Running commit: `{RUNNING_COMMIT[:12]}`")


@bot.command()
@commands.has_permissions(manage_guild=True)
@commands.is_owner() # Uncomment this line if you want to restrict this command.
async def reload(ctx: Context, extension: str | None = None):
    """
    Reload a cog.

    Parameters
    ----------
    extension : str
        The name of the cog to reload.
    """
    if extension is None:
        for extension in cogs.default:
            try:
                if bot.extensions.get("cogs." + extension):
                    await bot.reload_extension("cogs." + extension)
                    await ctx.send(f"Reloaded {extension}!")
                else:
                    await ctx.send(f"Cog {extension} not loaded, skipping...")
            except Exception as e:
                await ctx.send(f"Failed to reload {extension}: {e}")
        return
    try:
        await bot.reload_extension("cogs." + extension)
        await ctx.send(f"Reloaded {extension}!")
    except Exception as e:
        await ctx.send(f"Failed to reload {extension}: {e}")


@bot.command()
@commands.has_permissions(manage_guild=True)
@commands.is_owner() # Uncomment this line if you want to restrict this command.
async def unload(ctx: Context, extension: str):
    """
    Unload a cog.

    Parameters
    ----------
    extension : str
        The name of the cog to unload.
    """
    try:
        await bot.unload_extension("cogs." + extension)
        await ctx.send(f"Unloaded {extension}!")
    except Exception as e:
        await ctx.send(f"Failed to unload {extension}: {e}")


@bot.command()
@commands.has_permissions(manage_guild=True)
@commands.is_owner() # Uncomment this line if you want to restrict this command.
async def load(ctx: Context, extension: str):
    """
    Load a cog.

    Parameters
    ----------
    extension : str
        The name of the cog to load.
    """
    try:
        await bot.load_extension("cogs." + extension)
        await ctx.send(f"Loaded {extension}!")
    except Exception as e:
        await ctx.send(f"Failed to load {extension}: {e}")


@bot.command(description="test command", hidden=True)
async def test(ctx: Context):
    """
    Command to debug the bot.
    """
    await ctx.send("Test command works!")
    print(bot.cogs.keys())
    print([com for com in bot.all_commands.keys() if not bot.all_commands[com].cog])
    print([com for com in bot.all_commands.keys() if bot.all_commands[com].cog])


@bot.event
async def on_ready():
    print(f"{bot.user.name if bot.user else 'Discord Bot'} - Online")
    print(f"discord.py {discord.__version__}\n")

    await prefix.callback(  # pyright: ignore[reportCallIssue]
        None,  # pyright: ignore[reportArgumentType]
        config_vars.COMMAND_PREFIX,
    )

    success: list[str] = []
    failed: list[str] = []
    for extension in cogs.default:
        try:
            await bot.load_extension("cogs." + extension)
            success.append(extension)
        except Exception as e:
            print(f"Failed to load {extension}: {e}")
            failed.append(extension)

    print(Fore.GREEN, end="")
    print("Loaded cogs: " + ", ".join(success) if success else "None")
    print(Fore.RED, end="")
    print("Failed cogs: " + ", ".join(failed) if failed else "None")
    print(Style.RESET_ALL, end="")
    print("-------------------------------\n")


@bot.event
async def on_command_error(ctx: Context, error: commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing a required argument.  Do >help")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "You do not have the appropriate permissions to run this command."
        )
    elif isinstance(error, commands.MissingRole):
        await ctx.send(
            "You do not have the required role to run this command."
        )
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("I don't have sufficient permissions!")
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send("This command cannot be used in private messages.")
    else:
        code = hex(int(time()))
        await ctx.send(
            f"An unexpected error occurred. Please contact @thefireskull"
        )
        print(f"[{code}] Uncaught Error: " + str(error))
        traceback.print_exception(type(error), error, error.__traceback__)


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    await bot.process_commands(message)


if __name__ == "__main__":
    bot.run(config_vars.DISCORD_TOKEN)
