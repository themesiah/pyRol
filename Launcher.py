# -*- coding: cp1252 -*-
import socket, os

TCP_IP = "localhost"
TCP_PORT = 6901
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


print "1- x86 bits"
print "2- x64 bits"
toOpen = int(raw_input("Elige tu versión: "))

if toOpen == 1:
    os.startfile("x86/rolClient.exe")
else:
    os.startfile("x64/rolClient.exe")
