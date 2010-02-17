from pymt import *
from audio_input import InputStream
from visualisation import *
from gareth_visualisation import *
import pygame
from OpenGL.GL import *

#--------------------
# If you have windowing issues you need to fix your config file.
# Apparently a new "feature" with 0.4 is to create a window with import (how exciting)
# so to fix windowing issues do:
# python -m pymt.tools.config -n
#--------------------
	
stream = InputStream()
stream.start()

i = 0
visualisations = [BasicVisualisation, CircleVisualisation, ParticleVisualisation, GarethVis]

a = MTWidget()
#v = GarethVis(width = int(pymt_config.get('graphics', 'width')), height = int(pymt_config.get('graphics', 'height')), stream=stream )
v = BasicVisualisation(width = int(pymt_config.get('graphics', 'width')), height = int(pymt_config.get('graphics', 'height')), stream=stream)
a.add_widget(v)

change = MTButton(label='Change Visualisation', pos=(0,0),size=(100, 50))
a.add_widget(change)

@change.event
def on_press(touch):
	global v, i
	a.remove_widget(v)
	i += 1
	i%=len(visualisations)
	v = visualisations[i](width = int(pymt_config.get('graphics', 'width')), height = int(pymt_config.get('graphics', 'height')), stream=stream)
	a.add_widget(v)
	change.bring_to_front()

try:
	runTouchApp(a)
finally:
	stream.close()
