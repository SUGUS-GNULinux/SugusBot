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

import sqlite3
from datetime import datetime


token = None
conn = sqlite3.connect('sugusBotDB.db')


with open('token', 'rb') as token_file:
    token = token_file.readline().decode('ascii')[:-1]

# Create bot object
bot = telegram.Bot(token)


def secInit():
    c = conn.cursor()
    c.execute('create table if not exists eventTable(date text, event text, name text, UNIQUE(event, name) ON CONFLICT REPLACE)')
    conn.commit()
    c.close()

def main():

    secInit()

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

            if checkTypeAndTextStart(aText= actText, cText='/who', aType=actType, cType='private'):
                who = getWho()

                if not who:
                    #changes in emojis in python3 telegram version
                    send_text = u"Parece que no hay nadie... {}".format(telegram.Emoji.DISAPPOINTED_FACE)
                else:
                    send_text = showList(u"Miembros en SUGUS:", who)

            if checkTypeAndTextStart(aText= actText, cText='/como', aType=actType, cType='private'):
                send_text = addTo('comida', actUser)

            if checkTypeAndTextStart(aText= actText, cText='/nocomo', aType=actType, cType='private'):
                send_text = removeFromEvent('comida', actUser)

            if checkTypeAndTextStart(aText= actText, cText='/quiencome', aType=actType, cType='private'):
                if len(findByEvent('comida')) != 0:
                    send_text = showList(u"Hoy come en Sugus:", findByEvent('comida'), [2, 0])
                else:
                    send_text = 'De momento nadie come en Sugus'

            if checkTypeAndTextStart(aText= actText, cText='/testingjoin', aType=actType, cType='private'):
                rtext = actText.replace('/testingjoin','').replace(' ','')
                if not rtext:
                    send_text = u"Elige un evento /testingparticipants"
                else:
                    addTo(rtext, actUser)

            if checkTypeAndTextStart(aText= actText, cText='/testingparticipants', aType=actType, cType='private'):
                rtext = actText.replace('/testingparticipants','').replace(' ','')
                if not rtext:
                    send_text = showList(u"Elige una de las listas:", listEvents(), [0])
                else:
                    if len(findByEvent(rtext)) == 0:
                        send_text = u"No hay nadie en {}".format(rtext)
                    else:
                        send_text = showList(u"Participantes en {}:".format(rtext), findByEvent(rtext), [2, 0])

            if checkTypeAndTextStart(aText= actText, cText='/testingdisjoin', aType=actType, cType='private'):
                rtext = actText.replace('/testingdisjoin','').replace(' ','')
                send_text = removeFromEvent(rtext, actUser)

            if checkTypeAndTextStart(aText= actText, cText='/testinghelp', aType=actType, cType='private'): #, aType=actType, cType='private'):
                send_text = helpTesting()

            if checkTypeAndTextStart(aText= actText, cText='/testingempty', aType=actType, cType='private'):
                rtext = actText.replace('/testingempty','').replace(' ','')
                if rtext != 'comida':
                    send_text = emptyEvent(rtext, actUser)
                else:
                    send_text = 'No soy tonto, no voy a dejar que borres quien come hoy'

            if send_text != None:
                sendMessages(send_text, chat_id)
            elif checkTypeAndTextStart(aType=actType, cType='private'):
                sendMessages(help(), chat_id)
            else:
                print("Mensaje enviado y no publicado por: "+str(actUser))

            LAST_UPDATE_ID = update_id + 1


def checkTypeAndTextStart(aText = None, aUName = None, cText = None, aType = None, cType = None, cUName = None):

    result = True

    if cType != None:
        result = result and aType == cType
    if cUName != None:
        if aUName in cUName:
            result = result and False
    if cText != None:
        result = result and aText.startswith(cText)

    return result

def showList(header, contains, positions = None):
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
    actComida = findByEvent('comida')

    for a in actComida:
        if a[0] != actDate:
            removeFromEvent('comida', a[2])

def help():
    header = "Elige una de las opciones: "
    contain = [['/help', 'Ayuda'], ['/who','¿Quien hay en Sugus?'], ['/como','Yo como aquí']]
    contain = contain + [['/nocomo', 'Yo no como aquí'], ['/quiencome', '¿Quien come aquí?']]
    contain = contain +[['/testinghelp', 'Ayuda testing']]
    return showList(header, contain, [0, 1])

def helpTesting():
    header = "Elige una de las opciones: "
    contain = [['/testinghelp', 'Ayuda testing'], ['/testingjoin','Apuntarse a un evento']]
    contain = contain + [['/testingdisjoin','Desapuntarse de un evento'], ['/testingparticipants', 'Listar una lista']]
    contain = contain + [['/testingempty', 'Vaciar una lista']]
    return showList(header, contain, [0, 1])

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
    who = [w.text() for w in ul.items() if w != "Parece que no hay nadie."]

    return who

def addTo(event, name):

    if event and name:
        c = conn.cursor()
        date = datetime.now().strftime("%d-%m-%y")

        c.execute('insert into eventTable values(?, ?, ?)', (date, event.replace(" ",""), u'@'+name.replace(" ", "")))
        conn.commit()
        c.close()
        result = name + ' añadido a ' + event

    elif name:
        result = "No tienes nombre de usuario o alias. \n Es necesario para poder añadirte a un evento"
    else:
        result = "No se ha podido añadir el usuario @" + name+ " a la lista " + name

    return result

def findByEvent(event):
    c = conn.cursor()

    result = c.execute('select * from eventTable where event=?', (event.replace(" ",""),)).fetchall()

    c.close()

    return result

def removeFromEvent(event, name):

    if any([('@' + name) in i for i in findByEvent(event)]):
        c = conn.cursor()

        c.execute('delete from eventTable where event=? and name=?', (event, u'@' + name))
        conn.commit()

        c.close()
        result = "Has sido eliminado del evento " + event
    else:
        result = "No estás en el evento " + event

    return result

def emptyEvent(event, name):

    if u'@' + name in findByEvent(event):
        c = conn.cursor()

        c.execute('delete from eventTable where event=?', (event))

        result = "El evento " + event +" ha sido eliminado"
        conn.commit()

        c.close()
    else:
        result = 'El evento ' + event + ' NO ha sido eliminado'

    return result

def listEvents():
    c = conn.cursor()

    h = c.execute('select distinct event from eventTable')

    return h

if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            with open('log','w+') as file:
                file.write(str(datetime.now().strftime("%d-%m-%y"))+"\n")
                file.write(str(e))
            pass
