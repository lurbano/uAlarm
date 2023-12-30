import board
import digitalio
import time

hall = digitalio.DigitalInOut(board.GP27)
hall.direction = digitalio.Direction.INPUT
hall.pull = digitalio.Pull.UP
#break_beam.value

power = digitalio.DigitalInOut(board.GP18)
power.direction = digitalio.Direction.OUTPUT
power.value = True

n=0
while True:
    #print(break_beam.value)
    n+=1
    print(n, hall.value)
    time.sleep(0.1)
