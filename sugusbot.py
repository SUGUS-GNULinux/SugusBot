#!/usr/bin/python3.5
# -*- coding: utf-8 -*-

import logging
import telegram

import codecs
import sys

from datetime import datetime, timedelta

import configparser

from repository import connection, sec_init, add_to_event, find_by_event, remove_from_event, empty_event, list_events, add_permission_group, list_permission_group
from messaging import create_bot, getUpdates, sendMessages
from ancillary_methods import getWho, check_type_and_text_start, show_list

config = configparser.ConfigParser()
config.read('myconfig.ini')
database = config['Database']['route']
token = config['Telegram']['token']
id_admin = config['Telegram']['id_admin']

# Create bot object
create_bot(token)

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
        updates = getUpdates(LAST_UPDATE_ID, timeout=1)
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

            if check_type_and_text_start(aText=actText, cText='/comida', aType=actType, cType='private'):
                send_text = help_eat()

            if check_type_and_text_start(aText=actText, cText='/group', aType=actType, cType='private'):
                send_text = help_group()

            if check_type_and_text_start(aText=actText, cText='/groupadd', aType=actType, cType='private', cUId=message.from_user.id, perm_required="admin"):
                rtext = actText.replace('/groupadd ','').replace('/groupadd','')
                send_text = add_permission_group(rtext)

            if check_type_and_text_start(aText= actText, cText='/groups', aType=actType, cType='private', cUId=message.from_user.id):
                send_text = show_list(u"Grupos de permisos disponibles:", list_permission_group(), [0])

            if check_type_and_text_start(aText=actText, cText='/testingjoin', aType=actType, cType='private'):
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


def periodicCheck():

    ## Remove periodic comida
    yesterdayDate = datetime.now() - timedelta(days = 1)
    yesterdayDate = yesterdayDate.strftime("%d-%m-%y")

    empty_event('comida',yesterdayDate)


def help():
    header = "Elige una de las opciones: "
    contain = [['/help', 'Ayuda'], ['/who','¿Quien hay en Sugus?'], ['/comida','Opciones de comida']]
    contain = contain + [['/group', 'Opciones de grupos de permisos']]
    contain = contain +[['/testinghelp', 'Ayuda testing']]
    return show_list(header, contain, [0, 1])


def help_eat():
    header = "Elige una de las opciones: "
    contain = [['/help', 'Ayuda']]
    contain = contain + [['/como','Yo como aquí'], ['/nocomo', 'Yo no como aquí'], ['/quiencome', '¿Quien come aquí?']]
    return show_list(header, contain, [0, 1])


def help_group():
    header = "Elige una de las opciones: "
    contain = [['/help', 'Ayuda']]
    contain = contain + [['/groups', 'Listar grupos'], ['/groupadd', 'Añadir un grupo']]
    return show_list(header, contain, [0, 1])


def helpTesting():
    header = "Elige una de las opciones: "
    contain = [['/testinghelp', 'Ayuda testing'], ['/testingjoin','Apuntarse a un evento']]
    contain = contain + [['/testingdisjoin','Desapuntarse de un evento'], ['/testingparticipants', 'Listar una lista']]
    contain = contain + [['/testingempty', 'Vaciar una lista']]
    return show_list(header, contain, [0, 1])


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            with open('log','w+') as f:
                f.write(str(datetime.now().strftime("%d-%m-%y"))+"\n")
                f.write(str(e)+"\n")
