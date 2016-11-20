#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from urllib.request import urlopen
from urllib.error import URLError
import time
from pyquery import PyQuery
import telegram
import string

import codecs
import sys

from datetime import datetime

import configparser

from repository import connection, sec_init, add_to_event, find_by_event, remove_from_event, empty_event, list_events

config = configparser.ConfigParser()
config.read('myconfig.ini')
database = config['Database']['route']
token = config['Telegram']['token']
id_admin = config['Telegram']['id_admin']

# Create bot object
bot = telegram.Bot(token)

connection(database)

def main():

    sec_init(id_admin)

    # UTF-8 console stuff thingies
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

    # Init logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Discard old updates, sent before the bot was started
    num_discarded = 0

    # Get last update ID
    LAST_UPDATE_ID = None

    while True:
        updates = bot.getUpdates(LAST_UPDATE_ID, timeout=1, network_delay=2.0)
        if updates is not None and updates:
            num_discarded = num_discarded + len(updates)
            LAST_UPDATE_ID = updates[-1].update_id + 1
        else:
            break

    print("Discarded {} old updates".format(num_discarded))

    # Main loop
    print('Working...')
    while True:
        updates = getUpdates(LAST_UPDATE_ID)

        for update in updates:
            message = update.message
            actText = message.text
            actType = message.chat.type
            chat_id = message.chat.id
            update_id = update.update_id
            actUser = message.from_user.username

            send_text = None

            periodicCheck()

            if check_type_and_text_start(aText= actText, cText='/who', aType=actType, cType='private'):
                who = getWho()

                if not who:
                    #changes in emojis in python3 telegram version
                    send_text = u"Parece que no hay nadie... {}".format(telegram.Emoji.DISAPPOINTED_FACE)
                else:
                    send_text = show_list(u"Miembros en SUGUS:", who)

            if check_type_and_text_start(aText= actText, cText='/como', aType=actType, cType='private'):
                send_text = add_to_event('comida', actUser)

            if check_type_and_text_start(aText= actText, cText='/nocomo', aType=actType, cType='private'):
                send_text = remove_from_event('comida', actUser)

            if check_type_and_text_start(aText= actText, cText='/quiencome', aType=actType, cType='private'):
                if len(find_by_event('comida')) != 0:
                    send_text = show_list(u"Hoy come en Sugus:", find_by_event('comida'), [2, 0])
                else:
                    send_text = 'De momento nadie come en Sugus'

            if check_type_and_text_start(aText= actText, cText='/testingjoin', aType=actType, cType='private'):
                rtext = actText.replace('/testingjoin','').replace(' ','')
                if not rtext:
                    send_text = u"Elige un evento /testingparticipants"
                else:
                    add_to_event(rtext, actUser)

            if check_type_and_text_start(aText= actText, cText='/testingparticipants', aType=actType, cType='private'):
                rtext = actText.replace('/testingparticipants','').replace(' ','')
                if not rtext:
                    send_text = show_list(u"Elige una de las listas:", list_events(), [0])
                else:
                    if len(find_by_event(rtext)) == 0:
                        send_text = u"No hay nadie en {}".format(rtext)
                    else:
                        send_text = show_list(u"Participantes en {}:".format(rtext), find_by_event(rtext), [2, 0])

            if check_type_and_text_start(aText= actText, cText='/testingdisjoin', aType=actType, cType='private'):
                rtext = actText.replace('/testingdisjoin','').replace(' ','')
                send_text = remove_from_event(rtext, actUser)

            if check_type_and_text_start(aText= actText, cText='/testinghelp', aType=actType, cType='private'): #, aType=actType, cType='private'):
                send_text = helpTesting()

            if check_type_and_text_start(aText= actText, cText='/testingempty', aType=actType, cType='private'):
                rtext = actText.replace('/testingempty','').replace(' ','')
                if rtext != 'comida':
                    send_text = empty_event(rtext, actUser)
                else:
                    send_text = 'No soy tonto, no voy a dejar que borres quien come hoy'

            if send_text != None:
                sendMessages(send_text, chat_id)
            elif check_type_and_text_start(aType=actType, cType='private'):
                sendMessages(help(), chat_id)
            else:
                print("Mensaje enviado y no publicado por: "+str(actUser))

            LAST_UPDATE_ID = update_id + 1


def check_type_and_text_start(aText = None, aUName = None, cText = None, aType = None, cType = None, cUName = None):

    result = True

    if cType != None:
        result = result and aType == cType
    if cUName != None:
        if aUName in cUName:
            result = result and False
    if cText != None:
        result = result and aText.startswith(cText)

    return result

def show_list(header, contains, positions = None):
    result = '{}'.format(header)
    if contains != None:
        for a in contains:
            #changes in emojis in python3 telegram version
            result = '{}\n {}'.format(result, telegram.Emoji.SMALL_BLUE_DIAMOND)
            if positions != None:
                for i in positions:
                    result = '{} {} '.format(result, a[i])
            else:
                result = '{} {} '.format(result, a[:])
    return result

def periodicCheck():

    ## Remove periodic comida
    actDate = datetime.now().strftime("%d-%m-%y")
    actComida = find_by_event('comida')

    for a in actComida:
        if a[0] != actDate:
            remove_from_event('comida', a[2][1:])

def help():
    header = "Elige una de las opciones: "
    contain = [['/help', 'Ayuda'], ['/who','¿Quien hay en Sugus?'], ['/como','Yo como aquí']]
    contain = contain + [['/nocomo', 'Yo no como aquí'], ['/quiencome', '¿Quien come aquí?']]
    contain = contain +[['/testinghelp', 'Ayuda testing']]
    return show_list(header, contain, [0, 1])

def helpTesting():
    header = "Elige una de las opciones: "
    contain = [['/testinghelp', 'Ayuda testing'], ['/testingjoin','Apuntarse a un evento']]
    contain = contain + [['/testingdisjoin','Desapuntarse de un evento'], ['/testingparticipants', 'Listar una lista']]
    contain = contain + [['/testingempty', 'Vaciar una lista']]
    return show_list(header, contain, [0, 1])

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

def getWho():
    while True:
        try:
            url = 'http://sugus.eii.us.es/en_sugus.html'
            #html = AssertionErrorurlopen(url).read()
            html = urlopen(url).read()
            pq = PyQuery(html)
            break
        except:
            raise

    ul = pq('ul.usuarios > li')
    who = [w.text() for w in ul.items() if w.text() != "Parece que no hay nadie."]

    return who


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            with open('log','w+') as file:
                file.write(str(datetime.now().strftime("%d-%m-%y"))+"\n")
                file.write(str(e)+"\n")
            pass
