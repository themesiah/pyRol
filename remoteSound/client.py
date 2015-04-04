import socket
import os, time, thread, wave, pyaudio
import pymedia.audio.acodec as acodec
import pymedia.audio.sound as sound
import pymedia.muxer as muxer
import sys

def playSound (fn, snd):
    fn = "recv/"+fn
    dm = muxer.Demuxer(str.split(fn, '.')[-1].lower())
    f = open(fn, 'rb')
    dec = None
    s = f.read( 32000 )
    while len(s):
        frames = dm.parse(s)
        if frames:
            for fr in frames:
                if dec == None:
                    dec = acodec.Decoder(dm.streams[fr[0]])
                r = dec.decode(fr[1])
                if r and r.data:
                    if snd != None:
                        snd = sound.Output(int(r.sample_rate),
                            r.channels,
                            sound.AFMT_S16_LE)
                        snd.setVolume(int(VOLUME * 65535))
                    data = r.data
                    snd.play(data)
        s = f.read(512)

    while snd.isPlaying():
        time.sleep(.05)

TCP_IP = "localhost"
TCP_PORT = 6900
BUFFER_SIZE = 1024
VOLUME = 1
snd = None

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

while 1:
    name = s.recv(BUFFER_SIZE)
    if "FINISH" in name:
        break
    elif "SEND" in name:
        name = s.recv(BUFFER_SIZE)
        f = open("recv/"+name, 'wb')
        while 1:
            data = s.recv(1024)
            if "FINISHED" in data:
                break
            f.write(data)
        f.close()
        s.send("OK")
    elif "PLAY" in name:
        try:
            name = s.recv(BUFFER_SIZE)

            thread.start_new_thread(playSound, (name, snd, ))
        except Exception as err:
            print sys.exc_info()[0]
            print err
            print "Intentando reproducir el archivo: " + name +"."
            print "No ha sido encontrado."
    elif "VOLU" in name:
        VOLUME = float(s.recv(BUFFER_SIZE))
        snd.setVolume(int(VOLUME * 65535))
