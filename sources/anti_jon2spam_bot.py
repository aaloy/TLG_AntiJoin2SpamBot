#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script:
    anti_join2spam_bot.py
Description:
    Telegram Bot that figths against the spammer users that join groups to publish
    their annoying and unwanted info.
    Author:
        Jose Rios Rubio
    Branch:
        aaloy
Creation date:
    04/04/2018
Last modified date:
    26/08/2018
Version:
    1.7.1 - Pep8 compliance
"""

####################################################################################################

# Imported modules

import re
import sys
import signal
import tsjson
from os import path, makedirs, listdir, execl
from threading import Thread
from datetime import datetime
from time import time, sleep, strptime, mktime
from constants import TEXT
from collections import OrderedDict
from telegram import ParseMode, MessageEntity
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.error import BadRequest
from urlextract import URLExtract
from user_info import user_is_admin
# from pathlib import Path
import constants as conf
import logging

# Globals ###
DEBUG = getattr(conf, "DEBUG", False)
files_users_list = []
files_messages_list = []
files_config_list = []
to_delete_messages_list = []
sent_antispam_messages_list = []
owner_notify = False

log = logging.getLogger(__name__)

####################################################################################################


def signal_handler(signal, frame):
    """Termination signals (SIGINT, SIGTERM) handler for program process"""
    log.info("Closing the bot ...")
    sys.exit(1)

    """
    TODO: Not suer if this is required
    # Acquire all messages and users files mutex to ensure not read/write operation on them
    for chat_users_file in files_users_list:
        chat_users_file["File"].lock.acquire()
    for chat_messages_file in files_messages_list:
        chat_messages_file["File"].lock.acquire()
    for chat_config_file in files_config_list:
        chat_config_file["File"].lock.acquire()
    # Close the program
    sys.exit(1)
    """


# Signals attachment ###
# SIGTERM (kill pid) to signal_handler
signal.signal(signal.SIGTERM, signal_handler)
# SIGINT (Ctrl+C) to signal_handler
signal.signal(signal.SIGINT, signal_handler)

####################################################################################################

# Debug print ###


def debug_print_tlg(bot, text):
    """Function to send text message to TLG chat just when DEBUG flag is active"""
    if conf.DEBUG:
        try:
            bot.send_message(conf.DEBUG_TO_CHAT, text)
            log.debug("{}-{}".format(conf.DEBUG_TO_CHAT, text))
        except:
            pass


####################################################################################################

# General functions


def initialize_resources():
    """Initialize resources by populating files list with chats found files"""
    # Create data directory if it does not exists
    if not path.exists(conf.DATA_DIR):
        makedirs(conf.DATA_DIR)
    else:
        # If directory data exists, check all subdirectories names (chats ID)
        files = listdir(conf.DATA_DIR)
        if files:
            for f_chat_id in files:
                # Populate users files list
                file_path = "{}/{}/{}".format(conf.DATA_DIR, f_chat_id, conf.F_USERS)
                files_users_list.append(
                    OrderedDict([("ID", f_chat_id), ("File", tsjson.TSjson(file_path))])
                )
                # Populate messages files list
                file_path = "{}/{}/{}".format(conf.DATA_DIR, f_chat_id, conf.F_MSG)
                files_messages_list.append(
                    OrderedDict([("ID", f_chat_id), ("File", tsjson.TSjson(file_path))])
                )
                # Populate config files list
                file_path = "{}/{}/{}".format(conf.DATA_DIR, f_chat_id, conf.F_CONF)
                files_config_list.append(
                    OrderedDict([("ID", f_chat_id), ("File", tsjson.TSjson(file_path))])
                )
                # Create default configuration file if it does not exists
                if not path.exists(file_path):
                    default_conf = get_default_config_data()
                    for key, value in default_conf.items():
                        save_config_property(f_chat_id, key, value)


def get_chat_users_file(chat_id):
    """Determine chat users file from the list by ID. Get the file if exists or create it if not"""
    user = OrderedDict([("ID", chat_id), ("File", None)])
    found = False
    if files_users_list:
        for chat_file in files_users_list:
            if chat_file["ID"] == chat_id:
                user = chat_file
                found = True
                break
        if not found:
            chat_users_file_name = "{}/{}/{}".format(
                conf.DATA_DIR, chat_id, conf.F_USERS
            )
            user["ID"] = chat_id
            user["File"] = tsjson.TSjson(chat_users_file_name)
            files_users_list.append(user)
    else:
        chat_users_file_name = "{}/{}/{}".format(conf.DATA_DIR, chat_id, conf.F_USERS)
        user["ID"] = chat_id
        user["File"] = tsjson.TSjson(chat_users_file_name)
        files_users_list.append(user)
    return user["File"]


def get_chat_messages_file(chat_id):
    """Determine chat msgs file from the list by ID. Get the file if exists or create it if not"""
    msg = OrderedDict([("ID", chat_id), ("File", None)])
    found = False
    if files_messages_list:
        for chat_file in files_messages_list:
            if chat_file["ID"] == chat_id:
                msg = chat_file
                found = True
                break
        if not found:
            chat_messages_file_name = "{}/{}/{}".format(
                conf.DATA_DIR, chat_id, conf.F_MSG
            )
            msg["File"] = tsjson.TSjson(chat_messages_file_name)
            files_messages_list.append(msg)
    else:
        chat_messages_file_name = "{}/{}/{}".format(conf.DATA_DIR, chat_id, conf.F_MSG)
        msg["File"] = tsjson.TSjson(chat_messages_file_name)
        files_messages_list.append(msg)
    return msg["File"]


def get_chat_config_file(chat_id):
    """Determine chat config file from the list by ID. Get the file
    if exists or create it if not"""
    configuration = OrderedDict([("ID", chat_id), ("File", None)])
    found = False
    if files_config_list:
        for chat_file in files_config_list:
            if chat_file["ID"] == chat_id:
                configuration = chat_file
                found = True
                break
        if not found:
            chat_config_file_name = "{}/{}/{}".format(
                conf.DATA_DIR, chat_id, conf.F_CONF
            )
            configuration["ID"] = chat_id
            configuration["File"] = tsjson.TSjson(chat_config_file_name)
            files_config_list.append(configuration)
    else:
        chat_config_file_name = "{}/{}/{}".format(conf.DATA_DIR, chat_id, conf.F_CONF)
        configuration["ID"] = chat_id
        configuration["File"] = tsjson.TSjson(chat_config_file_name)
        files_config_list.append(configuration)
    return configuration["File"]


def get_default_config_data():
    """Get default config data structure"""
    config_data = OrderedDict(
        [
            ("Title", conf.INIT_TITLE),
            ("Link", conf.INIT_LINK),
            ("Language", conf.INIT_LANG),
            ("Antispam", conf.INIT_ENABLE),
            ("Time_for_allow_urls_h", conf.INIT_TIME_ALLOW_URLS),
            ("Num_messages_for_allow_urls", conf.INIT_MIN_MSG_ALLOW_URLS),
            ("Call_admins_when_spam_detected", conf.INIT_CALL_ADMINS_WHEN_SPAM),
            ("Allow_users_to_add_bots", conf.INIT_ALLOW_USERS_ADD_BOTS),
        ]
    )
    return config_data


def save_config_property(chat_id, property, value):
    """Store actual chat configuration in file"""
    fjson_config = get_chat_config_file(chat_id)
    config_data = fjson_config.read()
    if not config_data:
        config_data = get_default_config_data()
    config_data[property] = value
    fjson_config.write(config_data)


def get_chat_config(chat_id, param):
    """Get specific stored chat configuration property"""
    chat_config = get_chat_config_file(chat_id)
    if chat_config:
        config_data = chat_config.read()
        if not config_data:
            config_data = get_default_config_data()
    else:
        config_data = get_default_config_data()
    return config_data[param]


def register_new_user(chat_id, user_id, user_name, join_date, allow_user):
    """Add new member to the users file"""
    # Default new user data
    user_data = OrderedDict(
        [
            ("User_id", user_id),
            ("User_name", user_name),
            ("Join_date", join_date),
            ("Num_messages", 0),
            ("Allow_user", allow_user),
        ]
    )
    # Get the chat users file and write the user data to it
    fjson_usr = get_chat_users_file(chat_id)
    fjson_usr.write_content(user_data)


def add_new_message(chat_id, msg_id, user_id, user_name, text, msg_date):
    """Add new message to the messages file"""
    if conf.SAVE_CHAT_MESSAGES:
        msg_data = OrderedDict(
            [
                ("Chat_id", chat_id),
                ("Msg_id", msg_id),
                ("User_id", user_id),
                ("User_name", user_name),
                ("Text", text),
                ("Date", msg_date),
            ]
        )
        # Get the chat messages file and write the messages data to it
        fjson_msg = get_chat_messages_file(chat_id)
        fjson_msg.write_content(msg_data)


def _get_message(chat_id, msg_id):
    """Get message data of a chat by ID"""
    fjson_msg = get_chat_messages_file(chat_id)
    messages_data = fjson_msg.read_content()
    for msg in messages_data:
        if chat_id == msg["Chat_id"]:
            if msg_id == msg["Msg_id"]:
                return msg
    return None


def get_user_from_id(chat_id, user_id):
    """Get user data by member ID"""
    fjson_usr = get_chat_users_file(chat_id)
    users_data = fjson_usr.read_content()
    for usr in users_data:
        if user_id == usr["User_id"]:
            return usr
    return None


def get_user_from_alias(chat_id, user_alias):
    """Get user from an alias"""
    fjson_usr = get_chat_users_file(chat_id)
    users_data = fjson_usr.read_content()
    for usr in users_data:
        if user_alias == usr["User_name"]:
            return usr
    return None


def user_in_json(chat_id, user_id):
    """Check if a user is in the file by his ID"""
    fjson_usr = get_chat_users_file(chat_id)
    users_data = fjson_usr.read_content()
    for usr in users_data:
        if user_id == usr["User_id"]:
            return True
    return False


def update_user(chat_id, new_user_data):
    """Update an existing user from the JSON file. If the user does not exists, add to it"""
    fjson_usr = get_chat_users_file(chat_id)
    user_id = new_user_data["User_id"]
    if user_in_json(chat_id, user_id):
        fjson_usr.update(new_user_data, "User_id")
    else:
        fjson_usr.write_content(new_user_data)


def get_admins_usernames_in_string(bot, chat_id):
    """Get all the group Administrators usernames/alias in a single line string separed by \' \'"""
    try:
        group_admins = bot.get_chat_administrators(chat_id)
    except Exception as e:
        log.debug("Exception when checking Admins of {} - {}".format(chat_id, str(e)))
        return None
    list_admins_names = sorted(["@{}".format(admin.user.username) for admin in group_admins if not admin.user.is_bot])
    return "\n".join(list_admins_names)


