import time
import board
from analogio import AnalogIn

knob = AnalogIn(board.A1)

while True:
    print((knob.value, ))
    time.sleep(0.2)