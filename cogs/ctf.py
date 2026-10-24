import string
import time
import traceback

import discord
import requests
from discord.ext import commands

from common import Context
from config_vars import (
    ADMIN_ROLE,
    COMMAND_PREFIX,
    CTF_COMMAND_NAME,
    MEMBER_ROLE,
    serverdb,
    teamdb,
)

# All commands relating to server specific CTF data
# Credentials provided for pulling challenges from the CTFd platform are NOT stored in the database.
# they are stored in a pinned message in the discord channel.

# Members can create at most one CTF channel per hour; Admins are exempt.
CREATE_COOLDOWN_SECONDS = 60 * 60


def in_ctf_channel():
    async def tocheck(ctx: Context):
        if ctx.guild is None:
            raise commands.NoPrivateMessage

        # A check for ctf context specific commands
        if teamdb[str(ctx.guild.id)].find_one({"name": str(ctx.message.channel)}):
            return True
        else:
            await ctx.send("You must be in a created ctf channel to use ctf commands!")
            return False

    return commands.check(tocheck)


def _has_role(ctx: Context, role_name: str) -> bool:
    return any(role.name == role_name for role in getattr(ctx.author, "roles", []))


def _member_ok(ctx: Context) -> bool:
    if MEMBER_ROLE:
        return _has_role(ctx, MEMBER_ROLE)
    return ctx.author.guild_permissions.manage_channels


def _admin_ok(ctx: Context) -> bool:
    if ADMIN_ROLE:
        return _has_role(ctx, ADMIN_ROLE)
    return ctx.author.guild_permissions.administrator


async def is_member(ctx: Context) -> bool:
    """Check for creating/archiving CTFs: the configured member role, or the
    manage channels permission when no role is configured."""
    if ctx.guild is None:
        raise commands.NoPrivateMessage
    if _member_ok(ctx):
        return True
    if MEMBER_ROLE:
        raise commands.MissingRole(MEMBER_ROLE)
    raise commands.MissingPermissions(["manage_channels"])


async def is_admin(ctx: Context) -> bool:
    """Check for deleting CTFs and skipping the create rate limit: the
    configured admin role, or the administrator permission when no role is
    configured."""
    if ctx.guild is None:
        raise commands.NoPrivateMessage
    if _admin_ok(ctx):
        return True
    if ADMIN_ROLE:
        raise commands.MissingRole(ADMIN_ROLE)
    raise commands.MissingPermissions(["administrator"])


def strip_string(tostrip: str, whitelist: list[str] | set[str]):
    # A string validator to correspond with a provided whitelist.
    stripped = "".join([ch for ch in tostrip if ch in whitelist])
    return stripped.strip()


class InvalidProvider(Exception):
    pass


class InvalidCredentials(Exception):
    pass


class CredentialsNotFound(Exception):
    pass


class NonceNotFound(Exception):
    pass


def getChallenges(url: str, username: str, password: str):
    # Pull challenges from a ctf hosted with the commonly used CTFd platform using provided credentials
    whitelist = set(
        string.ascii_letters
        + string.digits
        + " "
        + "-"
        + "!"
        + "#"
        + "_"
        + "["
        + "]"
        + "("
        + ")"
        + "?"
        + "@"
        + "+"
        + "<"
        + ">"
    )
    fingerprint = "Powered by CTFd"
    s = requests.session()
    if url[-1] == "/":
        url = url[:-1]
    r = s.get(f"{url}/login")
    if fingerprint not in r.text:
        raise InvalidProvider("CTF is not based on CTFd, cannot pull challenges.")
    else:
        # Get the nonce from the login page.
        try:
            nonce = r.text.split("csrfNonce': \"")[1].split('"')[0]
        except:  # sometimes errors happen here, my theory is that it is different versions of CTFd
            try:
                nonce = r.text.split('name="nonce" value="')[1].split('">')[0]
            except:
                raise NonceNotFound(
                    "Was not able to find the nonce token from login, please >report this along with the ctf url."
                )
        # Login with the username, password, and nonce
        r = s.post(
            f"{url}/login",
            data={"name": username, "password": password, "nonce": nonce},
        )
        if "Your username or password is incorrect" in r.text:
            raise InvalidCredentials("Invalid login credentials")
        r_chals = s.get(f"{url}/api/v1/challenges")
        all_challenges = r_chals.json()
        r_solves = s.get(f"{url}/api/v1/teams/me/solves")
        team_solves = r_solves.json()
        if "success" not in team_solves:
            # ctf is user based.  There is a flag on CTFd for this (userMode), but it is not present in all versions, this way seems to be.
            r_solves = s.get(f"{url}/api/v1/users/me/solves")
            team_solves = r_solves.json()

        solves: list[str] = []
        if team_solves["success"] == True:
            for solve in team_solves["data"]:
                cat = solve["challenge"]["category"]
                challname = solve["challenge"]["name"]
                solves.append(f"<{cat}> {challname}")
        challenges: dict[str, str] = {}
        if all_challenges["success"] == True:
            for chal in all_challenges["data"]:
                cat = chal["category"]
                challname = chal["name"]
                name = f"<{cat}> {challname}"
                # print(name)
                # print(strip_string(name, whitelist))
                if name not in solves:
                    challenges.update({strip_string(name, whitelist): "Unsolved"})
                else:
                    challenges.update({strip_string(name, whitelist): "Solved"})
        else:
            raise Exception("Error making request")
        # Returns all the new challenges and their corresponding statuses in a dictionary compatible with the structure that would happen with 'normal' useage.
        return challenges


