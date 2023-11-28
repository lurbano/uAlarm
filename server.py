from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi
import json
import subprocess

def playRhythmbox():
    cmd = 'rhythmbox-client --play'
    subprocess.Popen(cmd, shell = True)
    print(cmd)
    return

def nextRhythmbox():
    cmd = 'rhythmbox-client --next'
    subprocess.Popen(cmd, shell = True)
    print(cmd)
    return

def pauseRhythmbox():
    cmd = 'rhythmbox-client --pause'
    subprocess.Popen(cmd, shell = True)
    print(cmd)
    return

def postDataToArray(postData):
    raw_text = postData.decode("utf8")
    print("Raw")
    data = json.loads(raw_text)
    return data

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

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
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = postDataToArray(post_data)
        self._set_headers()
        print(data)
        rData = {}
        rData['item'] = "Rhythmbox"
        rData['status'] = "start"
        self.wfile.write(bytes(json.dumps(rData), 'utf-8'))

        if data["action"] == "Rhythmbox":
            if data['value'] == "start":
                playRhythmbox()
            if data['value'] == 'pause':
                pauseRhythmbox()

httpd = HTTPServer(('', 8000), SimpleHTTPRequestHandler)
httpd.serve_forever()