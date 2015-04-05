# -*- coding: cp1252 -*-
import socket, os, thread, time

"""
M�dulo para actualizar cosas.
Es un env�o de archivos simple.
"""
class Updater(object):
    # Llamamos a las funciones b�sicas de inicializaci�n y bucle del programa.
    def __init__(self):
        self.init()
        self.update()

    # Inicializamos el socket con los datos elegidos.
    def initSocket(self):
        self.IP = ""
        self.PORT = 6903
        self.BUFFER = 4098
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.IP, self.PORT))
        print "Listening on port " + str(self.PORT)

    # Inicializamos el motor de versi�n.
    # Esto consiste en comprobar la �ltima versi�n y obtener la lista de archivos que se deben cambiar para cada versi�n.
    def initVersion(self):
        f = open("lastversion.txt", 'r')
        self.VERSION = f.read()
        f.close()

        f = open("updates.txt", 'r')
        updates = f.readlines()
        f.close()

        self.fileupdates = dict()
        last = 0

        # A�ade para cada versi�n los archivos a cambiar.
        for up in updates:
            up = up.rstrip()
            if up[0] == "$":
                last = int(up[1:])
                self.fileupdates[last] = []
            else:
                self.fileupdates[last].append(up)
                
    # Inicializamos socket y versi�n.
    def init(self):
        self.initSocket()
        self.initVersion()
        
    # Obtenemos los archivos a cambiar dada la versi�n de un cliente y nuestra �ltima versi�n.
    def getFiles(self, version):
        i = int(self.VERSION)
        version = int(version)
        toUpdate = []
        # Desde los archivos m�s nuevos a los m�s antiguos se elije cuales actualizar.
        # N�tese que no se repiten archivos, asi que si un archivo se actualiza en la versi�n 2 y la 3, solo se enviar� el de la 3.
        while i != version:
            for u in self.fileupdates[i]:
                if not u in toUpdate:
                    toUpdate.append(u)
            i -= 1

        return toUpdate

    # Env�o de archivo.
    def sendFile(self, fi, conn):
        f = open (fi, 'rb')
        data = f.read()
        f.close()

        # Se env�a el nombre del archivo.
        conn.send(fi)
        time.sleep(0.5)
        # Se env�a el archivo en s�.
        conn.send(data)
        time.sleep(0.5)
        # Se env�a el indicador de que se ha enviado el archivo entero.
        conn.send("FINISHED")
        time.sleep(0.5)

    def update(self):
        # Aceptamos una nueva conexi�n.
        self.s.listen(1)
        conn, addr = self.s.accept()
        print "Sending update to: " + str(addr)
        # Creamos un thread nuevo para aceptar nuevas conexiones.
        thread.start_new_thread( self.update, () )
        # Recibimos la versi�n del cliente.
        version = conn.recv(self.BUFFER)
        # Obtenemos los archivos a enviar al cliente.
        files = self.getFiles(version)
        # Enviamos dichos archivos.
        for fi in files:
            self.sendFile(fi, conn)
        # Enviamos el indicador de que la actualizaci�n ha terminado.
        conn.send("UPDATED")
        print "Finished updating: " + str(addr)
        # Enviamos la nueva versi�n actual al cliente y cerramos.
        conn.send(self.VERSION)
        conn.close()
