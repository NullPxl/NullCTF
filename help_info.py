import requests
import re
import random
from string import *

help_page = '''


`>ctftime <upcoming/top/current> <number/year>`
return info on a number of upcoming ctfs, leaderboards from a certain year, or currently running ctfs from ctftime.org

`>ctf <create/challenge/join/leave/timeleft> <channel_name/[add/solved/list/working]>`
create a channel and role for a ctf name of your choosing (in a catagory labeled CTF), and commands for collaboration.  ctf challenge add, adds a challenge to a list of challenges, solved marks a challenge as solved, working allows you to tell others in your server what challenge you're working on by adding your name to the list, which shows all of this info! (and more!)

`>rot <message> <direction(optional, will default to left)>`
return all 25 different possible combinations for the popular caesar cipher - use quotes for messages more than 1 word

`>magicb <filetype>`
return the magicbytes/file header of a supplied filetype.

`>b64 <encode/decode> <message>`
encode or decode in base64 - if message has spaces use quotations

`>binary <encode/decode> <message>`
encode or decode in binary - if message has spaces use quotations

`>hex <encode/decode> <message>`
encode or decode in hex - if message has spaces use quotations

`>url <encode/decode> <message>`
encode or decode based on url encoding - if message has spaces use quotations

`>reverse <message>`
reverse the supplied string - if message has spaces use quotations

`>counteach <message>`
count the occurences of each character in the supplied message - if message has spaces use quotations

`>clear <amount of messages>`
clear the supplied amount of messages in the current channel

`>characters <message>`
count the amount of characters in your supplied message

`>wordcount <phrase>`
count the amount of words in your supplied message

**page: 1/2 - (>help 1)**
'''
help_page_2 = '''

`>atbash <message>`
encode or decode in the atbash cipher - if message has spaces use quotations (encode/decode do the same thing)

`>calc <expression>`
evaluate a math expression (put it in quotations)

`>htb`
return the latest tweet from @hackthebox_eu that says when the next box will be released

`>github <user>`
get a direct link to a github profile page with your supplied user

`>twitter <user>`
get a direct link to a twitter profile page with your supplied user

`>cointoss`
get a 50/50 cointoss to make all your life's decisions

`>amicool`
for the truth

`>report <"an issue">`
report an issue you found with the bot, if it is helpful your name will be added to the 'cool names' list!

**page: 2/2 - (>help 2)** ; more commands and documentation viewable on the github page (>source)
'''

src = "https://github.com/NullPxl/NullSig"
creator_info = "https://youtube.com/nullpxl\nhttps://github.com/nullpxl\nhttps://twitter.com/nullpxl"