def notify_all_chats(bot, message):
    """Publish a notify message in all the Chats where the Bot is, except
    for the public chats (the ones with non negative ids"""
    # If directory data exists, check all subdirectories names (chats ID)
    chats_files = [chat for chat in listdir(conf.DATA_DIR) if chat.startswith("-")]
    for chat_id in chats_files:
        try:
            bot.send_message(chat_id, message)
        except Exception as e:
            log.debug("Exception when publishing in {} - {}".format(chat_id, str(e)))


####################################################################################################

# Received Telegram not-command messages handlers ###

def left_user(bot, update):
    """Member left the group event handler. On this case we try to
    avoid the message that telegram sends when removing the user
    form the group."""

    chat_id = update.message.chat.id
    message_id = update.message.message_id
    user = update.message.left_chat_member
    left_user_name = "{} {}".format(user.first_name, user.last_name)
    log.info('{} left the group'.format(left_user_name))
    # Delete left message if the user name has an URL or is too long
    has_url = re.findall(conf.REGEX_URLS, left_user_name)
    try:
        if has_url:
            bot.delete_message(chat_id, message_id)
        else:
            if len(left_user_name) > conf.MAX_USERNAME_LENGTH:
                bot.delete_message(chat_id, message_id)
    except Exception as e:
        log.error("Error on deleting left message {}".format(e))


