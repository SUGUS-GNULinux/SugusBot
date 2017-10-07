#!/usr/bin/python3.5
# -*- coding: utf-8 -*-

from urllib.request import urlopen
from pyquery import PyQuery
import telegram
from repository import find_user_by_telegram_user_id, check_user_permission
from emoji import emojize
from datetime import datetime


def get_who():

    while True:
        try:
            url = 'https://sugus.eii.us.es/en_sugus.html'
            #html = AssertionErrorurlopen(url).read()
            html = urlopen(url).read()
            pq = PyQuery(html)
            break
        except:
            raise

    ul = pq('ul.usuarios > li')
    who = [w.text() for w in ul.items() if w.text() != "Parece que no hay nadie."]

    return who


def check_type_and_text_start(aText = None,
                              aUName = None,
                              cText = None,
                              aType = None,
                              cType = None,
                              cUId = None,
                              perm_required=None):
    # Si perm_required es None y cUId no es None entonces se busca que el usuario esté en cualquier grupo

    result = True

    if cType is not None:
        result = aType == cType
    if cUId is not None:
        if perm_required is None:  # Comprobar solo usuario y permiso
            result = result and find_user_by_telegram_user_id(cUId)
        else:  # Comprobar usuario y permisos
            for a in perm_required:
                if check_user_permission(cUId, a):
                    result = result and True
    if cText is not None:
        result = result and aText.startswith(cText)

    return result

def check_permissions(user_id, required_perm):
    return all([check_user_permission(user_id, perm) for perm in required_perm])

def show_list(header, contains, positions = None):

    result = [header + "\n"]

    if contains:
        if positions:
            for a in contains:
                a_ordered = [str(a[i]) for i in positions]
                result.append("{} {}\n".format(emojize(":small_blue_diamond:", use_aliases=True), " ".join(a_ordered)))
        else:
            if isinstance(contains[0], str):
                rows = ["{} {}\n".format(emojize(":small_blue_diamond:", use_aliases=True) ,a) for a in contains]
            else:
                rows = ["{} {}\n".format(emojize(":small_blue_diamond:", use_aliases=True) ," ".join(a)) for a in contains]
            result += rows

    return "".join(result)


def check_date(date):
    res = True

    try:
        if datetime.strptime(date, '%d-%m-%Y').date() < datetime.today().date():
            res = False
    except ValueError:
        res = False
    return res
