#!/usr/bin/python3.5
# -*- coding: utf-8 -*-

import telegram
from urllib.error import URLError
import time

bot = None


def create_bot(token):
    # Create bot object
    global bot
    bot = telegram.Bot(token)


def getUpdates(LAST_UPDATE_ID, timeout = 30):
    while True:
        try:
            updates = bot.getUpdates(LAST_UPDATE_ID, timeout=timeout, network_delay=2.0)
        except telegram.TelegramError as error:
            if error.message == "Timed out":
                print(u"Timed out! Retrying...")
            elif error.message == "Bad Gateway":
                    print("Bad gateway. Retrying...")
            else:
                raise

        except URLError as error:
            print("URLError! Retrying...")
            time.sleep(1)
        except Exception as e:
            print("Exception: " + e)
            print('Ignore errors')
            pass
        else:
            break
    return updates

def sendMessages(send_text, chat_id):
    while True:
        try:
            bot.sendMessage(chat_id=chat_id, text=send_text)
            print("Mensaje enviado a id: " + str(chat_id))
            break
        except telegram.TelegramError as error:
            if error.message == "Timed out":
                print("Timed out! Retrying...")
            else:
                print(error)
        except URLError as error:
            print("URLError! Retrying to send message...")
            time.sleep(1)
        except Exception as e:
            print("Exception: " + e)
            print('Ignore exception')
            pass
