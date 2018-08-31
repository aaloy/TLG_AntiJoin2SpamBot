
from peewee import (
    SqliteDatabase,
    Model,
    IntegrityError,
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

log = logging.getLogger(__name__)
db_path = "{}".format((Path(conf.DATA_DIR) / conf.DATABASE_NAME).resolve())

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
db.connect()


class BaseModel(Model):
    class Meta:
        database = db


class Chat(BaseModel):
    chat_id = BigIntegerField(primary_key=True)
    created_date = DateTimeField(default=datetime.datetime.now)


class User(BaseModel):
    chat = ForeignKeyField(Chat, backref="users")
    user_id = BigIntegerField()
    user_name = CharField()
    join_date = DateTimeField(default=datetime.datetime.now)
    num_messages = IntegerField(default=0)
    last_name = CharField()
    language_code = CharField()
    created_date = DateTimeField(default=datetime.datetime.now)

    def is_url_allowed(self):
        """The user is allowed to post urls if:
            a) is group admin
            b) is a new user that not has been joined recently 
            thats is more than INIT_TIME_ALLOW_URLS minutes ago.
            c) is a new user who has posts more that 
            INIT_MIN_MSG_ALLOW_URLS posts
        """

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
        defautl=conf.INIT_CALL_ADMINS_WHEN_SPAM
    )
    allow_users_to_add_bots = BooleanField(default=conf.INIT_ALLOW_USERS_ADD_BOTS)

    @property
    def min_messages(self):
        return self.num_messages_for_allow_urls

    @property
    def min_time(self):
        """Minimum time in minutes that a user must be in the chat before is
        allowed to add urls"""
        return self.time_for_allow_urls

    @property
    def warn_admin(self):
        return self.call_admins_when_spam_detected

    class Meta:
        primary_key = CompositeKey("chat")


class Storage:
    def __init__(self):
        db.create_tables([Chat, Config, User, Message])
        self.db = db.connect(reuse_if_open=True)

    def get_user(user_id, chat_id):
        return User.get(User.chat_id == chat_id & User.user_id == user_id)

    def get_chat_config(chat_id):
        return Config.get(Config.chat_id == chat_id)

    def register_new_user(self, chat_id, user_id, user_name, join_date, allow_user):
        user, created = User.get_or_create(chat.id=chat_id,
                                            user_id=user_id,
                                            user_name=user_name,
                                            join_date=join_date,
                                            num_messages=0,
                                            join_date=join_date,
                                            last_name='',
                                            language_code=conf.INIT_LANG
            )
        return user
        
    def save_user(chat_id, user):
        pass

    def save_config(chat_id, config):
        pass

    def add_message(chat_id, msg):
        pass


if __name__ == "__main__":
    storage = Storage()
