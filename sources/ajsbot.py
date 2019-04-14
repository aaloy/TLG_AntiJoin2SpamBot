#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script:
    ajsbot.py
Description:
    Telegram Bot that figths against the spammer users that join groups to publish
    their annoying and unwanted info.
    Author:
        Jose Rios Rubio
    Branch:
        aaloy
Creation date:
    04/04/2018
"""

####################################################################################################

# Imported modules


import sys
import signal
from os import execl
from threading import Thread
from telegram import MessageEntity
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import constants as conf
import commands
import events
import notifications
import logging
import models

# Globals ###
DEBUG = getattr(conf, "DEBUG", False)
_ = lambda s: s


to_delete_messages_list = []
sent_antispam_messages_list = []
owner_notify = False

# Start the storage
storage = models.storage

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


def main():
    """Main Function"""
    # Initialize resources by populating files list and configs with chats found files
    log.info("Launching Bot...")

    # Create an event handler (updater) for a Bot with the given Token and get the dispatcher
    updater = Updater(conf.TOKEN)
    dp = updater.dispatcher

    link_sanbox_handler = MessageHandler(
        Filters.text
        & (Filters.entity(MessageEntity.URL) | Filters.entity(MessageEntity.TEXT_LINK)),
        events.link_control,
    )
    dp.add_handler(link_sanbox_handler)

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
            events.msg_nocmd,
        )
    )
    # Set to dispatcher a new member join the group and member left the group events handlers
    dp.add_handler(
        MessageHandler(Filters.status_update.new_chat_members, events.new_user)
    )
    dp.add_handler(
        MessageHandler(Filters.status_update.left_chat_member, events.left_user)
    )
    # Set to dispatcher all expected commands messages handler
    dp.add_handler(CommandHandler("start", commands.cmd_start))
    dp.add_handler(CommandHandler("help", commands.cmd_help))
    dp.add_handler(CommandHandler("test", commands.cmd_test))
    dp.add_handler(CommandHandler("commands", commands.cmd_commands))
    dp.add_handler(CommandHandler("language", commands.cmd_language, pass_args=True))
    dp.add_handler(
        CommandHandler("set_messages", commands.cmd_set_messages, pass_args=True)
    )
    dp.add_handler(CommandHandler("set_hours", commands.cmd_set_hours, pass_args=True))
    dp.add_handler(CommandHandler("status", commands.cmd_status))
    dp.add_handler(CommandHandler("call_admins", commands.cmd_call_admins))
    dp.add_handler(
        CommandHandler("call_when_spam", commands.cmd_call_when_spam, pass_args=True)
    )
    dp.add_handler(
        CommandHandler("users_add_bots", commands.cmd_users_add_bots, pass_args=True)
    )
    dp.add_handler(
        CommandHandler("allow_user", commands.cmd_allow_user, pass_args=True)
    )
    dp.add_handler(
        CommandHandler("disable_user", commands.cmd_disable_user, pass_args=True)
    )
    dp.add_handler(CommandHandler("enable", commands.cmd_enable))
    dp.add_handler(CommandHandler("disable", commands.cmd_disable))
    dp.add_handler(CommandHandler("notify_all_chats", commands.cmd_notify_all_chats))
    dp.add_handler(CommandHandler("notify_discard", commands.cmd_notify_discard))
    dp.add_handler(CommandHandler("version", commands.cmd_version))
    dp.add_handler(CommandHandler("about", commands.cmd_about))

    # Allow restar
    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        execl(sys.executable, sys.executable, *sys.argv)

    def restart(bot, update):
        models.storage.clean_cache()
        update.message.reply_text("Bot is restarting...")
        Thread(target=stop_and_restart).start()

    dp.add_handler(
        CommandHandler("r", restart, filters=Filters.user(username=conf.MANAGERS_LIST))
    )
    # Launch the Bot ignoring pending messages (clean=True)
    updater.start_polling(clean=True, poll_interval=5, timeout=20)
    # Handle self-messages delete
    notifications.selfdestruct_messages(updater.bot)
    # Allow bot stop
    updater.idle()


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    log.info("Bot Starting ...")
    main()
