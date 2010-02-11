from pymt import *
from audio_input import InputStream
from visualisation import *
from gareth_visualisation import *
import pygame

#--------------------
# If you have windowing issues you need to fix your config file.
# Apparently a new "feature" with 0.4 is to create a window with import (how exciting)
# so to fix windowing issues do:
# python -m pymt.tools.config -n
#--------------------

stream = InputStream()
stream.start()
 
v = GarethVis(width = w.width, height = w.height, stream=stream)
 
try:
	runTouchApp(v)
finally:
	stream.close()
