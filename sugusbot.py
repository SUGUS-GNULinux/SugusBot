#!/usr/bin/python3.5
# -*- coding: utf-8 -*-

import logging
import telegram

import codecs
import sys

from datetime import datetime, timedelta

import configparser

from emoji import emojize

from repository import connection, sec_init, add_to_event, find_users_by_event, remove_from_event, empty_event, list_events, add_permission_group, list_permission_group
from messaging import create_bot, getUpdates, sendMessages
from auxilliary_methods import get_who, check_type_and_text_start, show_list

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
            act_user_id = message.from_user.id

            send_text = None

            periodic_check()

            if check_type_and_text_start(aText= actText, cText='/who', aType=actType, cType='private'):
                who = get_who()

                if not who:
                    send_text = u"Parece que no hay nadie... {}".format(emojize(":disappointed_face:", use_aliases=True))
                else:
                    send_text = show_list(u"Miembros en SUGUS:", who)

            if check_type_and_text_start(aText= actText, cText='/como', aType=actType, cType='private'):
                send_text = add_to_event('comida', act_user_id)

            if check_type_and_text_start(aText= actText, cText='/nocomo', aType=actType, cType='private'):
                send_text = remove_from_event('comida', act_user_id)

            if check_type_and_text_start(aText= actText, cText='/quiencome', aType=actType, cType='private'):
                quiencome = find_users_by_event('comida')
                if quiencome:
                    send_text = show_list(u"Hoy come en Sugus:", quiencome, [2])
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
                send_text = show_list(u"Grupos de permisos disponibles:", list_permission_group())

            if check_type_and_text_start(aText=actText, cText='/helpevents', aType=actType, cType='private'):
                send_text = help_event()

            if check_type_and_text_start(aText=actText, cText='/events', aType=actType, cType='private'):
                send_text = show_list(u"Elige una de las listas:", list_events(), [0])

            if check_type_and_text_start(aText=actText, cText='/addevent', aType=actType, cType='private'):
                send_text = "No disponible"

            if check_type_and_text_start(aText=actText, cText='/removeevent', aType=actType, cType='private'):
                send_text = "No disponible"

            if check_type_and_text_start(aText=actText, cText='/jointoevent', aType=actType, cType='private'):
                rtext = actText.replace('/jointoevent','').replace(' ','')
                if not rtext:
                    send_text = u"Elige un evento /events"
                else:
                    add_to_event(rtext, act_user_id)

            if check_type_and_text_start(aText= actText, cText='/participants', aType=actType, cType='private'):
                rtext = actText.replace('/participants','').replace(' ','')
                if not rtext:
                    send_text = show_list(u"Elige una de las listas:", list_events())
                else:
                    if len(find_users_by_event(rtext)) == 0:
                        send_text = u"No hay nadie en {}".format(rtext)
                    else:
                        send_text = show_list(u"Participantes en {}:".format(rtext), find_users_by_event(rtext), [2])

            if check_type_and_text_start(aText= actText, cText='/leaveevent', aType=actType, cType='private'):
                rtext = actText.replace('/leaveevent','').replace(' ','')
                send_text = remove_from_event(rtext, act_user_id)

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


def periodic_check():

    yesterdayDate = datetime.now() - timedelta(days = 1)
    yesterdayDate = yesterdayDate.strftime("%d-%m-%y")

    empty_event('comida', yesterdayDate)


def help():
    header = "Elige una de las opciones: "
    contain = [['/help', 'Ayuda'], ['/who','¿Quien hay en Sugus?'], ['/comida','Opciones de comida']]
    contain = contain + [['/group', 'Opciones de permisos']]
    contain = contain + [['/helpevents', 'Opciones de eventos']]
    contain = contain +[['/testinghelp', 'Ayuda testing']]
    return show_list(header, contain)


def help_eat():
    header = "Elige una de las opciones: "
    contain = [['/help', 'Ayuda']]
    contain = contain + [['/como','Yo como aquí'], ['/nocomo', 'Yo no como aquí'], ['/quiencome', '¿Quien come aquí?']]
    return show_list(header, contain)


def help_event():
    header = "Elige una de las opciones: "
    contain = [['/help', 'Ayuda']]
    contain += [['/events', 'Listar eventos'], ['/addevent', 'Añadir un evento'], ['/removeevent', 'Eliminar un evento']]
    contain += [['/leaveevent', 'Abandonar un evento'], ['/jointoevent', 'Unirte a un evento'], ['/participants', 'Listar participantes']]
    return show_list(header, contain)

def help_group():
    header = "Elige una de las opciones: "
    contain = [['/help', 'Ayuda']]
    contain = contain + [['/groups', 'Listar grupos'], ['/groupadd', 'Añadir un grupo']]
    return show_list(header, contain)


def helpTesting():
    header = "Elige una de las opciones: "
    contain = [['/testinghelp', 'Ayuda testing'], ['/testingjoin','Apuntarse a un evento']]
    contain = contain + [['/testingdisjoin','Desapuntarse de un evento'], ['/testingparticipants', 'Listar una lista']]
    contain = contain + [['/testingempty', 'Vaciar una lista']]
    return show_list(header, contain)


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            with open('log','w+') as f:
                f.write(str(datetime.now().strftime("%d-%m-%y"))+"\n")
                f.write(str(e)+"\n")
