import gettext
import logging
import constants as conf
from pathlib import Path

log = logging.getLogger(__name__)


def debug_print_tlg(bot, text):
    """Function to send text message to TLG chat just when DEBUG flag is active"""
    if conf.DEBUG:
        try:
            bot.send_message(conf.DEBUG_TO_CHAT, text)
            log.debug("{}-{}".format(conf.DEBUG_TO_CHAT, text))
        except:
            pass


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


def get_chat_admins_ids(bot, chat_id):
    """Returns a list with the ids of the administrators
    for the given chat_id and bot
    """
    try:
        return [x.user.id for x in bot.get_chat_administrators(chat_id)]
    except Exception as e:
        log.error("Unable to get administrators for {}".format(chat_id))
        log.error(e)
        return []


def user_is_admin(bot, user_id, chat_id):
    """Check if the specified user is an Administrator of a group given by IDs"""
    return user_id in get_chat_admins_ids(bot, chat_id)


def bot_is_admin(bot, chat_id):
    return bot.id in get_chat_admins_ids(bot, chat_id)


def set_language(lang="en"):
    localedir = "{}".format((Path(conf.ROOT_DIR) / "locale").resolve())
    translate = gettext.translation("messages", localedir, languages=[lang])
    translate.install()
    return translate


def get_msg_file(lang, command_name):
    """Returns the message content from a file.
    I could return a FileNotFound exception if the file does not
    exists."""

    lang = lang.lower()
    arx = Path(conf.ROOT_DIR) / "doc" / "{}/{}.mk".format(lang, command_name)
    with open(arx) as f:
        bot_msg = "".join(f.readlines())
    return bot_msg

    """"
    pybabel extract --project=bot --input-dirs=. -o messages.pot
    pybabel init -i messages.po -l fr -d locale
    pybabel update  -i messages.pot -l en -d locale
    """


def text_msg(lang, text):
    translate = set_language(lang=lang.lower())
    return translate.gettext(text)


def msg(lang, key):
    """Gets the message from the contants file in the language
    neeeded. Returns the key itself if not found"""

    translate = set_language(lang=lang.lower())
    s = conf.MSG.get(key, key)
    return translate.gettext(s)
