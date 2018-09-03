import gettext
import logging
import constants as conf
from pathlib import Path


log = logging.getLogger(__name__)


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

    """"
    pybabel extract --project=bot --input-dirs=. -o messages.pot
    pybabel init -i messages.po -l fr -d locale
    pybabel update  -i messages.pot -l en -d locale
    """

