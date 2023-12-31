
import socketpool
import wifi

from adafruit_httpserver.mime_type import MIMEType
from adafruit_httpserver.request import HTTPRequest
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.server import HTTPServer

import adafruit_requests as requests

import json
import board
from digitalio import DigitalInOut, Direction
import touchio
from analogio import AnalogIn
import time
import os
import math
from ledPixelsPico import *
from uKnob import uKnob
from u3WaySwitch import u3WaySwitch
from uMomentarySwitch import uMomentarySwitch
from uNetComm import *


ledMode = "rainbow"
old_ledMode = ledMode
ledPix = ledPixels(144, board.GP2)

modeSequence = ["rainbow", "red", "white", "solid", "off"]
#ledPix.brightness = 50
solidColor = (255, 255, 255)
modeColors = {}
modeColors["solidColor"] = solidColor
modeColors["white"] = '#f6d32d' 
# touch sensor
#touch = touchio.TouchIn(board.GP16)
#print("Start touch", touch.value)

# brightness Knob
brightKnob = uKnob(board.A1)
l_lightsON = True

betaKnob = uKnob(board.A2)


# 3 way switches
doorSwitch = u3WaySwitch(pin1 = board.GP3, pin2 = board.GP18)
kSwitch = u3WaySwitch(pin1 = board.GP15, pin2 = board.GP11)

# momentary switch
doorButton = uMomentarySwitch(board.GP19)




with open("index.html") as f:
    webpage = f.read()



#ssid, password = secrets.WIFI_SSID, secrets.WIFI_PASSWORD  # pylint: disable=no-member
ssid, password = "Wifipower", "defacto1"  # pylint: disable=no-member

print("Connecting to", ssid)
wifi.radio.connect(ssid, password)
print("Connected to", ssid)

pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool)
#httpRequests = requests.Session(pool)
comm = uNetComm(pool)


def requestToArray(request):
    raw_text = request.body.decode("utf8")
    print("Raw")
    data = json.loads(raw_text)
    return data

@server.route("/", "GET")
def base(request: HTTPRequest):
    """
    Serve the default index.html file.
    """
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        #response.send(f"{webpage()}")
        response.send(webpage)

@server.route("/", "POST")
def base(request: HTTPRequest):
    """
    Serve the default index.html file.
    """
    global ledMode
    global modeColors
    rData = {}
        
    print("POST")
    data = requestToArray(request)
    print(f"data: {data} ")
    print(f"action: {data['action']} & value: {data['value']}")

    # SET MODE
    if (data['action'] == "setMode"):
        
        print("IN \setmode")
        ledMode = data['value']
        print("ledMode:", ledMode)
            
        rData['item'] = "mode"
        rData['status'] = ledMode


    # SPECIFY COLOR FROM COLOR PICKER
    if (data['action'] == "setColor"):
        vals = data['value']
        modeColors[vals['id']] = vals['value']
        rData['item'] = vals['id']
        rData['status'] = vals['value']
        
    with HTTPResponse(request) as response:
        response.send(json.dumps(rData))

        



led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = False
@server.route("/led", "POST")
def ledButton(request: HTTPRequest):
    # raw_text = request.body.decode("utf8")
    print("Raw")
    # data = json.loads(raw_text)
    data = requestToArray(request)
    print(f"data: {data} & action: {data['action']}")
    rData = {}
    
    if (data['action'] == 'ON'):
        led.value = True
        
    if (data['action'] == 'OFF'):
        led.value = False
    
    rData['item'] = "led"
    rData['status'] = led.value
        
    with HTTPResponse(request) as response:
        response.send(json.dumps(rData))
 
def changeMode(newMode):
    global old_ledMode, ledMode
    old_ledMode = ledMode
    ledMode = newMode
    
def nextMode():
    global old_ledMode, ledMode
    print("Old mode:", ledMode)
    nSeq = len(modeSequence)
    for i in range(nSeq):
        print(i, ledMode, modeSequence[i])
        if ledMode == modeSequence[i]:
            if i < nSeq-1:
                changeMode(modeSequence[i+1])
            else:
                changeMode(modeSequence[0])
            break
    print("New mode", ledMode)
        

def touchCheck():
    if touch.value:
        while touch.value:
            time.sleep(0.1)
        return True
    else:
        return False
    
def setBrightness():
    brightness = brightKnob.getPercent()/100
    if brightness < 0.02:
        ledPix.off()
        l_lightsON = False
    else:
        l_lightsON = True
        ledPix.brightness = brightness
        
        
def houseSwitchCheck():
    if kSwitch.change():
        print("kSwitch:", kSwitch.getState())
        if kSwitch.state == 1:
            comm.request("bedroomSpeaker", "Rhythmbox", "play")
            comm.request("bedroomSpeaker", "setVolume", "100")
            comm.request("kitchen", "setMode", "rainbow")
        elif kSwitch.state == 0:
            comm.request("bedroomSpeaker", "Rhythmbox", "pause")
            comm.request("kitchen", "setMode", "red")
            
        elif kSwitch.state == 2:
            comm.request("kitchen", "setMode", "off")
            
def doorSwitchCheck():
    global ledMode, old_ledMode
    if doorSwitch.change():
        print("doorSwitch:", doorSwitch.state)
        if doorSwitch.state == 1:
            ledMode = old_ledMode
        elif doorSwitch.state == 0:
            ledMode = "off"
        elif doorSwitch.state == 2:
            ledMode = "red"
        
def doorButtonCheck():
    global ledMode, old_ledMode
    if doorButton.pressed():
        nextMode()

# 192.168.1.131

print(f"Listening on http://{wifi.radio.ipv4_address}:80")
# Start the server.
server.start(str(wifi.radio.ipv4_address))

while True:
    try:
        '''
            LEDs
        '''
        #doorSwitchState = doorSwitch.getState()
        setBrightness()
        houseSwitchCheck()
        doorSwitchCheck()
        doorButtonCheck()
        
        
        brightness = brightKnob.getPercent()/100
        if brightness < 0.02:
            ledPix.off()
        else:
            ledPix.brightness = brightness
                        
            if ledMode == "rainbow":
                # rainbow
                for j in range(255):
                    for i in range(ledPix.nPix):
                        setBrightness()
                        pixel_index = (i * 256 // ledPix.nPix) + j
                        
                        ledPix.pixels[i] = ledPix.wheel(pixel_index & 255, 0.5)
                        
                    houseSwitchCheck()
                    doorSwitchCheck()
                    doorButtonCheck()
                        
                    if l_lightsON:
                        ledPix.pixels.show()
                    server.poll()
                    if ledMode == "rainbow":
                        time.sleep(0.01)
                        # check brightness dial
                        ledPix.brighness = brightKnob.getPercent()/100
                        
                    else:
                        break
                    
                    #if doorSwitch.change():
                    #    changeMode("red")

            elif ledMode == "red":
                ledPix.lightAll((255,0,0))

                        
            elif ledMode == "solid":
                # solid color
                server.poll()
                ledPix.lightAll(modeColors['solidColor'])


            elif ledMode == "white":
                ledPix.lightAll(modeColors['white'])
                        
            
            elif ledMode == "off":
                ledPix.off()
                        
                        
            else:
                changeMode("off")
        # Process any waiting requests
        server.poll()
    except OSError as error:
        print(error)
        continue

        








