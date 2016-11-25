#!/usr/bin/python3.5
# -*- coding: utf-8 -*-


class conversation_session():
    def __init__(self):
        self.__inConversation = {}

    @staticmethod
    def __g_key(act_user, conversation_id=None):
        # Generate the key based on actUser and conversationId
        if conversation_id is None:
            conversation_id = act_user.id

        return str(act_user.id) + "-" + str(conversation_id)

    def __add(self, key, options):
        self.__inConversation[key] = options

    def add_option(self, act_user, option, value, conversation_id=None):
        """Añade el par de valores (option, value) para el usuario"""
        key = self.__g_key(act_user, conversation_id)
        if not self.get(act_user):
            self.__inConversation[key] = {option: value}
        else:
            self.__inConversation[key][option] = value

    def del_option(self, act_user, option, conversation_id=None):
        """Elimina la opción 'option' del usuario"""
        key = self.__g_key(act_user, conversation_id)
        del self.__inConversation[key][option]

    def empty(self, act_user, conversation_id=None):
        """Elimina todas las opciones para el usuario"""
        key = self.__g_key(act_user, conversation_id)
        del self.__inConversation[key]

    def get(self, act_user, conversation_id=None):
        """Devuelve todas las opciones del usuario"""
        key = self.__g_key(act_user, conversation_id)
        try:
            result = self.__inConversation[key]
        except KeyError as error:
            result = []
            pass
        return result

    def contain_option(self, act_user, option, conversation_id=None, c_opt_value=None):
        """Comprueba si existe la opción 'option' para el usuario"""
        options = self.get(act_user, conversation_id)
        if option in options:
            if c_opt_value == options[option]:
                return True
            elif c_opt_value == None:
                return True
            else:
                return False
        else:
            return False

    def status(self, act_user, conversation_id=None):
        """Dice si el usuario tiene alguna sesión en curso"""
        key = self.__g_key(act_user, conversation_id)
        if key in self.__inConversation:
            return True
        else:
            return False
