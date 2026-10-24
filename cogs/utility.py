import json
import random

from discord.ext import commands

from common import Context

# This can be thought of as a miscellaneous category (anything 'utility' based.)


class Utility(commands.Cog):
    """
    A list of helpful commands.
    """

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.command(aliases=["char"])
    async def characters(self, ctx: Context, string: str):
        """
        Count the number of characters in your supplied message

        Parameters
        ----------
        string : str
            The string to count characters in
        """
        await ctx.send(str(len(string)))

    @commands.command(aliases=["wc"])
    async def wordcount(self, ctx: Context, *args: str):
        """
        Count the number of words in your supplied message

        Parameters
        ----------
        args : str
            The words to count
        """
        await ctx.send(str(len(args)))

    @commands.command(aliases=["rev"])
    async def reverse(self, ctx: Context, message: str):
        """
        Reverse the supplied string - if message has spaces use quotations

        Parameters
        ----------
        message : str
            The string to reverse
        """
        await ctx.send(message[::(-1)])

    @commands.command()
    async def counteach(self, ctx: Context, message: str):
        """
        Count the occurences of each character in the supplied message - if message has spaces use quotations

        Parameters
        ----------
        message : str
            The string to count characters in
        """
        count: dict[str, int] = {}

        for char in message:
            if char in count.keys():
                count[char] += 1
            else:
                count[char] = 1

        await ctx.send(str(count))

    @commands.command(aliases=["head"])
    async def magicb(self, ctx: Context, filetype: str):
        """
        Return the magicbytes/file header of a supplied filetype.

        Parameters
        ----------
        filetype : str
            The filetype to get the magic bytes of
        """
        file = open("magic.json").read()
        alldata = json.loads(file)
        try:
            messy_signs = str(alldata[filetype]["signs"])
            signs = (
                messy_signs.split("[")[1].split(",")[0].split("]")[0].replace("'", "")
            )
            filetype = alldata[filetype]["mime"]
            await ctx.send(f"""{filetype}: {signs}""")
        except:  # if the filetype is not in magicb.json...
            await ctx.send(
                f"{filetype} not found :(  If you think this filetype should be included please do `>request 'magicb {filetype}'`"
            )

    @commands.command()
    async def twitter(self, ctx: Context, twituser: str):
        """
        Get a direct link to a twitter profile page with your supplied user

        Parameters
        ----------
        twituser : str
            The twitter user to get a link to
        """
        await ctx.send("https://twitter.com/" + twituser)

    @commands.command()
    async def github(self, ctx: Context, gituser: str):
        """
        Get a direct link to a github profile page with your supplied user

        Parameters
        ----------
        gituser : str
            The github user to get a link to
        """
        await ctx.send("https://github.com/" + gituser)

    @commands.command(aliases=["5050", "flip"])
    async def cointoss(self, ctx: Context):
        """
        Get a 50/50 cointoss to make all your life's decisions
        """
        choice = random.randint(1, 2)

        if choice == 1:
            await ctx.send("heads")

        if choice == 2:
            await ctx.send("tails")


async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))
