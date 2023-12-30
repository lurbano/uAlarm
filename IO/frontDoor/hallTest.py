import board
import digitalio
import time


hall = digitalio.DigitalInOut(board.GP19)

hall.direction = digitalio.Direction.INPUT

n=0
while True:
    n+=1
    print(n, hall.value)
    time.sleep(0.1)

