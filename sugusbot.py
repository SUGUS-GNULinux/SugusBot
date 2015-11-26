#!/usr/bin/python

import logging
import urllib
import time
from pyquery import PyQuery
import telegram

TOKEN = None
with open('token', 'r') as token_file:
    TOKEN = token_file.readline().replace('\n', '')

def main():
    # Init logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create bot object
    bot = telegram.Bot(TOKEN)

    # Get last update ID
    LAST_UPDATE_ID = None

    # Discard old updates, sent before the bot was started
    num_discarded = 0
    while True:
        updates = bot.getUpdates(LAST_UPDATE_ID, timeout=1, network_delay=2.0)
        if updates is not None and len(updates) > 0:
            num_discarded = num_discarded + len(updates)
            LAST_UPDATE_ID = updates[-1].update_id + 1
        else:
            break

    print("Discarded {} old updates".format(num_discarded))

    # Main loop
    print("Working...")
    while True:
        updates = bot.getUpdates(LAST_UPDATE_ID, timeout=30, network_delay=2.0)
        for update in updates:
            message = update.message;
            text = message.text
            chat_id = message.chat.id
            update_id = update.update_id

            send_text = None

            if text == '/who':
                who = getWho()
                #who = [u"SugusBot {}".format(telegram.Emoji.PENGUIN.decode('utf-8'))] + who

                if len(who) == 0:
                    send_text = u"Parece que no hay nadie... {}".format(telegram.Emoji.DISAPPOINTED_FACE.decode('utf-8'))
                else:
                    who_bonito = [u"{}{}".format(telegram.Emoji.SMALL_BLUE_DIAMOND.decode('utf-8'), w) for w in who]
                    send_text = u"Miembros en SUGUS:\n{}".format('\n'.join(who_bonito))

            elif text.startswith('/yes'):
                if False:
                    text = text[len('/yes '):]
                    text = text.replace('\n', ' ')

                    if len(text) == 0:
                        text = "y";

                    text = [text for i in xrange(20)]
                    send_text = "\n".join(text)
                else:
                    send_text = u"Al final lo he terminado quitando {}".format(telegram.Emoji.PENGUIN.decode('utf-8'));

            if send_text != None:
                bot.sendMessage(chat_id=chat_id, text=send_text)
                print(u"Mensaje enviado a {}/{} ({})".format(message.from_user.username, message.from_user.first_name, str(message.chat.id)))

            LAST_UPDATE_ID = update_id + 1

def getWho():
    url = 'http://sugus.eii.us.es/en_sugus.html'
    html = urllib.urlopen(url).read()
    pq = PyQuery(html)
    ul = pq('ul.usuarios > li')
    
    who = []
    ul.each(lambda w : who.append(ul.eq(w).text()))

    who_filtered = [w for w in who if w != "Parece que no hay nadie."]

    return who_filtered

if __name__ == '__main__':
    main()
