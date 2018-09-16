# /usr/bin/python3
# -*- coding: utf-8 -*-
"""
Script:
    Constants.py
Description:
    Constants values for anti_join2spam_Bot.py.
Author:
    Jose Rios Rubio
Creation date:
    04/04/2018
Last modified date:
    12/08/2018
Version:
    1.7.0
"""

####################################################################################################
import sys

try:
    import config as conf
except ImportError as error:
    print("""You need to create and configure the config.py module. """)
    print(
        """The config.py module contains the configuration parameter the bot
needs to work properly. Please refer to the README file for more information."""
    )
    sys.exit(1)

# Constants
# Bot Token (get it from @BotFather) this is mandatory
TOKEN = conf.TELEGRAM_API_TOKEN
# list of user ides o usernames allowed to reset the bot
MANAGERS_LIST = conf.MANAGERS_LIST
# If true activates debug messages
DEBUG = getattr(conf, "DEBUG", False)
# Owner ID (The one that can send notify messages to all chats)
OWNER_ID = getattr(conf, "OWNER_ID", 000000000)
# Chat ID where the Bot is going to send debug messages
DEBUG_TO_CHAT = getattr(conf, "DEBUG_TO_CHAT", 000000000)
# Data directory path
ROOT_DIR = getattr(conf, "ROOT_DIR", ".")
DATA_DIR = getattr(conf, "DATA_DIR", "./data")
DATABASE_NAME = getattr(conf, "DATABASE_NAME", "bot.sqlite")
# Chat JSON files name
# Initial chat title at Bot start
INIT_TITLE = getattr(conf, "INIT_TITLE", "Unknown Chat")
# Initial chat link at Bot start
INIT_LINK = getattr(conf, "INIT_LINK", "Unknown")
# Initial language at Bot start
INIT_LANG = getattr(conf, "INIT_LANG", "EN")
# Allowed languages
LANGUAGES = ["EN", "ES", "CA"]
# Initial enable/disable status at Bot start
INIT_ENABLE = getattr(conf, "INIT_ENABLE", True)
# Initial hours until allow a user to publish URLs in messages
INIT_TIME_ALLOW_URLS = getattr(conf, "INIT_TIME_ALLOW_URLS", 24)
# Initial number of users messages until allow publish URLs
INIT_MIN_MSG_ALLOW_URLS = getattr(conf, "INIT_MIN_MSG_ALLOW_URLS", 10)
# Initial notify admins value when Spam is detected
INIT_CALL_ADMINS_WHEN_SPAM = getattr(conf, "INIT_CALL_ADMINS_WHEN_SPAM", False)
# Initial allow users to invite and add Bots to the group
INIT_ALLOW_USERS_ADD_BOTS = getattr(conf, "INIT_ALLOW_USERS_ADD_BOTS", False)
# Time (in mins) to remove self-destruct sent messages from the Bot
T_DEL_MSG = getattr(conf, "T_DEL_MSG", 3)
# Save messages for each chat
SAVE_CHAT_MESSAGES = getattr(conf, "SAVE_CHAT_MESSAGES", True)
# Config parameters
MAX_USERNAME_LENGTH = getattr(conf, "MAX_USERNAME_LENGTH", 30)
MAX_USERNAME_ALIAS = getattr(conf, "MAX_USERNAME_ALIAS", 50)

DEVELOPER = "@JoseTLG & @aaloy"  # Bot developer
REPOSITORY = (
    "https://https://github.com/J-Rios/TLG_AntiJoin2SpamBot \n "
)  # Bot code repository
DEV_PAYPAL = "https://www.paypal.me/josrios"  # Developer Paypal address
DEV_BTC = "3N9wf3FunR6YNXonquBeWammaBZVzTXTyR"  # Developer Bitcoin address
VERSION = "1.8.0"  # Bot version


_ = lambda s: s


