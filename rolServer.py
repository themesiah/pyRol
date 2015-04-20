# -*- coding: cp1252 -*-
import socket
import thread
import random
import time
from Message import Message
from upserv import Updater
from soundServer import RemoteSound


# Creación del mensaje para el el comando HELP.
def getHelpMessage(player, cmd):
    msg = Message()
    msg.player = "Help"
    msg.target = player
    msg.addMessage(cmd + "help: Muestra la ayuda.")
    msg.addMessage(cmd + "w <usuario> <mensaje>: Envía un mensaje privado.")
    msg.addMessage(cmd + "roll <macro>: Utiliza una macro.")
    msg.addMessage(cmd + "proll <macro>: Utiliza una macro invisible.")
    return msg

# Comprobación de que el nombre sea correcto.
def checkNameOk(name, pl):
    incorrect = False
    # Comprobamos que no esté repetido.
    for n in pl:
        if n[1] == name:
            incorrect = True
    # Que el nombre tenga menos de 12 caracteres.
    if len(name) > 12:
        incorrect = True
    # Que no se llame Server.
    if name == "Server":
        incorrect = True
    # Que no contenga los siguientes símbolos.
    regex = ",;.:-_*/\\ "
    for symbol in regex:
        if symbol in name:
            incorrect = True
    return not incorrect

# Función que devuelve el resultado de una tirada.
def roll(dice):
    # Dice consiste en:
    # [0] Numero de dados
    # [1] Numero de caras (o especial)
    # [2] Bono

    rolled = 0
    diceActual = 99
    abiertas = 0
    # En caso de tirada tipo anima.
    if dice[1] == "anima":
        while diceActual >= 90 and abiertas < 2:
            diceActual = random.randrange(1, 100)
            rolled += diceActual
            abiertas += 1
        if abiertas == 1 and rolled <= 3:
            diceActual = random.randrange(1, 100)
            rolled -= diceActual
            pifia = diceActual
        rolled += int(dice[2])

    # En caso de tiradas de FATE.
    elif dice[1] == "fudge":
        for i in range(4):
            rolled += (random.randrange(3)-1)
        rolled += int(dice[2])

    # En cualquier otro caso.
    else:
        for x in range(int(dice[0])):
            rolled += random.randrange(1, int(dice[1]))
            rolled += int(dice[2])

    return rolled


# Función principal que se replicará por threads.
# Gestiona las conexiones con los players.
def connection(s, pl):
    # Iniciamos una conexión.
    s.listen(1)
    conn, addr = s.accept()
    print 'Server rol nueva conexión: '+ str(addr)
    name = None
    # Añadimos la conexión a nuestra lista.
    pl.append([conn, None, False])
    # Iniciamos un nuevo thread para aceptar otra conexión.
    thread.start_new_thread( connection, (s, pl,) )
    while not name:
        # Recibimos los primeros datos de un jugador (nombre, charcommand, status de master)
        data = conn.recv(BUFFER)
        msg = Message()
        msg = msg.unserialize(data)
        name = msg.player
        cmd = msg.getAll()[0]
        if msg.master == "password":
            masterStatus = True
            print "Logged a Master with name: " + name
        else:
            masterStatus = False
        # Comprobamos si el nombre es válido.
        # Si no lo es, negamos la conexión.
        if not checkNameOk(name, pl):
            msg = Message()
            msg.type = 5
            conn.send(msg.serialize())
            conn.close()
            finished = True
            for x in pl:
                if x[0] == conn:
                    temp = x
            pl.remove(temp)
        # Si el nombre es válido, informamos a todos los jugadores.
        # Además, enviamos a la nueva conexión información sobre los comandos.
        else:
            print 'With name: ', name
            for p in pl:
                if p[0] == conn:
                    p[1] = name
                    p[2] = masterStatus
            msg = Message()
            msg.type = 1
            for n in pl:
                msg.addMessage(n[1])
            for c in pl:
                c[0].send(msg.serialize())
            time.sleep(0.5)
            msg = getHelpMessage(name, cmd)
            msg.addMessage("Bienvenido a pyRol!")
            conn.send(msg.serialize())
            finished = False
    # Bucle principal.
    # Se reciben datos, se deserializan y se actua dependiendo del tipo de mensaje.
    while not finished:
        data = conn.recv(BUFFER)
        msg = Message()
        msg = msg.unserialize(data)
        # En caso de mensaje de chat, solo se replica.
        if msg.type == 0:
            for c in pl:
                c[0].send(data)
        # En caso de mensaje de finalización, terminamos la conexión con ese usuario.
        elif msg.type == 2:
            for p in pl:
                if p[1] == msg.player:
                    temp = p
            temp[0].close()
            pl.remove(temp)
            for p in pl:
                if p[0] == conn:
                    p[1] = name
            msg = Message()
            msg.type = 1
            for n in pl:
                msg.addMessage(n[1])
            for c in pl:
                c[0].send(msg.serialize())
            finished = True
        # En caso de tirada de dado, realizamos la tirada y replicamos a todos el resultado.
        elif msg.type == 3:
            dice = msg.roll
            rolled = roll(dice)
            finalText = msg.player + "(" + str(dice[2]) + ") ha sacado un "
            finalText += str(rolled)
            msg = Message()
            msg.player = "Server"
            msg.addMessage(finalText)
            for c in pl:
                c[0].send(msg.serialize())
        # En caso de tirada de dado privada, realizamos la tirada y replicamos a los masters el resultado.      
        elif msg.type == 4:
            dice = msg.roll
            rolled = roll(dice)
            finalText = "(oculto) " + msg.player + "(" + str(dice[2]) + ") ha sacado un "
            finalText += str(rolled)
            msg = Message()
            msg.player = "Server"
            msg.addMessage(finalText)
            for c in pl:
                if c[2]:
                    c[0].send(msg.serialize())
        # En caso de whisp, replicamos el mensaje al que lo envía, al destinatario y a los masters.
        elif msg.type == 6:
            for p in pl:
                if p[1] == msg.target or p[2] == True or p[1] == msg.player:
                    p[0].send(msg.serialize())
        # En caso de pedir mensaje de ayuda, devuelve el mensaje de ayuda solo a ese jugador.
        elif msg.type == 7:
            cmd = msg.getAll()[0]
            player = msg.player
            msg = getHelpMessage(player, cmd)
            for p in pl:
                if p[1] == msg.target:
                    p[0].send(msg.serialize())
                

# Iniciamos el módulo del actualizador.
thread.start_new_thread( Updater, ())

time.sleep(0.1)

# Iniciamos el módulo de RemoteSound.
thread.start_new_thread( RemoteSound, ())

time.sleep(0.1)

# Inicializamos los valores del servidor.
IP = ""
PORT = 6901
BUFFER = 4098

# Iniciamos el socket principal.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((IP, PORT))
print "Servidor de rol escuchando en el puerto " + str(PORT)

# Iniciamos el bucle del programa.
playersList = []
connection(s, playersList, )
while 1:
    pass
conn.close()

