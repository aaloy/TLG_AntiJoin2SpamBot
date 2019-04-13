"""This module contains the events the bot deals with"""

import logging
import models
import datetime
from telegram.error import BadRequest
from urlextract import URLExtract
import tldextract
from utils import msg, text_msg, debug_print_tlg
import constants as conf
import notifications
from exceptions import UserDoesNotExists

# Globals ###

_ = lambda s: s

# Start the storage
storage = models.storage

log = logging.getLogger(__name__)


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
        lang, _("The Bot has been added to a new group:\n\n- ID: {}\n")
    ).format(chat_id)
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
    bot_message = text_msg(
        lang,
        _(
            "Hello, I am a Bot that fight against Spammers that join groups to publish their\n"
            "annoying and unwanted info. To work properly, give me Admin privileges.\n"
            "Check /help command for more information about my usage."
            ""
        ),
    )
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
        user = storage.get_user(user_id=msg_from_user_id, chat_id=chat_id)
    except UserDoesNotExists:
        storage.register_new_user(
            chat_id=chat_id,
            user_id=msg_from_user_id,
            user_name=from_user.name,
            first_name=from_user.first_name,
            last_name=from_user.last_name,
            join_date=datetime.datetime(1971, 1, 1),
            allow_user=False,
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
        join_user_name = "{} {}".format(join_user.first_name, join_user.last_name)

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
                        notifications.tlg_send_selfdestruct_msg(
                            bot, chat_id, bot_message
                        )
                    except Exception as e:
                        log.debug(
                            "Exception when deleting a Spammer (URL name) join "
                            "message - {}".format(str(e))
                        )
                        if str(e) == "Message can't be deleted":
                            bot_message = msg(
                                lang, "USER_URL_NAME_JOIN_CANT_REMOVE"
                            ).format(join_user_name)
                            notifications.tlg_send_selfdestruct_msg(
                                bot, chat_id, bot_message
                            )
                    continue
                else:
                    # Check if user name and last name are too long
                    if len(join_user_name) > conf.MAX_USERNAME_LENGTH:
                        join_user_name = "{}...".format(join_user_name)[0:10]
                        try:
                            bot.delete_message(chat_id, message_id)
                            bot_message = msg(lang, "USER_LONG_NAME_JOIN").format(
                                join_user_name
                            )
                            log.info(
                                "Spammer (long name) join message successfully removed."
                                "  (Chat) - ({}).".format(chat_id)
                            )

                        except Exception as e:
                            log.error(
                                "Exception when deleting a Spammer (long name) join "
                                "message - {}".format(str(e))
                            )
                            if str(e) == "Message can't be deleted":
                                bot_message = msg(
                                    lang, "USER_LONG_NAME_JOIN_CANT_REMOVE"
                                ).format(join_user_name)

                        notifications.tlg_send_selfdestruct_msg(
                            bot, chat_id, bot_message
                        )

                if len(join_user_alias) > conf.MAX_USERNAME_ALIAS:
                    # if the alias is to large, just short it
                    join_user_alias = "{}...".format(join_user_alias)[
                        0 : conf.MAX_USERNAME_ALIAS - 3
                    ]
            if storage.last_addition(chat_id) > conf.VERBOSE_LIMIT:
                notifications.tlg_send_selfdestruct_msg(
                    bot=bot,
                    chat_id=chat_id,
                    message=msg(lang, "WELCOME_MSG").format(
                        join_user_alias,
                        chat_config.num_messages_for_allow_urls,
                        chat_config.time_for_allow_urls,
                    ),
                    minutes=conf.VERBOSE_LIMIT,
                )

            storage.register_new_user(
                chat_id=chat_id,
                user_id=join_user_id,
                user_name=join_user_alias,
                first_name=join_user.first_name,
                last_name=join_user.last_name,
                join_date=join_date,
                allow_user=False,
            )

            log.info("{} added to the group {}".format(join_user_alias, chat_id))


def msg_nocmd(bot, update):
    """All Not-command messages handler.
        If the user does not exists assumes that the user joined before
        the bot, so allows pot post the message and creates the user

        If the user exist, checks for hers permisions to allow or not
        to post messages.
    """
    global owner_notify

    check_forwards(bot, update)

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
                notifications.notify_all_chats(bot, message)
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
            user = storage.get_user(user_id=user_id, chat_id=chat_id)
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
                    storage.save_message(chat_id, user_id, message.message_id, text)
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
                join_date=datetime.datetime(1971, 1, 1),
                allow_user=True,
            )
            user.num_messages = chat_config.num_messages_for_allow_urls + 1
            user.save()


def check_forwards(bot, update):
    """ We do not allow forwads fron any bot. This is to avoid attach that
    uses legitimate users to perform their spam
    """

    message = update.message
    chat_id = message.chat.id
    msg_id = message.message_id
    user_id = message.from_user.id
    forward_from = message.forward_from

    if forward_from.is_bot:
        try:
            storage.save_message(chat_id, user_id, msg_id, message.text)
            result = bot.delete_message(chat_id, msg_id)
        except BadRequest:
            result = False
        if result:
            log.info("Message {} deleted".format(msg_id))
        else:
            log.error("Error deleting msg {}".format(msg_id))


def link_control(bot, update):
    """ This hook control if a user can post links or not
    in a message group. If the user is not allowed to post link,
    for any restriction applied, the whole message is deleted.
    """
    check_forwards(bot, update)
    message = update.message
    chat_id = message.chat.id
    chat_config = storage.get_chat_config(chat_id)
    msg_id = message.message_id
    user_id = message.from_user.id

    if not chat_config.enabled:
        return

    try:
        user = storage.get_user(user_id=user_id, chat_id=chat_id)
    except UserDoesNotExists:
        user_name = update.message.from_user.name
        user = storage.register_new_user(
            chat_id=chat_id,
            user_id=user_id,
            user_name=user_name,
            first_name=update.message.from_user.first_name,
            last_name=update.message.from_user.last_name,
            join_date=datetime.datetime(1971, 1, 1),
            allow_user=False,
        )
        user.save()

    entities = update.message.parse_entities()
    log.info(
        "Found {} links on {}".format(
            len(entities.items()), update.message.from_user.name
        )
    )

    if not user.can_post_links(bot):
        # check if the links are in the white list
        in_white_list = False
        for e, link in entities.items():
            log.info("detected {}".format(link))
            ext = tldextract.extract(link)
            if not storage.is_link_in_white_list(ext.registered_domain):
                break
        else:
            in_white_list = True
            log.info("All links in white list")
        if not in_white_list:
            log.info("User {} can't post links in {}".format(user_id, chat_id))
            try:
                storage.save_message(chat_id, user_id, msg_id, message.text)
                result = bot.delete_message(chat_id, msg_id)
            except BadRequest:
                result = False
            if result:
                log.info("Message {} deleted".format(msg_id))
            else:
                log.error("Error deleting msg {}".format(msg_id))
    else:
        user.num_messages = chat_config.num_messages_for_allow_urls + 1
        user.try_to_verify(chat_id, datetime.datetime(1971, 1, 1))
        user.save()
