# ajsbot

This code is a fork for the original https://github.com/J-Rios/TLG_AntiJoin2SpamBot
from which I have made a re-rewite of some parts to make the code PEP8 compliant
and more Pythonic.

## News

* April 2019 version:
  * Added black and white list on links and names
  * Do not allow a new user invite another one
  * kicks offending users
  * Improved logging

### Improvements

* Added a configuration file config.py that the administrators could tune to add the bot parameters. Contants.py has
now sensible default values.

* Improved the link detection:
	* added [urlextract](https://github.com/lipoja/URLExtract) to check for links in username.
	* use telegram to check for links in messages, addding a filter to check the messages and decide if they are spam or not.
* Refactored the whole configuration to a sqlite database by default. Using [Peewee](http://docs.peewee-orm.com/en/latest/) ORM to access the data, so it can be moved to any other Peewee database in the future.

* Simplified and refactored most code to avoid writing and searching in json files.

* Installation throught Pipfile so allows pipenv to run the bot itself.

* Added logger

* Bot rename, first to lower case, then to a new different name.

* Moved message translation to gettext files
* Splited the bot code in modules:
	* commands
	* messages
	* exceptions
* Addedd an option to restrict users
* Add a fast command to delete the last message and restrict an annoying user.





-------------------------------------------------------------------------------------------------------------------------

## How to install, setup and execute the Bot:

1 - Install Python3 and their tools:
```
sudo -i
apt-get install python3
apt-get install python3-pip
pip3 install --upgrade pip
pip3 install --upgrade setuptools
pip3 install pipenv
```

2 - Download Bot repository and go inside sources directory:
```git clone https://github.com/aaloy/TLG_AntiJoin2SpamBot
cd TLG_AntiJoin2SpamBot/sources
pipenv --python 3
pipenv shell
pipenv install
```

1. Create your custom configuration file from the template
```
	cp config.py.template config.py
```

4 - Change the TOKEN line of Constants file to set the TOKEN of your Bot account (from @BotFather):

```
nano config.py
[Change this line -> 'TOKEN' : 'XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX']
```

in `constants.py` you can find the parameters and defaults that you can configure. Just add the to `config.py` with their values.


5 - Run the Bot:

```
A - Run it at normal:
	python3 ajsbot.py

B - Run it in background and unassociated to actual tty
(preserve execution when terminal/console is closed):

	nohup python3 ajsbot.py &

C - Use screen/byobu to run in your server

D - Install in a virtual machine o virtual server
```

6 - Enjoy of a Telegram free of "join2spam" users ;)

-------------------------------------------------------------------------------------------------------------------------

Note: If you install the bot (as me) on a RPi and use pipenv you'll have some warnings and errors about packages signatures. This seems a problem with pipenv and hashes for different architectures.

## Bot help:

- To get working the Anti-spam, you must add me to a group ang give me Administration privileges to let me delete spam messages.

- Once I got Admin privileges, I'll watch for all new users that join the group and don't let them to publish messages that contains URLs until they have been in the group long as an specific time, and they have written an enough number of messages.

- The time that new users need to wait and the number of messages that they need to write before they can publish messages with URLs are, by default, 24 hours and 10 messages, but this values can be modified and configured by using the commands /set_messages and /set_hours.

- To preserve a clean group, I auto-remove messages related to me, after 5 minutes (except Spam detection messages and Admins calls).

- Configuration and enable/disable commands just can be used by the group Administrators.

- You can change the language that I speak, using the command /language.

- Check /commands for get a list of all avaliable commands, and a short description of all of them.

-------------------------------------------------------------------------------------------------------------------------

## List of implemented commands:

/start - Show the initial information about the bot.

/help - Show the help information.

/commands - Show the actual message. Information about all the available commands and their description.

/language - Allow to change the language of the bot messages. Actual available languages: en (english) - es (spanish).

/status - Check actual configured values of all properties.

/set_messages - Set how many published messages are need for new users to be allowed to publish URLs in messages.

/set_hours - Set how many hours for new users are need to wait to get allowed to publish URLs in messages.

/call_admins - Call to all Admins of the group.

/call_when_spam - Enable/disable Admins notify when a spam message is detected.

/users_add_bots - Enable/disable allow users to invite and add Bots to the group.

/allow_user - Allow an user to publish URLs in messages.

/disable_usr - Disables a user, so he can't post links and is considered a potential spammer.

/enable - Enable the Anti-Spam.

/disable - Disable the Anti-Spam.

/version - Show the version of the Bot.

/about - Show about info.

-------------------------------------------------------------------------------------------------------------------------

## Notes

- This Bot uses [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) library.

- This Bot was developed using Python 3.6.


## Contribute:

This code is open to contributions and improvements. As the original code the goal is to create a bot that has one task, the spam control, so tasks and improvements not related to this are not going to be included.

I usually code at evenings, after work and on weekends, so if you have a question, new feature, merge request, etc. please week at least one week before thinking nobody is at home.

If you need a custom bot or any kind of python development the apsl.net team is available for projects.

# Disclaimer

Use at your own risk.
