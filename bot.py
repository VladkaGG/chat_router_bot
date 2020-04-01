from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
import logging
from callbacks.all_callbacks import *

logger = logging.getLogger('root')
logger.setLevel('CRITICAL')

start_handler = CommandHandler('start', start)
help_handler = CommandHandler('help', help_callback)
add_group_handler = ConversationHandler(entry_points=[CommandHandler('add_group', add_group)],
                                        states={
                                            0: [MessageHandler(Filters.text, add_group)],
                                            1: [CallbackQueryHandler(add_group_button),
                                                MessageHandler(Filters.text, ending_add_group)]
                                        },
                                        fallbacks=[CommandHandler('add_group', add_group)])
show_groups_handler = ConversationHandler(entry_points=[CommandHandler('show_groups', show_groups)],
                                          states={
                                              0: [CallbackQueryHandler(show_groups)],
                                              1: [CallbackQueryHandler(show_chats)]
                                          },
                                          fallbacks=[CommandHandler('show_groups', show_groups)])
delete_groups_handler = ConversationHandler(entry_points=[CommandHandler('delete_group', delete_group)],
                                            states={
                                                0: [CommandHandler('delete_group', delete_group)],
                                                1: [CallbackQueryHandler(delete_group_button),
                                                    MessageHandler(Filters.text, ending_delete_group)]
                                            },
                                            fallbacks=[CommandHandler('delete_group', delete_group)])
add_chat_handler = ConversationHandler(entry_points=[CommandHandler('add_chat', add_chat)],
                                       states={
                                           0: [CommandHandler('add_chat', add_chat)],
                                           1: [CallbackQueryHandler(add_chat_button)],
                                           2: [MessageHandler(Filters.text, ending_add_chat)]
                                       },
                                       fallbacks=[CommandHandler('add_chat', add_chat)])
add_user_handler = ConversationHandler(entry_points=[CommandHandler('add_user', add_chat)],
                                       states={
                                           0: [CommandHandler('add_user', add_chat)],
                                           1: [CallbackQueryHandler(add_chat_button)],
                                           2: [MessageHandler(Filters.text, ending_add_user)]
                                       },
                                       fallbacks=[CommandHandler('add_user', add_chat)])
delete_chat_handler = ConversationHandler(entry_points=[CommandHandler('delete_chat', delete_chat)],
                                          states={
                                              0: [CallbackQueryHandler(delete_chat)],
                                              1: [CallbackQueryHandler(delete_chat_button)],
                                              2: [CallbackQueryHandler(ending_delete_chat)]
                                          },
                                          fallbacks=[CommandHandler('delete_chat', delete_chat)])
error_handler = MessageHandler(Filters.text, error)

if __name__ == '__main__':
    updater = Updater(token='your_token', use_context=True, workers=20)
    dispatcher = updater.dispatcher
    job = updater.job_queue

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(add_group_handler)
    dispatcher.add_handler(show_groups_handler)
    dispatcher.add_handler(delete_groups_handler)
    dispatcher.add_handler(add_chat_handler)
    dispatcher.add_handler(delete_chat_handler)
    dispatcher.add_handler(add_user_handler)
    dispatcher.add_handler(error_handler)

    updater.start_polling()
    updater.idle()
