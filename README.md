# cctunes
A websocket radio server for CC: Tweaked.

## Client Installation
``wget https://raw.githubusercontent.com/Hellscaped/cctunes/master/computer/startup.lua startup.lua``

## Server Installation
1. Install [Python 3](https://www.python.org/downloads/).
2. Install [flask](https://pypi.org/project/Flask/).
3. Install [flask-sock](https://pypi.org/project/Flask-Sock)
4. Run the server with `python server.py`.

Put the actual song files and artworks (32x20 NFP) into the songfiles directory.
Put the data files (.json) into the songs directory.
```json
{
    "title": "Altars of Apostasy (incl. Hall of Sacreligious Remains)",
    "artist": "Heaven Pierce Her",
    "album": "IMPERFECT HATRED",
    "artwork": "1.nfp",
    "file": "1.dfpwm"
}
```