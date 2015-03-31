# -*- coding: cp1252 -*-
import socket, os


f = open("data.ini", 'r')
for line in f:
    parts = line.split("=")
    if parts[0] == "IP":
        TCP_IP = parts[1].rstrip()
    if parts[0] == "PORT":
        TCP_PORT = int(parts[1].rstrip())
f.close()

BUFFER_SIZE = 4098

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

f = open("version.txt", 'r')
version = f.read()
f.close()

s.send(version)


while 1:
    name = s.recv(BUFFER_SIZE)
    
    if "UPDATED" in name:
        break
    
    f = open(name, 'wb')
    while 1:
        data = s.recv(BUFFER_SIZE)
        
        if "FINISHED" in data or "UPDATED" in data:
            break
        
        f.write(data)
    f.close()
    
    if "UPDATED" in data:
        break

version = s.recv(BUFFER_SIZE)
f = open("version.txt", 'w')
f.write(version)
f.close()
s.close()

os.startfile("rol/rolClient.exe")
