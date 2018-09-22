import logging
import models
from notifications import (
    tlg_msg_to_selfdestruct,
    send_bot_msg,
    tlg_send_selfdestruct_msg,
)
from utils import (
    user_is_admin,
    set_language,
    get_msg_file,
    msg,
    text_msg,
    _get_user_alias,
)
import constants as conf
from exceptions import UserDoesNotExists

# Globals ###

_ = lambda s: s

# Start the storage
storage = models.storage

log = logging.getLogger(__name__)


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
        bot_msg = get_msg_file(lang, "help")
    except OSError:
        bot_msg = _("Help file {} not found".format("help"))
    send_bot_msg(chat_type, bot, chat_id, bot_msg, update)


def cmd_commands(bot, update):
    """Command /commands message handler"""
    chat_type = update.message.chat.type
    chat_id = update.message.chat_id
    chat_config = storage.get_chat_config(chat_id)
    lang = chat_config.language
    try:
        bot_msg = get_msg_file(lang, "commands")
    except OSError:
        bot_msg = _("commands help file {} not found".format("commands"))
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
        bot_msg = msg(chat_config.language, "SET_MSG_CHANGED").format(num_msgs_provided)
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
    command_user = storage.get_user(user_id=user_id, chat_id=chat_id)
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
    command_user = storage.get_user(user_id=user_id, chat_id=chat_id)
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
        bot_msg = get_msg_file(lang, "about")
    except OSError:
        bot_msg = _("Help file {} not found".format("about"))
    send_bot_msg(chat_type, bot, chat_id, bot_msg, update)


def cmd_test(bot, update):
    """Command for test purposes"""
    chat_id = update.message.chat_id
    chat_config = storage.get_chat_config(chat_id)
    set_language(chat_config.language)
    info = _("These are the admins {}").format(
        chat_config.get_admins_usernames_in_string(bot)
    )
    tlg_send_selfdestruct_msg(bot, chat_id, info)
    other_info = _("import this")

    tlg_send_selfdestruct_msg(bot, chat_id, other_info)
