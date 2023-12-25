

# Requires
* Raspberry Pi Pico or Pico W (RPi)

# Installation
## Install Circuitpython
* For Pico W: https://circuitpython.org/board/raspberry_pi_pico_w/

The Pico will rename itself CIRCUITPI

## Copy files
* Copy all files in this repository to the RPi.

* _code.py_: runs server with webpage (for picoW)
* code_basic.py: runs without server (for pico)

# Sources
Files included in this repository but you might find updated versions in their source repositories.

* lib/ledPixelsPico.py (from https://github.com/lurbano/ledPixelsPico)

* ledTest.py (from https://github.com/lurbano/mayaLamps)

* lib/neopixels.mpy (from the circuitpython bundle: https://circuitpython.org/libraries)

* pgn games mostly from chess.com
* pgn-extract (https://www.cs.kent.ac.uk/people/staff/djb/pgn-extract/help.html#-W)
    * Install: > sudo apt install pgn-extract
    * Convert pgn files to uci use:
        * > pgn-extract -Wuci file.pgn > file.uci
