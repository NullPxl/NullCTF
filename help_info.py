ctftime_help = '''
`>ctftime upcoming [1-5]`
return info on a number of upcoming ctfs from ctftime.org

`>ctftime current`
return info on the currently running ctfs on ctftime.org

`>ctftime [countdown/timeleft]`
return specific times for the time until a ctf begins, or until a currently running ctf ends

`>ctftime top [year]`
display the leaderboards from ctftime from a certain year
'''

ctf_help = '''
`>ctf create "CTF NAME"`
create a text channel and role in the CTF category for a ctf (must have permissions to manage channels)*

`>ctf challenge [add/working/solved/remove] "challenge name"`
add a ctf challenge to a list of challenges in the ctf, then mark it as solved or being worked on.  Shorthand: challenge -> chal/chall, add -> a, working -> w, solved -> s, remove -> r

`>ctf challenge list`
get a list of the challenges in the ctf, and their statuses

`>ctf [join/leave]`
give the user the role of the ctf channel they are in

`>ctf end`
delete the ctf role, and entry from the database for the ctf (must have permissions to manage channels)*
'''

utility_help = '''

`>magicb [filetype]`
return the magicbytes/file header of a supplied filetype.

`>htb`
returns the latest tweet from @hackthebox_eu that says when the next box will be released

`>rot "message"`
return all 25 different possible combinations for the popular caesar cipher - use quotes for messages more than 1 word

`>b64 [encode/decode] "message"`
encode or decode in base64 - if message has spaces use quotations

`>binary [encode/decode] "message"`
encode or decode in binary - if message has spaces use quotations

`>hex [encode/decode] "message"`
encode or decode in hex - if message has spaces use quotations

`>url [encode/decode] "message"`
encode or decode based on url encoding - if message has spaces use quotations

`>reverse "message"`
reverse the supplied string - if message has spaces use quotations

`>counteach "message"`
count the occurences of each character in the supplied message - if message has spaces use quotations

`>characters "message"`
count the amount of characters in your supplied message

`>wordcount "phrase"`
count the amount of words in your supplied message

`>atbash "message"`
encode or decode in the atbash cipher - if message has spaces use quotations (encode/decode do the same thing)

`>github [user]`
get a direct link to a github profile page with your supplied user

`>twitter [user]`
get a direct link to a twitter profile page with your supplied user

`>cointoss`
get a 50/50 cointoss to make all your life's decisions

`>amicool`
for the truth.


'''


help_page = '''

`>help ctftime`
info for all ctftime commands

`>help ctf`
info for all ctf commands

`>help utility`
everything else! (basically misc)

`>report/request "an issue or feature"`
report an issue, or request a feature for NullCTF, if it is helpful your name will be added to the 'cool names' list!

'''


src = "https://github.com/NullPxl/NullCTF"