# -*- coding: cp1252 -*-
import socket
import thread
import random
import time
from Message import Message
from upserv import Updater



def getHelpMessage(player, cmd):
    msg = Message()
    msg.player = "Help"
    msg.target = player
    msg.addMessage(cmd + "help: Muestra la ayuda.")
    msg.addMessage(cmd + "w <usuario> <mensaje>: Envía un mensaje privado.")
    msg.addMessage(cmd + "roll <macro>: Utiliza una macro.")
    msg.addMessage(cmd + "proll <macro>: Utiliza una macro invisible.")
    return msg

def checkNameOk(name, pl):
    incorrect = False
    for n in pl:
        if n[1] == name:
            incorrect = True
    if len(name) > 12:
        incorrect = True
    if name == "Server":
        incorrect = True
    regex = ",;.:-_*/\\ "
    for symbol in regex:
        if symbol in name:
            incorrect = True
    return not incorrect

def roll(dice):
    # Dice consiste en:
    # [0] Numero de dados
    # [1] Numero de caras (o especial)
    # [2] Bono

    rolled = 0
    diceActual = 99
    abiertas = 0
    if dice[1] == "anima":
        while diceActual >= 90 and abiertas < 2:
            diceActual = random.randrange(1, 100)
            rolled += diceActual
            abiertas += 1
        if abiertas == 0 and rolled <= 3:
            diceActual = random.randrange(1, 100)
            rolled -= diceActual
            pifia = diceActual
        rolled += int(dice[2])

    elif dice[1] == "fudge":
        for i in range(4):
            rolled += (random.randrange(3)-1)
        rolled += int(dice[2])

    else:
        for x in range(int(dice[0])):
            rolled += random.randrange(1, int(dice[1]))
            rolled += int(dice[2])

    return rolled


def connection(s, pl):
    s.listen(1)
    conn, addr = s.accept()
    print 'Connection address: '+ str(addr)
    name = None
    pl.append([conn, None, False])
    thread.start_new_thread( connection, (s, pl,) )
    while not name:
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
    while not finished:
        data = conn.recv(BUFFER)
        msg = Message()
        msg = msg.unserialize(data)
        if msg.type == 0:
            for c in pl:
                c[0].send(data)
                
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

        elif msg.type == 6:
            for p in pl:
                if p[1] == msg.target or p[2] == True:
                    p[0].send(msg.serialize())

        elif msg.type == 7:
            cmd = msg.getAll()[0]
            player = msg.player
            msg = getHelpMessage(player, cmd)
            for p in pl:
                if p[1] == msg.target:
                    p[0].send(msg.serialize())
                


thread.start_new_thread( Updater, ())
time.sleep(0.1)

IP = ""
PORT = 6899
BUFFER = 4098

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((IP, PORT))
print "Servidor de rol escuchando en el puerto " + str(PORT)

playersList = []
connection(s, playersList, )
while 1:
    pass
conn.close()

