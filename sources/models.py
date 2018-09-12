
from peewee import (
    SqliteDatabase,
    Model,
    BooleanField,
    CompositeKey,
    CharField,
    DateTimeField,
    BigIntegerField,
    ForeignKeyField,
    IntegerField,
)
import datetime
import constants as conf
import logging
from pathlib import Path
from urlextract import URLExtract
from exceptions import UserDoesNotExists

log = logging.getLogger(__name__)
db_path = "{}".format((Path(conf.DATA_DIR) / conf.DATABASE_NAME).resolve())


log.info("Connecting to {}".format(db_path))

db = SqliteDatabase(
    db_path,
    pragmas={
        "journal_mode": "wal",
        "cache_size": -1 * 64000,  # 64MB
        "foreign_keys": 1,
        "ignore_check_constraints": 0,
        "synchronous": 0,
    },
)


log.info("connecting to database {}".format(db_path))
db.connect(reuse_if_open=True)


class BaseModel(Model):
    class Meta:
        database = db


class Chat(BaseModel):
    chat_id = BigIntegerField(primary_key=True)
    created_date = DateTimeField(default=datetime.datetime.now)

    def get_chat_admins_ids(self, bot):
        """Returns a list with the ids of the administrators
        for the given chat_id and bot
        """
        try:
            return [x.user.id for x in bot.get_chat_administrators(self.chat_id)]
        except Exception as e:
            log.error("Unable to get administrators for {}".format(self.chat_id))
            log.error(e)
            return []

    def get_admins_usernames_in_string(self, bot):
        """Get all the group Administrators usernames/alias in a single line string separed by \' \'"""
        try:
            group_admins = bot.get_chat_administrators(self.chat_id)
        except Exception as e:
            log.debug(
                "Exception when checking Admins of {} - {}".format(self.chat_id, str(e))
            )
            return None
        list_admins_names = sorted(
            [
                "@{}".format(admin.user.username)
                for admin in group_admins
                if not admin.user.is_bot
            ]
        )
        return "\n".join(list_admins_names)

    def user_is_admin(self, bot, user_id):
        """Check if the specified user is an Administrator of a group given by IDs"""
        return user_id in self.get_chat_admins_ids(bot, self.chat_id)

    def bot_is_admin(self, bot):
        return bot.id in self.get_chat_admins_ids(bot, self.chat_id)


class User(BaseModel):
    chat = ForeignKeyField(Chat, backref="users")
    user_id = BigIntegerField()
    user_name = CharField()
    join_date = DateTimeField(default=datetime.datetime.now)
    num_messages = IntegerField(default=0)
    first_name = CharField(default="")
    last_name = CharField(default="")
    language_code = CharField(default=conf.INIT_LANG)
    verified = BooleanField(default=False)
    created_date = DateTimeField(default=datetime.datetime.now)

    def penalize(self, bot):
        """Penalize a user without baning him. On this way
        he would have the same treatement than a new and potential
        spammer user"""

        self.verified = False
        self.join_date = datetime.now()
        self.num_message = 0
        self.save()
        log.info("User: {} has been penalized".format(self.user_name))

    def can_post_links(self, bot):
        """The user is allowed to post urls if:
            a) is group admin
            b) is a new user that not has been joined recently
            thats is more than INIT_TIME_ALLOW_URLS minutes ago.
            c) is a new user who has posts more that
            INIT_MIN_MSG_ALLOW_URLS posts
        """
        if self.is_admin(bot) or self.is_verified:
            return True
        chat_config = Config.get(chat_id=self.chat.chat_id)

        user_hours_in_group = (
            datetime.datetime.now() - self.join_date
        ).total_seconds() // 3600

        value = (user_hours_in_group >= chat_config.time_for_allow_urls) or (
            self.num_messages >= chat_config.num_messages_for_allow_urls
        )
        if value and not self.is_verified:
            # if the user can post links mark it as verified
            self.verified = True
            self.save()
        return value

    def is_admin(self, bot):
        """Check if the specified user is an Administrator of a group given by IDs"""
        chat = Chat.get_by_id(self.chat.chat_id)
        return self.user_id in chat.get_chat_admins_ids(bot)

    @property
    def is_verified(self):
        chat = Chat.get_by_id(self.chat.chat_id)
        try:
            user = User.get(chat=chat, user_id=self.user_id)
            return user.verified
        except User.DoesNotExist:
            return None

    def update_message_counter(self, chat_id, delta=1):
        User.update(num_messages=User.num_messages + delta).where(
            User.user_id == self.user_id, User.chat.chat_id == chat_id
        )

    def try_to_verify(self, chat_id, msg_date):
        """Check if we can mark a user as verified"""
        if self.is_admin or self.is_verified:
            return False
        chat_config = Config.get(chat_id=chat_id)
        user_hours_in_group = (msg_date - self.join_date).total_seconds() // 3600
        verified = (user_hours_in_group >= chat_config.time_for_allow_urls) or (
            self.num_messages >= chat_config.num_messages_for_allow_urls
        )
        if verified:
            self.verified = True
            self.save()

    def is_spammer(self, chat_id, msg_date, text):
        """User is not enabled to post links due to his join date or the
        number of messages, and his still trying
        The user is allowed to post urls if:
            a) is group admin
            b) is a new user that not has been joined recently
            thats is more than INIT_TIME_ALLOW_URLS minutes ago.
            c) is a new user who has posts more that
            INIT_MIN_MSG_ALLOW_URLS posts
        """

        if self.is_admin or self.is_verified:
            return False
        chat_config = Config.get(chat_id=chat_id)

        # Let's check for urls
        extractor = URLExtract()
        any_url = extractor.has_urls(text)
        if not any_url:
            # if no url posted we'll give him the benefit of doubt
            return False

        # OK he has posts urls
        # Check if allowed by time or num os posted messages

        user_hours_in_group = (msg_date - self.join_date).total_seconds() // 3600
        return (user_hours_in_group < chat_config.time_for_allow_urls) or (
            self.num_messages < chat_config.num_messages_for_allow_urls
        )

    class Meta:
        primary_key = CompositeKey("chat", "user_id")


