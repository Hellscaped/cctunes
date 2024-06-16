#!/usr/bin/env python3

# CCTunes - Music Streaming Server for CC:Tweaked

import flask, flask_sock, threading, random, os, json, time

app = flask.Flask(__name__)
sock = flask_sock.Sock(app)

class RadioThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.clients = []
        self.currentSong = {
            "title": "No song playing",
            "artist": "N/A",
            "album": "N/A",
            "artwork": "0.nfp",
            "file": "0.dfpwm"
        }
        self.start()
    def broadcast(self, msg):
        for client in self.clients:
            try:
                client.send(msg)
            except:
                self.clients.remove(client)
    def run(self):
        songs = iter(os.listdir("songs"))
        while True:
            try:
                self.currentSong = json.load(open("songs/"+next(songs)))
            except StopIteration:
                songs = iter(os.listdir("songs"))
                self.currentSong = json.load(open("songs/"+next(songs)))
            print("Now playing:", self.currentSong["title"], "by", self.currentSong["artist"])
            self.broadcast("fetchStreamInfo")
            with open("songfiles/"+self.currentSong["file"], "rb") as f:
                while True:
                    chunk = f.read(6000)
                    if not chunk:
                        break
                    self.broadcast(chunk)
                    time.sleep(1)

radio = RadioThread()

@app.route('/getStreamInfo')
def getStreamInfo():
    d = radio.currentSong.copy()
    del d["file"]
    return json.dumps(d)

@app.route('/getArtwork')
def getArtwork():
    return flask.send_file("songfiles/"+radio.currentSong["artwork"])

@sock.route('/')
def tune(ws):
    radio.clients.append(ws)
    while ws in radio.clients:
        time.sleep(1)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4146)