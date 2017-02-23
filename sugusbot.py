#!/usr/bin/python3.5
# -*- coding: utf-8 -*-

import logging
import telegram

import codecs
import sys
import os

from datetime import timedelta

import configparser

from emoji import emojize

from repository import *
from messaging import create_bot, getUpdates, sendMessages
from auxilliary_methods import *

config = configparser.ConfigParser()
config.read('myconfig.ini')
database = config['Database']['route']
token = config['Telegram']['token']
id_admin = config['Telegram']['id_admin']

last_periodic_check = None

# Get last update ID
LAST_UPDATE_ID = None

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

    while True:
        updates = getUpdates(LAST_UPDATE_ID, timeout=1)
        if updates is not None and updates:
            num_discarded += len(updates)
            update_last_update_id(updates[-1].update_id)
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

            stop, send_text = update_user(id_user_telegram=act_user_id, user_name=actUser)

            if send_text:
                sendMessages(send_text, chat_id)
                update_last_update_id(update_id)
                send_text = None

            if stop:
                break

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

            if check_type_and_text_start(aText=actText, cText='/addgroup', aType=actType, cType='private', cUId=message.from_user.id, perm_required=["admin"]):
                rtext = actText.replace('/addgroup ','').replace('/addgroup','')
                send_text = add_permission_group(rtext)

            if check_type_and_text_start(aText=actText, cText='/addtogroup', aType=actType, cType='private', cUId=message.from_user.id, perm_required=["admin", "sugus"]):
                rtext = actText.replace('/addtogroup ','').replace('/addtogroup','').split(" ")
                db_user = find_user_by_telegram_user_name(rtext[0])
                if len(rtext) != 2:
                    send_text = "Formato incorrecto. El formato debe ser: \n '/addtogroup @username group_name'"
                elif not db_user:
                    send_text = "Nombre de usuario '" + rtext[0] + "' no encontrado en la base de datos"
                else:
                    send_text = add_user_permission(db_user[1], rtext[1])

            if check_type_and_text_start(aText=actText, cText='/delfromgroup', aType=actType, cType='private', cUId=message.from_user.id, perm_required=["admin", "sugus"]):
                rtext = actText.split(" ")
                if len(rtext) != 3:
                    send_text = "Has introducido el comando de manera incorrecta. El formato debe ser:\n'/delfromgroup @usermane groupname'"
                else:
                    user = find_user_by_telegram_user_name(rtext[1])
                    send_text = remove_from_group(user[1], rtext[2])

            if check_type_and_text_start(aText= actText, cText='/groups', aType=actType, cType='private', cUId=message.from_user.id):
                send_text = show_list(u"Grupos de permisos disponibles:", list_permission_group())

            if check_type_and_text_start(aText=actText, cText='/event', aType=actType, cType='private'):
                send_text = help_event()

            if check_type_and_text_start(aText=actText, cText='/events', aType=actType, cType='private'):
                send_text = show_list(u"Elige una de las listas:", list_events(), [0])

            if check_type_and_text_start(aText=actText, cText='/addevent', aType=actType, cType='private', cUId=message.from_user.id, perm_required=["admin", "sugus"]):
                rtext = actText.replace('/addevent ','').replace('/addevent','').split(" ")
                if len(rtext) < 2:
                    send_text = "Formato incorrecto. El formato debe ser: \n '/addevent nombre-evento dd-mm-aaaa'"
                elif not check_date(rtext[len(rtext) - 1]):
                    send_text = "Formato de fecha incorrecto. Esperado 'dd-mm-aaaa'"
                else:
                    event_name = ' '.join([str(x) for x in rtext[0:len(rtext) - 1]])
                    send_text = add_event(event_name, rtext[len(rtext) - 1], message.from_user.id)

            if check_type_and_text_start(aText=actText, cText='/removeevent', aType=actType, cType='private', cUId=message.from_user.id, perm_required=["admin"]):
                rtext = actText.split(' ')
                if len(rtext) < 2:
                    send_text = "Formato incorrecto. El formato debe ser:\n/removeevent nombre-evento"
                else:
                    event = find_event_by_name(rtext[1])
                    if not event:
                        send_text = "El evento no existe"
                    elif int(event[3]) == message.from_user.id:
                        send_text = remove_event(rtext[1])
                    else:
                        send_text = "No tienes permiso para eliminar este evento"

            if check_type_and_text_start(aText=actText, cText='/jointoevent', aType=actType, cType='private'):
                rtext = actText.replace('/jointoevent','').replace(' ','')
                if not rtext:
                    send_text = u"Elige un evento /events"
                else:
                    send_text = add_to_event(rtext, act_user_id)

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

            if send_text != None:
                sendMessages(send_text, chat_id)
            elif check_type_and_text_start(aType=actType, cType='private'):
                sendMessages(help(), chat_id)
            else:
                print("Mensaje enviado y no publicado por: "+str(actUser))

            update_last_update_id(update_id)


def update_last_update_id(update_id):
    global LAST_UPDATE_ID

    LAST_UPDATE_ID = update_id + 1


def periodic_check():

    global last_periodic_check

    yesterday_date = datetime.now() - timedelta(days=1)
    yesterday_date = yesterday_date.strftime("%d-%m-%y")

    if last_periodic_check is yesterday_date:
        empty_event('comida')

        last_periodic_check = datetime.now().strftime("%d-%m-%y")

def help():
    header = "Elige una de las opciones: "
    contain = [['/help', 'Ayuda'], ['/who','¿Quien hay en Sugus?'], ['/comida','Opciones de comida']]
    contain = contain + [['/group', 'Opciones de permisos']]
    contain = contain + [['/event', 'Opciones de eventos']]
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
    contain = [['/help', 'Ayuda'], ['/groups', 'Listar grupos'], ['/addgroup', 'Añadir un grupo']]
    contain += [['/addtogroup', 'Añadir a alguien a un grupo'], ['/delfromgroup', 'Sacar a alguien de un grupo']]
    return show_list(header, contain)


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            if os.path.isfile('log') and os.stat('log').st_size > 1024:
                permission = 'w'
            else:
                permission = 'a'
            with open('log', permission) as f:
                f.write(str(datetime.now().strftime("%d-%m-%y"))+"\n")
                f.write(str(e)+"\n")
