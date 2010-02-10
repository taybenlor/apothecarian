from pymt import *
from audio_input import InputStream
from visualisation import *

w = MTWindow(width=1000, height=800)

# hack to escape fullscreen
w.toggle_fullscreen()

stream = InputStream()
stream.start()

v = CircleVisualisation(width = w.width, height = w.height, stream=stream)
w.add_widget(v)

try:
	runTouchApp()
finally:
	stream.close()