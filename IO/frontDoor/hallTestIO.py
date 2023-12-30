import board

import digitalio
import time



r0 = digitalio.DigitalInOut(board.GP0)
c0 = digitalio.DigitalInOut(board.GP3)

r0.direction = digitalio.Direction.OUTPUT
c0.direction = digitalio.Direction.INPUT

n=0
while True:
    n+=1
    print(n, r0.value, c0.value)
    time.sleep(0.1)