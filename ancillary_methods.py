#!/usr/bin/python3.5
# -*- coding: utf-8 -*-

from urllib.request import urlopen
from pyquery import PyQuery
import telegram


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
