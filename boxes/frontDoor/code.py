
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


ledMode = "rainbow"
ledPix = ledPixels(20, board.GP2)
#ledPix.brightness = 50

# touch sensor
#touch = touchio.TouchIn(board.GP16)
#print("Start touch", touch.value)

# brightness Knob
brightKnob = uKnob(board.A1)
l_lightsON = True

betaKnob = uKnob(board.A2)


# 3 way switches
doorSwitch = u3WaySwitch(pin1 = board.GP3, pin2 = board.GP18)
houseSwitch = u3WaySwitch(pin1 = board.GP11, pin2 = board.GP15)

# momentary switch
doorButton = uMomentarySwitch(board.GP19)


solidColor = (255, 255, 255)
modeColors = {}
modeColors["solidColor"] = solidColor

with open("index.html") as f:
    webpage = f.read()



#ssid, password = secrets.WIFI_SSID, secrets.WIFI_PASSWORD  # pylint: disable=no-member
ssid, password = "Wifipower", "defacto1"  # pylint: disable=no-member

print("Connecting to", ssid)
wifi.radio.connect(ssid, password)
print("Connected to", ssid)

pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool)
httpRequests = requests.Session(pool)

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
 
        

def touchCheck():
    if touch.value:
        while touch.value:
            time.sleep(0.1)
        return True
    else:
        return False
    
def setBrightness(knob, leds):
    brightness = knob.getPercent()/100
    if brightness < 0.02:
        leds.off()
        l_lightsON = False
    else:
        l_lightsON = True
        leds.brightness = brightness

print(f"Listening on http://{wifi.radio.ipv4_address}:80")
# Start the server.
server.start(str(wifi.radio.ipv4_address))

while True:
    try:
        '''
            LEDs
        '''
        #doorSwitchState = doorSwitch.getState()
        if doorSwitch.getState() == 1:
            #print("Led")
            brightness = brightKnob.getPercent()/100
            #print(brightness)
            
            ledPix.brightness = brightness
            #print(ledMode, ledPix.brightness)
            if ledMode == "rainbow":
                # rainbow
                for j in range(255):
                    for i in range(ledPix.nPix):
                        #setBrightness(brightKnob, ledPix)
                        ledPix.brightness = brightKnob.getPercent()/100
                        if doorSwitch.change():
                            break
                        pixel_index = (i * 256 // ledPix.nPix) + j
                        
                        ledPix.pixels[i] = ledPix.wheel(pixel_index & 255, 0.5) 
                    if l_lightsON:
                        ledPix.pixels.show()
                        
                    # check for input
                    server.poll()
                    if doorSwitch.state != 1:
                        break
                    
                    if doorButton.switchCheck():
                        ledMode = "red"

            
            elif ledMode == "red":
                ledPix.lightAll((255,0,0))

                if doorButton.switchCheck():
                        ledMode = "solid"
                        
            elif ledMode == "solid":
                # solid color
                server.poll()
                ledPix.lightAll(modeColors['solidColor'])
                
                if doorButton.switchCheck():
                        ledMode = "rainbow"

#             elif ledMode == "white":
#                 ledPix.lightAll((255,255,255))
# 
#                 if doorButton.switchCheck():
#                         ledMode = "rainbow"
            
            else:
                ledPix.off()
        else:
            ledPix.off()

        # Process any waiting requests
        server.poll()
    except OSError as error:
        print(error)
        continue

        