class CTF(commands.Cog):
    """
    Commands for managing CTFs.
    """

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.last_create: dict[int, float] = {}

    @commands.group(name=CTF_COMMAND_NAME)
    async def ctf(self, ctx: Context):
        """
        Command group for managing CTFs.
        """
        if ctx.invoked_subcommand is None:
            # If the subcommand passed does not exist, its type is None
            commands = list(
                set([f"`{c.qualified_name}`" for c in self.walk_commands()][1:])
            )
            # update this to include params
            await ctx.send(
                f"Unknown command. Possible values: {', '.join(commands)}\n"
                "See `help` for more information."
            )

    @commands.bot_has_permissions(manage_channels=True, manage_roles=True)
    @commands.check(is_member)
    @commands.guild_only()
    @ctf.command(aliases=["new"])
    async def create(self, ctx: Context, name: str):
        """
        create a text channel and role in the CTF category for a ctf (requires the member role or manage channels permission)*

        Limited to one channel per hour; admins are exempt.

        Parameters
        ----------
        name : str
            The name of the ctf.
        """
        if ctx.guild is None:
            raise commands.NoPrivateMessage
        # Rate limit channel creation for members (admins are exempt)
        if not _admin_ok(ctx):
            elapsed = time.monotonic() - self.last_create.get(ctx.author.id, 0.0)
            remaining = CREATE_COOLDOWN_SECONDS - elapsed
            if remaining > 0:
                minutes = int(remaining // 60)
                await ctx.send(
                    f"Rate limit: 1 CTF channel per hour. Try again in {minutes} "
                    "minute(s), or ask an Admin to create it for you."
                )
                return
        # Create a new channel in the CTF category (default='CTF' or configured with the configuration extension)
        try:
            sconf = serverdb[str(ctx.guild.id) + "-CONF"]
            servcatres = sconf.find_one({"name": "category_name"})
            servcat: str = servcatres["ctf_category"] if servcatres else "CTF"
        except:
            servcat = "CTF"

        category = discord.utils.get(ctx.guild.categories, name=servcat)
        if (
            category == None
        ):  # Checks if category exists, if it doesn't it will create it.
            await ctx.guild.create_category(name=servcat)
            category = discord.utils.get(ctx.guild.categories, name=servcat)

        ctf_name = (
            strip_string(name, set(string.ascii_letters + string.digits + " " + "-"))
            .replace(" ", "-")
            .lower()
        )
        if ctf_name[0] == "-":
            # edge case where channel names can't start with a space (but can end in one)
            ctf_name = ctf_name[1:]
        # There cannot be 2 spaces (which are converted to '-') in a row when creating a channel.  This makes sure these are taken out.
        new_ctf_name = ctf_name
        prev = ""
        while "--" in ctf_name:
            for i, c in enumerate(ctf_name):
                if c == prev and c == "-":
                    new_ctf_name = ctf_name[:i] + ctf_name[i + 1 :]
                prev = c
            ctf_name = new_ctf_name

        await ctx.guild.create_text_channel(name=ctf_name, category=category)
        server = teamdb[str(ctx.guild.id)]
        await ctx.guild.create_role(name=ctf_name, mentionable=True)
        ctf_info = {"name": ctf_name, "text_channel": ctf_name}
        server.update_one({"name": ctf_name}, {"$set": ctf_info}, upsert=True)
        # Only count the creation against the rate limit once it actually succeeded
        self.last_create[ctx.author.id] = time.monotonic()
        # Give a visual confirmation of completion.
        await ctx.message.add_reaction("✅")

    @commands.bot_has_permissions(manage_channels=True, manage_roles=True)
    @commands.check(is_admin)
    @ctf.command()
    @in_ctf_channel()
    async def delete(self, ctx: Context):
        """
        Delete the ctf role, and entry from the database for the ctf.

        **Admin only** — members should use `archive` instead.

        __This command will delete all data associated with the ctf.__
        """
        if ctx.guild is None:
            raise commands.NoPrivateMessage
        # Delete role from server, delete entry from db
        try:
            role = discord.utils.get(ctx.guild.roles, name=str(ctx.message.channel))
            if role == None:
                raise commands.RoleNotFound(str(ctx.message.channel))
            await role.delete()
            await ctx.send(f"`{role.name}` role deleted")
        except:  # role most likely already deleted with archive
            pass
        teamdb[str(ctx.guild.id)].delete_one({"name": str(ctx.message.channel)})
        await ctx.send(f"`{str(ctx.message.channel)}` deleted from db")

    @commands.bot_has_permissions(manage_channels=True, manage_roles=True)
    @commands.check(is_member)
    @ctf.command(aliases=["over"])
    @in_ctf_channel()
    async def archive(self, ctx: Context):
        """
        Move the ctf channel to the archive category.
        """
        if ctx.guild is None:
            raise commands.NoPrivateMessage
        # Delete the role, and move the ctf channel to either the default category (Archive) or whatever has been configured.
        role = discord.utils.get(ctx.guild.roles, name=str(ctx.message.channel))
        if role == None:
            raise commands.RoleNotFound(str(ctx.message.channel))
        await role.delete()
        await ctx.send(f"`{role.name}` role deleted, archiving channel.")
        try:
            sconf = serverdb[str(ctx.guild.id) + "-CONF"]
            servarchiveres = sconf.find_one({"name": "archive_category_name"})
            servarchive = (
                servarchiveres["archive_category"] if servarchiveres else "ARCHIVE"
            )
        except:
            servarchive = "ARCHIVE"  # default

        category = discord.utils.get(ctx.guild.categories, name=servarchive)
        await ctx.send(f"Archiving in category: {category}")

        if (
            category == None
        ):  # Checks if category exists, if it doesn't it will create it.
            await ctx.guild.create_category(name=servarchive)
            category = discord.utils.get(ctx.guild.categories, name=servarchive)
        if isinstance(ctx.message.channel, discord.TextChannel):
            await ctx.message.channel.edit(sync_permissions=True, category=category)

    @commands.bot_has_permissions(manage_roles=True)
    @ctf.command()
    @in_ctf_channel()
    async def join(self, ctx: Context):
        """
        Give the user the role of the ctf channel they are in.
        """
        user = ctx.message.author
        if ctx.guild is None or not isinstance(user, discord.Member):
            raise commands.NoPrivateMessage
        # Give the user the role of whatever ctf channel they're currently in.
        role = discord.utils.get(ctx.guild.roles, name=str(ctx.message.channel))
        if role == None:
            raise commands.RoleNotFound(str(ctx.message.channel))
        await user.add_roles(role)
        await ctx.send(f"{user} has joined the {str(ctx.message.channel)} team!")

    @commands.bot_has_permissions(manage_roles=True)
    @ctf.command()
    @in_ctf_channel()
    async def leave(self, ctx: Context):
        """
        Remove the user from the role of the ctf channel they are currently in.
        """
        user = ctx.message.author
        if ctx.guild is None or not isinstance(user, discord.Member):
            raise commands.NoPrivateMessage
        # Remove from the user the role of the ctf channel they're currently in.
        role = discord.utils.get(ctx.guild.roles, name=str(ctx.message.channel))
        if role == None:
            raise commands.RoleNotFound(str(ctx.message.channel))
        await user.remove_roles(role)
        await ctx.send(f"{user} has left the {str(ctx.message.channel)} team.")

    @ctf.group(aliases=["chal", "chall", "challenges"])
    @in_ctf_channel()
    async def challenge(self, ctx: Context):
        """
        Command group for managing challenges in a CTF.
        """
        pass

    @staticmethod
    def updateChallenge(ctx: Context, name: str, status: str):
        if ctx.guild is None:
            raise commands.NoPrivateMessage
        # Update the db with a new challenge and its status
        server = teamdb[str(ctx.guild.id)]
        whitelist = set(
            string.ascii_letters
            + string.digits
            + " "
            + "-"
            + "!"
            + "#"
            + "_"
            + "["
            + "]"
            + "("
            + ")"
            + "?"
            + "@"
            + "+"
            + "<"
            + ">"
        )
        challenge = {strip_string(str(name), whitelist): status}
        ctf_channel = server.find_one({"name": str(ctx.message.channel)})
        try:  # If there are existing challenges already...
            if ctf_channel is None:
                raise KeyError
            challenges: dict[str, str] = ctf_channel["challenges"]
            challenges.update(challenge)
        except:
            challenges = challenge
        ctf_info = {"name": str(ctx.message.channel), "challenges": challenges}
        server.update_one(
            {"name": str(ctx.message.channel)}, {"$set": ctf_info}, upsert=True
        )

    @challenge.command(aliases=["a"])
    @in_ctf_channel()
    async def add(self, ctx: Context, name: str):
        """
        Add a challenge to the challenge list for the ctf channel.

        Parameters
        ----------
        name : str
            The name of the challenge.
        """
        CTF.updateChallenge(ctx, name, "Unsolved")
        await ctx.send(
            f"`{name}` has been added to the challenge list for `{str(ctx.message.channel)}`"
        )

    @challenge.command(aliases=["s", "solve"])
    @in_ctf_channel()
    async def solved(self, ctx: Context, name: str):
        """
        Mark a challenge as solved.

        Parameters
        ----------
        name : str
            The name of the challenge."""
        solve = f"Solved - {str(ctx.message.author)}"
        CTF.updateChallenge(ctx, name, solve)
        await ctx.send(
            f":triangular_flag_on_post: `{name}` has been solved by `{str(ctx.message.author)}`"
        )

    @challenge.command(aliases=["w"])
    @in_ctf_channel()
    async def working(self, ctx: Context, name: str):
        """
        Mark a challenge as being worked on.

        Parameters
        ----------
        name : str
            The name of the challenge.
        """
        work = f"Working - {str(ctx.message.author)}"
        CTF.updateChallenge(ctx, name, work)
        await ctx.send(f"`{str(ctx.message.author)}` is working on `{name}`!")

    @challenge.command(aliases=["r", "delete", "d"])
    @in_ctf_channel()
    async def remove(self, ctx: Context, name: str):
        """
        Remove a challenge from the challenge list.

        Parameters
        ----------
        name : str
            The name of the challenge.
        """
        if ctx.guild is None:
            raise commands.NoPrivateMessage
        # Typos can happen (remove a ctf challenge from the list)
        ctf_channel = teamdb[str(ctx.guild.id)].find_one({"name": str(ctx.message.channel)})
        if ctf_channel is None:
            return
        challenges = ctf_channel["challenges"]
        whitelist = set(
            string.ascii_letters
            + string.digits
            + " "
            + "-"
            + "!"
            + "#"
            + "_"
            + "["
            + "]"
            + "("
            + ")"
            + "?"
            + "@"
            + "+"
            + "<"
            + ">"
        )
        name = strip_string(name, whitelist)
        challenges.pop(name, None)
        ctf_info = {"name": str(ctx.message.channel), "challenges": challenges}
        teamdb[str(ctx.guild.id)].update_one(
            {"name": str(ctx.message.channel)}, {"$set": ctf_info}, upsert=True
        )
        await ctx.send(f"Removed `{name}`")

    @challenge.command(aliases=["get", "ctfd"])
    @in_ctf_channel()
    async def pull(self, ctx: Context, url: str):
        """
        Will add all of the challenges on the provided CTFd CTF.

        This command will include solve state.

        If the website requires login, you must set the credentials first.
        See `setcreds`.

        Parameters
        ----------
        url : str
            The URL of the CTFd CTF.
        """
        if ctx.guild is None:
            raise commands.NoPrivateMessage
        # Pull challenges from a ctf hosted on the CTFd platform
        try:
            try:
                # Get the credentials from the pinned message
                pinned = await ctx.message.channel.pins()
                user_pass = CTF.get_creds(pinned)
            except CredentialsNotFound as cnfm:
                return await ctx.send(str(cnfm))
            ctfd_challs = getChallenges(url, user_pass[0], user_pass[1])
            ctf_channel = teamdb[str(ctx.guild.id)].find_one({"name": str(ctx.message.channel)})
            try:  # If there are existing challenges already...
                if ctf_channel is None:
                    raise KeyError
                challenges: dict[str, str] = ctf_channel["challenges"]
                challenges.update(ctfd_challs)
            except:
                challenges = ctfd_challs
            ctf_info = {"name": str(ctx.message.channel), "challenges": challenges}
            teamdb[str(ctx.guild.id)].update_one(
                {"name": str(ctx.message.channel)}, {"$set": ctf_info}, upsert=True
            )
            await ctx.message.add_reaction("✅")
        except InvalidProvider as ipm:
            await ctx.send(str(ipm))
        except InvalidCredentials as icm:
            await ctx.send(str(icm))
        except NonceNotFound as nnfm:
            await ctx.send(str(nnfm))
        except requests.exceptions.MissingSchema:
            await ctx.send("Supply a valid url in the form: `http(s)://ctfd.url`")
        except:
            traceback.print_exc()

    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @ctf.command(aliases=["login"])
    @in_ctf_channel()
    async def setcreds(self, ctx: Context, username: str, password: str):
        """
        Pin the message of ctf credentials.

        Can be fetched by the bot later in order to use.
        See `creds`.

        Parameters
        ----------
        username : str
            The username for the CTFd platform.
        """
        # Creates a pinned message with the credntials supplied by the user
        pinned = await ctx.message.channel.pins()
        for pin in pinned:
            if "CTF credentials set." in pin.content:
                # Look for previously pinned credntials, and remove them if they exist.
                await pin.unpin()
        msg = await ctx.send(
            f"CTF credentials set. name:{username} password:{password}"
        )
        await msg.pin()

    @commands.bot_has_permissions(manage_messages=True)
    @ctf.command(aliases=["getcreds"])
    @in_ctf_channel()
    async def creds(self, ctx: Context):
        """
        Gets the credentials from the pinned message.

        See `setcreds`.
        """
        # Send a message with the credntials
        pinned = await ctx.message.channel.pins()
        try:
            user_pass = CTF.get_creds(pinned)
            await ctx.send(f"name:`{user_pass[0]}` password:`{user_pass[1]}`")
        except CredentialsNotFound as cnfm:
            await ctx.send(str(cnfm))

    @staticmethod
    def get_creds(pinned: list[discord.Message]):
        for pin in pinned:
            if "CTF credentials set." in pin.content:
                user_pass = pin.content.split("name:")[1].split(" password:")
                return user_pass
        raise CredentialsNotFound(
            f'Set credentials with `{COMMAND_PREFIX}{CTF_COMMAND_NAME} setcreds "username" "password"`'
        )

    @staticmethod
    def gen_page(challengelist: list[str]):
        # Function for generating each page (message) for the list of challenges in a ctf.
        challenge_page = ""
        challenge_pages: list[str] = []
        for c in challengelist:
            # Discord message sizes cannot exceed 2000 characters.
            # This will create a new message every 2k characters.
            if not len(challenge_page + c) >= 1989:
                challenge_page += c
                if c == challengelist[-1]:  # if it is the last item
                    challenge_pages.append(challenge_page)

            elif len(challenge_page + c) >= 1989:
                challenge_pages.append(challenge_page)
                challenge_page = ""
                challenge_page += c

        # print(challenge_pages)
        return challenge_pages

    @challenge.command(aliases=["ls", "l"])
    @in_ctf_channel()
    async def list(self, ctx: Context):
        """
        Get a list of the challenges in the ctf, and their statuses.
        """
        if ctx.guild is None:
            raise commands.NoPrivateMessage
        # list the challenges in the current ctf.
        ctf_challenge_list = []
        server = teamdb[str(ctx.guild.id)]
        ctf_channel = server.find_one({"name": str(ctx.message.channel)})
        try:
            if ctf_channel is None:
                raise KeyError
            ctf_challenge_list: list[str] = []
            for k, v in ctf_channel["challenges"].items():
                challenge = f"[{k}]: {v}\n"
                ctf_challenge_list.append(challenge)

            for page in CTF.gen_page(ctf_challenge_list):
                await ctx.send(f"```ini\n{page}```")
                # ```ini``` makes things in '[]' blue which looks nice :)
        except KeyError as _:  # If nothing has been added to the challenges list
            await ctx.send("Error: No challeges added.")
        except:
            traceback.print_exc()


async def setup(bot: commands.Bot):
    await bot.add_cog(CTF(bot))
