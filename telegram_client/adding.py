from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors.rpcerrorlist import UserIdInvalidError, ChatIdInvalidError
from telethon.tl.functions.messages import GetDialogsRequest, AddChatUserRequest
from telethon.tl.types import InputPeerEmpty, InputUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
import configparser
import datetime
import os
import logging
logger = logging.getLogger(__name__)

target_chat = 'alala'
user_to_add = 'batalyoni'


def add_user(a, b):
    a+b
    pass


# def add_user(target_chat, user_to_add):
if __name__ == '__main__':
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
        client = TelegramClient(StringSession('1ApWapzMBu213br00TfVaTm4CUXqYgNLww_xNDW1cOuQfgZgR_UFf4Ok8e2LkDgCLfL4Ppv98hkpc1tKG7HU9Dv3pOAptl9pwPf8gqR80B3fvBd_Gtx-9zCOKBX_YdEGJ3lBVbsnBclM1I6P5fo4hfG5qiIT9M6COJMkPgH1U_QpJPpq5by7swvSTJ_cMqRXyoY0_Xdf--7fS3un_UJKr_OJVL_ggMjytDfMdMwtHmropSsjVFM1Rt4Pb2scFFD9FvzBvyAbCBAA_xp5pwPFhlJaPR0BZ2BSjNiJ1zrIhYjtcjT8uvpaK8UB0SB9Cok8w8AT9_csqmBPFCWWDafQVnWfltjCQLQo='), api_id, api_hash)
        print(1)
        client.connect()
    except Exception as e:
        print('HUETA {}'.format(e))
        raise
        # return 'HUETA {}'.format(e)
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
                    "(probably you doesn't have admin access or write a wrong chat name)".format(chat_to_add)
        logger.error(error_str)
        raise error_str
        # return error_str
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
                    "(probably you doesn't have admin access or write a wrong chat name)".format(chat_to_add)
    except:
        error_str = "Unexpected"
    finally:
        print(error_str or "{} added to {}".format(user_to_add, target_chat))
        # return error_str or "{} added to {}".format(user_to_add, target_chat)
