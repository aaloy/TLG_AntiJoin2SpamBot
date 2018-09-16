#! /usr/bin/env python3
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


import sys
import signal
from os import execl
from threading import Thread
from datetime import datetime
from time import time, sleep
from collections import OrderedDict
from telegram import MessageEntity
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.error import BadRequest
from urlextract import URLExtract
from utils import user_is_admin, set_language, get_msg_file, msg, text_msg
from exceptions import UserDoesNotExists
import constants as conf
import logging
import models

# Globals ###
DEBUG = getattr(conf, "DEBUG", False)
_ = lambda s: s


to_delete_messages_list = []
sent_antispam_messages_list = []
owner_notify = False

# Start the storage
storage = models.Storage()

log = logging.getLogger(__name__)

####################################################################################################


def signal_handler(signal, frame):
    """Termination signals (SIGINT, SIGTERM) handler for program process"""
    log.info("Closing the bot ...")
    storage.db.close()
    sys.exit(0)


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


def notify_all_chats(bot, message):
    """Publish a notify message in all the Chats where the Bot is, except
    for the public chats (the ones with non negative ids"""
    # If directory data exists, check all subdirectories names (chats ID)
    chats = storage.get_chats()
    chats_candidates = [chat.chat_id for chat in chats if chat.startswith("-")]
    for chat_id in chats_candidates:
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
    chat_config = storage.get_chat_config(chat_id)
    if not chat_config.enabled:
        return

    message_id = update.message.message_id
    user = update.message.left_chat_member
    left_user_name = "{} {}".format(user.first_name, user.last_name)
    log.info("{} left the group {}".format(left_user_name, chat_id))

    try:
        extractor = URLExtract()
        if extractor.has_urls(left_user_name):
            bot.delete_message(chat_id, message_id)
        else:
            if len(left_user_name) > conf.MAX_USERNAME_LENGTH:
                bot.delete_message(chat_id, message_id)
    except Exception as e:
        log.error("Error on deleting left message {}".format(e))


def anti_spam_bot_added_event(chat_id, bot, update):
    """The anti spam bot has been added to the chat,
    update the chat configuration files, and inform the group
    about the bot being added"""
    chat_config = storage.get_chat_config(chat_id)
    admin_language = update.message.from_user.language_code[0:2]
    if admin_language == "es":
        lang = "ES"
    else:
        lang = "EN"
    chat_config.language = lang
    # Notify to Bot Owner that the Bot has been added to a group
    notify_msg = text_msg(
        lang,
        _("The Bot has been added to a new group:\n\n- ID: {}\n")).format(chat_id)
    chat_title = update.message.chat.title
    if chat_title:
        chat_config.title = chat_title
        notify_msg = text_msg(lang, _("{}- Title: {}\n")).format(notify_msg, chat_title)
    else:
        notify_msg = text_msg(lang, _("{}- Title: Unknown\n")).format(notify_msg)
    chat_link = update.message.chat.username
    if chat_link:
        chat_link = "@{}".format(chat_link)
        chat_config.chat_link = chat_link
        notify_msg = text_msg(_("{}- Link: {}\n")).format(notify_msg, chat_link)
    else:
        notify_msg = text_msg(_("{}- Link: Unknown\n")).format(notify_msg)
    admin_name = update.message.from_user.name
    admin_id = update.message.from_user.id
    notify_msg = "{}- Admin: {} [{}]".format(notify_msg, admin_name, admin_id)
    debug_print_tlg(bot, notify_msg)
    # Send bot join message
    bot_message = text_msg(lang, _("Hello, I am a Bot that fight against Spammers that join groups to publish their\n"
                    "annoying and unwanted info. To work properly, give me Admin privileges.\n"
                    "Check /help command for more information about my usage."""))
    chat_config.save()
    bot.send_message(chat_id, bot_message)


