from telethon import TelegramClient
from telethon.errors.rpcerrorlist import UserIdInvalidError, ChatIdInvalidError
from telethon.tl.functions.messages import AddChatUserRequest
from telethon.tl.types import InputUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
import configparser
import datetime
import os
import logging

logger = logging.getLogger(__name__)

api_id = 1281003
api_hash = 'b523684732ab938fcf71328229c3f789'
phone_number = '+79522645768'
client = TelegramClient('anon', api_id, api_hash)


async def main(chat, username):
    target_chat = chat
    chat_to_add = None
    async for dialog in client.iter_dialogs():
        if dialog.name == target_chat:
            chat_to_add = dialog.id
    if not chat_to_add:
        error_str = "Some troubles with chat {} " \
                    "(probably you doesn't have admin access or write a wrong chat name)".format(chat_to_add)
        logger.error(error_str)
        raise error_str
    error_str = None
    try:
        user_to_add = username
        user = await client.get_entity(user_to_add)
        await client(AddChatUserRequest(chat_to_add, InputUser(user.id, user.access_hash), fwd_limit=10))
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


def add_user(chat, username):
    with client:
        client.loop.run_until_complete(main(chat, username))


if __name__ == '__main__':
    chat = 'Тест группы'
    username = 'vladka_gg'
    with client:
        client.loop.run_until_complete(main(chat, username))
