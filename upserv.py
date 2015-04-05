# -*- coding: cp1252 -*-
import socket, os, thread, time

"""
Módulo para actualizar cosas.
Es un envío de archivos simple.
"""
class Updater(object):
    # Llamamos a las funciones básicas de inicialización y bucle del programa.
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

    # Inicializamos el motor de versión.
    # Esto consiste en comprobar la última versión y obtener la lista de archivos que se deben cambiar para cada versión.
    def initVersion(self):
        f = open("lastversion.txt", 'r')
        self.VERSION = f.read()
        f.close()

        f = open("updates.txt", 'r')
        updates = f.readlines()
        f.close()

        self.fileupdates = dict()
        last = 0

        # Añade para cada versión los archivos a cambiar.
        for up in updates:
            up = up.rstrip()
            if up[0] == "$":
                last = int(up[1:])
                self.fileupdates[last] = []
            else:
                self.fileupdates[last].append(up)
                
    # Inicializamos socket y versión.
    def init(self):
        self.initSocket()
        self.initVersion()
        
    # Obtenemos los archivos a cambiar dada la versión de un cliente y nuestra última versión.
    def getFiles(self, version):
        i = int(self.VERSION)
        version = int(version)
        toUpdate = []
        # Desde los archivos más nuevos a los más antiguos se elije cuales actualizar.
        # Nótese que no se repiten archivos, asi que si un archivo se actualiza en la versión 2 y la 3, solo se enviará el de la 3.
        while i != version:
            for u in self.fileupdates[i]:
                if not u in toUpdate:
                    toUpdate.append(u)
            i -= 1

        return toUpdate

    # Envío de archivo.
    def sendFile(self, fi, conn):
        f = open (fi, 'rb')
        data = f.read()
        f.close()

        # Se envía el nombre del archivo.
        conn.send(fi)
        time.sleep(0.5)
        # Se envía el archivo en sí.
        conn.send(data)
        time.sleep(0.5)
        # Se envía el indicador de que se ha enviado el archivo entero.
        conn.send("FINISHED")
        time.sleep(0.5)

    def update(self):
        # Aceptamos una nueva conexión.
        self.s.listen(1)
        conn, addr = self.s.accept()
        print "Sending update to: " + str(addr)
        # Creamos un thread nuevo para aceptar nuevas conexiones.
        thread.start_new_thread( self.update, () )
        # Recibimos la versión del cliente.
        version = conn.recv(self.BUFFER)
        # Obtenemos los archivos a enviar al cliente.
        files = self.getFiles(version)
        # Enviamos dichos archivos.
        for fi in files:
            self.sendFile(fi, conn)
        # Enviamos el indicador de que la actualización ha terminado.
        conn.send("UPDATED")
        print "Finished updating: " + str(addr)
        # Enviamos la nueva versión actual al cliente y cerramos.
        conn.send(self.VERSION)
        conn.close()