def anti_spam_bot_added_event(chat_id, bot, update):
    """The anti spam bot has been added to the chat,
    update the chant configuration files, and inform the group
    about the bot being added"""

    admin_language = update.message.from_user.language_code[0:2]
    if admin_language == "es":
        lang = "ES"
        save_config_property(chat_id, "Language", lang)
    else:
        lang = "EN"
        save_config_property(chat_id, "Language", lang)
    # Notify to Bot Owner that the Bot has been added to a group
    notify_msg = "The Bot has been added to a new group:\n\n- ID: {}\n".format(chat_id)
    chat_title = update.message.chat.title
    if chat_title:
        save_config_property(chat_id, "Title", chat_title)
        notify_msg = "{}- Title: {}\n".format(notify_msg, chat_title)
    else:
        notify_msg = "{}- Title: Unknown\n".format(notify_msg)
    chat_link = update.message.chat.username
    if chat_link:
        chat_link = "@{}".format(chat_link)
        save_config_property(chat_id, "Link", chat_link)
        notify_msg = "{}- Link: {}\n".format(notify_msg, chat_link)
    else:
        notify_msg = "{}- Link: Unknown\n".format(notify_msg)
    admin_name = update.message.from_user.name
    admin_id = update.message.from_user.id
    notify_msg = "{}- Admin: {} [{}]".format(notify_msg, admin_name, admin_id)
    debug_print_tlg(bot, notify_msg)
    # Send bot join message
    bot_message = TEXT[lang]["ANTI-SPAM_BOT_ADDED_TO_GROUP"]
    bot.send_message(chat_id, bot_message)


def try_to_add_a_bot_event(bot, message, join_user, chat_id):
    """Check if the join user is a bot and has been added by
    someone with authorization. Delete the bot if not.

    Returns true if the bot can be registered."""

    to_register_user = True
    msg_from_user_id = message.from_user.id
    join_user_id = join_user.id
    join_user_alias = join_user.name
    lang = get_chat_config(chat_id, "Language")

    # If the user that has been added the Bot is not an Admin
    if not user_is_admin(bot, msg_from_user_id, chat_id):
        # If not allow users to add Bots
        if not get_chat_config(chat_id, "Allow_users_to_add_bots") is False:
            # Kick the Added Bot and notify
            log.debug("An user has added a Bot.\n  (Chat) - ({}).".format(chat_id))
            try:
                bot.kickChatMember(chat_id, join_user_id)
                bot_message = TEXT[lang]["USER_CANT_ADD_BOT"].format(
                    message.from_user.name, join_user_alias
                )
                log.debug("Added Bot successfully kicked.\n  (Chat) - ({}).".format(chat_id))
            except Exception as e:
                log.debug("Exception when kicking a Bot - {}".format(str(e)))
                if (str(e) == "Not enough rights to restrict/unrestrict chat member"):
                    bot_message = TEXT[lang]["USER_CANT_ADD_BOT_CANT_KICK"].format(message.from_user.name, join_user.name)

            if get_chat_config(chat_id, "Call_admins_when_spam_detected"):
                admins = get_admins_usernames_in_string(bot, chat_id)
                if admins:
                    bot_message = "{}{}".format(bot_message, TEXT[lang]["CALLING_ADMINS"].format(admins))
            bot.send_message(chat_id, bot_message)
            to_register_user = False
    return to_register_user


def new_user(bot, update):
    """New member join the group event handler"""
    message = update.message
    chat_id = message.chat_id
    message_id = message.message_id
    msg_from_user_id = message.from_user.id
    join_date = (message.date).now().strftime("%Y-%m-%d %H:%M:%S")
    lang = get_chat_config(chat_id, "Language")
    # For each new user that join or has been added
    for join_user in message.new_chat_members:
        join_user_id = join_user.id
        join_user_alias = join_user.name
        join_user_name = "{} {}".format(message.from_user.first_name, message.from_user.last_name)
        # If the added user is not myself (this Bot)
        if bot.id == join_user_id:
            # The Anti-Spam Bot has been added to a group
            anti_spam_bot_added_event(chat_id, bot, update)
        else:
            to_register_user = True
            # If the message user source is not the join user, it has been invited/added by another
            if msg_from_user_id != join_user_id and join_user.is_bot:
                # If a user has added a bot check if could be added and delete id if not
                to_register_user = try_to_add_a_bot_event(bot, msg_from_user_id, join_user, chat_id)
            # i
            if to_register_user:
                # Check if there is an URL in the user name
                extractor = URLExtract()
                has_url = extractor.has_urls(join_user_name) or extractor.has_urls(join_user_alias)
                if has_url:
                    log.debug(
                        "Spammer (URL name) join detected.\n  (Chat) - ({}).".format(
                            chat_id
                        )
                    )
                    if len(join_user_name) > 10:
                        join_user_name = join_user_name[0:10]
                        join_user_name = "{}...".format(join_user_name)
                    try:
                        bot.delete_message(chat_id, message_id)
                        bot_message = TEXT[lang]["USER_URL_NAME_JOIN"].format(
                            join_user_name
                        )
                        log.debug(
                            "Spammer (URL name) join message successfully removed.\n"
                            "  (Chat) - ({}).".format(chat_id)
                        )
                        tlg_send_selfdestruct_msg(bot, chat_id, bot_message)
                    except Exception as e:
                        log.debug(
                            "Exception when deleting a Spammer (URL name) join "
                            "message - {}".format(str(e))
                        )
                        if str(e) == "Message can't be deleted":
                            bot_message = TEXT[lang][
                                "USER_URL_NAME_JOIN_CANT_REMOVE"
                            ].format(join_user_name)
                            bot.send_message(chat_id, bot_message)
                else:
                    # Check if user name and last name are too long
                    if len(join_user_name) > conf.MAX_USERNAME_LENGTH:
                        join_user_name = join_user_name[0:10]
                        join_user_name = "{}...".format(join_user_name)
                        try:
                            bot.delete_message(chat_id, message_id)
                            bot_message = TEXT[lang]["USER_LONG_NAME_JOIN"].format(
                                join_user_name
                            )
                            log.debug(
                                "Spammer (long name) join message successfully removed.\n"
                                "  (Chat) - ({}).".format(chat_id)
                            )
                            tlg_send_selfdestruct_msg(bot, chat_id, bot_message)
                        except Exception as e:
                            log.debug(
                                "Exception when deleting a Spammer (long name) join "
                                "message - {}".format(str(e))
                            )
                            if str(e) == "Message can't be deleted":
                                bot_message = TEXT[lang][
                                    "USER_LONG_NAME_JOIN_CANT_REMOVE"
                                ].format(join_user_name)
                                bot.send_message(chat_id, bot_message)
                if len(join_user_alias) > conf.MAX_USERNAME_ALIAS:
                    join_user_alias = join_user_alias[0:conf.MAX_USERNAME_ALIAS-3]
                    join_user_alias = "{}...".format(join_user_alias)
                if not user_in_json(chat_id, join_user_id):
                    register_new_user(
                        chat_id, join_user_id, join_user_alias, join_date, False
                    )