def try_to_add_a_bot_event(bot, message, join_user, chat_id):
    """Check if the join user is a bot and has been added by
    someone with authorization. Delete the bot if not.

    Returns true if the bot can be registered."""
    chat_config = storage.get_chat_config(chat_id)
    if not chat_config.enabled:
        return

    to_register_user = True

    # who is trying to register
    from_user = message.from_user
    msg_from_user_id = from_user.id

    # to who is registering
    join_user_id = join_user.id
    join_user_alias = join_user.name

    lang = chat_config.language

    try:
        user = storage.get_user(msg_from_user_id, chat_id)
    except UserDoesNotExists:
        storage.register_new_user(
            chat_id=chat_id,
            user_id=msg_from_user_id,
            user_name=from_user.name,
            first_name=from_user.first_name,
            last_name=from_user.last_name,
            join_date=datetime(1971, 1, 1),
            allow_user=False
                    )

    # If the user that has been added the Bot is not an Admin
    if not user.is_admin(bot):
        # If not allow users to add Bots
        if not chat_config.allow_users_to_add_bots:
            # Kick the Added Bot and notify
            log.debug("An user has added a Bot.\n  (Chat) - ({}).".format(chat_id))
            try:
                bot.kickChatMember(chat_id, join_user_id)
                bot_message = msg(lang, "USER_CANT_ADD_BOT").format(
                    message.from_user.name, join_user_alias
                )
                user.penalize(bot)
                log.debug(
                    "Added Bot successfully kicked.\n  (Chat) - ({}).".format(chat_id)
                )
            except Exception as e:
                log.debug("Exception when kicking a Bot - {}".format(str(e)))
                if str(e) == "Not enough rights to restrict/unrestrict chat member":
                    bot_message = msg(lang, "USER_CANT_ADD_BOT_CANT_KICK").format(
                        message.from_user.name, join_user.name
                    )

            if chat_config.call_admins_when_spam_detected:
                admins = chat_config.get_admins_usernames_in_string(bot)
                if admins:
                    bot_message = "{}{}".format(
                        bot_message, msg(lang, "CALLING_ADMINS").format(admins)
                    )
            bot.send_message(chat_id, bot_message)
            to_register_user = False
    return to_register_user


