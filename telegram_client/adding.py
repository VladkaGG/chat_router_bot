from telegram_client import os, asyncio, logging, TelegramClient, AddChatUserRequest, InputUser, PeerFloodError, \
    UserIdInvalidError, UserPrivacyRestrictedError, ChatIdInvalidError, CreateChannelRequest, CheckUsernameRequest, \
    InputPeerChannel, UpdateUsernameRequest, InputChannel

logger = logging.getLogger('root')


def add_user(target_chat, user_to_add):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        client = TelegramClient('bot', os.getenv('API_ID'), os.getenv('HASH_ID')).start(
            bot_token='bot_token')
        print(client)
    except Exception as e:
        return 'HUETA {}'.format(e)
    # chat_to_add = None
    # for dialog in client.iter_dialogs():
    #     if dialog.name == target_chat:
    #         chat_to_add = int(dialog.id)
    #         print(chat_to_add)
    #         break
    # if not chat_to_add:
    #     client.disconnect()
    #     loop.close()
    #     return "Some troubles with chat {} " \
    #            "(probably you doesn't have admin access or write a wrong chat name)".format(target_chat)
    error_str = None
    try:
        user = client.get_entity(user_to_add)
        client(AddChatUserRequest(target_chat, InputUser(user.id, user.access_hash), fwd_limit=0))
    except PeerFloodError:
        error_str = "Getting Flood Error from telegram. Script is stopping now. Please try again after some time."
    except UserPrivacyRestrictedError:
        error_str = "The user's privacy settings do not allow you to do this. Skipping."
    except UserIdInvalidError:
        error_str = "Some troubles with username {} (maybe you've written a wrong username)".format(user_to_add)
    except ChatIdInvalidError:
        error_str = "Some troubles with chat {} " \
                    "(probably you doesn't have admin access or write a wrong chat name)".format(target_chat)
    except Exception as e:
        error_str = "Unexpected error: {}".format(e)
    finally:
        client.disconnect()
        loop.close()
        return error_str or "{} added to {}".format(user_to_add, target_chat)

# def create_chat(chat_name, user_id):
#     api_id = os.getenv('API_ID')
#     api_hash = os.getenv('HASH_ID')
#     user_id = os.getenv('USER_ID')
#     try:
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         client = TelegramClient(user_id, api_id, api_hash)
#         client.connect()
#
#     createdPrivateChannel = client(CreateChannelRequest("title", "about", megagroup=False))
#
#     # if you want to make it public use the rest
#     newChannelID = createdPrivateChannel.__dict__["chats"][0].__dict__["id"]
#     newChannelAccessHash = createdPrivateChannel.__dict__["chats"][0].__dict__["access_hash"]
#     desiredPublicUsername = "myUsernameForPublicChannel"
#     checkUsernameResult = client(
#         CheckUsernameRequest(InputPeerChannel(channel_id=newChannelID, access_hash=newChannelAccessHash),
#                              desiredPublicUsername))
#     if (checkUsernameResult == True):
#         publicChannel = client(
#             UpdateUsernameRequest(InputPeerChannel(channel_id=newChannelID, access_hash=newChannelAccessHash),
#                                   desiredPublicUsername))


print(add_user('alala', 'sofia_br'))
