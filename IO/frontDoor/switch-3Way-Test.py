import board
import digitalio
import time
from u3WaySwitch import u3WaySwitch

s1 = u3WaySwitch(board.GP18, board.GP3)

# s1 = digitalio.DigitalInOut(board.GP19)
# s1.direction = digitalio.Direction.INPUT
# s1.pull = digitalio.Pull.DOWN
# 
# s2 = digitalio.DigitalInOut(board.GP18)
# s2.direction = digitalio.Direction.INPUT
# s2.pull = digitalio.Pull.DOWN

n=0
while True:
    n+=1
    #print(n, s1.value, s2.value)
    print(n, s1.getState())
    time.sleep(0.1)