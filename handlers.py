#!/usr/bin/python3.5
# -*- coding: utf-8 -*-

import repository
from emoji import emojize
from auxilliary_methods import *

"""
This module contains the functions that handlers execute.
"""

# Help functions
def help_eat():
    header = "Elige una de las opciones: "
    contain = [['/help', 'Ayuda']]
    contain = contain + [['/como', 'Yo como aquí'],
                         ['/nocomo', 'Yo no como aquí'],
                         ['/quiencome', '¿Quien come aquí?']]
    return show_list(header, contain)


def help_event():
    header = "Elige una de las opciones: "
    contain = [['/help', 'Ayuda']]
    contain += [['/events', 'Listar eventos'],
                ['/addevent', 'Añadir un evento'],
                ['/removeevent', 'Eliminar un evento']]
    contain += [['/leaveevent', 'Abandonar un evento'],
                ['/jointoevent', 'Unirte a un evento'],
                ['/participants', 'Listar participantes']]
    return show_list(header, contain)


def help_group():
    header = "Elige una de las opciones: "
    contain = [['/help', 'Ayuda'], ['/groups', 'Listar grupos'],
               ['/addgroup', 'Añadir un grupo']]
    contain += [['/addtogroup', 'Añadir a alguien a un grupo'],
                ['/delfromgroup', 'Sacar a alguien de un grupo']]
    return show_list(header, contain)


# Command handlers definitions
def start(bot, update):
    update.message.reply_text('¡Hola! Soy SugusBot, escribe "/help" para ver'
                              ' la lista de comandos disponibles.')


def help(bot, update):
    header = "Elige una de las opciones: "
    contain = [['/help', 'Ayuda'], ['/who', '¿Quien hay en Sugus?'],
               ['/comida', 'Opciones de comida']]
    contain = contain + [['/group', 'Opciones de permisos']]
    contain = contain + [['/event', 'Opciones de eventos']]
    update.message.reply_text(show_list(header, contain))


def who(bot, update):
    actText = update.message.text
    actType = update.message.chat.type

    if check_type_and_text_start(aText=actText, cText='/who', aType=actType,
                                 cType='private'):
        max_retry = 2
        for i in range(max_retry):
            try:
                who = get_who()
                if not who:
                    send_text = u"Parece que no hay nadie... {}".format(
                        emojize(":disappointed_face:", use_aliases=True))
                else:
                    send_text = show_list(u"Miembros en SUGUS:", who)
                break
            except Exception as e:
                if i is max_retry - 1:
                    print("Hubo un error repetitivo al intentar conectar al "
                          "servidor: ", e)
                    send_text = u"Hubo algún error al realizar la petición" + \
                                u" a la web de sugus"

    if send_text is not None:
        update.message.reply_text(send_text)
    else:
        update.message.reply_text(help())


def como(bot, update):
    actText = update.message.text
    actType = update.message.chat.type
    act_user_id = update.message.from_user.id

    if check_type_and_text_start(aText=actText, cText='/como', aType=actType,
                                 cType='private'):
        send_text = add_to_event('comida', act_user_id)

    if send_text is not None:
        update.message.reply_text(send_text)
    else:
        update.message.reply_text(help())


def no_como(bot, update):
    actText = update.message.text
    actType = update.message.chat.type
    act_user_id = update.message.from_user.id

    if check_type_and_text_start(aText=actText, cText='/nocomo', aType=actType,
                                 cType='private'):
        send_text = remove_from_event('comida', act_user_id)

    if send_text is not None:
        update.message.reply_text(send_text)
    else:
        update.message.reply_text(help())


def quien_come(bot, update):
    actText = update.message.text
    actType = update.message.chat.type
    act_user_id = update.message.from_user.id

    if check_type_and_text_start(aText=actText, cText='/quiencome',
                                 aType=actType, cType='private'):
        quiencome = repository.find_users_by_event('comida')
        if quiencome:
            send_text = show_list(u"Hoy come en Sugus:", quiencome, [2])
        else:
            send_text = 'De momento nadie come en Sugus'

    if send_text is not None:
        update.message.reply_text(send_text)
    else:
        update.message.reply_text(help())


