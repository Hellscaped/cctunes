
local radio = "wss://cctunes.hellscaped.dev/"
local fetchStreamInfoURL = "https://cctunes.hellscaped.dev/getStreamInfo"
local fetchNFPArtURL = "https://cctunes.hellscaped.dev/getArtwork"
function fetchStreamInfo()
    local response = http.get(fetchStreamInfoURL)
    if response then
        local data = response.readAll()
        response.close()
        return textutils.unserializeJSON(data)
    else
        return {title = "Unknown", artist = "Unknown"}
    end
end
function fetchNFPArt()
    local response = http.get(fetchNFPArtURL)
    if response then
        local data = response.readAll()
        response.close()
        return data
    else
        return nil
    end
end
local speaker = peripheral.find("speaker")
local monitor = peripheral.find("monitor")
if monitor then
    term.redirect(monitor)
    monitor.setTextScale(0.5)
end
while true do
    songData = {}
    
    local ws, err = http.websocket(radio)
    if not ws then
        sleep(5)
        goto continue
    end

    songData = fetchStreamInfo()
    coverArt = fetchNFPArt()
    term.clear()
    term.setBackgroundColor(colors.black)
    local art = paintutils.parseImage(coverArt)
    paintutils.drawImage(art, 3, 1)
    term.setBackgroundColor(colors.black)
    term.setCursorPos(2, 21)
    term.write("Now Playing:")
    term.setCursorPos(2, 22)
    term.write(songData.title)
    term.setCursorPos(2, 23)
    term.write("by " .. songData.artist)
    term.setCursorPos(2, 24)
    term.write(songData.album)
    local decoder = require("cc.audio.dfpwm").make_decoder()
    while true do
        local msg = ws.receive()
        if msg then
            if msg == "fetchStreamInfo" then
                songData = fetchStreamInfo()
                coverArt = fetchNFPArt()
                term.clear()
                local art = paintutils.parseImage(coverArt)
                paintutils.drawImage(art, 3, 1)
                term.setCursorPos(2, 21)
                term.write("Now Playing:")
                term.setCursorPos(2, 22)
                term.write(songData.title)
                term.setCursorPos(2, 23)
                term.write("by " .. songData.artist)
                term.setCursorPos(2, 24)
                term.write(songData.album)
            else
                speaker.playAudio(decoder(msg))
            end
        end
    end
    ::continue::
end
