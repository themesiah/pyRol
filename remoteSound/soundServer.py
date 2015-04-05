import socket, time, thread, sys, os

class RemoteSound(object):
    def __init__ (self):
        self.initSocket()

    def initSocket(self):
        self.IP = ""
        self.PORT = 6898
        self.BUFFER = 4098
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.IP, self.PORT))
        print "Sound server listening on port " + str(self.PORT)


    def sendFile(self, fi, conn):
        f = open (fi, 'rb')
        data = f.read()
        f.close()
        
        conn.send(fi)
        time.sleep(0.5)
        conn.send(data)
        time.sleep(0.5)
        conn.send("SOUNDFINISHED")
        time.sleep(0.5)

    def playMessage(self):
