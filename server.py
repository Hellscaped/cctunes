#!/usr/bin/env python3

# CCTunes - Music Streaming Server for CC:Tweaked

import flask, flask_sock, threading, random, os, json, time, nfp
from io import BytesIO
from werkzeug.exceptions import BadRequest
from PIL import Image

request = flask.request
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
        songs = os.listdir("songs")
        random.shuffle(songs)
        songs = iter(songs)
        while True:
            try:
                self.currentSong = json.load(open("songs/"+next(songs)))
            except StopIteration:
                songs = os.listdir("songs")
                random.shuffle(songs)
                songs = iter(songs)
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

@app.route('/admin', methods=["GET"])
def getAdminLoginPage():
    return flask.send_file("admin_login.html")

@app.route("/<name>.css") # Serve CSS stylesheets, which each page has one. Don't need to keep duplicating code
def getStylesheet(name):
    if ".." in name:
        raise BadRequest("Name cannot include '..'")
    return flask.send_file(f"{name}.css")

@app.route("/panelArtwork/<name>")
def getPanelArtwork(name):
    if ".." in name:
        raise BadRequest("Name cannot include '..'")
    filename = f"songfiles/{name}.nfp"
    with open(f"{filename}","r") as f:
        nfpdata = f.read()
        img = nfp.nfp_to_img(nfpdata)
        size = img.size
        newx = size[0] * 8
        newy = size[1] * 8

        img = img.resize((newx,newy),Image.NEAREST)
        img_io = BytesIO()
        data = img.save(img_io,format="PNG")
        img_io.seek(0)
        return flask.send_file(img_io,mimetype="image/png", as_attachment=False)

@app.route("/admin", methods=["POST"])
def auth():
    username = request.form.get("username")
    password = request.form.get("password")
    checkbox = request.form.get("remember")
    print(f"{username=}, {password=}, {checkbox=}")
    return flask.redirect("/admin")


@sock.route('/')
def tune(ws):
    radio.clients.append(ws)
    while ws in radio.clients:
        time.sleep(1)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4146)
