help_page = '''



`>ctftime <upcoming/current> <number>`
return info on a number of upcoming ctfs, or currently running ctfs from ctftime.org (number param is just for upcoming)

`>ctftime <countdown/timeleft>`
return specific times for the time until a ctf begins, or until a currently running ctf ends.

`>ctftime top <year>`
display the leaderboards from ctftime from a certain year.

`>ctf create "<ctf name>"`
create a text channel and role in the CTF category for a ctf (must have permissions to manage channels).

`>ctf challenge <[add/working/solved> "<challenge name>"`
add a ctf challenge to a list of challenges in the ctf, then mark it as solved or being worked on.

`>ctf challenge <list>`
get a list of the challenges in the ctf, and their statuses.

`>ctf <join/leave>`
get or get rid of the ctf role that was created with ctf create.

`>ctf <end>`
delete the role, and entry from the database for the ctf (must have permissions to manage channels).

`>htb`
return the latest tweet from @hackthebox_eu that says when the next box will be released

*next page is utility commands*

**page: 1/2 - (>help 1)**
'''
help_page_2 = '''


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

`>characters <message>`
count the amount of characters in your supplied message

`>wordcount <phrase>`
count the amount of words in your supplied message

`>atbash <message>`
encode or decode in the atbash cipher - if message has spaces use quotations (encode/decode do the same thing)

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

src = "https://github.com/NullPxl/NullCTF"