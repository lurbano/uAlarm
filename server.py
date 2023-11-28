from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi
import json
import subprocess
import time


def rhythmboxCommand(opt):
    cmd = f'rhythmbox-client --{opt}'
    subprocess.Popen(cmd, shell = True)
    print(cmd)
    return

def setVolume(vol=1.0):
    ''' 0.0 < vol < 1.0 '''
    cmd = f'rhythmbox-client --set-volume {vol}'
    subprocess.Popen(cmd, shell = True)
    print(cmd)
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
        self._set_headers()
        print(data)
        rData = {}
        rData['item'] = "Rhythmbox"
        rData['status'] = "start"
        
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
            
        if data['action'] == "setAlarm":
            alarmTime = aTime(data['value'])
            alarmOn = False
            now = time.localtime()
            print(f"Now:{now.tm_hour}:{now.tm_min}")
            print("Alarm time: ", alarmTime)
        
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
