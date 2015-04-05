# -*- coding: cp1252 -*-
import socket, time, thread, sys, os

"""
Módulo para propagar envío y reproducción de audio a partir de Sockets.
"""
class RemoteSound(object):
    # Llamamos a las funciones que inicializan el módulo.
    def __init__ (self):
        self.initSocket()
        self.run()

    # Inicializamos el socket con los datos correspondientes.
    def initSocket(self):
        self.IP = ""
        self.PORT = 6902
        self.BUFFER = 4098
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.IP, self.PORT))
        self.connList = []
        print "Sound server listening on port " + str(self.PORT)

    # Enviamos un archivo a todos los usuarios.
    def sendFile(self, fi):
        try:
            print "Replicando mensaje: SEND " + fi
            f = open ("music/" + fi, 'rb')
            data = f.read()
            f.close()

            # Enviamos NAME y el nombre del archivo para avisar de que enviaremos un archivo.
            for c in self.connList:
                c[0].send("NAME " + fi)
                time.sleep(0.1)
            # Enviamos el archivo en si.
            for c in self.connList:
                c[0].send(data)
                time.sleep(0.1)
            # Enviamos el indicador de que hemos terminado de mandar el archivo.
            for c in self.connList:
                c[0].send("SOUNDFINISHED")
                time.sleep(0.1)
        except Exception as err:
            print "No se ha encontrado el archivo " + fi

    # Propagamos el mensaje de reproducción a todos los usuarios.
    def playMessage(self, fi):
        print "Replicando mensaje: PLAY " + fi
        for c in self.connList:
            c[0].send("PLAY " + fi)

    # Parseamos un mensaje recibido y actuamos en consecuencia.
    def parseMessage(self, data, master, a):
        # Mensajes que solo puede enviar el master.
        if master:
            if data.split(" ", 2)[0] == "PLAY":
                self.playMessage(data.split(" ", 2)[1])
            elif data.split(" ", 2)[0] == "SEND":
                self.sendFile(data.split(" ", 2)[1])
        # Mensajes que puede enviar cualquiera.
        if data.split(" ", 2)[0] == "RECEIVED":
            print "Received " + data.split(" ", 2)[1] + " from " + str(a)
            
    # Bucle principal.
    # Funciona por threads, y cada thread hace lo mismo.
    def run(self):
        # Aceptamos una conexión nueva.
        self.s.listen(1)
        conn, addr = self.s.accept()
        print "Nueva conexión sound server: " + str(addr)
        thread.start_new_thread( self.run, () )
        data = conn.recv(self.BUFFER)
        # Recibimos el status de master del usuario.
        if data == "password":
            master = True
        else:
            master = False

        # Añadimos la conexión.
        self.connList.append([conn, master])
        data = conn.recv(self.BUFFER)
        # No finalizaremos la conexión hasta recibir GOODBYE del usuario.
        while data != "GOODBYE":
            # Cada ciclo recibimos datos y los parseamos.
            self.parseMessage(data, master, addr)
            data = conn.recv(self.BUFFER)
        # Eliminamos la conexión de la lista y la cerramos.
        for c in self.connList:
            if c[0] == conn:
                temp = c
        self.connList.remove(temp)
        conn.close()
