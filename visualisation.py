from pymt import *
from audio_input import InputStream
import random, time, math
from OpenGL.GL import *
from numpy import maximum, array, arange
 
class Visualisation(MTWidget):
	#-----------------
	# Give it a stream if you have one already, otherwise it will create its own.
	#-----------------
	def __init__(self, stream=None, **kwargs):
		super(Visualisation, self).__init__(**kwargs)
		self.stream = stream
		if self.stream == None:
			self.stream = InputStream()
			self.stream.start()
		self._last_tick = time.time()
 
	def draw(self):
		temp = time.time()
		self.visualise((temp-self._last_tick)*1000)
		self._last_tick = temp
 
	#------------------
	# Override this method to make your own visualisation
	# ticks is millis since last call (float)
	#------------------
	def visualise(self, ticks):
		pass
 
class BasicVisualisation(Visualisation, MTScatterWidget):
	def __init__(self, **kwargs):
		super(BasicVisualisation, self).__init__(**kwargs)
		self.bg_color = (0.0, 0.0, 0.0)
		self.lit_color = (0.0, 0.8, 0.0)
		self.unlit_color=(0.2,0.2,0.2)
		self.max_color=(0.8, 0.0, 0.0)
		self.maxes = None
 
	def visualise(self, ticks):
		#draw the background		
		graphx.colors.set_color(*self.bg_color)
		graphx.draw.drawRectangle((0,0), (self.width, self.height))
 
		#get our visualisation values
		spectrum = array(self.stream.get_log_audio_spectrum(8)) # array of floats (each value is contribution, takes optional number of buckets)
		#note, this one is slower and can only return about 10 buckets max
 		if self.maxes == None:
			self.maxes = spectrum
		else:
			self.maxes -= 0.1
			self.maxes = maximum(self.maxes, spectrum)

		#draw points evenly across the screen
		x_mul = self.width/len(spectrum)
		width = int(x_mul*0.9)
		height = self.height/100
		#height = int(h*0.8)
		#gap = int(h*0.2)
		for i, item in enumerate(spectrum):
			x = int((x_mul * i) + ((x_mul * 0.1)/2))
			val = int(item*100)
			vmax = int(self.maxes[i]*100)
			for j in xrange(100):
				if j == vmax:
					graphx.colors.set_color(*self.max_color)
				elif val > j:
					#lit bar
					graphx.colors.set_color(*self.lit_color)
				else:
					graphx.colors.set_color(*self.unlit_color)
				
				graphx.draw.drawLine([x, j*height, x+width, j*height], int(height*0.8))
					#unlit bar
 
		#if its a beat randomly change the background colour
		#if self.stream.is_beat():
		#	self.bg_color = (random.random(), random.random(), random.random())
 
class CircleVisualisation(Visualisation):
	def __init__(self, **kwargs):
		super(CircleVisualisation, self).__init__(**kwargs)
		self.fg_color = (1.0, 1.0, 1.0)
		self.history = None
		self.volume = 0
 
	def visualise(self, ticks):
		graphx.colors.set_color(0.0,0.0,0.0)
		graphx.draw.drawRectangle((self.x,self.y), (self.width, self.height))
 
		graphx.colors.set_color(*self.fg_color)
		self.volume -= 0.01
		val = self.stream.get_average_energy()
		self.volume = max(self.volume, val)
		val = self.volume * (self.width/2)
		graphx.draw.drawCircle(self.center, val)
 
		#fall gracefully
		spectrum = array(self.stream.get_normal_audio_spectrum(100))
		if self.history != None:
			self.history -= 0.01
			self.history = maximum(self.history, spectrum)
		else:
			self.history = spectrum
		
		#arrange the points around in a circle
		cx, cy = self.center
		length = val
		angle = 0

		points = []
		for d in self.history:
			lx = ((d * (self.width/2)) +val) * math.cos(angle)
			ly = ((d * (self.width/2))+val) * math.sin(angle)
 
			points.append(cx+lx)
			points.append(cy+ly)
 
			angle += math.pi*2/(len(spectrum))
 
		#complete the circle
		points.append(points[0])
		points.append(points[1])
		graphx.draw.drawLine(points)
 
		#if its a beat change the fg colour
		if self.stream.is_beat():
			self.fg_color = (random.random(), random.random(), random.random())
 
