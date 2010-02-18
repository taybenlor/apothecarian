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


#b = MTScatterWidget(width = int(pymt_config.get('graphics', 'width')), height = int(pymt_config.get('graphics', 'height')))
#v = GarethVis(width = int(pymt_config.get('graphics', 'width')), height = int(pymt_config.get('graphics', 'height')), stream=stream )
v = BasicVisualisation(width = int(pymt_config.get('graphics', 'width')), height = int(pymt_config.get('graphics', 'height')), stream=stream)
container = MTWidget()
container.add_widget(v)

change = MTButton(label='Change Visualisation', pos=(20,20),size=(100, 50))
root = MTWidget()
root.add_widget(container)
root.add_widget(change)

@change.event
def on_press(touch):
	global v, i
	container.remove_widget(v)
	i += 1
	i%=len(visualisations)
	v = visualisations[i](width = int(pymt_config.get('graphics', 'width')), height = int(pymt_config.get('graphics', 'height')), stream=stream)
	container.add_widget(v)
	
try:
	runTouchApp(root)
finally:
	stream.close()
