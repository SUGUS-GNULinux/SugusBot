#!/usr/bin/python3.5
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

def add_to_event(event, name):

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

#el evento solo lo puede borrar un usuario con privilegios
def empty_event(event, date=None):

    if find_by_event(event):
        c = conn.cursor()

        if date:
            c.execute('DELETE FROM eventTable WHERE date=? AND event=?', (date,event))
            result = "El evento " + event + " de " + date + " ha sido eliminado"
        else:

            c.execute('DELETE FROM eventTable WHERE event=?', (event,))
            result = "El evento " + event +" ha sido eliminado"

        conn.commit()

        c.close()
    else:
        result = 'El evento ' + event + ' no existe'

    return result


def list_events():
    c = conn.cursor()

    h = c.execute('select distinct event from eventTable')

    return h


def find_user_by_user_id(user_id):
    c = conn.cursor()

    h = c.execute('select * from userTable where id_user_telegram=?', (user_id,)).fetchone()

    return h


def find_user_by_user_id_and_permission(user_id, permission):
    c = conn.cursor()

    h = c.execute('select * from userTable INNER JOIN rel_user_permission ON userTable.id_user = rel_user_permission.user INNER JOIN permissionTable ON permissionTable.id_permission = rel_user_permission.permission where userTable.id_user_telegram = ? and permissionTable.permission = ?', (user_id, permission)).fetchone()

    return h


def add_permission_group(permission_name):
    permission_name = permission_name.replace(" ", "_")
    if permission_name != None and permission_name is not "" and permission_name is not "_":
        c = conn.cursor()

        c.execute('INSERT INTO permissionTable(permission) VALUES (?)', (permission_name,))
        conn.commit()
        c.close()
        return "Añadido grupo de permiso '" + str(permission_name) + "'"
    else:
        return "Grupo de permiso no válido: " + str(permission_name)


def list_permission_group():
    c = conn.cursor()

    h = c.execute('SELECT permission FROM permissionTable')

    return h
