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
class MainWindow(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent, background="lightgray")

        parent.protocol('WM_DELETE_WINDOW', self.onClose)  # root is your root window
         
        self.parent = parent
        self.loadFromIni()
        self.loadMacros()
        self.BUFFER = 4098
        self.open = True
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.IP, self.PORT))
        msg = Message()
        msg.player = self.player
        msg.master = self.MASTER
        msg.addMessage(self.COMMANDCHAR)
        self.s.send(msg.serialize())
        parent.bind('<Return>', self.send)
        self.initUI()
        self.centerWindow()
        thread.start_new_thread(self.socketManager, ())

    def playSound (self):
        CHUNK = 1024
        wf = wave.open("Pomposity.mp3", 'rb')
        p = pyaudio.PyAudio()

        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        data = wf.readframes(CHUNK)

        while data != '':
            stream.write(data)
            data = wf.readframes(CHUNK)

        stream.stop_stream()
        stream.close()

        p.terminate()

    def playMusic(self):
        self.playSound("Pomposity.mp3")


    def onClose(self):
        msg = Message()
        msg.player = self.player
        msg.type = 2
        self.s.send(msg.serialize())
        self.s.close()
        self.open = False
        self.parent.destroy()
        

    def obtainPlayer(self):
        self.player = raw_input("Introduce nombre de usuario: ")

    def obtainIP(self):
        self.IP = raw_input("Introduce la dirección IP del servidor: ")

    def obtainPort(self):
        self.PORT = int(raw_input("Introduce el puerto del servidor: "))
        
    def loadFromIni(self):
        self.player = None
        self.IP = None
        self.PORT = None
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
        f.close()
        if self.player == None:
            self.obtainPlayer()
        if self.IP == None:
            self.obtainIP()
        if self.PORT == None:
            self.obtainPort()
        
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

    def socketManager(self):
        while(self.open):
            #time.sleep(0.3)
            if select([self.s], [self.s], [self.s])[0] and self.open:
                data = self.s.recv(self.BUFFER)
                recvMsg = Message()
                recvMsg = recvMsg.unserialize(data)
                if recvMsg.type == 0 or recvMsg.type == 6:
                    self.showMessage(recvMsg.player, recvMsg.getAll())
                elif recvMsg.type == 1:
                    self.setPlayers(recvMsg)
                elif recvMsg.type == 5:
                    self.onClose()

    def centerWindow(self):
      
        w = 820
        h = 480

        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        
        x = (sw - w)/2
        y = (sh - h)/2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

    
    def initUI(self):
      
        self.parent.title("Rol")
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
        self.volume = Scale(self, from_=0, to=100)
        self.volume.place(x=655, y=85)
        self.volume.set(100)

        # Texto para el scroll de volumen
        self.bonuslabel = Label(self, text="Volumen")
        self.bonuslabel.place(x=715, y=130)

        # Botón para reproducir música
        self.playButton = Button(self, text="Play", command = self.playMusic)
        self.playButton.place(x=655, y=200)
        

    def onDouble(self, event):
        selection = self.playersArea.curselection()
        value = self.playersArea.get(selection[0])
        self.sendArea.delete("1.0", END)
        whisp = self.COMMANDCHAR + "w " + value + " "
        self.sendArea.insert(INSERT, whisp)

    def roll(self):
        bonus = self.bonusArea.get("1.0", END)
        self.bonusArea.delete("1.0", END)
        bonus = bonus.rstrip()
        if bonus.isdigit() or bonus == "":
            if bonus == "":
                bonus = 0
            msg = Message()
            msg.player = self.player
            if self.onlymaster.get() == 1:
                msg.type = 4
            else:
                msg.type = 3
            msg.roll = ["1", "anima", bonus]
            self.s.send(msg.serialize())

    def parseMessage(self, txt):
        txt = txt.rstrip()
        msg = Message()
        msg.player = self.player
        if txt[0] == self.COMMANDCHAR:
            if txt.split(" ")[0][1:] == "help":
                msg.addMessage(self.COMMANDCHAR)
                msg.type = 7
            elif len(txt.split(" ")) > 1 and (txt.split(" ")[0][1:] == "w" or txt.split(" ")[0][1:] == "W"):
                pieces = txt.split(" ", 2)
                msg.target = pieces[1]
                msg.addMessage("("+msg.target+") " + pieces[2])
                msg.type = 6
            elif len(txt.split(" ")) > 1 and txt.split(" ")[0][1:] == "roll":
                if txt.split(" ")[1] in self.macros:
                    roll = self.macros[txt.split(" ")[1]]
                    msg = Message()
                    msg.type = 3
                    msg.roll = roll
                else:
                    msg = None
            elif len(txt.split(" ")) > 1 and txt.split(" ")[0][1:] == "proll":
                if txt.split(" ")[1] in self.macros:
                    roll = self.macros[txt.split(" ")[1]]
                    msg = Message()
                    msg.type = 4
                    msg.roll = roll
                else:
                    msg = None
            else:
                msg = None
        else:
            msg.addMessage(txt)
        return msg

    def send(self, event):
        self.sendB()
            
    def sendB(self):
        txt = self.sendArea.get("1.0", END)
        self.sendArea.delete("1.0", END)
        msg = self.parseMessage(txt[0:64])
        if msg != None and txt != "":
            if msg.target != None:
                lastwhisp = self.COMMANDCHAR + "w " + msg.target + " "
                self.sendArea.insert(INSERT, lastwhisp)
            self.s.send(msg.serialize())

    def showMessage(self, player, msg):
        self.recvArea.config(state=NORMAL)
        for message in msg:
            self.recvArea.insert(INSERT, player + ": " + message + "\n")
        self.recvArea.config(state=DISABLED)
        self.recvArea.yview(END)

    def addPlayer(self, player):
        self.playersArea.insert(END, player)
        
    def setPlayers(self, msg):
        self.playersArea.delete("0", END)
        players = msg.getAll()
        for p in players:
            self.addPlayer(p)


root = Tk()
root.resizable(width=FALSE, height=FALSE)
app = MainWindow(root)
root.mainloop()
