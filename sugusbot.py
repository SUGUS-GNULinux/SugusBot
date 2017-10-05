#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import logging
import repository
import handlers

from configparser import ConfigParser
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters,\
    CallbackQueryHandler

# Init logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s '
                    '- %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

# Retrieve configuration from config file
config = ConfigParser()
config.read('config.ini')
database = config['Database']['route']
token = config['Telegram']['token']
id_admin = config['Telegram']['id_admin']

# Start database connection
repository.connection(database)

def main():
    # Database initialization
    repository.sec_init(id_admin)

    # EventHandler creation
    updater = Updater(token)

    dispatcher = updater.dispatcher

    # Assign functions to handlers
    dispatcher.add_handler(CommandHandler('start',
                                          handlers.start))
    dispatcher.add_handler(CallbackQueryHandler(handlers.help,
                                                pattern = 'help'))
    dispatcher.add_handler(CommandHandler('help',
                                          handlers.help))
    dispatcher.add_handler(CommandHandler('who',
                                          handlers.who))
    dispatcher.add_handler(CallbackQueryHandler(handlers.como,
                                                pattern = 'como'))
    dispatcher.add_handler(CommandHandler('como',
                                          handlers.como))
    dispatcher.add_handler(CallbackQueryHandler(handlers.no_como,
                                                pattern = 'no_como'))
    dispatcher.add_handler(CallbackQueryHandler(handlers.quien_come,
                                                pattern = 'quien_come'))
    dispatcher.add_handler(CommandHandler('quiencome',
                                          handlers.quien_come))
    dispatcher.add_handler(CommandHandler('comida',
                                          handlers.comida))
    dispatcher.add_handler(CommandHandler('group',
                                          handlers.group))
    dispatcher.add_handler(CommandHandler('addgroup',
                                          handlers.add_group))
    dispatcher.add_handler(CommandHandler('addtogroup',
                                          handlers.add_to_group))
    dispatcher.add_handler(CommandHandler('delfromgroup',
                                          handlers.del_from_group))
    dispatcher.add_handler(CommandHandler('groups',
                                          handlers.groups))
    dispatcher.add_handler(CommandHandler('event',
                                          handlers.event))
    dispatcher.add_handler(CommandHandler('events',
                                          handlers.events))
    dispatcher.add_handler(CommandHandler('addevent',
                                          handlers.add_event))
    dispatcher.add_handler(CommandHandler('removeevent',
                                          handlers.remove_event))
    dispatcher.add_handler(CommandHandler('jointoevent',
                                          handlers.join_to_event))
    dispatcher.add_handler(CommandHandler('participants',
                                          handlers.participants))
    dispatcher.add_handler(CommandHandler('leaveevent',
                                          handlers.leave_event))

    # Error handler, for logging purposes
    dispatcher.add_error_handler(handlers.error)

    # Start the bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