def comida(bot, update):
    actText = update.message.text
    actType = update.message.chat.type

    if check_type_and_text_start(aText=actText, cText='/comida',
                                 aType=actType, cType='private'):
        send_text = help_eat()

    if send_text is not None:
        update.message.reply_text(send_text)
    else:
        update.message.reply_text(help())


def group(bot, update):
    actText = update.message.text
    actType = update.message.chat.type

    if check_type_and_text_start(aText=actText, cText='/group',
                                 aType=actType, cType='private'):
        send_text = help_eat()

    if send_text is not None:
        update.message.reply_text(send_text)
    else:
        update.message.reply_text(help())


def add_group(bot, update):
    actText = update.message.text
    actType = update.message.chat.type

    if check_type_and_text_start(aText=actText, cText='/addgroup',
                                 aType=actType, cType='private',
                                 cUId=update.message.from_user.id,
                                 perm_required=["admin"]):
        rtext = actText.replace('/addgroup ', '').replace('/addgroup', '')
        send_text = repository.add_permission_group(rtext)

    if send_text is not None:
        update.message.reply_text(send_text)
    else:
        update.message.reply_text(help())


def add_to_group(bot, update):
    actText = update.message.text
    actType = update.message.chat.type

    if check_type_and_text_start(aText=actText, cText='/addtogroup',
                                 aType=actType, cType='private',
                                 cUId=update.message.from_user.id,
                                 perm_required=["admin", "sugus"]):
        rtext = actText.replace('/addtogroup ', '').replace('/addtogroup', '')\
                .split(" ")
        db_user = repository.find_user_by_telegram_user_name(rtext[0])

        if len(rtext) != 2:
            send_text = "Formato incorrecto. El formato debe ser: \n" + \
                        "'/addtogroup @username group_name'"
        elif not db_user:
            send_text = "Nombre de usuario '" + rtext[0] + \
                        "' no encontrado en la base de datos"
        else:
            send_text = repository.add_user_permission(db_user[1], rtext[1])

    if send_text is not None:
        update.message.reply_text(send_text)
    else:
        update.message.reply_text(help())


def del_from_group(bot, update):
    actText = update.message.text
    actType = update.message.chat.type

    if check_type_and_text_start(aText=actText, cText='/delfromgroup',
                                 aType=actType, cType='private',
                                 cUId=update.message.from_user.id,
                                 perm_required=["admin", "sugus"]):
        rtext = actText.split(" ")

        if len(rtext) != 3:
            send_text = "Has introducido el comando de manera incorrecta." + \
                        "El formato debe ser:\n'/delfromgroup @usermane " + \
                        "groupname'"
        else:
            user = find_user_by_telegram_user_name(rtext[1])
            send_text = repository.remove_from_group(user[1], rtext[2])

    if send_text is not None:
        update.message.reply_text(send_text)
    else:
        update.message.reply_text(help())


def groups(bot, update):
    actText = update.message.text
    actType = update.message.chat.type

    if check_type_and_text_start(aText=actText, cText='/groups',
                                 aType=actType, cType='private',
                                 cUId=update.message.from_user.id):
        send_text = show_list(u"Grupos de permisos disponibles:",
                              repository.list_permission_group())

    if send_text is not None:
        update.message.reply_text(send_text)
    else:
        update.message.reply_text(help())


def event(bot, update):
    actText = update.message.text
    actType = update.message.chat.type

    if check_type_and_text_start(aText=actText, cText='/event',
                                 aType=actType, cType='private'):
        send_text = help_event()

    if send_text is not None:
        update.message.reply_text(send_text)
    else:
        update.message.reply_text(help())


