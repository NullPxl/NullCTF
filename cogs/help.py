from typing import Any, Generator, Mapping

import discord
from discord.ext import commands

type _Command = commands.Command[Any, ..., Any]
type _Mapping = Mapping[commands.Cog | None, list[_Command]]
type _Group = commands.Group[Any, ..., Any]

from common import Context, EmbedData, FieldData, MessageableChannel


class PaginationView(discord.ui.View):
    _cur_page_idx: int = 0

    def __init__(
        self,
        data: EmbedData,
        ctx: Context,
        channnel: MessageableChannel,
        max_fields: int = 2,
        field_txt_lim: int = 1024,
        total_txt_lim: int = 6000,
    ):
        super().__init__()
        self.ctx = ctx
        self.channnel = channnel
        pages: list[EmbedData] = []

        def trav_data(data: EmbedData) -> Generator[FieldData, bool | None, None]:
            for field in data.fields:
                for value in field:
                    while not (yield value):
                        pass

        data_gen = trav_data(data)
        acc: FieldData | None = None
        while True:
            page = EmbedData(title=data.title)
            if len(pages) == 0:
                page.description = data.description
            for _ in range(max_fields):
                page_len = len(page)
                acc = next(data_gen, None)
                if acc is None:
                    break
                try:
                    while True:
                        curr = data_gen.send(True)
                        if not acc.is_same(curr):
                            break
                        sm = acc + curr
                        sm_len = len(sm)
                        if (
                            page_len + sm_len > total_txt_lim
                            or len(sm.value) > field_txt_lim
                        ):
                            break
                        acc = sm
                except StopIteration:
                    pass
                page.fields.append(acc)

            pages.append(page)
            if next(data_gen, None) is None:
                break

        self._pages = list(map(lambda x: self.create_embed(x), pages))

    async def send(self):
        match (len(self._pages)):
            case 0:
                return
            case 1:
                await self.channnel.send(embed=self._pages[0])
            case _:
                self.update_buttons()
                self.message = await self.channnel.send(
                    embed=self._pages[self._cur_page_idx], view=self
                )

    async def update_message(self):
        self.update_buttons()
        await self.message.edit(embed=self._pages[self._cur_page_idx], view=self)

    def create_embed(self, page: EmbedData):
        emb = discord.Embed(
            title=page.title,
            description=page.description,
            color=page.color,
        )
        for field in page.fields:
            emb.add_field(
                name=field.name,
                value=field.value,
                inline=field.inline,
            )
        if self.ctx.bot.user and self.ctx.bot.user.avatar:
            emb.set_thumbnail(url=f"{self.ctx.bot.user.avatar.url}")
        return emb

    def update_buttons(self):
        if self._cur_page_idx == 0:
            self.first_page_button.disabled = True
            self.prev_button.disabled = True
            self.first_page_button.style = discord.ButtonStyle.gray
            self.prev_button.style = discord.ButtonStyle.gray
        else:
            self.first_page_button.disabled = False
            self.prev_button.disabled = False
            self.first_page_button.style = discord.ButtonStyle.green
            self.prev_button.style = discord.ButtonStyle.primary

        if self._cur_page_idx == len(self._pages) - 1:
            self.next_button.disabled = True
            self.last_page_button.disabled = True
            self.last_page_button.style = discord.ButtonStyle.gray
            self.next_button.style = discord.ButtonStyle.gray
        else:
            self.next_button.disabled = False
            self.last_page_button.disabled = False
            self.last_page_button.style = discord.ButtonStyle.green
            self.next_button.style = discord.ButtonStyle.primary

    @discord.ui.button(label="|<", style=discord.ButtonStyle.green)
    async def first_page_button(self, interaction: discord.Interaction, _):
        await interaction.response.defer()
        self._cur_page_idx = 1

        await self.update_message()

    @discord.ui.button(label="<", style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction: discord.Interaction, _):
        await interaction.response.defer()
        self._cur_page_idx -= 1
        await self.update_message()

    @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, _):
        await interaction.response.defer()
        self._cur_page_idx += 1
        await self.update_message()

    @discord.ui.button(label=">|", style=discord.ButtonStyle.green)
    async def last_page_button(self, interaction: discord.Interaction, _):
        await interaction.response.defer()
        self._cur_page_idx = len(self._pages) - 1
        await self.update_message()