PARTICLE_LIMIT = 200
class ParticleVisualisation(Visualisation):
	def __init__(self, max=5000, **kwargs):
		super(ParticleVisualisation, self).__init__(**kwargs)
		self.image = Image('dot.png')
		self.particles = []
		self.max = max
		for i in xrange(self.max):
			self.particles.append(Particle())
		self.count = 0
		self.gravity_wells = {}
		
	def on_touch_down(self, touch):
		self.gravity_wells[touch.id] = (touch.x, touch.y)
		touch.grab(self)
		return True

	def on_touch_move(self, touch):
		self.gravity_wells[touch.id] = (touch.x, touch.y)
		return True

	def on_touch_up(self, touch):
		if touch.id in self.gravity_wells:
			self.gravity_wells.pop(touch.id)
		return True
 
	def visualise(self, ticks):
		self.count += ticks
 
		cx, cy = self.center
		angle = 0
		spectrum = self.stream.get_normal_audio_spectrum(100)
		todo = []
		for d in spectrum: 
			d*=100
			dx = math.cos(angle)
			dy = math.sin(angle)
 
			x = cx + random.randint(-10, 10)
			y = cy + random.randint(-10, 10)
 
			dx *= 20
			dy *= 20
 
			#for i in xrange(count):
			if d > 5:
				todo.append((x, y, dx, dy))
 
			angle += math.pi*2/(len(spectrum))
		
		glTexEnvf(GL_POINT_SPRITE_ARB, GL_COORD_REPLACE_ARB, GL_TRUE)
		blend = GlBlending(sfactor=GL_SRC_ALPHA, dfactor=GL_ONE)
		set_texture(self.image.texture)
		glPointSize(25)
		with DO(blend, gx_enable(self.image.texture.target), gx_enable(GL_POINT_SPRITE_ARB), gx_begin(GL_POINTS)):
			for particle in self.particles:
				if particle.visible:
					particle.update(self.width, self.height,self.gravity_wells.values())
					glColor4f(particle.color[0], particle.color[1], particle.color[2], particle.alpha)
					glVertex2f(particle.x, particle.y)
				elif len(todo):
					particle.animate(*todo.pop(-1))

 
GRAVITY_WELL_FORCE = 200000
class Particle(object):
	def __init__(self):
		self.visible = False
 
	def update(self, wx, wy, gravity_wells=[]):
		self.update_velocity(gravity_wells)
		self.x += self.dx
		self.y += self.dy
		self.alpha -= self.decay
		self.decay *= self.decay_rate
		if self.alpha <= 0.0:
			self.visible = False
		if self.x > wx*1.5 or self.x < (0-wx*0.5):
			self.visible = False
		elif self.y > wy*1.5 or self.y < (0-wy*0.5):
			self.visible = False
		
	def update_velocity(self, gravity_wells=[]):
		self.dx *=0.95
		self.dy *=0.95
		if not gravity_wells:
			return 
		for wx,wy in gravity_wells:
			distance = ((self.x - wx)**2 + (self.y - wy)**2)**0.5
			ndx = (wx-self.x)/(distance+0.01)
			ndy = (wy-self.y)/(distance+0.01)
			gf = (GRAVITY_WELL_FORCE)*((1/(distance+0.01))**2)
			fdx = ndx*gf
			fdy = ndy*gf
			self.dx += fdx
			self.dy += fdy

	def animate(self, x, y, dx, dy):
		self.x = x
		self.y = y
		#self.z = random.randint(-100,100)
		self.dx = dx
		self.dy = dy
		self.color = (random.uniform(0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0))
		#self.color=(0.0,0.8,0.0)
		self.alpha = 1.0
		self.decay = 0.01
		self.decay_rate = 1.05
		self.size = (random.randint(10,40))
		self.visible = True
 

class WaveVisualisation(Visualisation):
	def __init__(self, **kwargs):
		super(WaveVisualisation, self).__init__(**kwargs)
		self.image = Image('dot.png')
		self.fg_color = (0.2,1.0,0.2)
		self.beat_count = 0

	def visualise(self, ticks):
		ad = self.stream.audio_data
		width = self.width/float(len(ad))
		ad = ad * (self.height/6.0)
		xpoints = []
		ypoints = []
		for i, y in enumerate(ad):
			xpoints.append(i*width)
			ypoints.append(y + (self.height/2))
			
		#graphx.colors.set_color(1.0,1.0,1.0)
		#graphx.draw.drawLine(points)
		
		glTexEnvf(GL_POINT_SPRITE_ARB, GL_COORD_REPLACE_ARB, GL_TRUE)
		blend = GlBlending(sfactor=GL_SRC_ALPHA, dfactor=GL_ONE)
		set_texture(self.image.texture)
		glPointSize(5)
		with DO(blend, gx_enable(self.image.texture.target), gx_enable(GL_POINT_SPRITE_ARB), gx_begin(GL_POINTS)):
			prev = 0
			points = 5
			for i in xrange(len(xpoints)-1):
				x_now = xpoints[i]
				x_next = xpoints[i+1]
				y_now = ypoints[i]
				y_next = ypoints[i+1]
				step = 2
				if y_next < y_now:
					step = -step
				y_range = arange(y_now, y_next, step)
				x_range = arange(x_now, x_next, width/(float(len(y_range))+0.001))
				for x,y in zip(x_range,y_range):
					glColor3f(*self.fg_color)
					glVertex2f(x,y)
		
		if self.stream.is_beat():
			self.beat_count += 1
			if self.beat_count == 4:
				self.fg_color = (random.random(), random.random(), random.random())
				self.beat_count = 0
			
		
				
				
				
				
				
		
			