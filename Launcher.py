# -*- coding: cp1252 -*-
import socket, os


# Obtenemos la información del host.
f = open("updata.ini", 'r')
for line in f:
    parts = line.split("=")
    if parts[0] == "IP":
        TCP_IP = parts[1].rstrip()
    if parts[0] == "PORT":
        TCP_PORT = int(parts[1].rstrip())
f.close()

BUFFER_SIZE = 4098

# Inicializamos socket.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

# Leemos la versión en la que estamos.
f = open("version.txt", 'r')
version = f.read()
f.close()
# Enviamos al servidor nuestra versión actual.
s.send(version)


# Iniciamos el proceso de actualización.
while 1:
    # Nombre del archivo.
    name = s.recv(BUFFER_SIZE)
    
    if "UPDATED" in name:
        break
    
    f = open(name, 'wb')
    # Recibimos el archivo completo.
    while 1:
        data = s.recv(BUFFER_SIZE)
        
        if "FINISHED" in data or "UPDATED" in data:
            break
        
        f.write(data)
    f.close()
    
    if "UPDATED" in data:
        break

# Recibimos y cambiamos la versión nueva.
version = s.recv(BUFFER_SIZE)
f = open("version.txt", 'w')
f.write(version)
f.close()
s.close()

# Iniciamos el programa en cuestión.
os.startfile("rol\\rolClient.exe")
