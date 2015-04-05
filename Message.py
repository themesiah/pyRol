# -*- coding: cp1252 -*-
import pickle

"""
Type 0 = Mensaje de chat
Type 1 = Lista de players
Type 2 = Salir del programa
Type 3 = Roll
Type 4 = Invisible roll
Type 5 = Refused connection
Type 6 = Whisp
Type 7 = Comando HELP
"""
class Message(object):
    """
    Inicializamos todas las variables que tendrán los mensajes.
    """
    def __init__ (self):
        self.msgList = []
        self.type = 0
        self.player = None
        self.master = None
        self.target = None
        self.roll = []

    """
    Añadimos un mensaje a la lista de mensajes.
    """
    def addMessage(self, msg):
        self.msgList.append(msg)

    """
    Serializamos el objeto.
    """
    def serialize(self):
        return pickle.dumps(self)

    """
    Deserializamos el objeto a partir
    de datos y devolvemos la versión deserializada.
    """
    def unserialize(self, data):
        return pickle.loads(data)

    """
    Obtenemos todos los mensajes del objeto.
    """
    def getAll(self):
        return self.msgList
