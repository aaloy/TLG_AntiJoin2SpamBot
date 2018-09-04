# /usr/bin/python3
# -*- coding: utf-8 -*-
"""
Script:
    Constants.py
Description:
    Constants values for anti_join2spam_Bot.py.
Author:
    Jose Rios Rubio
Creation date:
    04/04/2018
Last modified date:
    12/08/2018
Version:
    1.7.0
"""

####################################################################################################
import sys

try:
    import config as conf
except ImportError as error:
    print("""You need to create and configure the config.py module. """)
    print(
        """The config.py module contains the configuration parameter the bot
needs to work properly. Please refer to the README file for more information."""
    )
    sys.exit(1)

# Constants
# Bot Token (get it from @BotFather) this is mandatory
TOKEN = conf.TELEGRAM_API_TOKEN
# list of user ides o usernames allowed to reset the bot
MANAGERS_LIST = conf.MANAGERS_LIST
# If true activates debug messages
DEBUG = getattr(conf, "DEBUG", False)
# Owner ID (The one that can send notify messages to all chats)
OWNER_ID = getattr(conf, "OWNER_ID", 000000000)
# Chat ID where the Bot is going to send debug messages
DEBUG_TO_CHAT = getattr(conf, "DEBUG_TO_CHAT", 000000000)
# Data directory path
ROOT_DIR = getattr(conf, "ROOT_DIR", ".")
DATA_DIR = getattr(conf, "DATA_DIR", "./data")
DATABASE_NAME = getattr(conf, "DATABASE_NAME", "bot.sqlite")
# Chat JSON files name
F_USERS = getattr(conf, "F_USERS", "users.json")
# Messages JSON files name
F_MSG = getattr(conf, "F_MSG", "msgs.json")
# Chat configurations JSON files name
F_CONF = getattr(conf, "F_CONF", "configs.json")
# Initial chat title at Bot start
INIT_TITLE = getattr(conf, "INIT_TITLE", "Unknown Chat")
# Initial chat link at Bot start
INIT_LINK = getattr(conf, "INIT_LINK", "Unknown")
# Initial language at Bot start
INIT_LANG = getattr(conf, "INIT_LANG", "EN")
# Allowed languages
LANGUAGES = ["EN", "ES"]
# Initial enable/disable status at Bot start
INIT_ENABLE = getattr(conf, "INIT_ENABLE", True)
# Initial hours until allow a user to publish URLs in messages
INIT_TIME_ALLOW_URLS = getattr(conf, "INIT_TIME_ALLOW_URLS", 24)
# Initial number of users messages until allow publish URLs
INIT_MIN_MSG_ALLOW_URLS = getattr(conf, "INIT_MIN_MSG_ALLOW_URLS", 10)
# Initial notify admins value when Spam is detected
INIT_CALL_ADMINS_WHEN_SPAM = getattr(conf, "INIT_CALL_ADMINS_WHEN_SPAM", False)
# Initial allow users to invite and add Bots to the group
INIT_ALLOW_USERS_ADD_BOTS = getattr(conf, "INIT_ALLOW_USERS_ADD_BOTS", False)
# Time (in mins) to remove self-destruct sent messages from the Bot
T_DEL_MSG = getattr(conf, "T_DEL_MSG", 3)
# Save messages for each chat
SAVE_CHAT_MESSAGES = getattr(conf, "SAVE_CHAT_MESSAGES", True)
DEVELOPER = "@JoseTLG & @aaloy"  # Bot developer
REPOSITORY = (
    "https://https://github.com/J-Rios/TLG_AntiJoin2SpamBot \n "
)  # Bot code repository
DEV_PAYPAL = "https://www.paypal.me/josrios"  # Developer Paypal address
DEV_BTC = "3N9wf3FunR6YNXonquBeWammaBZVzTXTyR"  # Developer Bitcoin address
VERSION = "1.8.0"  # Bot version
REGEX_URLS = "https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'"
MAX_USERNAME_LENGTH = getattr(conf, "MAX_USERNAME_LENGTH", 30)
MAX_USERNAME_ALIAS = getattr(conf, "MAX_USERNAME_ALIAS", 50)


