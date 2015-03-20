# -*- coding: cp1252 -*-
from Tkinter import Tk, BOTH, Frame, Label, Text, E, W, S, N, DISABLED, END, INSERT
from Tkinter import NORMAL, Scrollbar, RIGHT, Y, Checkbutton, IntVar, FALSE
from ttk import Button, Style
from select import select
import ScrolledText
import socket, time
import thread
from Message import Message

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
        self.s.send(msg.serialize())
        parent.bind('<Return>', self.send)
        self.initUI()
        self.centerWindow()
        thread.start_new_thread(self.socketManager, ())


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
        self.IP = raw_input("Introduce la direcci�n IP del servidor: ")

    def obtainPort(self):
        self.PORT = int(raw_input("Introduce el puerto del servidor: "))
        
    def loadFromIni(self):
        self.player = None
        self.IP = None
        self.PORT = None
        self.MASTER = "Nope"
        
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
                self.MASTER = "password"
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
            time.sleep(0.3)
            if select([self.s], [self.s], [self.s])[0] and self.open:
                data = self.s.recv(self.BUFFER)
                recvMsg = Message()
                recvMsg = recvMsg.unserialize(data)
                if recvMsg.type == 0:
                    self.showMessage(recvMsg.player, recvMsg.getAll()[0])
                elif recvMsg.type == 1:
                    self.setPlayers(recvMsg)
                elif recvMsg.type == 5:
                    self.onClose()
                elif recvMsg.type == 6:
                    if recvMsg.target == self.player:
                        self.showMessage(recvMsg.player, recvMsg.getAll()[0])

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
        self.playersArea = Text(self, height= 27, width=12)
        self.playersArea.place(x=550, y=5)

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

        # Bot�n para tirar dado
        self.rollButton = Button(self, text="Tirar dado", command = self.roll)
        self.rollButton.place(x=655, y=55)

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
        if txt[0] == "@":
            if txt[1] == 'w' or txt[1] == 'W':
                pieces = txt.split(" ", 2)
                msg.target = pieces[1]
                msg.addMessage("(whisp): " + pieces[2])
                msg.type = 6
            if txt.split(" ")[0][1:] == "roll":
                if txt.split(" ")[1] in self.macros:
                    roll = self.macros[txt.split(" ")[1]]
                    msg = Message()
                    msg.player = self.player
                    msg.type = 3
                    msg.roll = roll
                else:
                    msg = None
            if txt.split(" ")[0][1:] == "proll":
                if txt.split(" ")[1] in self.macros:
                    roll = self.macros[txt.split(" ")[1]]
                    msg = Message()
                    msg.player = self.player
                    msg.type = 4
                    msg.roll = roll
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
        if (txt != "" and msg != None):
            self.s.send(msg.serialize())

    def showMessage(self, player, msg):
        self.recvArea.config(state=NORMAL)
        self.recvArea.insert(INSERT, player + ": " + msg + "\n")
        self.recvArea.config(state=DISABLED)
        self.recvArea.yview(END)

    def addPlayer(self, player):
        self.playersArea.config(state=NORMAL)
        self.playersArea.insert(INSERT, player + "\n")
        self.playersArea.config(state=DISABLED)

    def setPlayers(self, msg):
        self.playersArea.config(state=NORMAL)
        self.playersArea.delete("1.0", END)
        self.playersArea.config(state=DISABLED)
        players = msg.getAll()
        for p in players:
            self.addPlayer(p)


root = Tk()
root.resizable(width=FALSE, height=FALSE)
app = MainWindow(root)
root.mainloop()