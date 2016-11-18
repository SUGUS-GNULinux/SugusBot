#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime

conn = None

def connection(database):
    global conn
    conn = sqlite3.connect(database)


def sec_init(id_admin):
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS eventTable(date TEXT, event TEXT, name TEXT, UNIQUE(event, name) ON CONFLICT REPLACE)')
    c.execute('CREATE TABLE IF NOT EXISTS userTable(id_user INTEGER PRIMARY KEY, id_user_telegram NUMBER, user_name text, UNIQUE(id_user_telegram, user_name))')
    c.execute('CREATE TABLE IF NOT EXISTS permissionTable(id_permission INTEGER PRIMARY KEY, permission TEXT, UNIQUE(permission))')
    c.execute('CREATE TABLE IF NOT EXISTS rel_user_permission(user INTEGER, permission INTEGER, FOREIGN KEY(user) REFERENCES userTable(id_user), FOREIGN KEY(permission) REFERENCES permissionTable(id_permission))')

    if not c.execute('SELECT COUNT(*) FROM permissionTable').fetchone()[0]:
        c.executemany('INSERT INTO permissionTable(permission) VALUES (?)', [('admin',), ('sugus',)])
        c.execute('INSERT INTO userTable(id_user_telegram) VALUES (?)', (id_admin,))
        #es necesario?
        permission = c.execute('SELECT id_permission FROM permissionTable WHERE permission = ?', ('admin',)).fetchone()[0]
        c.execute('INSERT INTO rel_user_permission VALUES (?, ?)', (1, permission))

    conn.commit()
    c.close()

def add_to(event, name):

    if event and name:
        c = conn.cursor()
        date = datetime.now().strftime("%d-%m-%y")

        c.execute('insert into eventTable values(?, ?, ?)', (date, event.replace(" ",""), u'@'+name))
        conn.commit()
        c.close()
        result =u'@' + name + ' añadido a ' + event

    elif name:
        result = "No tienes nombre de usuario o alias. \n Es necesario para poder añadirte a un evento"
    else:
        result = "No se ha podido añadir el usuario @" + name+ " a la lista " + name

    return result

def find_by_event(event):
    c = conn.cursor()

    result = c.execute('select * from eventTable where event=?', (event.replace(" ",""),)).fetchall()

    c.close()

    return result

def remove_from_event(event, name):

    if any([('@' + name) in i for i in find_by_event(event)]):
        c = conn.cursor()

        c.execute('delete from eventTable where event=? and name=?', (event, u'@' + name))
        conn.commit()

        c.close()
        result = "Has sido eliminado del evento " + event
    else:
        result = "No estás en el evento " + event

    return result

def empty_event(event, name):

    if u'@' + name in find_by_event(event):
        c = conn.cursor()

        c.execute('delete from eventTable where event=?', (event))

        result = "El evento " + event +" ha sido eliminado"
        conn.commit()

        c.close()
    else:
        result = 'El evento ' + event + ' NO ha sido eliminado'

    return result

def list_events():
    c = conn.cursor()

    h = c.execute('select distinct event from eventTable')

    return h
