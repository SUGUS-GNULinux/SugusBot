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
    c.execute('CREATE TABLE IF NOT EXISTS event_table(id_event INTEGER PRIMARY KEY, date TEXT, name TEXT, UNIQUE(date, name))')
    c.execute('CREATE TABLE IF NOT EXISTS userTable(id_user INTEGER PRIMARY KEY, id_user_telegram NUMBER UNIQUE, user_name text UNIQUE)')
    c.execute('CREATE TABLE IF NOT EXISTS rel_user_event(user INTEGER, event INTEGER, date TEXT, FOREIGN KEY(user) REFERENCES userTable(id_user), FOREIGN KEY(event) REFERENCES event_table(id_event), UNIQUE(user, event) ON CONFLICT REPLACE)')
    c.execute('CREATE TABLE IF NOT EXISTS permissionTable(id_permission INTEGER PRIMARY KEY, permission TEXT, UNIQUE(permission))')
    c.execute('CREATE TABLE IF NOT EXISTS rel_user_permission(user INTEGER, permission INTEGER, FOREIGN KEY(user) REFERENCES userTable(id_user), FOREIGN KEY(permission) REFERENCES permissionTable(id_permission))')

    if not c.execute('SELECT COUNT(*) FROM permissionTable').fetchone()[0]:
        c.executemany('INSERT INTO permissionTable(permission) VALUES (?)', [('admin',), ('sugus',)])
        c.execute('INSERT INTO userTable(id_user_telegram) VALUES (?)', (id_admin,))
        #es necesario?
        permission = c.execute('SELECT id_permission FROM permissionTable WHERE permission = ?', ('admin',)).fetchone()[0]
        c.execute('INSERT INTO rel_user_permission VALUES (?, ?)', (1, permission))

    if not c.execute('SELECT COUNT(*) FROM event_table').fetchone()[0]:
        c.execute('INSERT INTO event_table(date, name) VALUES (?, ?)', ("", "comida"))

    conn.commit()
    c.close()


def add_to_event(event_name, user_id):
    user = find_user_by_telegram_user_id(user_id=user_id)
    event = find_event_by_name(event_name=event_name)

    if event and user:
        c = conn.cursor()
        date = datetime.now().strftime("%d-%m-%y")

        c.execute('insert into rel_user_event values(?, ?, ?)', (user[0], event[0], date))
        conn.commit()
        c.close()
        result = "añadido a " + event_name

    elif not user:
        result = "No estás registrado en el sistema"
    else:
        result = "Evento no encontrado"

    return result


def find_event_by_name(event_name):
    c = conn.cursor()
    h = c.execute('select * from event_table where name=?', (event_name,)).fetchone()

    c.close()

    return h


def find_users_by_event(event_name):
    event = find_event_by_name(event_name=event_name)

    if event:
        c = conn.cursor()

        result = c.execute('SELECT * FROM userTable INNER JOIN rel_user_event ON userTable.id_user = rel_user_event.user where rel_user_event.event = ?', (event[0],)).fetchall()

        c.close()
    else:
        result = "Evento no encontrado"

    return result


def remove_from_event(event, name):

    result = "No implementado"

#    if any([('@' + name) in i for i in find_users_by_event(event)]):
#        c = conn.cursor()
#
#        c.execute('delete from eventTable where event=? and name=?', (event, u'@' + name))
#        conn.commit()
#
#        c.close()
#        result = "Has sido eliminado del evento " + event
#    else:
#        result = "No estás en el evento " + event

    return result


#el evento solo lo puede borrar un usuario con privilegios
def empty_event(event, date=None):

    result = "No implementado"

    # if find_users_by_event(event):
    #     c = conn.cursor()
    #
    #     if date:
    #         c.execute('DELETE FROM eventTable WHERE date=? AND event=?', (date,event))
    #         result = "El evento " + event + " de " + date + " ha sido eliminado"
    #     else:
    #
    #         c.execute('DELETE FROM eventTable WHERE event=?', (event,))
    #         result = "El evento " + event +" ha sido eliminado"
    #
    #     conn.commit()
    #
    #     c.close()
    # else:
    #     result = 'El evento ' + event + ' no existe'

    return result


def list_events():
    c = conn.cursor()
    h = c.execute('select distinct name from event_table').fetchall()
    c.close()

    return h


def find_user_by_telegram_user_id(user_id):
    c = conn.cursor()
    h = c.execute('select * from userTable where id_user_telegram=?', (user_id,)).fetchone()

    c.close()

    return h


def check_user_permission(user_id, permission):
    c = conn.cursor()
    h = c.execute('select * from userTable INNER JOIN rel_user_permission ON userTable.id_user = rel_user_permission.user INNER JOIN permissionTable ON permissionTable.id_permission = rel_user_permission.permission where userTable.id_user_telegram = ? and permissionTable.permission = ?', (user_id, permission)).fetchone()

    if h:
        h = h[0]

    c.close()

    return h


def add_permission_group(permission_name):
    if permission_name and permission_name is not " ":
        permission_name = permission_name.replace(" ", "_")
        c = conn.cursor()

        c.execute('INSERT INTO permissionTable(permission) VALUES (?)', (permission_name,))
        conn.commit()
        c.close()
        return "Añadido grupo de permiso '" + str(permission_name) + "'"
    else:
        return "Grupo de permiso no válido: " + str(permission_name)


def list_permission_group():
    c = conn.cursor()

    h = c.execute('SELECT permission FROM permissionTable').fetchall()
    if h:
        h = [i[0] for i in c.execute('SELECT permission FROM permissionTable').fetchall()]

    c.close()
    return h


def add_user_permission(id_user_telegram, permission):
    c = conn.cursor()
    permission = c.execute('SELECT id_permission FROM permissionTable WHERE permission = ?', (permission,)).fetchone()

    if permission:
        c.execute('INSERT INTO userTable(id_user_telegram) VALUES (?)', (id_user_telegram,))
        id_user = c.execute('SELECT id_user from userTable WHERE id_user_telegram = ?', (id_user_telegram,)).fetchone()[0]
        c.execute('INSERT INTO rel_user_permission VALUES (?, ?)', (id_user, permission[0]))
        conn.commit()
        return "Rol añadido a usuario " + str(id_user_telegram)
    else:
        return "El rol indicado no existe"

    c.close()