def msg_nocmd(bot, update):
    """All Not-command messages handler"""
    global owner_notify
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    user_id = update.message.from_user.id
    lang = get_chat_config(chat_id, "Language")
    if chat_type == "private":
        if user_id == conf.OWNER_ID:
            if owner_notify is True:
                owner_notify = False
                message = update.message.text
                notify_all_chats(bot, message)
                bot.send_message(chat_id, TEXT[lang]["CMD_NOTIFY_ALL_OK"])
    else:
        chat_title = update.message.chat.title
        if chat_title:
            save_config_property(chat_id, "Title", chat_title)
        chat_link = update.message.chat.username
        if chat_link:
            chat_link = "@{}".format(chat_link)
            save_config_property(chat_id, "Link", chat_link)
        msg_id = update.message.message_id
        user_name = update.message.from_user.name
        msg_date = (update.message.date).now().strftime("%Y-%m-%d %H:%M:%S")
        text = update.message.text
        if text is None:
            text = getattr(update.message, "caption_html", None)
            if text is None:
                text = getattr(update.message, "caption", None)
        enable = get_chat_config(chat_id, "Antispam")
        time_for_allow_urls_h = get_chat_config(chat_id, "Time_for_allow_urls_h")
        num_messages_for_allow_urls = get_chat_config(
            chat_id, "Num_messages_for_allow_urls"
        )
        call_admins_when_spam_detected = get_chat_config(
            chat_id, "Call_admins_when_spam_detected"
        )
        # If user not yet register, it means it was there before the bot, 
        # assume that is legit, add to users file, else, get his number of published msgs
        if not user_in_json(chat_id, user_id):
            # Register user and set "Num_messages" and "Join_date" to allow publish URLs
            register_new_user(chat_id, user_id, user_name, msg_date, True)
            user_data = get_user_from_id(chat_id, user_id)
            user_data["Num_messages"] = num_messages_for_allow_urls + 1
            user_data["Join_date"] = datetime(1971, 1, 1).strftime("%Y-%m-%d %H:%M:%S")
            update_user(chat_id, user_data)
        else:
            # Increase num messages count
            user_data = get_user_from_id(chat_id, user_id)
            user_data["Num_messages"] = user_data["Num_messages"] + 1
            update_user(chat_id, user_data)
            # If it is a text message
            if text is not None:
                # If the user is not an Admin and the Bot Anti-Spam is enabled
                is_admin = user_is_admin(bot, user_id, chat_id)
                if (is_admin is False) and (enable is True):
                    # If there is any URL in the message
                    any_url = re.findall(conf.REGEX_URLS, text)
                    if any_url:
                        # If user does not have allowed to publish
                        if user_data["Allow_user"] is False:
                            num_published_messages = user_data["Num_messages"]
                            # Check user time in the group
                            user_join_date = user_data["Join_date"]
                            user_join_date_dateTime = strptime(
                                user_join_date, "%Y-%m-%d %H:%M:%S"
                            )
                            msg_date_dateTime = strptime(msg_date, "%Y-%m-%d %H:%M:%S")
                            t0 = mktime(user_join_date_dateTime)  # Date to epoch
                            t1 = mktime(msg_date_dateTime)  # Date to epoch
                            user_hours_in_group = (t1 - t0) / 3600
                            # If user is relatively new in the group or has not write enough msgs
                            if (user_hours_in_group < time_for_allow_urls_h) or (
                                num_published_messages < num_messages_for_allow_urls + 1
                            ):
                                log.debug(
                                    "Spam message detected.\n  (Chat, User, Message) -({}, {}, {}).".format(
                                        chat_id, user_name, user_id
                                    )
                                )
                                # Decrease this message from the user messages count
                                user_data["Num_messages"] = (
                                    user_data["Num_messages"] - 1
                                )
                                update_user(chat_id, user_data)
                                # Check if there was another spam messages in the chat from same
                                # user, and remove it
                                for antispam_msg in sent_antispam_messages_list:
                                    if (antispam_msg["User_id"] == user_id) and (
                                        antispam_msg["Chat_id"] == chat_id
                                    ):
                                        # Try to delete that sent message if possible (still exists)
                                        try:
                                            if bot.delete_message(
                                                chat_id, antispam_msg["Msg_id"]
                                            ):
                                                sent_antispam_messages_list.remove(
                                                    antispam_msg
                                                )
                                                log.debug(
                                                    "Previous Spam message successfully "
                                                    "removed.\n  (Chat, User, Message) - "
                                                    "({}, {}, {}).".format(
                                                        chat_id, user_name, user_id
                                                    )
                                                )
                                        except Exception as e:
                                            log.debug(
                                                "Exception when deleting a previous Spam "
                                                "message from an user - {}".format(
                                                    str(e)
                                                )
                                            )
                                            sent_antispam_messages_list.remove(
                                                antispam_msg
                                            )
                                # Delete user message and notify what happen
                                bot_msg_head = TEXT[lang]["MSG_SPAM_HEADER"]
                                try:
                                    if bot.delete_message(chat_id, msg_id):
                                        bot_msg_0 = TEXT[lang][
                                            "MSG_SPAM_DETECTED_0"
                                        ].format(user_name)
                                        bot_msg_1 = TEXT[lang][
                                            "MSG_SPAM_DETECTED_1"
                                        ].format(
                                            num_messages_for_allow_urls,
                                            time_for_allow_urls_h,
                                        )
                                        bot_message = "{}{}{}".format(
                                            bot_msg_head, bot_msg_0, bot_msg_1
                                        )
                                        log.debug(
                                            "Spam message successfully removed.\n  "
                                            "(Chat, User, Message) - ({}, {}, {}).".format(
                                                chat_id, user_name, user_id
                                            )
                                        )
                                except Exception as e:
                                    log.debug(
                                        "Exception when deleting an Spam message - {}".format(
                                            str(e)
                                        )
                                    )
                                    if str(e) == "Message can't be deleted":
                                        bot_message = "{}{}".format(
                                            bot_msg_head,
                                            TEXT[lang]["MSG_SPAM_DETECTED_CANT_REMOVE"],
                                        )
                                if call_admins_when_spam_detected:
                                    admins = get_admins_usernames_in_string(
                                        bot, chat_id
                                    )
                                    if admins:
                                        bot_msg_2 = TEXT[lang]["CALLING_ADMINS"].format(
                                            admins
                                        )
                                        bot_message = "{}{}".format(
                                            bot_message, bot_msg_2
                                        )
                                sent_msg = bot.send_message(
                                    chat_id, bot_message, parse_mode=ParseMode.HTML
                                )
                                # Store sent anti-spam message in to delete list
                                antispam_msg = OrderedDict(
                                    [
                                        ("User_id", user_id),
                                        ("Chat_id", chat_id),
                                        ("Msg_id", sent_msg.message_id),
                                        ("Msg_date", t1),
                                    ]
                                )
                                sent_antispam_messages_list.append(antispam_msg)
                            # If the user is allowed to publish URLs
                            else:
                                # Give user permission
                                user_data["Allow_user"] = True
                                update_user(chat_id, user_data)
                # Truncate the message text to 500 characters
                if len(text) > 50:
                    text = text[0:50]
                    text = "{}...".format(text)
                # Add the message to messages file
                add_new_message(chat_id, msg_id, user_id, user_name, text, msg_date)
        # Remove from list all messages from 5h ago or more
        msg_date_epoch = mktime(
            strptime(msg_date, "%Y-%m-%d %H:%M:%S")
        )  # Date string to epoch
        for antispam_msg in sent_antispam_messages_list:
            if msg_date_epoch - antispam_msg["Msg_date"] >= 40:
                sent_antispam_messages_list.remove(antispam_msg)


