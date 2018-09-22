"""
Notifications module contains the funcionts needed to interact with
the chat and group and deal with messages
"""

import models
import logging
from time import sleep
import constants as conf

_ = lambda s: s

# Start the storage
storage = models.storage
log = logging.getLogger(__name__)


def tlg_send_selfdestruct_msg(bot, chat_id, message, minutes=0):
    """tlg_send_selfdestruct_msg_in() with default delete time
    If a diferent value of minutes is given we'll wait until then.
    """
    sent_msg = bot.send_message(chat_id, message)
    # If has been succesfully sent
    if sent_msg:
        # Get sent message ID and calculate delete time
        msg_id = sent_msg.message_id
        storage.add_message_to_destroy(chat_id, msg_id, minutes)


def tlg_msg_to_selfdestruct(bot, message, minutes=0):
    """tlg_msg_to_selfdestruct_in() with default delete time"""
    chat_id = message.chat_id
    msg_id = message.message_id
    storage.add_message_to_destroy(chat_id, msg_id, minutes)


def selfdestruct_messages(bot):
    """Handle remove messages sent by the Bot with the timed self-delete function"""
    while True:
        # Check each Bot sent message
        storage.delete_messages_list(bot)
        sleep(conf.DESTROY_FREQ)


def send_bot_msg(chat_type, bot, chat_id, bot_msg, update):
    if chat_type == "private":
        bot.send_message(chat_id, bot_msg)
    else:
        tlg_msg_to_selfdestruct(bot, update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


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
