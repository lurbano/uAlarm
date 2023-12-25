
import socketpool
import wifi

from adafruit_httpserver.mime_type import MIMEType
from adafruit_httpserver.request import HTTPRequest
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.server import HTTPServer

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


ledMode = "rainbow"
ledPix = ledPixels(30, board.GP22)
#ledPix.brightness = 50

# touch sensor
touch = touchio.TouchIn(board.GP3)
print("Start touch", touch.value)

# brightness Knob
brightKnob = uKnob(board.A2)



with open("index.html") as f:
    webpage = f.read()



#ssid, password = secrets.WIFI_SSID, secrets.WIFI_PASSWORD  # pylint: disable=no-member
ssid, password = "Wifipower", "defacto1"  # pylint: disable=no-member

print("Connecting to", ssid)
wifi.radio.connect(ssid, password)
print("Connected to", ssid)

pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool)


def requestToArray(request):
    raw_text = request.body.decode("utf8")
    print("Raw")
    data = json.loads(raw_text)
    return data

@server.route("/")
def base(request: HTTPRequest):
    """
    Serve the default index.html file.
    """
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        #response.send(f"{webpage()}")
        response.send(webpage)


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
 
@server.route("/setMode", "POST")
def setLedMode(request: HTTPRequest):
    # raw_text = request.body.decode("utf8")
    #print("Raw")
    # data = json.loads(raw_text)
    
    global ledMode
    
    data = requestToArray(request)
    print("IN \setmode")
    print(f"data: {data} & action: {data['action']} & value: {data['value']}")
    rData = {}
    
    ledMode = data['value']
        
    print("ledMode:", ledMode)
        
    
    rData['item'] = "mode"
    rData['status'] = ledMode
        
    with HTTPResponse(request) as response:
        response.send(json.dumps(rData))
        

@server.route("/checkerboard", "POST")
def checkerboard(request: HTTPRequest):
    # raw_text = request.body.decode("utf8")
    #print("Raw")
    # data = json.loads(raw_text)
    
    data = requestToArray(request)
    print(f"data: {data} & action: {data['action']} & value: {data['value']}")
    rData = {}
    
    if data['action'] == "1":
        game.whiteColor = hex_to_rgb(data['value'])
    elif data['action'] == '2':
        game.blackColor = hex_to_rgb(data['value'])
            
    
    rData['item'] = "checkerboard"
    rData['status'] = f'checkColor{data["action"]}'
        
    with HTTPResponse(request) as response:
        response.send(json.dumps(rData))

def touchCheck():
    if touch.value:
        while touch.value:
            time.sleep(0.1)
        return True
    else:
        return False
 
print(f"Listening on http://{wifi.radio.ipv4_address}:80")
# Start the server.
server.start(str(wifi.radio.ipv4_address))

while True:
    try:
        # Do something useful in this section,
        # for example read a sensor and capture an average,
        # or a running total of the last 10 samples
        if ledMode == "rainbow":
            # rainbow
            for j in range(255):
                for i in range(ledPix.nPix):
                    pixel_index = (i * 256 // ledPix.nPix) + j
                    #ledPix.brightness = 0.1
                    #ledPix.brighness = brightKnob.getPercent()/100
                    #print(brightKnob.getPercent()/100)
                    ledPix.brightness = brightKnob.getPercent()/100
                    print("brightness", brightKnob.getPercent(), ledPix.brightness)
                    ledPix.pixels[i] = ledPix.wheel(pixel_index & 255, 0.5) 

                ledPix.pixels.show()
                server.poll()
                if ledMode == "rainbow":
                    time.sleep(0.1)
                    # check brightness dial
                    ledPix.brighness = brightKnob.getPercent()/100
                    
                else:
                    break
                
                if touchCheck():
                    ledMode = "checkerboard"
        elif ledMode == "checkerboard":
            # checkerboard
            server.poll()
            ledPix.checkerBoard()
            
            if touchCheck():
                    ledMode = "playThrough"

        
        else:
            ledPix.off()

        # Process any waiting requests
        server.poll()
    except OSError as error:
        print(error)
        continue

        