####################################################################################################

# Received Telegram command messages handlers ###


def cmd_start(bot, update):
    """Command /start message handler"""
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    if chat_type == "private":
        log.info("The bot started in {} private chat".format(chat_id))
        bot.send_message(chat_id, TEXT[lang]["START"])
    else:
        log.info("The bot started in {} group chat".format(chat_id))
        tlg_msg_to_selfdestruct(bot, update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["START"])


def cmd_help(bot, update):
    """Command /help message handler"""
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    bot_msg = TEXT[lang]["HELP"].format(
        conf.INIT_TIME_ALLOW_URLS, conf.INIT_MIN_MSG_ALLOW_URLS, conf.T_DEL_MSG
    )
    if chat_type == "private":
        bot.send_message(chat_id, bot_msg)
    else:
        tlg_msg_to_selfdestruct(bot, update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_commands(bot, update):
    """Command /commands message handler"""
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    if chat_type == "private":
        bot.send_message(chat_id, TEXT[lang]["COMMANDS"])
    else:
        tlg_msg_to_selfdestruct(bot, update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["COMMANDS"])


def cmd_language(bot, update, args):
    """Command /language message handler"""
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    allow_command = True
    if chat_type != "private":
        is_admin = user_is_admin(bot, user_id, chat_id)
        if is_admin is False:
            allow_command = False
    if allow_command:
        if len(args) == 1:
            lang_provided = args[0]
            if lang_provided == "en" or lang_provided == "es":
                lang_provided = lang_provided.upper()
                if lang_provided != lang:
                    lang = lang_provided
                    save_config_property(chat_id, "Language", lang)
                    bot_msg = TEXT[lang]["LANG_CHANGE"]
                else:
                    bot_msg = TEXT[lang]["LANG_SAME"]
            else:
                bot_msg = TEXT[lang]["LANG_BAD_LANG"]
        else:
            bot_msg = TEXT[lang]["LANG_NOT_ARG"]
    elif is_admin is False:
        bot_msg = TEXT[lang]["CMD_NOT_ALLOW"]
    else:
        bot_msg = TEXT[lang]["CAN_NOT_GET_ADMINS"]
    if chat_type == "private":
        bot.send_message(chat_id, bot_msg)
    else:
        tlg_msg_to_selfdestruct(bot, update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_set_messages(bot, update, args):
    """Command /set_messages message handler"""
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    is_admin = user_is_admin(bot, user_id, chat_id)
    if is_admin is True:
        if len(args) == 1:
            num_msgs_provided = args[0]
            if num_msgs_provided.isdigit():
                num_msgs_provided = int(num_msgs_provided)
                if num_msgs_provided >= 0:
                    save_config_property(
                        chat_id, "Num_messages_for_allow_urls", num_msgs_provided
                    )
                    bot_msg = TEXT[lang]["SET_MSG_CHANGED"].format(num_msgs_provided)
                else:
                    bot_msg = TEXT[lang]["SET_MSG_NEGATIVE"]
            else:
                bot_msg = TEXT[lang]["SET_MSG_BAD_ARG"]
        else:
            bot_msg = TEXT[lang]["SET_MSG_NOT_ARG"]
    elif is_admin is False:
        bot_msg = TEXT[lang]["CMD_NOT_ALLOW"]
    else:
        bot_msg = TEXT[lang]["CAN_NOT_GET_ADMINS"]
    if chat_type == "private":
        bot.send_message(chat_id, bot_msg)
    else:
        tlg_msg_to_selfdestruct(bot, update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_set_hours(bot, update, args):
    """Command /set_hours message handler"""
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    is_admin = user_is_admin(bot, user_id, chat_id)
    if is_admin is True:
        if len(args) == 1:
            hours_provided = args[0]
            if hours_provided.isdigit():
                hours_provided = int(hours_provided)
                if hours_provided >= 0:
                    save_config_property(
                        chat_id, "Time_for_allow_urls_h", hours_provided
                    )
                    bot_msg = TEXT[lang]["SET_HOURS_CHANGED"].format(hours_provided)
                else:
                    bot_msg = TEXT[lang]["SET_HOURS_NEGATIVE_HOUR"]
            else:
                bot_msg = TEXT[lang]["SET_HOURS_BAD_ARG"]
        else:
            bot_msg = TEXT[lang]["SET_HOURS_NOT_ARG"]
    elif is_admin is False:
        bot_msg = TEXT[lang]["CMD_NOT_ALLOW"]
    else:
        bot_msg = TEXT[lang]["CAN_NOT_GET_ADMINS"]
    if chat_type == "private":
        bot.send_message(chat_id, bot_msg)
    else:
        tlg_msg_to_selfdestruct(bot, update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_status(bot, update):
    """Command /status message handler"""
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    enable = get_chat_config(chat_id, "Antispam")
    num_messages_for_allow_urls = get_chat_config(
        chat_id, "Num_messages_for_allow_urls"
    )
    time_for_allow_urls_h = get_chat_config(chat_id, "Time_for_allow_urls_h")
    call_admins_when_spam_detected = get_chat_config(
        chat_id, "Call_admins_when_spam_detected"
    )
    allow_users_to_add_bots = get_chat_config(chat_id, "Allow_users_to_add_bots")
    bot_msg = TEXT[lang]["STATUS"].format(
        num_messages_for_allow_urls,
        time_for_allow_urls_h,
        call_admins_when_spam_detected,
        allow_users_to_add_bots,
        enable,
    )
    if chat_type == "private":
        bot.send_message(chat_id, bot_msg)
    else:
        tlg_msg_to_selfdestruct(bot, update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_call_admins(bot, update):
    """Command /call_admins message handler"""
    chat_id = update.message.chat_id
    lang = get_chat_config(chat_id, "Language")
    admins = get_admins_usernames_in_string(bot, chat_id)
    if admins:
        bot_msg = TEXT[lang]["CALLING_ADMINS"].format(admins)
    else:
        bot_msg = TEXT[lang]["CALLING_ADMINS_NO_ADMINS"]
    bot.send_message(chat_id, bot_msg)


def cmd_call_when_spam(bot, update, args):
    """Command /call_when_spam message handler"""
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    call_admins_when_spam_detected = get_chat_config(
        chat_id, "Call_admins_when_spam_detected"
    )
    is_admin = user_is_admin(bot, user_id, chat_id)
    if is_admin is True:
        if len(args) == 1:
            value_provided = args[0]
            if value_provided == "enable" or value_provided == "disable":
                if value_provided == "enable":
                    if call_admins_when_spam_detected is True:
                        bot_msg = TEXT[lang]["CALL_WHEN_SPAM_ALREADY_ENABLE"]
                    else:
                        bot_msg = TEXT[lang]["CALL_WHEN_SPAM_ENABLE"]
                        call_admins_when_spam_detected = True
                        save_config_property(
                            chat_id,
                            "Call_admins_when_spam_detected",
                            call_admins_when_spam_detected,
                        )
                else:
                    if call_admins_when_spam_detected is True:
                        bot_msg = TEXT[lang]["CALL_WHEN_SPAM_DISABLE"]
                        call_admins_when_spam_detected = False
                        save_config_property(
                            chat_id,
                            "Call_admins_when_spam_detected",
                            call_admins_when_spam_detected,
                        )
                    else:
                        bot_msg = TEXT[lang]["CALL_WHEN_SPAM_ALREADY_DISABLE"]
            else:
                bot_msg = TEXT[lang]["CALL_WHEN_SPAM_NOT_ARG"]
        else:
            bot_msg = TEXT[lang]["CALL_WHEN_SPAM_NOT_ARG"]
    elif is_admin is False:
        bot_msg = TEXT[lang]["CMD_NOT_ALLOW"]
    else:
        bot_msg = TEXT[lang]["CAN_NOT_GET_ADMINS"]
    if chat_type == "private":
        bot.send_message(chat_id, bot_msg)
    else:
        tlg_msg_to_selfdestruct(bot, update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_users_add_bots(bot, update, args):
    """Command /users_add_bots message handler"""
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    allow_users_to_add_bots = get_chat_config(chat_id, "Allow_users_to_add_bots")
    is_admin = user_is_admin(bot, user_id, chat_id)
    if is_admin is True:
        if len(args) == 1:
            value_provided = args[0]
            if value_provided == "enable" or value_provided == "disable":
                if value_provided == "enable":
                    if allow_users_to_add_bots is True:
                        bot_msg = TEXT[lang]["USERS_ADD_BOTS_ALREADY_ENABLE"]
                    else:
                        bot_msg = TEXT[lang]["USERS_ADD_BOTS_ENABLE"]
                        allow_users_to_add_bots = True
                        save_config_property(
                            chat_id, "Allow_users_to_add_bots", allow_users_to_add_bots
                        )
                else:
                    if allow_users_to_add_bots is True:
                        bot_msg = TEXT[lang]["USERS_ADD_BOTS_DISABLE"]
                        allow_users_to_add_bots = False
                        save_config_property(
                            chat_id, "Allow_users_to_add_bots", allow_users_to_add_bots
                        )
                    else:
                        bot_msg = TEXT[lang]["USERS_ADD_BOTS_ALREADY_DISABLE"]
            else:
                bot_msg = TEXT[lang]["USERS_ADD_BOTS_NOT_ARG"]
        else:
            bot_msg = TEXT[lang]["USERS_ADD_BOTS_NOT_ARG"]
    elif is_admin is False:
        bot_msg = TEXT[lang]["CMD_NOT_ALLOW"]
    else:
        bot_msg = TEXT[lang]["CAN_NOT_GET_ADMINS"]
    if chat_type == "private":
        bot.send_message(chat_id, bot_msg)
    else:
        tlg_msg_to_selfdestruct(bot, update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_allow_user(bot, update, args):
    """Command /allow_user message handler"""
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    lang = get_chat_config(chat_id, "Language")
    is_admin = user_is_admin(bot, user_id, chat_id)
    if is_admin:
        if len(args) >= 1:
            user_alias = ""
            for arg in args:
                if user_alias == "":
                    user_alias = arg
                else:
                    user_alias = "{} {}".format(user_alias, arg)
            user_data = get_user_from_alias(chat_id, user_alias)
            if user_data is not None:
                if user_data["Allow_user"] is False:
                    user_data["Allow_user"] = True
                    update_user(chat_id, user_data)
                    bot_msg = TEXT[lang]["CMD_ALLOW_USR_OK"].format(user_alias)
                else:
                    bot_msg = TEXT[lang]["CMD_ALLOW_USR_ALREADY_ALLOWED"].format(
                        user_alias
                    )
            else:
                bot_msg = TEXT[lang]["CMD_ALLOW_USR_NOT_FOUND"]
        else:
            bot_msg = TEXT[lang]["CMD_ALLOW_USR_NOT_ARG"]
    else:
        bot_msg = TEXT[lang]["CMD_NOT_ALLOW"]
    bot.send_message(chat_id, bot_msg)


def cmd_enable(bot, update):
    """Command /enable message handler"""
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    enable = get_chat_config(chat_id, "Antispam")
    is_admin = user_is_admin(bot, user_id, chat_id)
    if is_admin is True:
        if enable:
            bot_msg = TEXT[lang]["ALREADY_ENABLE"]
        else:
            enable = True
            save_config_property(chat_id, "Antispam", enable)
            bot_msg = TEXT[lang]["ENABLE"]
    elif is_admin is False:
        bot_msg = TEXT[lang]["CMD_NOT_ALLOW"]
    else:
        bot_msg = TEXT[lang]["CAN_NOT_GET_ADMINS"]
    if chat_type == "private":
        bot.send_message(chat_id, bot_msg)
    else:
        tlg_msg_to_selfdestruct(bot, update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_disable(bot, update):
    """Command /disable message handler"""
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    enable = get_chat_config(chat_id, "Antispam")
    is_admin = user_is_admin(bot, user_id, chat_id)
    if is_admin is True:
        if enable:
            enable = False
            save_config_property(chat_id, "Antispam", enable)
            bot_msg = TEXT[lang]["DISABLE"]
        else:
            bot_msg = TEXT[lang]["ALREADY_DISABLE"]
    elif is_admin is False:
        bot_msg = TEXT[lang]["CMD_NOT_ALLOW"]
    else:
        bot_msg = TEXT[lang]["CAN_NOT_GET_ADMINS"]
    if chat_type == "private":
        bot.send_message(chat_id, bot_msg)
    else:
        tlg_msg_to_selfdestruct(bot, update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_notify_all_chats(bot, update):
    """Command /notify_all_chats message handler"""
    global owner_notify
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    user_id = update.message.from_user.id
    lang = get_chat_config(chat_id, "Language")
    if chat_type == "private":
        if user_id == conf.OWNER_ID:
            if owner_notify is False:
                owner_notify = True
                bot.send_message(chat_id, TEXT[lang]["CMD_NOTIFY_ALL"])
            else:
                bot.send_message(chat_id, TEXT[lang]["CMD_NOTIFYING"])
        else:
            bot.send_message(chat_id, TEXT[lang]["CMD_JUST_ALLOW_OWNER"])
    else:
        tlg_msg_to_selfdestruct(bot, update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CMD_JUST_ALLOW_IN_PRIVATE"])


def cmd_notify_discard(bot, update):
    """Command /notify_discard message handler"""
    global owner_notify
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    user_id = update.message.from_user.id
    lang = get_chat_config(chat_id, "Language")
    if chat_type == "private":
        if user_id == conf.OWNER_ID:
            if owner_notify is True:
                owner_notify = False
                bot.send_message(chat_id, TEXT[lang]["CMD_NOTIFY_DISCARD"])
            else:
                bot.send_message(chat_id, TEXT[lang]["CMD_NOTIFY_CANT_DISCARD"])
        else:
            bot.send_message(chat_id, TEXT[lang]["CMD_JUST_ALLOW_OWNER"])
    else:
        tlg_msg_to_selfdestruct(bot, update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CMD_JUST_ALLOW_IN_PRIVATE"])


def cmd_version(bot, update):
    """Command /version message handler"""
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    bot_msg = TEXT[lang]["VERSION"].format(conf.VERSION)
    if chat_type == "private":
        bot.send_message(chat_id, bot_msg)
    else:
        tlg_msg_to_selfdestruct(bot, update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_about(bot, update):
    """Command /about handler"""
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    bot_msg = TEXT[lang]["ABOUT_MSG"].format(
        conf.DEVELOPER, conf.REPOSITORY, conf.DEV_PAYPAL, conf.DEV_BTC
    )
    if chat_type == "private":
        bot.send_message(chat_id, bot_msg)
    else:
        tlg_msg_to_selfdestruct(bot, update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_test(bot, update):
    """Command for test purposes"""
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    info = "xx{}".format(get_admins_usernames_in_string(bot, chat_id))
    tlg_send_selfdestruct_msg(bot, chat_id, info)

####################################################################################################


def tlg_send_selfdestruct_msg(bot, chat_id, message):
    """tlg_send_selfdestruct_msg_in() with default delete time"""
    tlg_send_selfdestruct_msg_in(bot, chat_id, message, conf.T_DEL_MSG)


def tlg_msg_to_selfdestruct(bot, message):
    """tlg_msg_to_selfdestruct_in() with default delete time"""
    tlg_msg_to_selfdestruct_in(bot, message, conf.T_DEL_MSG)


def tlg_send_selfdestruct_msg_in(bot, chat_id, message, time_delete_min):
    """Send a telegram message that will be auto-delete in specified time"""
    # Send the message
    sent_msg = bot.send_message(chat_id, message)
    # If has been succesfully sent
    if sent_msg:
        # Get sent message ID and calculate delete time
        msg_id = sent_msg.message_id
        destroy_time = int(time()) + int(time_delete_min * 60)
        # Add sent message data to to-delete messages list
        sent_msg_data = OrderedDict(
            [("Chat_id", None), ("Msg_id", None), ("delete_time", None)]
        )
        sent_msg_data["Chat_id"] = chat_id
        sent_msg_data["Msg_id"] = msg_id
        sent_msg_data["delete_time"] = destroy_time
        to_delete_messages_list.append(sent_msg_data)
        log.debug(
            "Sent message has been set to selfdestruct.\n  (Chat, Msg, When) - "
            "({}, {}, {}).".format(chat_id, msg_id, (destroy_time - int(time())) / 60)
        )


def tlg_msg_to_selfdestruct_in(bot, message, time_delete_min):
    """Add a telegram message to be auto-delete in specified time"""
    # Get sent message ID and calculate delete time
    chat_id = message.chat_id
    msg_id = message.message_id
    destroy_time = int(time()) + int(time_delete_min * 60)
    # Add sent message data to to-delete messages list
    sent_msg_data = OrderedDict(
        [("Chat_id", None), ("Msg_id", None), ("delete_time", None)]
    )
    sent_msg_data["Chat_id"] = chat_id
    sent_msg_data["Msg_id"] = msg_id
    sent_msg_data["delete_time"] = destroy_time
    to_delete_messages_list.append(sent_msg_data)
    log.debug(
        "Chat message has been set to selfdestruct.\n  (Chat, Msg, When) - "
        "({}, {}, {}).".format(chat_id, msg_id, destroy_time)
    )


def selfdestruct_messages(bot):
    """Handle remove messages sent by the Bot with the timed self-delete function"""
    while True:
        # Check each Bot sent message
        for sent_msg in to_delete_messages_list:
            # If actual time is equal or more than the expected sent msg delete time
            if int(time()) >= sent_msg["delete_time"]:
                # Try to delete that sent message if possible (still exists)
                log.debug(
                    "Time accomplished for delete message.\n  (Chat, Msg) - ({}, {}).".format(
                        sent_msg["Chat_id"], sent_msg["Msg_id"]
                    )
                )
                log.debug("Trying to remove it...")
                try:
                    if bot.delete_message(sent_msg["Chat_id"], sent_msg["Msg_id"]):
                        to_delete_messages_list.remove(sent_msg)
                        log.debug("Message successfully removed.")
                except Exception as e:
                    log.error("{} Fail - Can't delete message.".format(e))
                    to_delete_messages_list.remove(sent_msg)
        # Wait 10s (release CPU usage)
        sleep(10)


def user_can_post_links(user, chat_id):
    """Check if the user can post a link
    given is his or her history, name, and other parameters
    """
    return True


def link_control(bot, update):
    """ This hook control if a user can post links or not
    in a message group. If the user is not allowed to post link,
    for any restriction applied, the whole message is deleted.
    """
    chat_id = update.message.chat.id
    msg_id = update.message.message_id
    user = update.message.left_chat_member
    entities = update.message.parse_entities()
    log.info("Found {} links".format(len(entities.items())))
    if not user_can_post_links(user, chat_id):
        try:
            result = bot.delete_message(chat_id, msg_id)
        except BadRequest:
            result = False
        if result:
            log.info("Message {} deleted".format(msg_id))
        else:
            log.error("Error deleting msg {}".format(msg_id))

####################################################################################################

# Main Function ###


def main():
    """Main Function"""
    # Initialize resources by populating files list and configs with chats found files
    log.info("Launching Bot...")
    initialize_resources()
    # Create an event handler (updater) for a Bot with the given Token and get the dispatcher
    updater = Updater(conf.TOKEN)
    dp = updater.dispatcher

    link_sandox_handler = MessageHandler(
        Filters.text
        & (Filters.entity(MessageEntity.URL) | Filters.entity(MessageEntity.TEXT_LINK)),
        link_control,
    )
    dp.add_handler(link_sandox_handler)

    # Set to dispatcher a not-command messages handler
    dp.add_handler(
        MessageHandler(
            Filters.text
            | Filters.photo
            | Filters.audio
            | Filters.voice
            | Filters.video
            | Filters.sticker
            | Filters.document
            | Filters.location
            | Filters.contact,
            msg_nocmd,
        )
    )
    # Set to dispatcher a new member join the group and member left the group events handlers
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_user))
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, left_user))
    # Set to dispatcher all expected commands messages handler
    dp.add_handler(CommandHandler("start", cmd_start))
    dp.add_handler(CommandHandler("help", cmd_help))
    dp.add_handler(CommandHandler("test", cmd_test))
    dp.add_handler(CommandHandler("commands", cmd_commands))
    dp.add_handler(CommandHandler("language", cmd_language, pass_args=True))
    dp.add_handler(CommandHandler("set_messages", cmd_set_messages, pass_args=True))
    dp.add_handler(CommandHandler("set_hours", cmd_set_hours, pass_args=True))
    dp.add_handler(CommandHandler("status", cmd_status))
    dp.add_handler(CommandHandler("call_admins", cmd_call_admins))
    dp.add_handler(CommandHandler("call_when_spam", cmd_call_when_spam, pass_args=True))
    dp.add_handler(CommandHandler("users_add_bots", cmd_users_add_bots, pass_args=True))
    dp.add_handler(CommandHandler("allow_user", cmd_allow_user, pass_args=True))
    dp.add_handler(CommandHandler("enable", cmd_enable))
    dp.add_handler(CommandHandler("disable", cmd_disable))
    dp.add_handler(CommandHandler("notify_all_chats", cmd_notify_all_chats))
    dp.add_handler(CommandHandler("notify_discard", cmd_notify_discard))
    dp.add_handler(CommandHandler("version", cmd_version))
    dp.add_handler(CommandHandler("about", cmd_about))
    
    # Allow restar
    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        execl(sys.executable, sys.executable, *sys.argv)

    def restart(bot, update):
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()

    dp.add_handler(CommandHandler('r', restart, filters=Filters.user(username='@aaloy')))        
    # Launch the Bot ignoring pending messages (clean=True)
    updater.start_polling(clean=True)
    # Handle self-messages delete
    selfdestruct_messages(updater.bot)
    # Allow bot stop
    updater.idle()


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    log.info("Bot Starting ...")
    main()
