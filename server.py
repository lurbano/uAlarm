from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import json
import subprocess
import time
from urllib.parse import quote
from pactlAudio import *

fileURI = 'file:///home/lurbano/Music/'
audioCtrl = pactlAudio()

def rhythmboxCommand(opt):
    cmd = f'rhythmbox-client --{opt}'
    subprocess.run(cmd, shell = True)
    print(cmd)
    return

def playSong(fileName):
    fileName = quote(fileName)
    cmd = f'rhythmbox-client --enqueue {fileURI}{fileName}'
    subprocess.run(cmd, shell = True)
    print("playSong:", cmd)
    rhythmboxCommand("next")
    return



def getSongInfo():
    '''from rhythmbox'''
    cmd = f'rhythmbox-client --print-playing'
    result = subprocess.run(cmd, shell = True, 
                            capture_output=True, text=True)
    print(cmd)
    print(result.stdout)
    song = result.stdout.split(" - ", maxsplit=1)
    print(song)
    return song[1]

def setVolume(vol=1.0):
    ''' 0.0 < vol < 1.0 '''
    cmd = f'rhythmbox-client --set-volume {vol}'
    subprocess.run(cmd, shell = True)
    print(cmd)
    return

def getAllArtists():
    path = "/home/lurbano/Music/"
    dir_list = os.listdir(path)
    return sorted(dir_list, key=str.lower)

def getAllSongs(artist=None):
    if artist == None:
        return None
    else:
        path = f"/home/lurbano/Music/{artist}"
        dir_list = os.listdir(path)
        return sorted(dir_list, key=str.lower)

def connectToBluetooth(addr):
    cmd = f'bluetoothctl disconnect {addr}'
    subprocess.run(cmd, shell = True)
    cmd = f'bluetoothctl connect {addr}'
    subprocess.run(cmd, shell = True)

def selectBluetoothSpeaker(speaker="BedroomSpeaker"):
    ''' 0.0 < vol < 1.0 '''
    cmd = f'bluetoothctl devices'
    result = subprocess.run(cmd, shell = True, 
                            capture_output=True, text=True)
    # print (result)
    devices = result.stdout.split("\n")
    for device in devices[:-1]:
        info = device.split(" ")
        print(info)
        if info[2] == speaker:
            addr = info[1]
            print(speaker, " found at ", addr)
            connectToBluetooth(addr)
    return

def postDataToArray(postData):
    raw_text = postData.decode("utf8")
    print("Raw")
    data = json.loads(raw_text)
    return data

class aTime:
    def __init__(self, str):
        self.hr = int(str.split(":")[0])
        self.min = int(str.split(":")[1])
    def __repr__(self):
        return f'{self.hr}:{self.min}'


def sayTime():
    now = time.localtime()
    toSay = f'It is now {now.tm_hour} {now.tm_min}.'
    subprocess.Popen(f'echo {toSay} | festival --tts', shell=True)
    time.sleep(4)

def sayText(toSay):
    subprocess.Popen(f'echo {toSay} | festival --tts', shell=True)
    time.sleep(4)


    

class uHTTPRequestHandler(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        try:
            file_to_open = open(self.path[1:]).read()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(file_to_open, 'utf-8'))
        except:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'404 - Not Found')

    def do_POST(self):
        global alarmTime
        global alarmOn
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = postDataToArray(post_data)
        '''
        data consists of 
            data['action'] and 
            data['value']
        '''
        self._set_headers()
        print(data)
        rData = {}
        rData['item'] = ""
        rData['status'] = ""
        
        rhythmboxOptions = ["play", 
                            "pause", 
                            "play-pause",
                            "next", 
                            "previous", 
                            "volume-up", 
                            "volume-down"]

        if data['action'] == "Rhythmbox":
            if data['value'] in rhythmboxOptions:
                rhythmboxCommand(data['value'])
                rData['item'] = f'Rhythmbox-{data["value"]}'
                rData['status'] = getSongInfo()
            
        if data['action'] == "setAlarm":
            alarmTime = aTime(data['value'])
            alarmOn = False
            now = time.localtime()
            print(f"Now:{now.tm_hour}:{now.tm_min}")
            print("Alarm time: ", alarmTime)
            sayText(f'Alarm set for {alarmTime}')
        
        if data['action'] == "checkAlarm":
            now = time.localtime()
            if (now.tm_hour == alarmTime.hr) and (now.tm_min == alarmTime.min) and not alarmOn:
                print("We have alarm!")
                alarmOn = True 
                rhythmboxCommand("play")
                setVolume(1.0)
                rData['item'] = "alarmOn"
                rData['status'] = "ON"
            else:
                rData['item'] = "alarmOff"
                rData['status'] = "OFF"

        if data['action'] == "sayTime":
            sayTime()

        if data['action'] == "songInfo":
            rData['item'] = 'songInfo'
            rData['status'] = getSongInfo()

        if data['action'] == "chooseSpeaker":
            selectBluetoothSpeaker(data['value'])
            rData['item'] = "speaker"
            rData['status'] = data['value']

        if data['action'] == 'getArtistList':
            dir_list = getAllArtists()
            rData['item'] = "artists"
            rData['status'] = dir_list
            print("Got artist list")
            print(rData)

        if data['action'] == 'getSongList':
            rData['item'] = "songs"
            rData['status'] = getAllSongs(data['value'])

        if data['action'] == 'playSong':
            playSong(data['value'])
            rData['item'] = "playSong"
            rData['status'] = data['value']

        if data['action'] == 'getVolume':
            vol = audioCtrl.getVolume()
            rData['item'] = "Volume"
            rData['status'] = vol
        
        if data['action'] == 'dVolume':
            vol = audioCtrl.getVolume()
            if data['value'] == "+":
                vol += 5
            elif data['value'] == "-":
                vol -= 5
            audioCtrl.setVolume(vol)
            rData['item'] = "Volume"
            rData['status'] = vol

        self.wfile.write(bytes(json.dumps(rData), 'utf-8'))



alarmOn = False
alarmTime = aTime("5:35")

httpd = HTTPServer(('', 8000), uHTTPRequestHandler)
httpd.serve_forever()


# while True:
#     httpd.handle_request()
#     now = time.localtime()
#     print(f"Time: {now.tm_hour}:{now.tm_min} | {alarmTime.hr}:{alarmTime.min}")
#     if (now.tm_hour == alarmTime.hr) and (now.tm_min == alarmTime.min) and not alarmOn:
#         print("We have alarm!")
#         alarmOn = True 
#         rhythmboxCommand("play")
