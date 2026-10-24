from typing import NotRequired, TypedDict, Union, Unpack

import discord
from discord.ext import commands

Context = commands.Context[commands.Bot | commands.AutoShardedBot]
PartialMessageableChannel = Union[
    discord.TextChannel,
    discord.VoiceChannel,
    discord.StageChannel,
    discord.Thread,
    discord.DMChannel,
    discord.PartialMessageable,
]
MessageableChannel = Union[PartialMessageableChannel, discord.GroupChannel]


class DurationT(TypedDict):
    hours: int
    days: int


class EventT(TypedDict):
    title: str
    start: str
    finish: str
    duration: DurationT
    url: str
    logo: str
    format: str
    onsite: bool


class FieldDataT(TypedDict):
    name: str
    value_raw: NotRequired[list[str]]
    inline: NotRequired[bool]
    joiner: NotRequired[str]


class FieldData:
    name: str
    value_raw: list[str]
    inline: bool
    joiner: str

    def __init__(self, **kwargs: Unpack[FieldDataT]) -> None:
        self.name = kwargs["name"]
        self.value_raw = kwargs.get("value_raw", [])
        self.inline = kwargs.get("inline", True)
        self.joiner = kwargs.get("joiner", "\n\n")

    @property
    def value(self) -> str:
        return self.joiner.join(self.value_raw)

    def __iter__(self):
        self.idx = 0
        return self

    def __next__(self):
        if self.idx < len(self.value_raw):
            self.idx += 1
            return FieldData(
                **{
                    "name": self.name,
                    "value_raw": [self.value_raw[self.idx - 1]],
                    "inline": self.inline,
                    "joiner": self.joiner,
                }
            )
        raise StopIteration

    def is_same(self, other: "FieldData"):
        return (
            self.name == other.name
            and self.inline == other.inline
            and self.joiner == other.joiner
        )

    def __len__(self):
        return len(self.name) + len(self.value)

    def __add__(self, other: "FieldData"):
        if not self.is_same(other):
            raise ValueError("Fields are not the same")
        return FieldData(
            name=self.name,
            value_raw=self.value_raw + other.value_raw,
            inline=self.inline,
            joiner=self.joiner,
        )


class EmbedDataT(TypedDict):
    title: str
    description: NotRequired[str]
    color: NotRequired[discord.Color]
    fields: NotRequired[list[FieldDataT]]


class EmbedData:
    title: str
    description: str
    color: discord.Color
    fields: list[FieldData] = []

    def __init__(
        self,
        **kwargs: Unpack[EmbedDataT],
    ):
        self.title = kwargs["title"]
        self.description = kwargs.get("description", "")
        self.color = kwargs.get("color", discord.Color.blue())
        self.fields = [FieldData(**field) for field in kwargs.get("fields", [])]

    def __len__(self):
        return (
            len(self.title)
            + len(self.description)
            + sum(len(field) for field in self.fields)
        )