class Message(BaseModel):
    chat = ForeignKeyField(Chat, backref="messages")
    msg_id = IntegerField()
    user_id = BigIntegerField()
    user_name = CharField()
    text = CharField()
    date = DateTimeField()


class Config(BaseModel):
    chat = ForeignKeyField(Chat, backref="users")
    title = CharField(default="")
    link = CharField(default=conf.INIT_LINK)
    language = CharField(default=conf.INIT_LANG)
    antispam = BooleanField(conf.INIT_ENABLE)
    time_for_allow_urls = IntegerField(default=conf.INIT_TIME_ALLOW_URLS)
    num_messages_for_allow_urls = IntegerField(default=conf.INIT_MIN_MSG_ALLOW_URLS)
    call_admins_when_spam_detected = BooleanField(
        default=conf.INIT_CALL_ADMINS_WHEN_SPAM
    )
    allow_users_to_add_bots = BooleanField(default=conf.INIT_ALLOW_USERS_ADD_BOTS)
    enabled = BooleanField(default=True)

    @property
    def min_messages(self):
        return self.num_messages_for_allow_urls

    @property
    def min_time(self):
        """Minimum time in minutes that a user must be in the chat before is
        allowed to add urls"""
        return self.time_for_allow_urls

    @property
    def warn_admins(self):
        return self.call_admins_when_spam_detected

    def get_admins_usernames_in_string(self, bot):
        return self.chat.get_admins_usernames_in_string(bot)

    def user_is_admin(self, bot, user_id):
        return user_id in self.chat.get_chat_admins_ids(bot)

    class Meta:
        primary_key = CompositeKey("chat")


class Storage:
    def __init__(self):
        db.create_tables([Chat, Config, User, Message])
        db.connect(reuse_if_open=True)
        self.db = db

    def get_user(self, user_id, chat_id):
        chat, created = Chat.get_or_create(chat_id=chat_id)
        try:
            user = User.get(User.chat == chat_id, User.user_id == user_id)
            return user
        except User.DoesNotExist:
            raise UserDoesNotExists

    def get_chats(self):
        return Chat.select()

    def get_user_from_alias(self, chat_id, user_alias):
        """Get a user from its alias. Returns None if the
        user is not in the database, or the user object
        if she's found"""
        chat, created = Chat.get_or_create(chat_id=chat_id)
        try:
            user = User.get(User.chat == chat, User.user_name == user_alias)
            return user
        except User.DoesNotExist:
            raise UserDoesNotExists

    def get_chat_config(self, chat_id):
        """Check if chat config exits, if not creates a
        new configuration with the defaults"""
        chat, created = Chat.get_or_create(chat_id=chat_id)
        config, created = Config.get_or_create(chat=chat)
        return config

    def register_new_user(
        self, chat_id, user_id, user_name, first_name, last_name, join_date, allow_user
    ):
        if not first_name:
            first_name = user_name
        if not last_name:
            last_name = "-"
        chat, created = Chat.get_or_create(chat_id=chat_id)
        user, created = User.get_or_create(
            chat=chat,
            user_id=user_id,
            defaults={
                "user_name": user_name,
                "num_messages": 0,
                "join_date": join_date,
                "first_name": first_name,
                "last_name": last_name,
                "language_code": conf.INIT_LANG,
            },
        )
        return user


if __name__ == "__main__":
    storage = Storage()