TEXT = {
    "EN": {
        "START": "I am a Bot that fight against Spammers that join groups to publish their annoying "
        "and unwanted info. Check /help command for more information about my usage.",
        "ANTI-SPAM_BOT_ADDED_TO_GROUP": "Hello, I am a Bot that fight against Spammers that join groups to publish their "
        "annoying and unwanted info. To work properly, give me Admin privileges.\n"
        "\n"
        "Check /help command for more information about my usage.",
        "CMD_NOT_ALLOW": "Just an Admin can use this command",
        "CMD_JUST_ALLOW_IN_PRIVATE": "This command just can be use in a private chat.",
        "CMD_JUST_ALLOW_OWNER": "This command just can be use by the Owner of the Bot.",
        "CMD_NOTIFY_ALL": "Ok, tell me now the message that you want that I publish in all the Chats where I "
        "am...\n\nUse the command /notify_discard if you don't want to stop publishing it.",
        "CMD_NOTIFYING": "A massive publish is already running, please wait until it finish before send "
        "another.",
        "CMD_NOTIFY_ALL_OK": "Message published in all the chats where I am.",
        "CMD_NOTIFY_DISCARD": "Massive publish discarted.",
        "CMD_NOTIFY_CANT_DISCARD": "The massive publish is not running.",
        "LANG_CHANGE": "Language changed to english.",
        "LANG_SAME": "I am already in english.\n\nMay you want to say:\n/language es",
        "LANG_BAD_LANG": "Invalid language provided. The actual languages supported are english and spanish, "
        'change any of them using "en" or "es".\n'
        "\n"
        "Example:\n"
        "/language en\n"
        "/language es",
        "LANG_NOT_ARG": "The command needs a language to set (en - english, es - spanish).\n"
        "\n"
        "Example:\n"
        "/language en\n"
        "/language es",
        "STATUS": "Actual configuration:\n"
        "————————————————\n"
        "Number of messages to allow URLs:\n"
        "    {}\n"
        "\n"
        "Hours until allow URLs:\n"
        "    {}\n"
        "\n"
        "Admins call when Spam detected:\n"
        "    {}\n"
        "\n"
        "Allow users to add Bots:\n"
        "    {}\n"
        "\n"
        "Anti-Spam:\n"
        "    {}\n",
        "SET_HOURS_CHANGED": "Time successfully changed.\n\nNew users need to wait {} hours to get allowed to "
        "publish URLs in messages.",
        "SET_HOURS_NEGATIVE_HOUR": "Invalid time provided. The hours need to be positives.",
        "SET_HOURS_BAD_ARG": "Invalid time provided. You need to specify how many hours want to set for a new "
        "user to wait, until get allowed to publish URLs in messages.\n"
        "\n"
        "Example (5h or 24h):\n"
        "/set_hours 5\n"
        "/set_hours 24",
        "SET_HOURS_NOT_ARG": "No time provided. You need to specify how many hours want to set for a new "
        "user to wait, until get allowed to publish URLs in messages.\n"
        "\n"
        "Example (5h or 24h):\n"
        "/set_hours 5\n"
        "/set_hours 24",
        "SET_MSG_CHANGED": "Number of messages successfully changed.\n\nNew users need to send {} messages "
        "to get allowed to publish URLs in messages.",
        "SET_MSG_NEGATIVE": "Invalid number of messages provided. The number of messages needs to be positive.",
        "SET_MSG_BAD_ARG": "Invalid number of messages provided. You need to specify how many messages want to "
        "set for a new user to wait, until get allowed to publish URLs in messages.\n"
        "\n"
        "Example (5 or 20):\n"
        "/set_messages 5\n"
        "/set_messages 20",
        "SET_MSG_NOT_ARG": "No number of messages provided. You need to specify how many messages want to set "
        "for a new user to wait, until get allowed to publish URLs in messages.\n"
        "\n"
        "Example (5 or 20):\n"
        "/set_messages 5\n"
        "/set_messages 20",
        "CMD_ALLOW_USR_OK": "User {} granted to publish URLs in messages.",
        "CMD_ALLOW_USR_ALREADY_ALLOWED": "User {} is already allowed to publish URLs in messages.",
        "CMD_ALLOW_USR_NOT_FOUND": "User not found in my data base.",
        "CMD_ALLOW_USR_NOT_ARG": "No user provided. You need to specify the user alias/name that we want to give "
        "permission to publish URLs in messages.\n"
        "\n"
        "Examples:\n"
        "/allow_user @mr_doe\n"
        "/allow_user Jhon Doe",
        "ENABLE": "Anti-Spam enabled. Stop it with /disable command.",
        "DISABLE": "Anti-Spam disabled. Start it with /enable command.",
        "ALREADY_ENABLE": "I am already enabled.",
        "ALREADY_DISABLE": "I am already disabled.",
        "MSG_SPAM_HEADER": "Anti-Spam message:\n" "————————————————\n",
        "MSG_SPAM_DETECTED_CANT_REMOVE": "Spam message detected, but I don't have permission for remove it. Please, give me "
        "administration privileges for delete messages ;)",
        "MSG_SPAM_DETECTED_0": "Message from user {} removed for the sake of a free of Spam Telegram.",
        "MSG_SPAM_DETECTED_1": "\n\nNew members need to write <b>{} messages</b> and wait <b>{} hours</b> to be "
        "allowed to publish URLs in their messages.",
        "CALLING_ADMINS": "\n\nCalling to Admins:\n\n{}",
        "CALLING_ADMINS_NO_ADMINS": "There is not Admins in this chat.",
        "CALL_WHEN_SPAM_ENABLE": "Automatic call Admins when Spam is detected enabled.",
        "CALL_WHEN_SPAM_DISABLE": "Automatic call Admins when Spam is detected disabled.",
        "CALL_WHEN_SPAM_ALREADY_ENABLE": "Call Admins when Spam is detected is already enabled.",
        "CALL_WHEN_SPAM_ALREADY_DISABLE": "Call Admins when Spam is detected is already disabled.",
        "CALL_WHEN_SPAM_NOT_ARG": "The command needs enable/disable keyword.\n"
        "\n"
        "Example:\n"
        "/call_when_spam enable\n"
        "/call_when_spam disable",
        "USERS_ADD_BOTS_ENABLE": "Allow users to add Bots enabled.",
        "USERS_ADD_BOTS_DISABLE": "Allow users to add Bots disabled.",
        "USERS_ADD_BOTS_ALREADY_ENABLE": "Allow users to add Bots is already enabled.",
        "USERS_ADD_BOTS_ALREADY_DISABLE": "Allow users to add Bots is already disabled.",
        "USERS_ADD_BOTS_NOT_ARG": "The command needs enable/disable keyword.\n"
        "\n"
        "Example:\n"
        "/users_add_bots enable\n"
        "/users_add_bots disable",
        "USER_CANT_ADD_BOT": "This group doesn't allow that users invite and add Bots.\n"
        "\n"
        "User {} try to add the Bot {}. The Bot has been kicked and banned.",
        "USER_CANT_ADD_BOT_CANT_KICK": "This group don't allow users to invite and add Bots.\n"
        "\n"
        "User {} has added the Bot {}, I try to kick the Bot, but I don't have permission "
        "to do it. Please, give me administration privileges for ban members ;)",
        "CAN_NOT_GET_ADMINS": "Can't use this command in the current chat.",
        "USER_LONG_NAME_JOIN": "Anti-Spam Warning:\n"
        "————————————————\n"
        "An user with a name that is too long has joined the chat.\n"
        "\n"
        '"{}" has joined the chat.',
        "USER_LONG_NAME_JOIN_CANT_REMOVE": "Anti-Spam Warning:\n"
        "————————————————\n"
        "An user with a name that is too long has joined the chat. But I don't have "
        "permission for remove the message. Please, give me administration privileges for "
        "delete messages ;)\n"
        "\n"
        '"{}" has joined the chat.',
        "USER_URL_NAME_JOIN": "Anti-Spam Warning:\n"
        "————————————————\n"
        "An user with a name that contains an URL has joined the chat.\n"
        "\n"
        '"{}" has joined the chat.',
        "USER_URL_NAME_JOIN_CANT_REMOVE": "Anti-Spam Warning:\n"
        "————————————————\n"
        "An user with a name that contains an URL has joined the chat. But I don't have "
        "permission for remove the message. Please, give me administration privileges for "
        "delete messages ;)\n"
        "\n"
        '"{}" has joined the chat.',
        "VERSION": "Actual Bot version: {}",
        "ABOUT_MSG": "This is an open-source GNU-GPL licensed Bot developed by the telegram user {}. You "
        "can check the code here:\n{}\n\n-----------------------------------------------\n\n"
        "Do you like my work? Buy me a coffee.\n\nPaypal:\n{}\n\nBTC:\n{}",
        "LINE": "\n————————————————\n",
        "LINE_LONG": "\n————————————————————————————————————————————————\n",
    },
    "ES": {
        "START": "Soy un Bot que se enfrenta a aquellos Spammers que se unen a un grupo para "
        "exclusivamente publicar sus molestos y no bienvenidos mensajes de Spam. Echa un "
        "vistazo al comando /help para conocer más información sobre mi uso.",
        "ANTI-SPAM_BOT_ADDED_TO_GROUP": "Hola, soy un Bot que se enfrenta a los Spammers que se unen a un grupo para "
        "publicar sus molestos y no bienvenidos mensajes de Spam. Para que pueda funcionar "
        "de forma correcta, dame permisos de administración.\n"
        "\n"
        "Echa un vistazo al comando /help para conocer más información sobre mi uso.",
        "CMD_NOT_ALLOW": "Solo un Admin puede utilizar este comando.",
        "CMD_JUST_ALLOW_IN_PRIVATE": "Este comando solo puede ser usado en el chat privado.",
        "CMD_JUST_ALLOW_OWNER": "Este comando solo puede ser usado por el propietario del Bot.",
        "CMD_NOTIFY_ALL": "Ok, dime ahora el mensaje que quieres que publique en todos los chats en los que "
        "estoy...\n\nUtiliza el comando /notify_discard si quieres detener la publicación.",
        "CMD_NOTIFYING": "Una publicación masiva ya está en curso, por favor, espera a que termine para mandar "
        "otra.",
        "CMD_NOTIFY_ALL_OK": "Mensaje publicado en todos los chats en los que estoy.",
        "CMD_NOTIFY_DISCARD": "Publicación masiva descartada.",
        "CMD_NOTIFY_CANT_DISCARD": "No se esta ejecutando una publicación masiva.",
        "LANG_CHANGE": "Idioma cambiado a español.",
        "LANG_SAME": "Ya estoy en español.\n\nQuizás querías decir:\n/language en",
        "LANG_BAD_LANG": "Idioma inválidado. Los idiomas actualmente soportados son el español y el inglés, "
        'cambia a uno de ellos mediante las etiquetas "es" o "en".\n'
        "\n"
        "Ejemplo:\n"
        "/language es\n"
        "/language en",
        "LANG_NOT_ARG": "El comando necesita un idioma que establecer (es - español, en - inglés).\n"
        "\n"
        "Ejemplo:\n"
        "/language es\n"
        "/language en",
        "STATUS": "Configuración actual:\n"
        "————————————————\n"
        "Número de mensajes hasta permitir URLs:\n"
        "    {}\n"
        "\n"
        "Número de horas hasta permitir URLs:\n"
        "    {}\n"
        "\n"
        "Llamada a los Admins cuando se detecta Spam:\n"
        "    {}\n"
        "\n"
        "Permitir que los usuarios puedan añadir Bots:\n"
        "    {}\n"
        "\n"
        "Anti-Spam:\n"
        "    {}\n",
        "SET_HOURS_CHANGED": "Tiempo cambiado correctamente.\n\nLos usuarios nuevos tendrán que esperar {} horas "
        "antes de poder publicar mensajes que contengan URLs.",
        "SET_HOURS_NEGATIVE_HOUR": "Tiempo proporcionado inválido. Las horas deben ser positivas.",
        "SET_HOURS_BAD_ARG": "Tiempo proporcionado inválido. Tienes que especificar cuántas horas serán "
        "necesarias que pasen desde que un usuario se unió al grupo, antes de que se le "
        "permita publicar mensajes que contengan URLs.\n"
        "\n"
        "ejemplo (5h o 24h):\n"
        "/set_hours 5\n"
        "/set_hours 24",
        "SET_HOURS_NOT_ARG": "No se proporcionó ningún tiempo. Tienes que especificar cuántas horas quieres que "
        "un nuevo usuario deba esperar antes de poder publicar mensajes que contengan URLs.\n"
        "\n"
        "Ejemplo (5h o 24h):\n"
        "/set_hours 5\n"
        "/set_hours 24",
        "SET_MSG_CHANGED": "Número de mensajes cambiado correctamente.\n\nLos usuarios nuevos tendrán que "
        "escribir {} mensajes, antes de que se les permita publicar mensajes que contengan "
        "URLs.",
        "SET_MSG_NEGATIVE": "Número de mensajes inválido. El número de mensajes debe ser positivo.",
        "SET_MSG_BAD_ARG": "Número de mensajes inválido. Tienes que especificar cuántos mensajes "
        "deberán de escribir los nuevos usuarios antes de que se les permita publicar "
        "mensajes que contengan URLs.\n"
        "\n"
        "Ejemplo (5 o 20):\n"
        "/set_messages 5\n"
        "/set_messages 20",
        "SET_MSG_NOT_ARG": "No se proporcionó el número de mensajes. Tienes que especificar cuántos mensajes "
        "deberán de escribir los nuevos usuarios antes de que se les permita publicar "
        "mensajes que contengan URLs.\n"
        "\n"
        "Ejemplo (5 o 20):\n"
        "/set_messages 5\n"
        "/set_messages 20",
        "CMD_ALLOW_USR_OK": "Usuario {} habilitado para publicar URLs en sus mensajes.",
        "CMD_ALLOW_USR_ALREADY_ALLOWED": "El usuario {} ya tenía permiso para publicar URLs en sus mensajes.",
        "CMD_ALLOW_USR_NOT_FOUND": "Usuario no encontrado en la base de datos.",
        "CMD_ALLOW_USR_NOT_ARG": "No se proporcionó el usuario. Tienes que especificar el alias/nombre del usuario al "
        "que se le quiere dar permiso para publicar URLs en sus mensajes.\n"
        "\n"
        "Ejemplos:\n"
        "/allow_user @mr_doe\n"
        "/allow_user Jhon Doe",
        "ENABLE": "Anti-Spam activado. Desactívalo con el comando /disable.",
        "DISABLE": "Anti-Spam desactivado. Actívalo con el comando /enable.",
        "ALREADY_ENABLE": "Ya estoy activado.",
        "ALREADY_DISABLE": "Ya estoy desactivado.",
        "MSG_SPAM_HEADER": "Mensaje Anti-Spam:\n" "————————————————\n",
        "MSG_SPAM_DETECTED_CANT_REMOVE": "Mensaje de Spam detectado, pero no tengo permiso para eliminarlo. Por favor, dame "
        "privilegios de administración para eliminar mensajes ;)",
        "MSG_SPAM_DETECTED_0": "Mensaje del usuario {} eliminado en aras de un Telegram libre de Spam.",
        "MSG_SPAM_DETECTED_1": "\n\nLos nuevos usuarios necesitan escribir más de <b>{} mensajes</b> y esperar "
        "<b>{} horas</b> para poder publicar mensajes que contengan URLs.",
        "CALLING_ADMINS": "\n\nLlamando a los Admins:\n{}",
        "CALLING_ADMINS_NO_ADMINS": "No hay Administradores en el chat actual.",
        "CALL_WHEN_SPAM_ENABLE": "Activada la llamada automática a los Admins cuando se detecta Spam.",
        "CALL_WHEN_SPAM_DISABLE": "Desactivada la llamada automática a los Admins cuando se detecta Spam.",
        "CALL_WHEN_SPAM_ALREADY_ENABLE": "La llamada a los Admins cuando se detecta Spam ya está activada.",
        "CALL_WHEN_SPAM_ALREADY_DISABLE": "La llamada a los Admins cuando se detecta Spam ya está desactivada.",
        "CALL_WHEN_SPAM_NOT_ARG": "El comando requiere el parámetro enable/disable.\nRestableciendo valor por defecto\n"
        "\n"
        "Ejemplo:\n"
        "/call_when_spam enable\n"
        "/call_when_spam disable",
        "USERS_ADD_BOTS_ENABLE": "Activado el permiso de los usuarios para añadir Bots al grupo.",
        "USERS_ADD_BOTS_DISABLE": "Desactivado el permiso de los usuarios para añadir Bots al grupo.",
        "USERS_ADD_BOTS_ALREADY_ENABLE": "El permiso de los usuarios para añadir Bots ya está activado.",
        "USERS_ADD_BOTS_ALREADY_DISABLE": "El permiso de los usuarios para añadir Bots ya está desactivado.",
        "USERS_ADD_BOTS_NOT_ARG": "El comando requiere el parámetro enable/disable.\nRestableciendo valor por defecto\n"
        "\n"
        "Ejemplo:\n"
        "/users_add_bots enable\n"
        "/users_add_bots disable",
        "USER_CANT_ADD_BOT": "Este grupo no permite que los usuarios inviten y añadan Bots.\n"
        "\n"
        "El usuario {} intento añadir al Bot {}. El Bot fue kickeado y baneado.",
        "USER_CANT_ADD_BOT_CANT_KICK": "Este grupo no permite que los usuarios inviten y añadan Bots.\n"
        "\n"
        "El usuario {} intento añadir al Bot {}. Intente kickear al Bot, pero no tengo "
        "permisos para hacerlo. Por favor, dame privilegios de administración para suspender "
        "miembros del grupo ;)",
        "CAN_NOT_GET_ADMINS": "No se puede usar este comando en el chat actual.",
        "USER_LONG_NAME_JOIN": "Aviso Anti-Spam:\n"
        "————————————————\n"
        "Un usuario con un nombre demasiado largo se ha unido al chat.\n"
        "\n"
        '"{}" se unió al chat.',
        "USER_LONG_NAME_JOIN_CANT_REMOVE": "Aviso Anti-Spam:\n"
        "————————————————\n"
        "Un usuario con un nombre demasiado largo se ha unido al chat. No tengo permiso "
        "para eliminar el mensaje. Por favor, dame privilegios de administración para "
        "eliminar mensajes ;)\n"
        "\n"
        '"{}" se unió al chat.',
        "USER_URL_NAME_JOIN": "Aviso Anti-Spam:\n"
        "————————————————\n"
        "Un usuario con URL en su nombre se ha unido al chat.\n"
        "\n"
        '"{}" se unió al chat.',
        "USER_URL_NAME_JOIN_CANT_REMOVE": "Aviso Anti-Spam:\n"
        "————————————————\n"
        "Un usuario con una URL en su nombre se ha unido al chat. No tengo permiso "
        "para eliminar el mensaje. Por favor, dame privilegios de administración para "
        "eliminar mensajes ;)\n"
        "\n"
        '"{}" se unió al chat.',
        "VERSION": "Versión actual del Bot: {}",
        "ABOUT_MSG": "Este es un Bot open-source con licencia GNU-GPL, desarrollado por el usuario de "
        "telegram {}. Puedes consultar el código aquí:\n{}\n\n"
        "-----------------------------------------------\n\nTe gusta lo que hago? "
        "Invítame a un café.\n\nPaypal:\n{}\n\nBTC:\n{}",
        "LINE": "\n————————————————\n",
        "LINE_LONG": "\n————————————————————————————————————————————————\n",
    },
}
