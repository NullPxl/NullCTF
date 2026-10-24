import base64
import binascii
import collections
import string
import urllib.parse
from typing import Literal

from discord.ext import commands

from common import Context

# Encoding/Decoding from various schemes.

# TODO: l14ck3r0x01: ROT47 , base32 encoding

type opTypes = Literal["encode", "decode"]

class Encoding(commands.Cog):
    """
    Various encoding/decoding and cipher commands.
    """

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    async def cog_command_error(self, ctx: Context, error: Exception):
        await ctx.send("There was an error with the data :[")

    @commands.command()
    async def b64(
        self, ctx: Context, opMode: opTypes, string: str
    ):
        """
        Encode or decode in base64 - if message has spaces use quotations

        Parameters
        ----------
        opMode : "encode" | "decode"
            encode or decode
        string : str
            The string to encode or decode
        """
        byted_str = str.encode(string)

        if opMode == "decode":
            decoded = base64.b64decode(byted_str).decode("utf-8")
            await ctx.send(decoded)

        if opMode == "encode":
            encoded = base64.b64encode(byted_str).decode("utf-8").replace("\n", "")
            await ctx.send(encoded)

    @commands.command()
    async def b32(
        self, ctx: Context, opMode: opTypes, string: str
    ):
        """
        Encode or decode in base32 - if message has spaces use quotations

        Parameters
        ----------
        opMode : "encode" | "decode"
            encode or decode
        string : str
            The string to encode or decode
        """
        byted_str = str.encode(string)

        if opMode == "decode":
            decoded = base64.b32decode(byted_str).decode("utf-8")
            await ctx.send(decoded)

        if opMode == "encode":
            encoded = base64.b32encode(byted_str).decode("utf-8").replace("\n", "")
            await ctx.send(encoded)

    @commands.command()
    async def binary(
        self, ctx: Context, opMode: opTypes, string: str
    ):
        """
        Encode or decode in binary - if message has spaces use quotations

        Parameters
        ----------
        opMode : "encode" | "decode"
            encode or decode
        string : str
            The string to encode or decode
        """
        if opMode == "decode":
            string = string.replace(" ", "")
            data = int(string, 2)
            decoded = data.to_bytes((data.bit_length() + 7) // 8, "big").decode()
            await ctx.send(decoded)

        if opMode == "encode":
            encoded = bin(int.from_bytes(string.encode(), "big")).replace("b", "")
            await ctx.send(encoded)

    @commands.command()
    async def hex(
        self, ctx: Context, opMode: opTypes, string: str
    ):
        """
        Encode or decode in hex - if message has spaces use quotations

        Parameters
        ----------
        opMode : "encode" | "decode"
            encode or decode
        string : str
            The string to encode or decode
        """
        if opMode == "decode":
            string = string.replace(" ", "")
            decoded = binascii.unhexlify(string).decode("ascii")
            await ctx.send(decoded)

        if opMode == "encode":
            byted = string.encode()
            encoded = binascii.hexlify(byted).decode("ascii")
            await ctx.send(encoded)

    @commands.command()
    async def url(
        self, ctx: Context, opMode: opTypes, message: str
    ):
        """
        Encode or decode based on url encoding - if message has spaces use quotations

        Parameters
        ----------
        opMode : "encode" | "decode"
            encode or decode
        message : str
            The message to encode or decode
        """
        if opMode == "decode":

            if "%20" in message:
                message = message.replace("%20", "(space)")
                await ctx.send(urllib.parse.unquote(message))
            else:
                await ctx.send(urllib.parse.unquote(message))

        if opMode == "encode":
            await ctx.send(urllib.parse.quote(message))

    @commands.command()
    async def rot(self, ctx: Context, message: str):
        """
        Eeturn all 25 different possible combinations for the popular caesar cipher - use quotes for messages more than 1 word

        Parameters
        ----------
        message : str
            The message to rotate
        """
        allrot = ""

        for i in range(0, 26):
            upper = collections.deque(string.ascii_uppercase)
            lower = collections.deque(string.ascii_lowercase)

            upper.rotate((-i))
            lower.rotate((-i))

            upper = "".join(list(upper))
            lower = "".join(list(lower))
            translated = message.translate(
                str.maketrans(string.ascii_uppercase, upper)
            ).translate(str.maketrans(string.ascii_lowercase, lower))
            allrot += "{}: {}\n".format(i, translated)

        await ctx.send(f"```{allrot}```")

    @commands.command()
    async def atbash(self, ctx: Context, message: str):
        """
        Encode or decode in the atbash cipher - if message has spaces use quotations (encode/decode do the same thing)

        Parameters
        ----------
        message : str
            The message to atbash
        """
        normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        changed = "zyxwvutsrqponmlkjihgfedcbaZYXWVUTSRQPONMLKJIHGFEDCBA"
        trans = str.maketrans(normal, changed)
        atbashed = message.translate(trans)
        await ctx.send(atbashed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Encoding(bot))