class Help(commands.HelpCommand):
    def __init__(self):
        super().__init__(
            command_attrs={
                "help": "Get more info/aliases/param types about a command/category.",
                "hidden": True,
            },
            verify_checks=False,
        )

    async def command_callback(
        self,
        ctx: Context,
        /,
        *,
        command: str | None = commands.parameter(
            default=None,
            description="The command to get more info about.",
            displayed_name="command/category",
        ),
    ):
        """
        The callback for the help command.

        Parameters
        ----------
        command : str | None
            The command or category to get more info about.
        """
        await super().command_callback(ctx, command=command)

    async def send_bot_help(self, mapping: _Mapping):
        """
        Sends the help message for the bot.

        Parameters
        ----------
        mapping : Mapping[commands.Cog | None, list[commands.Command]]
            A mapping of cogs to their commands.
        """
        ctx = self.context
        category = [
            f"**{cog.qualified_name}**\n" f"{cog.description}" for cog in mapping if cog
        ]
        filtered = await self.filter_commands(mapping[None])
        commands = [
            f"`{self.get_command_signature(command)}`\n{command.short_doc}"
            for command in filter(
                lambda x: x in filtered, ctx.bot.all_commands.values()
            )
        ]
        data = EmbedData(
            **{
                "title": "Help",
                "description": f"`{self.get_command_signature(self._command_impl)}`\n{self._command_impl.help}\n\n",
                "color": discord.Color.blue(),
                "fields": [
                    {
                        "name": "Categories",
                        "value_raw": category,
                    },
                    {
                        "name": "Commands",
                        "value_raw": commands,
                    },
                ],
            }
        )
        await PaginationView(data, ctx, self.get_destination()).send()

    async def send_cog_help(self, cog: commands.Cog):
        """
        Sends the help message for a specific cog.

        Parameters
        ----------
        cog : commands.Cog
            The cog to get help for.
        """
        ctx = self.context
        filtered = await self.filter_commands(cog.walk_commands())
        commands = [
            f"`{self.get_command_signature(command)}`\n{command.short_doc}"
            for command in filtered
        ]
        data = EmbedData(
            **{
                "title": f"{cog.qualified_name} Category",
                "description": cog.description,
                "fields": [
                    {
                        "name": "Commands",
                        "value_raw": commands,
                    },
                ],
            }
        )

        await PaginationView(data, ctx, self.get_destination(), max_fields=1).send()

    async def send_group_help(self, group: _Group):
        """
        Sends the help message for a specific group.

        Parameters
        ----------
        group : commands.Group
            The group to get help for.
        """
        ctx = self.context
        usage = [f"`{self.get_command_signature(group)}`"]

        parameters = [
            f"`{self.get_parameter_type_str(param)}`\n"
            f"{param.description if param.description else 'No description'}"
            for param in group.params.values()
        ]
        if not parameters:
            parameters = ["No parameters"]

        aliases = [f"`{alias}`" for alias in group.aliases]
        if not aliases:
            aliases = ["No aliases"]

        description = "\n\n".join(
            [
                group.help if group.help else "No description",
                "**Usage**\n" + "\n\n".join(usage),
                "**Parameters**\n" + "\n\n".join(parameters),
                "**Aliases**\n" + ", ".join(aliases),
            ]
        )

        filtered = await self.filter_commands(group.walk_commands())
        subcommands = [
            f"`{self.get_command_signature(command)}`\n{command.short_doc}"
            for command in filtered
        ]

        data = EmbedData(
            **{
                "title": f"`{group.qualified_name}` Command Group",
                "description": description,
                "fields": [
                    {
                        "name": "Subcommands",
                        "value_raw": subcommands,
                    },
                ],
            }
        )

        await PaginationView(data, ctx, self.get_destination(), max_fields=1).send()

    async def send_command_help(self, command: _Command):
        """
        Sends the help message for a specific command.

        Parameters
        ----------
        command : commands.Command
            The command to get help for.
        """
        ctx = self.context

        usage = [f"`{self.get_command_signature(command)}`"]

        parameters = [
            f"`{self.get_parameter_type_str(param)}`\n"
            f"{param.description if param.description else 'No description'}"
            for param in command.params.values()
        ]
        if not parameters:
            parameters = ["No parameters"]

        aliases = [f"`{alias}`" for alias in command.aliases]
        if not aliases:
            aliases = ["No aliases"]

        description = "\n\n".join(
            [
                command.help if command.help else "No description",
                "**Usage**\n" + "\n\n".join(usage),
                "**Parameters**\n" + "\n\n".join(parameters),
                "**Aliases**\n" + ", ".join(aliases),
            ]
        )

        data = EmbedData(
            **{
                "title": f"`{command.qualified_name}` Command",
                "description": description,
            }
        )

        await PaginationView(data, ctx, self.get_destination()).send()

    @staticmethod
    def get_parameter_type_str(param: commands.Parameter):
        """
        Returns a string representation of the parameter type.

        Parameters
        ----------
        param : commands.Parameter
            The parameter to get the string representation of."""
        return (param.displayed_name or param.name) + ":" + str(param).split(":")[1]

    def get_command_signature(self, command: _Command):
        """
        Returns the command signature.

        Parameters
        ----------
        command : commands.Command
            The command to get the signature of.
        """
        return super().get_command_signature(command).strip()


class _Bot(commands.Bot):
    old_help_command: commands.HelpCommand | None


async def setup(bot: _Bot):
    bot.old_help_command = bot.help_command
    bot.help_command = Help()


async def teardown(bot: _Bot):
    bot.help_command = bot.old_help_command
