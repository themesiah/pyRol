import socket, os, time, thread, sys

def connection(s, c):
    s.listen(1)
    conn, addr = s.accept()
    c.append((conn, addr))
    #print 'Connection address: ', addr
    thread.start_new_thread( connection, (s, c,) )

def sendTo(conn, data):
    conn.send(data)


    
TCP_IP = ''
TCP_PORT = 6900
BUFFER_SIZE = 1024
BYTES_TOTAL = 0

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))

c = []

connection(s, c,)

comm = ""
while comm != "FINISH":

    comm = str(raw_input("Introduce el nombre del archivo o FINISH para acabar: "))

    if comm == "FINISH":
        for conn in c:
            conn[0].send("FINISH")
    elif comm == "INFO":
        for conn in c:
            print conn[1]
    else:
        try:
            name = comm[5:]
            if (comm[0:4] == "SEND"):
                for conn in c:
                    thread.start_new_thread( sendTo, (conn[0], "SEND",) )
                time.sleep(1)
                f = open ("data/"+name, 'rb')

                #size = str(os.path.getsize("data/"+name))
                #print size

                
                for conn in c:
                    thread.start_new_thread( sendTo, (conn[0], name,) )

                data = f.read()

                for conn in c:
                    thread.start_new_thread( sendTo, (conn[0], data,) )
                    
                time.sleep(1)

                for conn in c:
                    thread.start_new_thread( sendTo, (conn[0], "FINISHED",) )
                    conn[0].recv(1024)
                    
                print "Recibido por los clientes."

                f.close()
            elif (comm[0:4] == "PLAY"):
                for conn in c:
                    conn[0].send("PLAY")
                    conn[0].send(name)

            elif (comm[0:4] == "VOLU"):
                for conn in c:
                    conn[0].send("VOLU")
                    conn[0].send(name)
                
        except Exception as err:
            print sys.exc_info()[0]
            print err
for conn in c:
    conn[0].close()
