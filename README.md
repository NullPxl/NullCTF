<img src="https://i.imgur.com/mZ2bVY4.png"/>

>### *A [discord.py](http://discordpy.readthedocs.io/en/latest/) bot focused on providing CTF tools for collaboration in Discord servers!  If you have a feature request, make it a GitHub issue or use the >request "x" command.*

[Invite to your server](https://discordapp.com/oauth2/authorize?client_id=455502163452362753&scope=bot&permissions=268545136)

#  How to Use
>This bot has commands for encoding/decoding, ciphers, and other commonly accessed tools during CTFs.  But, the main use for NullCTF is to easily set up a CTF for your discord server to play as a team.  The following commands listed are probably going to be used the most.
*NOTE: For now (until I find how to check if a category exists...) to setup your server for use with this, create a category labeled CTF*

* `>ctf create "ctf name"`  This is the command you'll use when you want to begin a new CTF.  This command will make a text channel with your supplied name under the category 'CTF'.  *Only available to server owners*

*NOTE: the following ctf specific commands will only be accepted under the channel created for that ctf.  This is to avoid clashes with multiple ctfs going on in the same server.*

 * `>ctf join/leave` Using this command will either give or remove the role of a created ctf to/from you.
 ![enter image description here](https://i.imgur.com/4QPUgvM.png)
 
 * `>ctf challenge add/working/solved "challenge name"` Allows users to add challenges to a list, and then set the status of that challenge.
 
 * `>ctf challenge list` This is the list command that was previously mentioned, it displays the added challenges, who's working on what, and if a challenge is solved (and by who).
 ![enter image description here](https://i.imgur.com/KH5dYZr.png)

---
>The following commands use the api from [ctftime](https://ctftime.org/api)

 * `>ctftime countdown/timeleft` Countdown will return when a selected CTF starts, and timeleft will return when any currently running CTFs end in the form of days hours minutes and seconds.
 ![enter image description here](https://i.imgur.com/LFSTr33.png)  
 ![enter image description here](https://i.imgur.com/AkBfp6E.png)

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

* `>htb` Return when the next hackthebox machine is going live from @hackthebox_eu on twitter.

* `>cointoss` Get a 50/50 cointoss to make all your life's decisions.

* `>request/report "a feature"/"a bug"` Dm's the creator with your feature/bug  request/report.

* `>help pagenumber` Returns the help page of your supplied number (currently there are 2 pages)

## Have a feature request?  Make a GitHub issue or use the >request command.

