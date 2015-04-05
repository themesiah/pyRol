# -*- coding: cp1252 -*-
from Tkinter import Tk, BOTH, Frame, Label, Text, E, W, S, N, DISABLED, END, INSERT
from Tkinter import NORMAL, Scrollbar, RIGHT, Y, Checkbutton, IntVar, FALSE
from Tkinter import Listbox, SINGLE, Scale
from ttk import Button, Style
from select import select
import ScrolledText
import socket, time
import thread
from Message import Message

import os, wave, pyaudio, sys
import pymedia.audio.acodec as acodec
import pymedia.audio.sound as sound
import pymedia.muxer as muxer

"""
La clase de la ventana que contiene todo el programa.
"""
class MainWindow(Frame):

    """
    Inicializamos todo y llamamos a varias funciones para
    iniciar el programa.
    """
    def __init__(self, parent):
        Frame.__init__(self, parent, background="lightgray")

        parent.protocol('WM_DELETE_WINDOW', self.onClose)  # root is your root window
         
        self.parent = parent
        # Leemos los datos del "data.ini"
        self.loadFromIni()
        # Leemos las macros de "macros.txt"
        self.loadMacros()
        self.BUFFER = 4098
        self.open = True
        self.VOLUME = 1.0
        self.PLAYING = False
        # Inicializamos sockets de rolServer y remoteSound.
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.IP, self.PORT))
        self.ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ss.connect((self.IP, self.SPORT))
        # Enviamos nuestro nombre a rolServer y nuestro status de master.
        msg = Message()
        msg.player = self.player
        msg.master = self.MASTER
        msg.addMessage(self.COMMANDCHAR)
        self.s.send(msg.serialize())
        # Enviamos nuestro status de master al remoteSound.
        if self.MASTER != None:
            self.ss.send(self.MASTER)
        else:
            self.ss.send("NOPE")
        # La tecla Intro realizará self.send.
        parent.bind('<Return>', self.send)
        # Inicializamos la Interfaz de Usuario.
        self.initUI()
        self.centerWindow()
        # Iniciamos los procesos principales de recibida de mensajes.
        thread.start_new_thread(self.socketManager, ())
        thread.start_new_thread(self.ssocketManager, ())

    def updateVolume(self, evt):
        # Función que se llama al cambiar el volumen.
        # Cambia el volumen a un valor entre 0 y 1 (float).
        self.VOLUME = float(float(self.volume.get()) / float(100))

    # Función para reproducir sonidos.
    # No es la mejor que existe, pero funciona...
    def playSound (self, fn):
        try:
            fn = "audio/"+fn
            dm = muxer.Demuxer(str.split(fn, '.')[-1].lower())
            f = open(fn, 'rb')
            snd = dec = None
            s = f.read( 32000 )
            while len(s) and self.PLAYING:
                frames = dm.parse(s)
                if frames:
                    for fr in frames:
                        if dec == None:
                            dec = acodec.Decoder(dm.streams[fr[0]])

                        r = dec.decode(fr[1])
                        if r and r.data:
                            if snd == None:
                                snd = sound.Output(
                                    int(r.sample_rate),
                                    r.channels,
                                    sound.AFMT_S16_LE)
                            snd.setVolume(int(self.VOLUME * 65535))
                            data = r.data
                            snd.play(data)
                s = f.read(512)

            while snd.isPlaying():
                time.sleep(.05)
            self.PLAYING = False
        except Exception as err:
            print err

    # Igual que playSound.
    def playChatSound (self):
        try:
            fn = "audio/message.mp3"
            dm = muxer.Demuxer(str.split(fn, '.')[-1].lower())
            f = open(fn, 'rb')
            snd = dec = None
            s = f.read( 32000 )
            while len(s):
                frames = dm.parse(s)
                if frames:
                    for fr in frames:
                        if dec == None:
                            dec = acodec.Decoder(dm.streams[fr[0]])

                        r = dec.decode(fr[1])
                        if r and r.data:
                            if snd == None:
                                snd = sound.Output(
                                    int(r.sample_rate),
                                    r.channels,
                                    sound.AFMT_S16_LE)
                            #snd.setVolume(int(self.VOLUME * 65535))
                            data = r.data
                            snd.play(data)
                s = f.read(512)

            while snd.isPlaying():
                time.sleep(.05)
        except Exception as err:
            print err

    # Función que se llama al clickar en el botón Play.
    # Simplemente hace un playSound del archivo escrito en el area de texto.
    def playMusic(self):
        self.PLAYING = True
        txt = self.songArea.get("1.0", END)
        #self.songArea.delete("1.0", END)
        txt = str(txt.rstrip())
        if txt != "":
            thread.start_new_thread(self.playSound, (txt,))

    # Desactiva el flag de que la música se esté reproduciendo, así que la para.
    def stopMusic(self):
        self.PLAYING = False

    # Envía el mensaje para propagar el envío de una canción.
    def sendFileSound(self, fi):
        self.ss.send("SEND " + fi)

    # Envía el mensaje para propagar la reproducción de una canción.
    def sendPlaySound(self, fi):
        self.ss.send("PLAY " + fi)

    # Función que se ejecuta al cerrar el programa.
    # Cierra conexiones y avisa a los servidores de que se va.
    def onClose(self):
        msg = Message()
        msg.player = self.player
        msg.type = 2
        self.s.send(msg.serialize())
        self.s.close()
        self.ss.send("GOODBYE")
        self.ss.close()
        self.stopMusic()
        self.open = False
        self.parent.destroy()
        
    # Set de funciones para introducir manualmente los datos del programa.
    def obtainPlayer(self):
        self.player = raw_input("Introduce nombre de usuario: ")

    def obtainIP(self):
        self.IP = raw_input("Introduce la dirección IP del servidor: ")

    def obtainPort(self):
        self.PORT = int(raw_input("Introduce el puerto del servidor: "))

    def obtainSPort(self):
        self.SPORT = int(raw_input("Introduce el puerto del servidor de sonido: "))

    # Función que lee de "data.ini" todos los datos necesarios.
    # IP: IP
    # Puerto de rolServer: PORT
    # Puerto de remoteSound: SPORT
    # Contraseña de master: MASTER
    # Nombre del player: NAME
    # Carácter para comandos: COMMANDCHAR
    
    def loadFromIni(self):
        self.player = None
        self.IP = None
        self.PORT = None
        self.SPORT = None
        self.MASTER = "Nope"
        self.COMMANDCHAR = "@"
        
        f = open("data.ini", 'r')
        for line in f:
            parts = line.split("=")
            if parts[0] == "IP":
                self.IP = parts[1].rstrip()
            if parts[0] == "PORT":
                self.PORT = int(parts[1].rstrip())
            if parts[0] == "NAME":
                self.player = parts[1].rstrip()
            if parts[0] == "MASTER":
                self.MASTER = parts[1].rstrip()
            if parts[0] == "COMMANDCHAR":
                self.COMMANDCHAR = parts[1].rstrip()
            if parts[0] == "SPORT":
                self.SPORT = int(parts[1].rstrip())
        f.close()
        if self.player == None:
            self.obtainPlayer()
        if self.IP == None:
            self.obtainIP()
        if self.PORT == None:
            self.obtainPort()
        if self.SPORT == None:
            self.obtainSPort()

    # Función que lee las macros de "macros.txt"
    def loadMacros(self):
        f = open("macros.txt", 'r')
        m = f.readlines()
        f.close()
        
        self.macros = dict()

        for macro in m:
            if not macro[0] == "#":
                macro = macro.rstrip()
                pieces = macro.split(" ")
                self.macros[pieces[0]] = [pieces[1], pieces[2], pieces[3]]

    # Función que parsea mensajes del remoteSound.
    def parseSMessage(self, data):
        # En caso de recibir un mensaje de reproducción, reproduce.
        if data.split(" ")[0] == "PLAY":
            self.PLAYING = True
            self.songArea.delete("1.0", END)
            self.songArea.insert(INSERT, str(data[5:]))
            thread.start_new_thread(self.playSound, ((str(data[5:]),)))
        # En caso de recibir un mensaje de envío, recibe el audio.
        elif data.split(" ")[0] == "NAME":
            try:
                name = data[5:]

                data = self.ss.recv(self.BUFFER)
                    
                f = open("audio/" + name, 'wb')
                while 1:
                    data = self.ss.recv(self.BUFFER)
                        
                    if "SOUNDFINISHED" in data:
                        break
                        
                    f.write(data)
                f.close()
                self.ss.send("RECEIVED " + name)
            except Exception as err:
                print err

    # Función que gestiona los datos recibidos de remoteSound.
    # Funciona en un thread a parte.
    def ssocketManager(self):
        while(self.open):
            # Comprueba si hay mensajes, los recibe y los parsea.
            if select([self.ss], [self.ss], [self.ss])[0] and self.open:
                data = self.ss.recv(self.BUFFER)
                self.parseSMessage(data)

    # Función que gestiona los datos recibidos de rolServer.
    # Funciona en un thread a parte.
    def socketManager(self):
        while(self.open):
            #time.sleep(0.3)
            # Comprueba si hay mensajes, los recibe y los parsea.
            if select([self.s], [self.s], [self.s])[0] and self.open:
                data = self.s.recv(self.BUFFER)
                recvMsg = Message()
                recvMsg = recvMsg.unserialize(data)
                # Casos de mensaje y whisp.
                if recvMsg.type == 0 or recvMsg.type == 6:
                    self.showMessage(recvMsg.player, recvMsg.getAll())
                # Caso de recibir lista de players.
                elif recvMsg.type == 1:
                    self.setPlayers(recvMsg)
                # Caso de conexión negada (nombre inválido, por ejemplo).
                elif recvMsg.type == 5:
                    self.onClose()

    # Función para situar la ventana en el centro.
    def centerWindow(self):
      
        w = 820
        h = 480

        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        
        x = (sw - w)/2
        y = (sh - h)/2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

    # Función que inicializa cada objeto de la UI.
    def initUI(self):
      
        self.parent.title("pyRol")
        self.pack(fill=BOTH, expand=1)
        self.style = Style()
        self.style.theme_use("alt")

        self.pack(fill=BOTH, expand=1)

        
        # Boton de enviar del chat
        self.sendButton = Button(self, text="Enviar", command = self.sendB)
        self.sendButton.place(x=550, y=450)

        # Area para escribir del chat
        self.sendArea = Text(self, height=1, width=65)
        self.sendArea.place(x=5, y=450)

        # Area donde salen los mensajes del chat
        self.recvArea = ScrolledText.ScrolledText(self, height=27, width=65)
        self.recvArea.place(x=5, y=5)
        self.recvArea.config(state=DISABLED)

        # Area donde salen los nombres de los players
        self.playersArea = Listbox(self, height= 27, width=12, selectmode=SINGLE)
        self.playersArea.place(x=550, y=5)
        self.playersArea.bind("<Double-Button-1>", self.onDouble)

        # Texto para el Area para poner el bono con el que tiras
        self.bonuslabel = Label(self, text="Bonus")
        self.bonuslabel.place(x=655, y=5)

        # Area para poner el bono con el que tiras
        self.bonusArea = Text(self, height=1, width=4)
        self.bonusArea.place(x=655, y=30)

        # Texto para el Checkbox solo para master
        self.invisiblelabel = Label(self, text="Solo para el Master")
        self.invisiblelabel.place(x=700, y=5)

        # Checkbox solo para master
        self.onlymaster = IntVar()
        self.invisible = Checkbutton(self, variable=self.onlymaster,
                                     onvalue = 1, offvalue = 0)
        self.invisible.place(x=700, y=30)

        # Botón para tirar dado
        self.rollButton = Button(self, text="Tirar dado", command = self.roll)
        self.rollButton.place(x=655, y=55)

        # Scroll de volumen
        self.volume = Scale(self, from_=0, to=100, command = self.updateVolume)
        self.volume.place(x=655, y=85)
        self.volume.set(100)

        # Texto para el scroll de volumen
        self.volumelabel = Label(self, text="Volumen")
        self.volumelabel.place(x=715, y=130)

        # Botón para reproducir música
        self.playButton = Button(self, text="Play", command = self.playMusic)
        self.playButton.place(x=655, y=200)

        # Botón para parar música
        self.stopButton = Button(self, text="Stop", command = self.stopMusic)
        self.stopButton.place(x=655, y=255)

        # Area de texto para la canción a reproducir
        self.songArea = Text(self, height = 1, width = 20)
        self.songArea.place(x=655, y=230)

        # Checkbox de la alerta de mensaje
        self.alert = IntVar()
        self.alertCheck = Checkbutton(self, variable=self.alert,
                                     onvalue = 1, offvalue = 0)
        self.alertCheck.place(x=655, y=450)
        self.alert.set(1)

        # Texto para el checkbox de la alerta de mensaje
        self.alertlabel = Label(self, text="Sonido de alerta")
        self.alertlabel.place(x=690, y=452)
        
    # Función que se llama al hacer doble click en el nombre de un player.
    # Sirve para añadir el texto del whisp rápidamente.
    def onDouble(self, event):
        selection = self.playersArea.curselection()
        value = self.playersArea.get(selection[0])
        #self.sendArea.delete("1.0", END)
        whisp = self.COMMANDCHAR + "w " + value + " "
        self.sendArea.insert("1.0", whisp)

    # Función para realizar las tiradas básicas.
    def roll(self):
        # Obtiene el bono...
        bonus = self.bonusArea.get("1.0", END)
        self.bonusArea.delete("1.0", END)
        bonus = bonus.rstrip()
        if bonus.isdigit() or bonus == "":
            if bonus == "":
                bonus = 0
            # Crea el mensaje y añade los datos...
            msg = Message()
            msg.player = self.player
            if self.onlymaster.get() == 1:
                msg.type = 4
            else:
                msg.type = 3
            msg.roll = ["1", "anima", bonus]
            # Envía el mensaje a rolServer.
            self.s.send(msg.serialize())

    # Función que parsea el mensaje que vas a enviar.
    # Es la función que detecta si realizas un comando o no, y cuál.
    def parseMessage(self, txt):
        txt = txt.rstrip()
        msg = Message()
        msg.player = self.player
        # En caso de que sea un comando...
        if txt[0] == self.COMMANDCHAR:
            # Comando Help.
            # Devolverá información sobre comandos.
            if txt.split(" ")[0][1:] == "help":
                msg.addMessage(self.COMMANDCHAR)
                msg.type = 7
            # Comando Whisp.
            # Enviará mensaje privado a un usuario.
            elif len(txt.split(" ")) > 1 and (txt.split(" ")[0][1:] == "w" or txt.split(" ")[0][1:] == "W"):
                pieces = txt.split(" ", 2)
                msg.target = pieces[1]
                msg.player = self.player
                msg.addMessage("("+msg.target+") " + pieces[2])
                msg.type = 6
            # Comando roll.
            # Realizará una tirada de una macro.
            elif len(txt.split(" ")) > 1 and txt.split(" ")[0][1:] == "roll":
                if txt.split(" ")[1] in self.macros:
                    roll = self.macros[txt.split(" ")[1]]
                    msg = Message()
                    msg.type = 3
                    msg.roll = roll
                    msg.player = self.player
                else:
                    msg = None
            # Comando proll.
            # Realizará una tirada oculta de una macro.
            elif len(txt.split(" ")) > 1 and txt.split(" ")[0][1:] == "proll":
                if txt.split(" ")[1] in self.macros:
                    roll = self.macros[txt.split(" ")[1]]
                    msg = Message()
                    msg.type = 4
                    msg.roll = roll
                    msg.player = self.player
                else:
                    msg = None
            # Comando send (para master).
            # Inicia la propagación para el envío de audio.
            elif len(txt.split(" ")) > 1 and txt.split(" ")[0][1:] == "send":
                self.sendFileSound(txt.split(" ")[1])
            # Comando play (para master).
            # Inicia la propagación para la reproducción de audio.
            elif len(txt.split(" ")) > 1 and txt.split(" ")[0][1:] == "play":
                self.sendPlaySound(txt.split(" ")[1])
            else:
                msg = None
        else:
            # Si no era un comando, enviaremos texto y ya está.
            msg.player = self.player
            msg.addMessage(txt)
        return msg

    # Al pulsar enter.
    def send(self, event):
        self.sendB()

    # Al pulsar enter o el botón de enviar.
    def sendB(self):
        # Obtenemos el texto y actuamos en consecuencia.
        txt = self.sendArea.get("1.0", END)
        self.sendArea.delete("1.0", END)
        if txt.rstrip() != "":
            msg = self.parseMessage(txt[0:64])
        else:
            msg = None
        if msg != None and txt != "":
            if msg.target != None:
                lastwhisp = self.COMMANDCHAR + "w " + msg.target + " "
                self.sendArea.insert(INSERT, lastwhisp)
            self.s.send(msg.serialize())

    # Mostramos por pantalla un mensaje recibido (o varios).
    def showMessage(self, player, msg):
        self.recvArea.config(state=NORMAL)
        for message in msg:
            self.recvArea.insert(END, player + ": " + message + "\n")
        self.recvArea.config(state=DISABLED)
        self.recvArea.yview(END)
        if self.alert.get() == 1:
            thread.start_new_thread(self.playChatSound, ())

    # Añadimos un jugador a la lista de jugadores.
    def addPlayer(self, player):
        self.playersArea.insert(END, player)

    # Quitamos a los jugadores de la lista de jugadores y los añadimos de nuevo.
    def setPlayers(self, msg):
        self.playersArea.delete("0", END)
        players = msg.getAll()
        for p in players:
            self.addPlayer(p)

# Iniciamos el módulo TKinter.
root = Tk()
# Que la ventana no pueda cambiar de tamaño.
root.resizable(width=FALSE, height=FALSE)
# Elegimos icono.
root.iconbitmap(r'Launcher.ico')
# Iniciamos la aplicación.
app = MainWindow(root)
root.mainloop()
