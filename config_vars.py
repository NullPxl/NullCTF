import os
from typing import Any, Dict

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection

from common import EventT

load_dotenv()

SRC_URL = "https://github.com/NullPxl/NullCTF"

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
MONGODB_CONNECTION = os.getenv("MONGODB_CONNECTION", "")
if DISCORD_TOKEN == "" and MONGODB_CONNECTION == "":
    with open(".env", "w") as f:
        f.write('DISCORD_TOKEN=""\n')
        f.write('MONGODB_CONNECTION=""\n')
    print("Please set the DISCORD_TOKEN and MONGODB_CONNECTION in the .env file")
    raise ValueError("DISCORD_TOKEN or MONGODB_CONNECTION not set")


# The command prefix (e.g. `>ctf create`). Set COMMAND_PREFIX in .env to
# change it for your instance.
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", ">")

# Name of the command group used to manage CTFs (e.g. `<ctf create`).
# Set CTF_COMMAND_NAME in .env to rename it for your instance (e.g. an acronym).
CTF_COMMAND_NAME = os.getenv("CTF_COMMAND_NAME", "ctf")

# Roles allowed to manage CTFs. When unset, permissions are used instead:
# manage channels for members, administrator for admins.
MEMBER_ROLE = os.getenv("MEMBER_ROLE", "")
ADMIN_ROLE = os.getenv("ADMIN_ROLE", "")


client: MongoClient[Dict[str, Any]] = MongoClient(MONGODB_CONNECTION)

ctfdb = client["ctftime"]  # Create ctftime database
ctfs: Collection[EventT] = ctfdb[
    "ctfs"
]  # pyright: ignore[reportAssignmentType] | Create ctfs collection

teamdb = client["ctfteams"]  # Create ctf teams database

serverdb = client["serverinfo"]  # configuration db
