from pymt import *
from audio_input import InputStream
import random, time, math

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
		
class BasicVisualisation(Visualisation):
	def __init__(self, **kwargs):
		super(BasicVisualisation, self).__init__(**kwargs)
		self.bg_color = (0.0, 0.0, 0.0)
	
	def visualise(self, ticks):
		#draw the background		
		graphx.colors.set_color(*self.bg_color)
		graphx.draw.drawRectangle((0,0), (self.width, self.height))
		
		#get our visualisation values
		val = self.stream.get_average_energy() # 0.0 -> 1.0
		spectrum = self.stream.get_audio_spectrum() # array of floats (each value is contribution, takes optional number of buckets)
		
		#draw the foreground
		graphx.colors.set_color(1.0,1.0,1.0)
		#circle in the middle of the widget with radius val* (1/3 of screen) means circle can only be as bit as 2/3rds screen
		graphx.draw.drawCircle(self.center, val * (self.width/3))
		
		#draw points evenly across the screen
		points = []
		x_mul = self.width/len(spectrum)
		for i, item in enumerate(spectrum):
			points.append(i*x_mul) #x coordinate of point
			points.append(item*150) #y coordinate of point (ie height = spectrum contribution)
		graphx.draw.drawLine(points)
		
		#if its a beat randomly change the background colour
		if self.stream.is_beat():
			self.bg_color = (random.random(), random.random(), random.random())
		
class CircleVisualisation(Visualisation):
	def __init__(self, **kwargs):
		super(CircleVisualisation, self).__init__(**kwargs)
		self.fg_color = (1.0, 1.0, 1.0)
		
	def visualise(self, ticks):
		graphx.colors.set_color(0.0,0.0,0.0)
		graphx.draw.drawRectangle((self.x,self.y), (self.width, self.height))
		
		graphx.colors.set_color(*self.fg_color)
		val = self.stream.get_average_energy() * (self.width/3)
		graphx.draw.drawCircle(self.center, val)
		
		#arrange the points around in a circle
		cx, cy = self.center
		length = val
		angle = 0
		spectrum = self.stream.get_audio_spectrum()
		points = []
		for d in spectrum:
			lx = ((d * 75) +val) * math.cos(angle)
			ly = ((d * 75)+val) * math.sin(angle)

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
	def __init__(self, **kwargs):
		super(ParticleVisualisation, self).__init__(**kwargs)
		self.particles = {}
		self.uid = 0
		
	def visualise(self, ticks):
		graphx.colors.set_color(0.0, 0.0, 0.0)
		graphx.draw.drawRectangle((self.x,self.y), (self.width, self.height))
		
		cx, cy = self.center
		angle = 0
		spectrum = self.stream.get_audio_spectrum()

		if len(self.particles) < PARTICLE_LIMIT:
			for d in spectrum:
				count = int(round(d))
			
				dx = math.cos(angle)
				dy = math.sin(angle)

				x = cx + random.randint(-10, 10)
				y = cy + random.randint(-10, 10)
			
				dx *= 20
				dy *= 20
			
				#for i in xrange(count):
				if count > 1:
					self.particles[self.uid] = Particle(x, y, dx, dy)
					self.uid += 1
			
				angle += math.pi*2/(len(spectrum))
			
		for p in self.particles.keys():
			self.particles[p].draw()
			self.particles[p].update()
			x, y = self.particles[p].x, self.particles[p].y
			if x < 0 or y < 0 or x > self.width or y > self.height:
				self.particles.pop(p)
				

class Particle(object):
	def __init__(self, x, y, dx, dy, color=None, radius=None):
		self.color = color
		if self.color == None:
			self.color = (random.random(), random.random(), random.random())
		
		self.radius = radius
		if self.radius == None:
			self.radius = random.randint(1,10)
		
		self.x = x
		self.y = y
		self.dx = dx
		self.dy = dy
		self.alive = 0

	def update(self):
		self.x += self.dx
		self.y += self.dy
		self.alive += 1

	def draw(self):
		graphx.colors.set_color(*self.color)
		graphx.draw.drawCircle((int(self.x), int(self.y)), self.radius)
