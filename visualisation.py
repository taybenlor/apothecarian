from pymt import *
from audio_input import InputStream
import random, time, math
from OpenGL.GL import *
 
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
		spectrum = self.stream.get_audio_spectrum()
		todo = []
		if self.count > 50:
			self.count = 0
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

 
GRAVITY_WELL_FORCE = 400000
class Particle(object):
	def __init__(self):
		self.visible = False
 
	def update(self, wx, wy, gravity_wells=[]):
		self.update_velocity(gravity_wells)
		self.x += self.dx
		self.y += self.dy
		self.alpha -= 0.02
		if self.alpha <= 0.0:
			self.visible = False
		if self.x > wx or self.x < 0:
			self.visible = False
		elif self.y > wy or self.y < 0:
			self.visible = False
		
	def update_velocity(self, gravity_wells=[]):
		if not gravity_wells:
			return 
		for wx,wy in gravity_wells:
			distance = ((self.x - wx)**2 + (self.y - wy)**2)**0.5
			ndx = (wx-self.x)/(distance+0.01)
			ndy = (wy-self.y)/(distance+0.01)
			gf = GRAVITY_WELL_FORCE*((1/(distance+0.01))**2)
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
		self.alpha = 1.0
		self.size = (random.randint(10,40))
		self.visible = True
 