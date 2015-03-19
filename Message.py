import pickle

"""
Type 0 = Mensaje de chat
Type 1 = Lista de players
Type 2 = Salir del programa
Type 3 = Roll
Type 4 = Invisible roll
Type 5 = Refused connection
Type 6 = Whisp
"""
class Message(object):
    def __init__ (self):
        self.msgList = []
        self.type = 0
        self.player = None
        self.master = None
        self.target = None
        self.roll = []

    def addMessage(self, msg):
        self.msgList.append(msg)

    def serialize(self):
        return pickle.dumps(self)

    def unserialize(self, data):
        return pickle.loads(data)

    def getAll(self):
        return self.msgList
