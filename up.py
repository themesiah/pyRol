import socket

TCP_IP = "mesi.zapto.org"
TCP_PORT = 6901
BUFFER_SIZE = 1024
csize = 0

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
name = s.recv(BUFFER_SIZE)

f = open("new"+name, 'wb')

while 1:
    data = s.recv(1024)
    if "FINISHED" in data:
        break
    f.write(data)
f.close()
