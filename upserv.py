import socket, os, thread, time

class Updater(object):
    def __init__(self):
        self.init()
        self.update()

    def initSocket(self):
        self.IP = ""
        self.PORT = 6900
        self.BUFFER = 4098
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.IP, self.PORT))
        print "Listening on port " + str(self.PORT)

    def initVersion(self):
        f = open("lastversion.txt", 'r')
        self.VERSION = f.read()
        f.close()

        f = open("updates.txt", 'r')
        updates = f.readlines()
        f.close()

        self.fileupdates = dict()
        last = 0
        
        for up in updates:
            up = up.rstrip()
            if up[0] == "$":
                last = int(up[1:])
                self.fileupdates[last] = []
            else:
                self.fileupdates[last].append(up)
                

    def init(self):
        self.initSocket()
        self.initVersion()
        
    
    def getFiles(self, version):
        print "Version is: " + str(self.VERSION)
        i = int(self.VERSION)
        version = int(version)
        toUpdate = []
        while i != version:
            for u in self.fileupdates[i]:
                if not u in toUpdate:
                    toUpdate.append(u)
            i -= 1

        return toUpdate

    def sendFile(self, fi, conn):
        f = open (fi, 'rb')
        data = f.read()
        f.close()
        
        conn.send(fi)
        time.sleep(0.5)
        conn.send(data)
        time.sleep(0.5)
        conn.send("FINISHED")
        time.sleep(0.5)

    def update(self):
        self.s.listen(1)
        conn, addr = self.s.accept()
        print "Sending update to: " + str(addr)
        thread.start_new_thread( self.update, () )
        version = conn.recv(self.BUFFER)
        files = self.getFiles(version)
        for fi in files:
            self.sendFile(fi, conn)
        conn.send("UPDATED")
        print "Finished updating: " + str(addr)
        conn.send(self.VERSION)
        conn.close()
