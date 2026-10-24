from datetime import UTC, datetime, timezone

import discord
import requests
from colorama import Fore, Style
from dateutil.parser import isoparse  # pip install python-dateutil
from discord.ext import commands, tasks

from common import Context, EventT
from config_vars import ctfs

# All commands for getting data from ctftime.org (a popular platform for finding CTF events)


class CTFTime(commands.Cog):
    """
    CTFtime commands to show status of CTFs.
    """

    limit = 5

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.upcoming_l = []
        self.updateDB.start()

    async def cog_command_error(self, ctx: Context, error: Exception):
        print(error)

    async def cog_unload(self):
        self.updateDB.cancel()

    @tasks.loop(minutes=30.0, reconnect=True)
    async def updateDB(self):
        # Every 30 minutes, this will grab the 5 closest upcoming CTFs from ctftime.org and update my db with it.
        # I do this because there is no way to get current ctfs from the api, but by logging all upcoming ctfs [cont.]
        # I can tell by looking at the start and end date if it's currently running or not using unix timestamps.
        now = datetime.now(UTC)
        unix_now = int(now.replace(tzinfo=timezone.utc).timestamp())
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0",
        }
        upcoming = "https://ctftime.org/api/v1/events/"
        response = requests.get(upcoming, headers=headers, params={"limit": self.limit})
        jdata: list[EventT] = response.json()

        info: list[EventT] = []
        for num, _ in enumerate(jdata):  # Generate list of dicts of upcoming ctfs
            ctf: EventT = {
                "title": jdata[num]["title"],
                "start": jdata[num]["start"],
                "finish": jdata[num]["finish"],
                "duration": jdata[num]["duration"],
                "url": jdata[num]["url"],
                "logo": jdata[num]["logo"],
                "format": jdata[num]["format"],
                "onsite": jdata[num]["onsite"],
            }
            info.append(ctf)

        got_ctfs: list[str] = []
        for (
            ctf
        ) in info:  # If the document doesn't exist: add it, if it does: update it.
            ctfs.update_one({"title": ctf["title"]}, {"$set": ctf}, upsert=True)
            got_ctfs.append(ctf["title"])
        print(
            Fore.WHITE
            + f"{datetime.now()}: "
            + Fore.GREEN
            + f"Got and updated {got_ctfs}"
        )
        print(Style.RESET_ALL)

        # Delete ctfs that are over from the db
        for ctf in ctfs.find():
            if isoparse(ctf["finish"]).timestamp() < unix_now:
                ctfs.delete_one({"title": ctf["title"]})

    @updateDB.before_loop
    async def before_updateDB(self):
        await self.bot.wait_until_ready()

    @commands.group()
    async def ctftime(self, ctx: Context):
        """
        Command group for getting data from ctftime.org.
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

    @ctftime.command(aliases=["now", "running"])
    async def current(self, ctx: Context):
        """
        return info on the currently running ctfs on ctftime.org
        """
        now = datetime.now(UTC)
        unix_now = int(now.replace(tzinfo=timezone.utc).timestamp())
        running = False

        for ctf in ctfs.find():
            # Check if the ctf is running
            if (
                isoparse(ctf["start"]).timestamp() < unix_now
                and isoparse(ctf["finish"]).timestamp() > unix_now
            ):
                running = True
                embed = discord.Embed(
                    title=":red_circle: " + ctf["title"] + " IS LIVE",
                    description=ctf["url"],
                    color=15874645,
                )
                start = f"<t:{int(isoparse(ctf['start']).timestamp())}:F>"
                end = f"<t:{int(isoparse(ctf['finish']).timestamp())}:F>"
                if ctf["logo"] != "":
                    embed.set_thumbnail(url=ctf["logo"])
                else:
                    embed.set_thumbnail(
                        url="https://pbs.twimg.com/profile_images/2189766987/ctftime-logo-avatar_400x400.png"
                    )
                    # CTFtime logo
                dur = (
                    f"{ctf['duration']['days']} days, {ctf['duration']['hours']} hours"
                )
                embed.add_field(name="Duration", value=dur, inline=True)
                embed.add_field(name="Format", value=ctf["format"], inline=True)
                embed.add_field(
                    name="Timeframe", value=start + " -> " + end, inline=True
                )
                await ctx.channel.send(embed=embed)

        if running == False:  # No ctfs were found to be running
            await ctx.send(
                "No CTFs currently running! Check out >ctftime countdown, and >ctftime upcoming to see when ctfs will start!"
            )

    @ctftime.command(aliases=["next"])
    async def upcoming(self, ctx: Context, amount: int | None = None):
        """
        return info on a number of upcoming ctfs from ctftime.org

        Parameters
        ----------
        amount : int
            The number of upcoming ctfs to return
        """
        if not amount:
            amount = 3
        else:
            amount = int(amount)
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0",
        }
        upcoming_ep = "https://ctftime.org/api/v1/events/"
        default_image = "https://pbs.twimg.com/profile_images/2189766987/ctftime-logo-avatar_400x400.png"
        r = requests.get(upcoming_ep, headers=headers, params={"limit": amount})
        # print("made request")

        upcoming_data: list[EventT] = r.json()
        # print("HERE")

        for ctf in range(0, int(amount)):
            ctf_title = upcoming_data[ctf]["title"]
            start = f"<t:{int(isoparse(upcoming_data[ctf]['start']).timestamp())}:F>"
            end = f"<t:{int(isoparse(upcoming_data[ctf]['finish']).timestamp())}:F>"
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

            embed = discord.Embed(
                title=ctf_title, description=ctf_link, color=int("f23a55", 16)
            )
            if ctf_image != "":
                embed.set_thumbnail(url=ctf_image)
            else:
                embed.set_thumbnail(url=default_image)

            embed.add_field(
                name="Duration",
                value=((ctf_days + " days, ") + ctf_hours) + " hours",
                inline=True,
            )
            embed.add_field(
                name="Format", value=(ctf_place + " ") + ctf_format, inline=True
            )
            embed.add_field(name="Timeframe", value=(start + " -> ") + end, inline=True)
            await ctx.channel.send(embed=embed)

    @ctftime.command(aliases=["leaderboard"])
    async def top(self, ctx: Context, year: str | None = None):
        """
        display the leaderboards from ctftime from a certain year.

        Parameters
        ----------
        year : str
            The year to get the leaderboards for
        """
        if not year:
            # Default to current year
            year = str(datetime.today().year)
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0",
        }
        top_ep = f"https://ctftime.org/api/v1/top/{year}/"
        leaderboards = ""
        r = requests.get(top_ep, headers=headers)
        if r.status_code != 200:
            await ctx.send(
                'Error retrieving data, please report this with `>report "what happened"`'
            )
        else:
            try:
                top_data = (r.json())[year]
                for team in range(10):
                    # Leaderboard is always top 10 so we can just assume this for ease of formatting
                    rank = team + 1
                    teamname = top_data[team]["team_name"]
                    score = str(round(top_data[team]["points"], 4))

                    if team != 9:
                        # This is literally just for formatting.  I'm sure there's a better way to do it but I couldn't think of one :(
                        # If you know of a better way to do this, do a pull request or msg me and I'll add  your name to the cool list
                        leaderboards += f"\n[{rank}]    {teamname}: {score}"
                    else:
                        leaderboards += f"\n[{rank}]   {teamname}: {score}\n"

                await ctx.send(
                    f":triangular_flag_on_post:  **{year} CTFtime Leaderboards**```ini\n{leaderboards}```"
                )
            except KeyError as _:
                await ctx.send("Please supply a valid year.")
                # LOG THIS

    @ctftime.command()
    async def timeleft(self, ctx: Context):
        """
        return relative time until a currently running ctf ends.
        """
        now = datetime.now(UTC)
        unix_now = int(now.replace(tzinfo=timezone.utc).timestamp())
        running = False
        for ctf in ctfs.find():
            # Check if the ctf is running
            if (
                isoparse(ctf["start"]).timestamp() < unix_now
                and isoparse(ctf["finish"]).timestamp() > unix_now
            ):
                running = True
                time = isoparse(ctf["finish"]).timestamp() - unix_now
                days = time // (24 * 3600)
                time = time % (24 * 3600)
                hours = time // 3600
                time %= 3600
                minutes = time // 60
                time %= 60
                seconds = time
                await ctx.send(
                    f"```ini\n{ctf['title']} ends in: [{days} days], [{hours} hours], [{minutes} minutes], [{seconds} seconds]```\n{ctf['url']}"
                )

        if running == False:
            await ctx.send(
                "No ctfs are running! Use >ctftime upcoming or >ctftime countdown to see upcoming ctfs"
            )

    @ctftime.command()
    async def countdown(self, ctx: Context, params: int | None = None):
        """
        return specific times for the time until a ctf begins.

        Parameters
        ----------
        params : int
            The number of the ctf to get the countdown for
        """
        now = datetime.now(UTC)
        unix_now = int(now.replace(tzinfo=timezone.utc).timestamp())

        if params == None:
            self.upcoming_l: list[EventT] = []
            index = ""
            for ctf in ctfs.find():
                if isoparse(ctf["start"]).timestamp() > unix_now:
                    # if the ctf start time is in the future...
                    self.upcoming_l.append(ctf)
            for i, c in enumerate(self.upcoming_l):
                index += f"\n[{i + 1}] {c['title']}\n"

            await ctx.send(
                f"Type >ctftime countdown <number> to select.\n```ini\n{index}```"
            )
        else:
            if self.upcoming_l != []:
                x = int(params) - 1

                time = isoparse(self.upcoming_l[x]["start"]).timestamp() - unix_now
                days = time // (24 * 3600)
                time = time % (24 * 3600)
                hours = time // 3600
                time %= 3600
                minutes = time // 60
                time %= 60
                seconds = time

                await ctx.send(
                    f"```ini\n{self.upcoming_l[x]['title']} starts in: [{days} days], [{hours} hours], [{minutes} minutes], [{seconds} seconds]```\n{self.upcoming_l[x]['url']}"
                )
            else:  # TODO: make this a function, too much repeated code here.
                for ctf in ctfs.find():
                    if isoparse(ctf["start"]).timestamp() > unix_now:
                        self.upcoming_l.append(ctf)
                x = int(params) - 1

                time = isoparse(self.upcoming_l[x]["start"]).timestamp() - unix_now
                days = time // (24 * 3600)
                time = time % (24 * 3600)
                hours = time // 3600
                time %= 3600
                minutes = time // 60
                time %= 60
                seconds = time

                await ctx.send(
                    f"```ini\n{self.upcoming_l[x]['title']} starts in: [{days} days], [{hours} hours], [{minutes} minutes], [{seconds} seconds]```\n{self.upcoming_l[x]['url']}"
                )


async def setup(bot: commands.Bot):
    await bot.add_cog(CTFTime(bot))
