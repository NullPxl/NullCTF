# ![enter image description here](https://i.imgur.com/mZ2bVY4.png)

>## *A [discord.py](http://discordpy.readthedocs.io/en/latest/) bot focused on providing CTF tools for collaboration in Discord servers (ctftime.org commands, team setup + ctfd integration, utilites, etc)!  If you have a feature request, make it a GitHub issue.*

[Invite to your server](https://discord.com/api/oauth2/authorize?client_id=982358072611721246&permissions=268561520&scope=bot)

## Please let me know if there's any issues with the link! This is one of multiple alternate instances because the original is over the 100 server limit Discord imposes for non-verified bots ([verification requirements](https://support.discordapp.com/hc/en-us/articles/360040720412-Bot-Verification-and-Data-Whitelisting))

\
[Join the support server](https://discord.gg/yf8E2s8)

## How to Use

*If you ever forget a command, use `>help`!  The default prefix is `>`, and can be changed with the `COMMAND_PREFIX` setting in the `.env` file (or at runtime with the `prefix` command).*

After inviting to your server, it is recommended that you first configure the categories you want active and archived CTF channels to go into.

* When you create a ctf, it will by default go into the "CTF" category (it will create one if it is not present), and when you archive a ctf it will go into the ARCHIVE category.
* You can configure this with `>config ctf_category "Category for CTFs"` and `>config archive_category "Category for Archived CTFs"`
* The commands for managing CTFs live under the `ctf` group (e.g. `>ctf create`). If you prefer a different name for your instance (e.g. your club's acronym), set `CTF_COMMAND_NAME` in the `.env` file and the group will be renamed accordingly.
* Who may manage CTFs is controlled by roles: `MEMBER_ROLE` can create and archive, `ADMIN_ROLE` can also delete and skip the creation rate limit. Set both in the `.env` file. When unset, the bot falls back to Discord permissions (manage channels for members, administrator for admins), so a fresh instance works without any role setup.

---

## CTF Commands

The following commands are the ones you will most likely want to pay attention to, although if you do not expect to use this bot to manage CTFs you can skip this category and go down to CTFTime commands.

* `>ctf create "ctf name"`  This is the command you'll use when you want to begin a new CTF.  This command will make a text channel with your supplied name under the designated CTF category. *Requires the member role (or the manage channels permission by default); limited to one channel per hour, admins are exempt*
![ctf create](https://i.imgur.com/6PUPIX3.png)

*NOTE: the following ctf specific commands will only be accepted under the channel created for that ctf.  This is to avoid clashes with multiple ctfs going on in the same server.*

* `>ctf join/leave` Using this command will either give or remove the role of a created ctf to/from you.
 ![ctf join/leave](https://i.imgur.com/R1ktkMv.png)

* `>ctf challenge add/working/solved/remove "challenge"` Allows users to add or remove challenges to a list, and then set the status of that challenge. *Use quotations*

* `>ctf challenge list` This is the list command that was previously mentioned, it displays the added challenges, who's working on what, and if a challenge is solved (and by who).
 ![desc](https://i.imgur.com/l9jsuLz.png)

  > NOTE: There is shorthand!  challenge -> chal/chall, add -> a, working -> w, solved -> s, remove -> r

* `>ctf challenge pull "http(s)://ctfd.url"` Pull challenges and their solved states from a CTFd hosted CTF, and add them to your challenges list.  Requires the username and password to be set with `>ctf setcreds "username" "password"`

* `>ctf setcreds "ctfd username" "password"` Pin the message of ctf credentials, can be fetched by the bot later in order to use `>ctf challenge pull`.  Credentials are never stored outside of Discord.
![ctf pull and setcreds](https://i.imgur.com/Z3e0pE3.png)

* `>ctf creds` Gets the credentials from the pinned message.

> *IMPORTANT: credentials are never stored outside of the pinned message on Discord. They are needed to pull challenge data and solve state from the CTFd platform.*

* `>ctf archive` Move the CTF channel into the Archive category.  *Requires the member role (or the manage channels permission by default)*

* `>ctf delete` Delete the CTF info from the database, and delete the role. *Requires the admin role (or the administrator permission by default)*

---

## [CTFtime](https://ctftime.org) Commands

* `>ctftime countdown/timeleft` Countdown will return when a selected CTF starts, and timeleft will return when any currently running CTFs end in the form of days hours minutes and seconds.
 ![enter image description here](https://i.imgur.com/LFSTr33.png)  
 ![enter image description here](https://i.imgur.com/AkBfp6E.png)

* `>ctftime upcoming <number>` Uses the api mentioned to return an embed of the supplied number of upcoming CTFs.  If no number is provided the default is 3.
![enter image description here](https://i.imgur.com/UpouneO.png)

* `>ctftime current` Displays any currently running CTFs in the same embed as previously mentioned.
![enter image description here](https://i.imgur.com/RCh3xg6.png)

* `>ctftime top <year>`  Shows the ctftime leaderboards from a certain year *(dates back to 2011)*.
![enter image description here](https://i.imgur.com/jdPWmCV.png)

---

## Utility Commands

* `>help` Returns the help page

* `>amicool` Are you cool?

* `>version` Shows the git commit the bot is currently running. *Only works for names on the cool list*

* `>twitter <user>` / `>github <user>` Get a direct link to a Twitter/GitHub profile.

* `>magicb filetype` Returns the mime and magicbytes of your supplied filetype. Useful for stegonography challenges where a filetype is corrupt.

* `>rot  "a message"` Returns all 25 possible rotations for a message.

* `>b64 encode/decode "message"`  Encode or decode in base64 *(at the time of writing this, if there are any unprintable characters this command will not work, this goes for all encoding/decoding commands).*

* `>b32 encode/decode "message"` Encode or decode in base32

* `>binary encode/decode "message"` Encode or decode in binary.

* `>hex encode/decode "message"` Encode or decode in hex.

* `>url encode/decode "message"` Encode or decode with url parse.  This could be used for generating XSS payloads.

* `>reverse "message"` Reverse a message.

* `>counteach "message"` Count the occurrences of each character in the supplied message.

* `>characters "message"` Count the amount of characters in your message.

* `>wordcount a test` Counts the amount of words in  your message (don't use quotations).

* `>cointoss` Get a 50/50 cointoss to make all your life's decisions.

### Have a feature request?  Make a GitHub issue

## Setup - General Overview

---

* This may be necessary in the future because of Disord's recent [verification requirements](https://support.discordapp.com/hc/en-us/articles/360040720412-Bot-Verification-and-Data-Whitelisting) for bots in over 100 servers (which this bot is already over).  This rule, which will disallow users to invite bots that have not been verified by the owner (which requires photoid) will be enforced starting october 7th.

1. Clone the repository you are working with.
1. Install dependencies with `pip install -r requirements.txt`
1. Run the bot once with 'python nullctf.py' to generate the `.env` file.
1. Go to the Discord Developer Portal and create a new bot.
1. After creating the bot, navigate to the bot settings and copy the bot token into the `.env` file.
1. Create a new MongoDB account.
1. In your MongoDB account, create a new project.
1. Within the project, create a new cluster.
1. Create a new database user within the cluster.
1. Add your IP address to the database whitelist for access.
1. Connect to the cluster, and when prompted, select Python as the driver.
1. Obtain the connection string provided by MongoDB and follow the steps provided, inputting your password when required.
1. Copy the connection string into the `.env` file.

1. Build the project with Docker using the command `docker build`.
    * Note: You may need to set `pymongo==3.10.1` or a similar version in the `requirements.txt` file.
1. Invite the bot to your server. You can do this by going to the bot settings page on the Discord Developer Portal and generating an invite link.

### Configuration (`.env`)

The `.env` file is not committed to the repository, since it holds secrets. The bot creates it (with empty values) on first run; fill in the following:

| Variable | Required | Default | Description |
|---|---|---|---|
| `DISCORD_TOKEN` | yes | — | Your bot token from the Discord Developer Portal. |
| `MONGODB_CONNECTION` | yes | — | Connection string for your MongoDB cluster. |
| `CTF_COMMAND_NAME` | no | `ctf` | Name of the command group for managing CTFs |
| `COMMAND_PREFIX` | no | `>` | The prefix used for commands. |
| `MEMBER_ROLE` | no | *permission fallback* | Role allowed to create and archive CTFs. When unset, anyone who can manage channels may. |
| `ADMIN_ROLE` | no | *permission fallback* | Role allowed to delete CTFs and skip the creation rate limit. When unset, anyone with the administrator permission may. |

Example:

```
DISCORD_TOKEN="your-bot-token"
MONGODB_CONNECTION="mongodb+srv://user:password@cluster/?retryWrites=true&w=majority"
COMMAND_PREFIX=">"
CTF_COMMAND_NAME="ctf"
MEMBER_ROLE=""
ADMIN_ROLE=""
```

Settings are read once at startup, so restart the bot after changing them.