MSG = {
    "START": _(
        "I am a Bot that fight against Spammers that join groups to publish their annoying and unwanted info. Check /help command for more information about my usage."
    ),
    "ANTI-SPAM_BOT_ADDED_TO_GROUP": _(
        "Hello, I am a Bot that fight against Spammers that join groups to publish their annoying and unwanted info. To work properly, give me Admin privileges.Check /help command for more information about my usage."
    ),
    "CMD_NOT_ALLOW": _("Just an Admin can use this command"),
    "CMD_JUST_ALLOW_IN_PRIVATE": _("This command just can be use in a private chat."),
    "CMD_JUST_ALLOW_OWNER": _("This command just can be use by the Owner of the Bot."),
    "CMD_NOTIFY_ALL": _(
        "Ok, tell me now the message that you want that I publish in all the Chats where I am...\n\nUse the command /notify_discard if you don't want to stop publishing it."
    ),
    "CMD_NOTIFYING": _(
        "A massive publish is already running, please wait until it finish before send another."
    ),
    "CMD_NOTIFY_ALL_OK": _("Message published in all the chats where I am."),
    "CMD_NOTIFY_DISCARD": _("Massive publish discarted."),
    "CMD_NOTIFY_CANT_DISCARD": _("The massive publish is not running."),
    "LANG_CHANGE": _("Language changed to {}."),
    "LANG_SAME": _("I am already in english.\n\nMay you want to say:\n/language es"),
    "LANG_BAD_LANG": _(
        "Invalid language provided. The actual languages supported are english and spanish, change any of them using en or es.\n'\nExample:\n/language en\n/language es"
    ),
    "LANG_NOT_ARG": _(
        "The command needs a language to set (en - english, es - spanish).\n\nExample:\n/language en\n/language es"
    ),
    "STATUS": _(
        "Actual configuration:\n————————————————\nNumber of messages to allow URLs:\n{}\n\nHours until allow URLs:\n {}\n\nAdmins call when Spam detected:\n{}\n\nAllow users to add Bots:\n{}\n\nAnti-Spam:\n {}\n"
    ),
    "SET_HOURS_CHANGED": _(
        "Time successfully changed.\n\nNew users need to wait {} hours to get allowed to publish URLs in messages."
    ),
    "SET_HOURS_NEGATIVE_HOUR": _(
        "Invalid time provided. The hours need to be positives."
    ),
    "SET_HOURS_BAD_ARG": _(
        "Invalid time provided. You need to specify how many hours want to set for a new user to wait, until get allowed to publish URLs in messages.\n\n Example (5h or 24h):\n/set_hours 5\n /set_hours 24"
    ),
    "SET_HOURS_NOT_ARG": _(
        "No time provided. You need to specify how many hours want to set for a new user to wait, until get allowed to publish URLs in messages.\n\nExample (5h or 24h):\n/set_hours 5\n/set_hours 24"
    ),
    "SET_MSG_CHANGED": _(
        "Number of messages successfully changed.\n\nNew users need to send {} messages to get allowed to publish URLs in messages."
    ),
    "SET_MSG_NEGATIVE": _(
        "Invalid number of messages provided. The number of messages needs to be positive."
    ),
    "SET_MSG_BAD_ARG": _(
        "Invalid number of messages provided. You need to specify how many messages want to set for a new user to wait, until get allowed to publish URLs in messages.\n\nExample (5 or 20):\n/set_messages 5\n/set_messages 20"
    ),
    "SET_MSG_NOT_ARG": _(
        "No number of messages provided. You need to specify how many messages want to set for a new user to wait, until get allowed to publish URLs in messages.\n\nExample (5 or 20):\n/set_messages 5\n/set_messages 20"
    ),
    "CMD_ALLOW_USR_OK": _("User {} granted to publish URLs in messages."),
    "CMD_ALLOW_USR_ALREADY_ALLOWED": _(
        "User {} is already allowed to publish URLs in messages."
    ),
    "CMD_ALLOW_USR_NOT_FOUND": _("User not found in my data base."),
    "CMD_ALLOW_USR_NOT_ARG": _(
        "No user provided. You need to specify the user alias/name that we want to give permission to publish URLs in messages.\n\nExamples:\n/allow_user @mr_doe\n/allow_user Jhon Doe"
    ),
    "ENABLE": _("Anti-Spam enabled. Stop it with /disable command."),
    "DISABLE": _("Anti-Spam disabled. Start it with /enable command."),
    "ALREADY_ENABLE": _("I am already enabled."),
    "ALREADY_DISABLE": _("I am already disabled."),
    "MSG_SPAM_HEADER": _("Anti-Spam message:\n————————————————\n"),
    "MSG_SPAM_DETECTED_CANT_REMOVE": _(
        "Spam message detected, but I don't have permission for remove it. Please, give me administration privileges for delete messages ;)"
    ),
    "MSG_SPAM_DETECTED_0": _(
        "Message from user {} removed for the sake of a free of Spam Telegram."
    ),
    "MSG_SPAM_DETECTED_1": _(
        "\n\nNew members need to write <b>{} messages</b> and wait <b>{} hours</b> to be allowed to publish URLs in their messages."
    ),
    "CALLING_ADMINS": _("\n\nCalling to Admins:\n\n{}"),
    "CALLING_ADMINS_NO_ADMINS": _("There is not Admins in this chat."),
    "CALL_WHEN_SPAM_ENABLE": _("Automatic call Admins when Spam is detected enabled."),
    "CALL_WHEN_SPAM_DISABLE": _(
        "Automatic call Admins when Spam is detected disabled."
    ),
    "CALL_WHEN_SPAM_ALREADY_ENABLE": _(
        "Call Admins when Spam is detected is already enabled."
    ),
    "CALL_WHEN_SPAM_ALREADY_DISABLE": _(
        "Call Admins when Spam is detected is already disabled."
    ),
    "CALL_WHEN_SPAM_NOT_ARG": _(
        "The command needs enable/disable keyword.\n\nExample:\n/call_when_spam enable\n/ call_when_spam disable"
    ),
    "USERS_ADD_BOTS_ENABLE": _("Allow users to add Bots enabled."),
    "USERS_ADD_BOTS_DISABLE": _("Allow users to add Bots disabled."),
    "USERS_ADD_BOTS_ALREADY_ENABLE": _("Allow users to add Bots is already enabled."),
    "USERS_ADD_BOTS_ALREADY_DISABLE": _("Allow users to add Bots is already disabled."),
    "USERS_ADD_BOTS_NOT_ARG": _(
        "The command needs enable/disable keyword.\n\nExample:\n/users_add_bots enable\n/users_add_bots disable"
    ),
    "USER_CANT_ADD_BOT": _(
        "This group doesn't allow that users invite and add Bots.\n\nUser {} try to add the Bot {}. The Bot has been kicked and banned."
    ),
    "USER_CANT_ADD_BOT_CANT_KICK": _(
        "This group don't allow users to invite and add Bots.\n\nUser {} has added the Bot {}, I try to kick the Bot, but I don't have permission to do it. Please, give me administration privileges for ban members ;)"
    ),
    "CAN_NOT_GET_ADMINS": _("Can't use this command in the current chat."),
    "USER_LONG_NAME_JOIN": _(
        "Anti-Spam Warning:\n————————————————\n An user with a name that is too long has joined the chat.\n\n'{} has joined the chat.'"
    ),
    "USER_LONG_NAME_JOIN_CANT_REMOVE": _(
        "Anti-Spam Warning:\n————————————————\nAn user with a name that is too long has joined the chat. But I don't have permission for remove the message. Please, give me administration privileges for delete messages ;)\n\n{} has joined the chat."
    ),
    "USER_URL_NAME_JOIN": _(
        "Anti-Spam Warning:\n————————————————\nAn user with a name that contains an URL has joined the chat.\n\n{} has joined the chat."
    ),
    "USER_URL_NAME_JOIN_CANT_REMOVE": _(
        "Anti-Spam Warning:\n————————————————\nAn user with a name that contains an URL has joined the chat. But I don't have permission for remove the message. Please, give me administration privileges for delete messages ;)\n\n{} has joined the chat."
    ),
    "LINE": _("\n————————————————\n"),
    "LINE_LONG": _("\n————————————————————————————————————————————————\n"),
}
