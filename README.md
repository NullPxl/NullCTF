<img src="https://raw.githubusercontent.com/NullPxl/NullCTF/master/graphics/nullctf_github_banner.png" width ="700" height="130"/>

>### *A [discord.py](http://discordpy.readthedocs.io/en/latest/) bot focused on providing easy to use, basic CTF tools for collaboration in Discord servers!  If you have a feature request, make it a GitHub issue or use the >request "x" command while the bot is online.*
>#### This 'tutorial' should ideally be read by everyone who uses the bot, but if you are the server owner *please* read this.

#  How to Use
>This bot has a ton of commands for encoding/decoding, ciphers, and more commonly used ctf tools.  But, the main use for NullCTF is to easily set up a CTF for your discord server.  The following commands listed are most likely to be used the most.

* `>ctf create "ctf name"`  This is the command you'll use when you want to begin a new CTF.  This command will make a text channel with your supplied name under the category 'CTF'.  *Only available to server owners*

 * `>ctf join/leave` Using this command will either give or remove the role of the previously created CTF to/from you. 
 ![enter image description here](https://i.imgur.com/4QPUgvM.png)
 
 * `>ctf challenge add/working/solved "challenge name"` These commands are one of the most important parts of this bot, it allows your users to add a challenge to a list, add your discord username next to the challenge (so other users can see who's working on what challenge), and allow other users to see which challenges have been solved without leaving the discord chat.
 
 * `>ctf challenge list` This is the list command that was previously mentioned, it displays the added challenges, who's working on what, and if a challenge is solved.
 ![enter image description here](https://i.imgur.com/KH5dYZr.png)
 
 * `>ctf countdown/timeleft` Countdown will return when a selected CTF starts, and timeleft will return when any currently running CTFs end in the form of days hours minutes and seconds.
 ![enter image description here](https://i.imgur.com/PpGMZTh.png)  
 ![enter image description here](https://i.imgur.com/gp7sBJG.png)
---
>The following commands use the api from [ctftime](https://ctftime.org/)

* `>ctftime upcoming <number>` Uses the api mentioned to return an embed up to 5 upcoming CTFs.  If no number is provided the default is 3.
![enter image description here](https://i.imgur.com/UpouneO.png)

* `>ctftime current` Displays any currently running CTFs in the same embed as previously mentioned.
![enter image description here](https://i.imgur.com/RCh3xg6.png)

* `>ctftime top <year>`  Shows the ctftime leaderboards from a certain year *(dates back to 2011)*.
![enter image description here](https://i.imgur.com/2npW7gM.png)
---
>Utility commands
* `>magicb filetype` Returns the mime and magicbytes of your supplied filetype. Useful for stegonography challenges where a filetype is corrupt.

* `>rot  "a message" <right/left>` Returns all 25 possible rotations for a message with an optional direction (defaults to left).

* `>b64 encode/decode "message"`  Encode or decode in base64 *(at the time of writing this, if there are any unprintable characters this command will not work, this goes for all encoding/decoding commands).*

* `>binary encode/decode "message"` Encode or decode in binary.

* `>hex encode/decode "message"` Encode or decode in hex.

* `>url encode/decode "message"` Encode or decode with url parse.  This could be used for generating XSS payloads.

* `>reverse "message"` Reverse a message.

* `>counteach "message"` Count the occurrences of each character in the supplied message.

* `>clear amount` Clear the supplied amount of messages in the current channel.

* `>characters "message"` Count the amount of characters in your message.

* `>wordcount a test` Counts the amount of words in  your message (don't use quotations).

* `>calc "expression"` Evaluate a math expression.

* `>htb` Return when the next hackthebox machine is going live from @hackthebox_eu on twitter.

* `>cointoss` Get a 50/50 cointoss to make all your life's decisions.

* `>request/report "a feature"/"a bug"` Dm's the creator with your feature/bug  request/report.

* `>help pagenumber` Returns the help page of your supplied number (currently there are 2 pages)

## Have a feature request?  Make a GitHub issue or use the >request command.

