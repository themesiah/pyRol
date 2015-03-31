import socket, os


#name = str(raw_input("Introduce el nombre del archivo: "))
name = "BOE.swf"
f = open (name, 'rb')

size = str(os.path.getsize(name))
print size

TCP_IP = ''
TCP_PORT = 6901
BUFFER_SIZE = 1024
BYTES_TOTAL = 0

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
conn, addr = s.accept()
print 'Connection address: ', addr

conn.send(name)

data = f.read()

conn.send(data)
conn.send("FINISHED")

f.close()
conn.close()