def events(bot, update):
    actText = update.message.text
    actType = update.message.chat.type

    if check_type_and_text_start(aText=actText, cText='/events',
                                 aType=actType, cType='private'):
        send_text = show_list(u"Elige una de las listas:",
                              repository.list_events(), [0, 1])

    if send_text is not None:
        update.message.reply_text(send_text)
    else:
        update.message.reply_text(help())


def add_event(bot, update):
    actText = update.message.text
    actType = update.message.chat.type

    if check_type_and_text_start(aText=actText, cText='/addevent',
                                 aType=actType, cType='private',
                                 cUId=update.message.from_user.id,
                                 perm_required=["admin", "sugus"]):
        rtext = actText.replace('/addevent ', '').replace('/addevent', '')\
                .split(" ")
        if len(rtext) < 2:
            send_text = "Formato incorrecto. El formato debe ser: \n " + \
                        "'/addevent nombre-evento dd-mm-aaaa'"
        elif not check_date(rtext[len(rtext) - 1]):
            send_text = "Formato de fecha incorrecto ('dd-mm-aaaa') " + \
                        "o la fecha ya ha pasado"
        else:
            event_name = ' '.join([str(x) for x in rtext[0:len(rtext) - 1]])
            send_text = repository.add_event(event_name, rtext[len(rtext) - 1],
                                             update.message.from_user.id)

    if send_text is not None:
        update.message.reply_text(send_text)
    else:
        update.message.reply_text(help())


def remove_event(bot, update):
    actText = update.message.text
    actType = update.message.chat.type

    if check_type_and_text_start(aText=actText, cText='/removeevent',
                                 aType=actType, cType='private',
                                 cUId=update.message.from_user.id,
                                 perm_required=["admin"]):
        rtext = actText.split(' ')

        if len(rtext) < 2:
            send_text = "Formato incorrecto. El formato debe ser:\n" + \
                        "'/removeevent nombre-evento'"
        else:
            event = repository.find_event_by_name(rtext[1])

            if not event:
                send_text = "El evento no existe"
            elif (int(event[3]) == update.message.from_user.id and
                  not bool(repository.find_users_by_event(rtext[1])) and
                  check_date(event[1], "%d-%m-%Y")):
                send_text = remove_event(rtext[1])
            else:
                send_text = "No tienes permiso para eliminar este evento"

    if send_text is not None:
        update.message.reply_text(send_text)
    else:
        update.message.reply_text(help())


def join_to_event(bot, update):
    actText = update.message.text
    actType = update.message.chat.type

    if check_type_and_text_start(aText=actText, cText='/jointoevent',
                                 aType=actType, cType='private'):
        rtext = actText.replace('/jointoevent', '').replace(' ', '')
        if not rtext:
            send_text = u"Elige un evento /events"
        else:
            send_text = repository.add_to_event(rtext, act_user_id)

    if send_text is not None:
        update.message.reply_text(send_text)
    else:
        update.message.reply_text(help())


def participants(bot, update):
    actText = update.message.text
    actType = update.message.chat.type

    if check_type_and_text_start(aText=actText, cText='/participants',
                                 aType=actType, cType='private'):
        rtext = actText.replace('/participants', '').replace(' ', '')

        if not rtext:
            send_text = show_list(u"Elige una de las listas:", list_events())
        else:
            if len(find_users_by_event(rtext)) == 0:
                send_text = u"No hay nadie en {}".format(rtext)
            else:
                send_text = show_list(u"Participantes en {}:".format(rtext),
                                      find_users_by_event(rtext), [2])

    if send_text is not None:
        update.message.reply_text(send_text)
    else:
        update.message.reply_text(help())


def leave_event(bot, update):
    actText = update.message.text
    actType = update.message.chat.type

    if check_type_and_text_start(aText=actText, cText='/leaveevent',
                                 aType=actType, cType='private'):
        rtext = actText.replace('/leaveevent', '').replace(' ', '')
        send_text = repository.remove_from_event(rtext, act_user_id)

    if send_text is not None:
        update.message.reply_text(send_text)
    else:
        update.message.reply_text(help())


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))
