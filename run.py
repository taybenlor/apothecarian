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

#v = GarethVis(width = int(pymt_config.get('graphics', 'width')), height = int(pymt_config.get('graphics', 'height')), stream=stream )
v = ParticleVisualisation(width = int(pymt_config.get('graphics', 'width')), height = int(pymt_config.get('graphics', 'height')), stream=stream)
 

try:
	runTouchApp(v)
finally:
	stream.close()
