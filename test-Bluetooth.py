import subprocess

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

selectBluetoothSpeaker()