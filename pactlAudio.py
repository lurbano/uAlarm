import subprocess

class pactlAudio:
    def __init__(self):
        pass 

    def getInfo(self):
        cmd = 'pactl list short sinks'
        result = subprocess.run(cmd, shell = True, 
                            capture_output=True, text=True)
        #print(cmd)
        #print(result.stdout)
        return result.stdout

    def getRunning(self):
        info = {}
        data = self.getInfo().split("\n")
        for d in data:
            #print("x", d)
            s = d.split("\t")
            info["id"] = s[0]
            info['sink'] = s[1]
            info['module'] = s[2]
            info['freqData'] = s[3]
            info['status'] = s[4]
            
            if info['status'] == 'RUNNING':
                return info
        print("pactl found no RUNNING sink")
        return None
    
    def setVolume(self, vol=50):
        volPct = f"{vol}%"
        info = self.getRunning()
        if info != None:
            cmd = f'pactl set-sink-volume {info["id"]} {volPct}'
            subprocess.Popen(cmd, shell=True)
    

    def getVolume(self):
        info = self.getRunning()
        if info != None:
            cmd = f'pactl get-sink-volume {info["id"]}'
            result = subprocess.run(cmd, shell = True, 
                            capture_output=True, text=True)
            d = result.stdout.split(" ")
            #print(d)
            for s in result.stdout.split(" "):
                if len(s) > 0:
                    if s[-1] == "%":
                        vol = int(s[:-1])
            return vol


if __name__ == '__main__':
    audioCtrl = pactlAudio()

    running = audioCtrl.getRunning()
    print(running)
    v = audioCtrl.getVolume()
    print(f"Volume = {v}%")
    audioCtrl.setVolume(50)