def new_user(bot, update):
    """New member join the group event handler"""

    message = update.message
    chat_id = message.chat_id
    chat_config = storage.get_chat_config(chat_id)
    if not chat_config.enabled:
        return
    message_id = message.message_id
    msg_from_user_id = message.from_user.id
    join_date = message.date

    lang = chat_config.language
    # For each new user that join or has been added
    for join_user in message.new_chat_members:
        join_user_id = join_user.id
        join_user_alias = join_user.name
        join_user_name = "{} {}".format(
            join_user.first_name, join_user.last_name
        )

        # If the added user is not myself (this Bot)
        if bot.id == join_user_id:
            # The Anti-Spam Bot has been added to a group
            anti_spam_bot_added_event(chat_id, bot, update)
            continue
        else:
            to_register_user = True
            # If the message user source is not the join user,
            # means it has been invited/added by another
            if msg_from_user_id != join_user_id and join_user.is_bot:
                # If a user has added a bot check if could be added and delete id if not
                to_register_user = try_to_add_a_bot_event(
                    bot, msg_from_user_id, join_user, chat_id
                )
                if not to_register_user:
                    # if is not a legit bot log and no nothing
                    log.warn(
                        "{msg_from_user_id} has tried to join {join_user} to  {chat_id}".format(
                            msg_from_user_id=msg_from_user_id,
                            join_user=join_user,
                            chat_id=chat_id,
                        )
                    )
                    continue
            if to_register_user:
                # Check if there is an URL in the user name
                extractor = URLExtract()
                has_url = extractor.has_urls(join_user_name) or extractor.has_urls(
                    join_user_alias
                )
                if has_url:
                    log.warn(
                        "Spammer (URL name) join detected.\n  (Chat) - ({}).".format(
                            chat_id
                        )
                    )
                    if len(join_user_name) > 15:
                        join_user_name = "{}...".format(join_user_name)[0:10]
                    try:
                        bot.delete_message(chat_id, message_id)
                        bot_message = msg(lang, "USER_URL_NAME_JOIN").format(
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
                            bot_message = msg(lang, "USER_URL_NAME_JOIN_CANT_REMOVE").format(join_user_name)
                            tlg_send_selfdestruct_msg(bot, chat_id, bot_message)
                    continue
                else:
                    # Check if user name and last name are too long
                    if len(join_user_name) > conf.MAX_USERNAME_LENGTH:
                        join_user_name = "{}...".format(join_user_name)[0:10]
                        try:
                            bot.delete_message(chat_id, message_id)
                            bot_message = msg(lang, "USER_LONG_NAME_JOIN").format(join_user_name)
                            log.info(
                                "Spammer (long name) join message successfully removed.\n"
                                "  (Chat) - ({}).".format(chat_id)
                            )

                        except Exception as e:
                            log.error(
                                "Exception when deleting a Spammer (long name) join "
                                "message - {}".format(str(e))
                            )
                            if str(e) == "Message can't be deleted":
                                bot_message = msg(lang, "USER_LONG_NAME_JOIN_CANT_REMOVE").format(join_user_name)

                        tlg_send_selfdestruct_msg(bot, chat_id, bot_message)

                if len(join_user_alias) > conf.MAX_USERNAME_ALIAS:
                    # if the alias is to large, just short it
                    join_user_alias = "{}...".format(join_user_alias)[
                        0:conf.MAX_USERNAME_ALIAS - 3
                    ]

            storage.register_new_user(
                    chat_id=chat_id,
                    user_id=join_user_id,
                    user_name=join_user_alias,
                    first_name=join_user.first_name,
                    last_name=join_user.last_name,
                    join_date=join_date,
                    allow_user=False
                )
            log.info('{} added to the group {}'.format(join_user_alias, chat_id))


def msg_nocmd(bot, update):
    """All Not-command messages handler.
        If the user does not exists assumes that the user joined before
        the bot, so allows pot post the message and creates the user

        If the user exist, checks for hers permisions to allow or not
        to post messages.
    """
    global owner_notify

    message = update.message
    chat_id = message.chat_id
    chat_config = storage.get_chat_config(chat_id)
    if not chat_config.enabled:
        return

    chat_type = message.chat.type
    user_id = message.from_user.id
    lang = chat_config.language

    if chat_type == "private":
        if user_id == conf.OWNER_ID:
            if owner_notify:
                owner_notify = False
                message = message.text
                notify_all_chats(bot, message)
                bot.send_message(chat_id, msg(lang, "CMD_NOTIFY_ALL_OK"))
    else:
        if message.chat.title:
            chat_config.chat_title = message.chat.title
        if message.chat.username:
            chat_config.chat_link = "@{}".format(message.chat.username)
        user_name = message.from_user.name
        msg_date = (message.date).now().strftime("%Y-%m-%d %H:%M:%S")
        text = message.text
        text = (
            text
            if text is not None
            else getattr(message, "caption_html", getattr(message, "caption", None))
        )
        # If user not yet register, it means it was there before the bot,
        # assume that is legit, add to users file, else, get his number of published msgs
        try:
            user = storage.get_user(chat_id, user_id)
            user.update_message_counter(chat_id=chat_id, delta=1)
            if text:
                if user.is_spammer(chat_id, msg_date, text):
                    log.warn(
                        "Spam message detected.\n  (Chat, User, Message) -({}, {}, {}).".format(
                            chat_id, user_name, user_id
                        )
                    )
                    # Do not count this message as legit
                    user.update_message_counter(delta=-1)
                    # Save message for future reference
                    storage.save_message(chat_id, user_id, text)
                    bot.delete_message(chat_id, message.message_id)
                else:
                    user.try_to_verify(chat_id, msg_date)
        except UserDoesNotExists:

            user = storage.register_new_user(
                    chat_id=chat_id,
                    user_id=user_id,
                    user_name=user_name,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name,
                    join_date=datetime(1971, 1, 1),
                    allow_user=True
                )
            user.num_messages = chat_config.num_messages_for_allow_urls + 1
            user.save()


def link_control(bot, update):
    """ This hook control if a user can post links or not
    in a message group. If the user is not allowed to post link,
    for any restriction applied, the whole message is deleted.
    """
    chat_id = update.message.chat.id
    chat_config = storage.get_chat_config(chat_id)
    msg_id = update.message.message_id
    user_id = update.message.from_user.id

    if not chat_config.enabled:
        return

    try:
        user = storage.get_user(user_id, chat_id)
    except UserDoesNotExists:
        user_name = update.message.from_user.name
        user = storage.register_new_user(
                chat_id=chat_id,
                user_id=user_id,
                user_name=user_name,
                first_name=update.message.from_user.first_name,
                last_name=update.message.from_user.last_name,
                join_date=datetime(1971, 1, 1),
                allow_user=False
            )
        user.save()

    entities = update.message.parse_entities()
    log.info("Found {} links".format(len(entities.items())))
    if not user.can_post_links(bot):
        log.info("User {} can't post links in {}".format(user_id, chat_id))
        try:
            result = bot.delete_message(chat_id, msg_id)
        except BadRequest:
            result = False
        if result:
            log.info("Message {} deleted".format(msg_id))
        else:
            log.error("Error deleting msg {}".format(msg_id))
    else:
        user.num_messages = chat_config.num_messages_for_allow_urls + 1
        user.try_to_verify(chat_id, datetime(1971, 1, 1))
        user.save()


####################################################################################################

# Received Telegram command messages handlers ###


def cmd_start(bot, update):
    """Command /start message handler"""
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    chat_config = storage.get_chat_config(chat_id)
    chat_config.enabled = True
    chat_config.save()
    lang = chat_config.language
    if chat_type == "private":
        log.info("The bot started in {} private chat".format(chat_id))
        bot.send_message(chat_id, msg(lang, "START"))
    else:
        log.info("The bot started in {} group chat".format(chat_id))
        tlg_msg_to_selfdestruct(bot, update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, msg(lang, "START"))


def cmd_help(bot, update):
    """Command /help message handler"""
    chat_type = update.message.chat.type
    chat_id = update.message.chat_id
    chat_config = storage.get_chat_config(chat_id)
    lang = chat_config.language
    try:
        bot_msg = get_msg_file(lang, 'help')
    except OSError:
        bot_msg = _('Help file {} not found'.format('help'))
    send_bot_msg(chat_type, bot, chat_id, bot_msg, update)


def cmd_commands(bot, update):
    """Command /commands message handler"""
    chat_type = update.message.chat.type
    chat_id = update.message.chat_id
    chat_config = storage.get_chat_config(chat_id)
    lang = chat_config.language
    try:
        bot_msg = get_msg_file(lang, 'commands')
    except OSError:
        bot_msg = _('commands help file {} not found'.format('commands'))
    send_bot_msg(chat_type, bot, chat_id, bot_msg, update)


def cmd_language(bot, update, args):
    """Command /language message handler. Defauts to the configuration
    language if theris a problem or language does not exists."""
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    chat_config = storage.get_chat_config(chat_id)
    lang = chat_config.language
    if chat_config.user_is_admin(bot, user_id):
        if chat_type != "private":
            allow_command = user_is_admin(bot, user_id, chat_id)
        if allow_command:
            lang_provided = (
                args[0] if (args is not None) and len(args) > 0 else conf.INIT_LANG
            )
            lang_provided = lang_provided.upper()
            lang = lang_provided if lang_provided in conf.LANGUAGES else conf.INIT_LANG
            chat_config.language = lang
            chat_config.save()
            bot_msg = msg(lang, "LANG_CHANGE").format(lang)
    else:
        bot_msg = msg(lang, "CMD_NOT_ALLOW")
    send_bot_msg(chat_type, bot, chat_id, bot_msg, update)


def cmd_set_messages(bot, update, args):
    """Command /set_messages message handler"""
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    chat_config = storage.get_chat_config(chat_id)
    if chat_config.user_is_admin(bot, user_id):
        num_msgs_provided = (
            args[0]
            if (args is not None) and len(args) > 0
            else conf.INIT_MIN_MSG_ALLOW_URLS
        )
        try:
            num_msgs_provided = abs(int(num_msgs_provided))
        except ValueError:
            num_msgs_provided = conf.INIT_MIN_MSG_ALLOW_URLS
        chat_config.num_messages_for_allow_urls = num_msgs_provided
        chat_config.save()
        bot_msg = msg(chat_config.language, "SET_MSG_CHANGED").format(
            num_msgs_provided
        )
    send_bot_msg(chat_type, bot, chat_id, bot_msg, update)


def cmd_set_hours(bot, update, args):
    """Command /set_hours message handler
    Sets the waiting number of hours before allow a user to post an url
    If the value is not valid returns to default.
    """
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    chat_config = storage.get_chat_config(chat_id)
    if chat_config.user_is_admin(bot, user_id):
        hours_provided = (
            args[0]
            if (args is not None) and len(args) > 0
            else conf.INIT_TIME_ALLOW_URLS
        )
        try:
            hours_provided = abs(int(hours_provided))
        except ValueError:
            hours_provided = conf.INIT_TIME_ALLOW_URLS
        chat_config.time_for_allow_urls = hours_provided
        bot_msg = msg(chat_config.language, "SET_HOURS_CHANGED").format(hours_provided)
    else:
        bot_msg = msg(chat_config.language, "CMD_NOT_ALLOW")
    send_bot_msg(chat_type, bot, chat_id, bot_msg, update)


def cmd_status(bot, update):
    """Command /status message handler"""
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    chat_config = storage.get_chat_config(chat_id)
    bot_msg = msg(chat_config.language, "STATUS").format(
        chat_config.num_messages_for_allow_urls,
        chat_config.time_for_allow_urls,
        chat_config.call_admins_when_spam_detected,
        chat_config.allow_users_to_add_bots,
        chat_config.enabled,
    )
    send_bot_msg(chat_type, bot, chat_id, bot_msg, update)


def cmd_call_admins(bot, update):
    """Command /call_admins message handler"""
    chat_id = update.message.chat_id
    chat_config = storage.get_chat_config(chat_id)
    admins = chat_config.get_admins_usernames_in_string(bot)
    if admins:
        bot_msg = msg(chat_config.lang, "CALLING_ADMINS").format(admins)
    else:
        bot_msg = msg(chat_config.lang, "CALLING_ADMINS_NO_ADMINS")
    bot.send_message(chat_id, bot_msg)


def cmd_call_when_spam(bot, update, args):
    """Command /call_when_spam message handler.
    Allows enable/disable as commands. If no valid arguments are
    provided it returns to the default value"""

    chat_id = update.message.chat_id
    chat_config = storage.get_chat_config(chat_id)
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    lang = chat_config.language
    if chat_config.user_is_admin(bot, user_id):
        new_value = (
            args[0].upper()
            if (args is not None) and len(args) > 0
            else conf.INIT_CALL_ADMINS_WHEN_SPAM
        )
        if new_value in ["ENABLE", "DISABLE"]:
            chat_config.call_admins_when_spam_detected = new_value == "ENABLE"
            if chat_config.call_admins_when_spam_detected:
                bot_msg = msg(lang, "CALL_WHEN_SPAM_ENABLE")
            else:
                bot_msg = msg(lang, "CALL_WHEN_SPAM_DISABLE")
        else:
            new_value = conf.INIT_CALL_ADMINS_WHEN_SPAM
            bot_msg = msg(lang, "CALL_WHEN_SPAM_NOT_ARG")
        chat_config.save()
    else:
        bot_msg = msg(lang, "CMD_NOT_ALLOW")
    send_bot_msg(chat_type, bot, chat_id, bot_msg, update)


def cmd_users_add_bots(bot, update, args):
    """Command /users_add_bots message handler"""

    chat_id = update.message.chat_id
    chat_config = storage.get_chat_config(chat_id)
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    lang = chat_config.language
    if chat_config.user_is_admin(bot, user_id):
        new_value = (
            args[0].upper()
            if (args is not None) and len(args) > 0
            else conf.INIT_ALLOW_USERS_ADD_BOTS
        )
        if new_value in ["ENABLE", "DISABLE"]:
            chat_config.call_admins_when_spam_detected = new_value == "ENABLE"
            if chat_config.call_admins_when_spam_detected:
                bot_msg = msg(lang, "USERS_ADD_BOTS_ENABLE")
            else:
                bot_msg = msg(lang, "USERS_ADD_BOTS_DISABLE")
        else:
            chat_config.call_admins_when_spam_detected = conf.INIT_CALL_ADMINS_WHEN_SPAM
            bot_msg = msg(lang, "USERS_ADD_BOTS_NOT_ARG")
        chat_config.save()
    else:
        bot_msg = msg(lang, "CMD_NOT_ALLOW")
    send_bot_msg(chat_type, bot, chat_id, bot_msg, update)


def _get_user_alias(args):
    """Buids the user alias from the bot command"""
    user_alias = ""
    if len(args) >= 1:
        for arg in args:
            if user_alias == "":
                user_alias = arg
            else:
                user_alias = "{} {}".format(user_alias, arg)
    return user_alias


def cmd_allow_user(bot, update, args):
    """Command /allow_user message handler
        Givies the rights to post messages for
        the chat to the user alias passed as args.

        Checks that the user who runs the command is admin
        and changes the destination user configuration."""

    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    user_id = update.message.from_user.id
    chat_config = storage.get_chat_config(chat_id)
    # command user
    command_user = storage.get_user(user_id, chat_id)
    # destination_user
    destination_user_alias = _get_user_alias(args)
    lang = chat_config.language

    if command_user.is_admin(bot):
        try:
            destination_user = storage.get_user_from_alias(
                chat_id, destination_user_alias
            )
            if not destination_user.verified:
                destination_user.verified = True
                destination_user.save()
                bot_msg = msg(lang, "CMD_ALLOW_USR_OK").format(destination_user_alias)
            else:
                bot_msg = msg(lang, "CMD_ALLOW_USR_ALREADY_ALLOWED").format(
                    destination_user_alias
                )
        except UserDoesNotExists:
            bot_msg = msg(lang, "CMD_ALLOW_USR_NOT_FOUND")
    else:
        bot_msg = msg(lang, "CMD_NOT_ALLOW")

    send_bot_msg(chat_type, bot, chat_id, bot_msg, update)


def cmd_disable_user(bot, update, args):
    """Command disable_user message handler
        Removes the rights to post link messages to
        the chat to the user alias passed as args and
        considers him a possible spammer.

        Checks that the user who runs the command is admin
        and changes the destination user configuration."""

    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    user_id = update.message.from_user.id
    chat_config = storage.get_chat_config(chat_id)
    # command user
    command_user = storage.get_user(user_id, chat_id)
    # destination_user
    destination_user_alias = _get_user_alias(args)
    lang = chat_config.language

    if command_user.is_admin(bot):
        try:
            destination_user = storage.get_user_from_alias(
                chat_id, destination_user_alias
            )
            destination_user.penalize()
            bot_msg = _("User {} has ben considered a potential spammer").format(
                    destination_user_alias
                )
        except UserDoesNotExists:
            bot_msg = _("User not found")
    else:
        bot_msg = msg(lang, "CMD_NOT_ALLOW")

    send_bot_msg(chat_type, bot, chat_id, bot_msg, update)


def cmd_enable(bot, update):
    """Command /enable message handler.
    Enables bot spam filter actions"""

    chat_id = update.message.chat_id
    chat_config = storage.get_chat_config(chat_id)
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    lang = chat_config.language
    if chat_config.user_is_admin(bot, user_id):
        if chat_config.enabled:
            bot_msg = msg(lang, "ALREADY_ENABLE")
        else:
            bot_msg = msg(lang, "ENABLE")
            chat_config.enabled = True
            chat_config.save()
    else:
        bot_msg = msg(lang, "CMD_NOT_ALLOW")
    send_bot_msg(chat_type, bot, chat_id, bot_msg, update)


def cmd_disable(bot, update):
    """Command /disable message handler"""

    chat_id = update.message.chat_id
    chat_config = storage.get_chat_config(chat_id)
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    lang = chat_config.language

    if chat_config.user_is_admin(bot, user_id):
        if not chat_config.enabled:
            bot_msg = msg(lang, "ALREADY_DISABLE")
        else:
            bot_msg = msg(lang, "DISABLE")
            chat_config.enabled = False
            chat_config.save()
    else:
        bot_msg = msg(lang, "CMD_NOT_ALLOW")
    send_bot_msg(chat_type, bot, chat_id, bot_msg, update)


def cmd_notify_all_chats(bot, update):
    """Command /notify_all_chats message handler"""
    global owner_notify
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    user_id = update.message.from_user.id
    chat_config = storage.get_chat_config(chat_id)
    lang = chat_config.language
    if chat_type == "private":
        if user_id == conf.OWNER_ID:
            if owner_notify is False:
                owner_notify = True
                bot.send_message(chat_id, msg(lang, "CMD_NOTIFY_ALL"))
            else:
                bot.send_message(chat_id, msg(lang, "CMD_NOTIFYING"))
        else:
            bot.send_message(chat_id, msg(lang, "CMD_JUST_ALLOW_OWNER"))
    else:
        tlg_msg_to_selfdestruct(bot, update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, msg(lang, "CMD_JUST_ALLOW_IN_PRIVATE"))


def cmd_notify_discard(bot, update):
    """Command /notify_discard message handler"""
    global owner_notify
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    user_id = update.message.from_user.id
    chat_config = storage.get_chat_config(chat_id)
    lang = chat_config.language
    if chat_type == "private":
        if user_id == conf.OWNER_ID:
            if owner_notify is True:
                owner_notify = False
                bot.send_message(chat_id, msg(lang, "CMD_NOTIFY_DISCARD"))
            else:
                bot.send_message(chat_id, msg(lang, "CMD_NOTIFY_CANT_DISCARD"))
        else:
            bot.send_message(chat_id, msg(lang, "CMD_JUST_ALLOW_OWNER"))
    else:
        tlg_msg_to_selfdestruct(bot, update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, msg(lang, "CMD_JUST_ALLOW_IN_PRIVATE"))


def cmd_version(bot, update):
    """Command /version message handler"""
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    chat_config = storage.get_chat_config(chat_id)
    lang = chat_config.language
    bot_msg = text_msg(lang, _("Actual Bot version: {}")).format(conf.VERSION)
    send_bot_msg(chat_type, bot, chat_id, bot_msg, update)


def cmd_about(bot, update):
    """Command /about handler"""
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    chat_config = storage.get_chat_config(chat_id)
    lang = chat_config.language
    try:
        bot_msg = get_msg_file(lang, 'about')
    except OSError as e:
        bot_msg = _('Help file {} not found'.format('about'))
    send_bot_msg(chat_type, bot, chat_id, bot_msg, update)


def cmd_test(bot, update):
    """Command for test purposes"""
    chat_id = update.message.chat_id
    chat_config = storage.get_chat_config(chat_id)
    set_language(chat_config.language)
    info = _("These are the admins {}").format(chat_config.get_admins_usernames_in_string(bot))
    tlg_send_selfdestruct_msg(bot, chat_id, info)
    other_info = _("this *is* \n"
                   "a _great_ test\n\n"
                   "no trobes")

    tlg_send_selfdestruct_msg(bot, chat_id, other_info)


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


def send_bot_msg(chat_type, bot, chat_id, bot_msg, update):
    if chat_type == "private":
        bot.send_message(chat_id, bot_msg)
    else:
        tlg_msg_to_selfdestruct(bot, update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


####################################################################################################

# Main Function ###


def main():
    """Main Function"""
    # Initialize resources by populating files list and configs with chats found files
    log.info("Launching Bot...")

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
    dp.add_handler(CommandHandler("disable_user", cmd_disable_user, pass_args=True))
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
        update.message.reply_text("Bot is restarting...")
        Thread(target=stop_and_restart).start()

    dp.add_handler(
        CommandHandler("r", restart, filters=Filters.user(username=conf.MANAGERS_LIST))
    )
    # Launch the Bot ignoring pending messages (clean=True)
    updater.start_polling(clean=True, poll_interval=5, timeout=10)
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
