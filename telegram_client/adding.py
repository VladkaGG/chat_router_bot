from telethon.sync import TelegramClient
import configparser
import json
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import GetDialogsRequest, AddChatUserRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, Chat, InputUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
import datetime


target_chat = 'alala'
user_to_add = 'sofia_br'
config = configparser.ConfigParser()
config.read('config.ini')

api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']


if __name__ == '__main__':
    client = TelegramClient(username, api_id, api_hash)
    client.connect()

    result = client(GetDialogsRequest(
        offset_date=datetime.datetime.now(),
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=100,
        hash=0
    ))
    all_chats = []
    all_chats.extend(result.chats)
    chats = []
    for chat in all_chats:
        if chat.title == target_chat:
            target_chat = client.get_input_entity(chat.title)
            break
    # target_chats_entity = InputPeerChannel(target_chat.id, target_chat.access_hash)
    try:
        user = InputUser()
        result = client(InviteToChannelRequest(target_chat, [user]))
        print(result)
        # client(AddChatUserRequest(target_chat, user, fwd_limit=10))
    except PeerFloodError:
        print("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
    except UserPrivacyRestrictedError:
        print("The user's privacy settings do not allow you to do this. Skipping.")
    except TypeError:
        print('Type Error')
    except:
        print('Unexpected')