from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.errors.rpcerrorlist import UserIdInvalidError, ChatIdInvalidError
from telethon.tl.functions.messages import GetDialogsRequest, AddChatUserRequest
from telethon.tl.types import InputPeerEmpty, InputUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
import configparser
import datetime
import os
import logging
import asyncio
logger = logging.getLogger(__name__)


def add_user(target_chat, user_to_add):
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')

        api_id = config['Telegram']['api_id']
        api_hash = config['Telegram']['api_hash']
        phone_number = config['Telegram']['phone_number']
    except:
        api_id = os.getenv('API_ID') or 1241185
        api_hash = os.getenv('HASH_ID') or 'e4c55efb9a74a757fdeb232fd97590b8'
        phone_number = os.getenv('USER_ID') or '+79142438227'
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        client = TelegramClient(StringSession('your_stringsession'), api_id, api_hash)
        client.connect()
    except Exception as e:
        return 'HUETA {}'.format(e)
    if not client.is_user_authorized():
        client.send_code_request(phone_number)
        client.sign_in(phone_number, input('Enter the code: '))
    result = client(GetDialogsRequest(
        offset_date=datetime.datetime.now(),
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=100,
        hash=0
    ))
    all_chats = []
    all_chats.extend(result.chats)
    del result
    chat_to_add = None
    for chat in all_chats:
        if chat.title == target_chat:
            chat_to_add = client.get_input_entity(chat.title)
            del all_chats
            break
    if not chat_to_add:
        error_str = "Some troubles with chat {} " \
                    "(probably you doesn't have admin access or write a wrong chat name)".format(target_chat)
        logger.error(error_str)
        loop.close()
        return error_str
    error_str = None
    try:
        user = client.get_entity(user_to_add)
        client(AddChatUserRequest(chat_to_add, InputUser(user.id, user.access_hash), fwd_limit=10))
    except PeerFloodError:
        error_str = "Getting Flood Error from telegram. Script is stopping now. Please try again after some time."
    except UserPrivacyRestrictedError:
        error_str = "The user's privacy settings do not allow you to do this. Skipping."
    except UserIdInvalidError:
        error_str = "Some troubles with username {} (maybe you've written a wrong username)".format(user_to_add)
    except ChatIdInvalidError:
        error_str = "Some troubles with chat {} " \
                    "(probably you doesn't have admin access or write a wrong chat name)".format(target_chat)
    except:
        error_str = "Unexpected"
    finally:
        loop.close()
        return error_str or "{} added to {}".format(user_to_add, target_chat)
