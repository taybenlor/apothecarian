from __future__ import division

from pymt import *
from audio_input import InputStream
import random, time, math
import sys
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk as pm
from touch import TouchStream
import gareth

def add_ball(space):
    mass = 1
    radius = 14
    inertia = pm.moment_for_circle(mass, 0, radius, (0,0)) # 1
    body = pm.Body(mass, inertia) # 2
    x = random.randint(100,600)
    body.position = x, 150 # 3
    shape = pm.Circle(body, radius, (0,0)) # 4
    space.add(body, shape) # 5
    return shape

def add_static_L(space, x1, y1, x2, y2):
    body = pm.Body(pm.inf, pm.inf) # 1
    body.position = (300,300)    
    l1 = pm.Segment(body, (x1, y1), (x2, y2), 5.0) # 2
            
    space.add(l1)
    return l1
	
	
def to_pygame(p):
    """Small hack to convert pymunk to pygame coordinates"""
    return int(p.x), int(-p.y+600)
    
    
    
def to_pygame(p):
    """Small hack to convert pymunk to pygame coordinates"""
    return int(p.x), int(-p.y+600)
	
def draw_lines(lines):
	for line in lines:
		body = line.body
		pv1 = body.position + line.a.rotated(math.degrees(body.angle)) # 1
		pv2 = body.position + line.b.rotated(math.degrees(body.angle))
		p1 = to_pygame(pv1) # 2
		p2 = to_pygame(pv2)
		#print [p1[0], p1[1], p2[0], p2[1]]
		graphx.colors.set_color((1.0, 1.0, 1.0))
		graphx.draw.drawLine([p1[0], p1[1], p2[0], p2[1]], 5)

def draw_line(line):
	graphx.draw.drawLine([line[0][0], line[0][1] + 200, line[1][0], line[1][1] + 200], 1)

	
def draw_ball(ball):
    p = int(ball.body.position.x), 600-int(ball.body.position.y)
    graphx.draw.drawCircle(p, int(ball.radius))
 
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
 
class TouchVisualisation(Visualisation):
	def __init__(self, **kwargs):
		super(TouchVisualisation, self).__init__(**kwargs)
		self.touch = TouchStream()
		self.touch.start()
		
	def visualise(self, ticks):
		graphx.colors.set_color(0.0,0.0,0.0)
		graphx.draw.drawRectangle((self.x,self.y), (self.width, self.height))
		self.fg_color = (1.0, 1.0, 1.0)
		graphx.colors.set_color(*self.fg_color)
		val = 100
		
		touches = self.touch.isTouch()
		
		if (len(touches) > 0):
			for each in touches:
				draw_line(each)
				
		int_points = []		
				
		for each1 in touches:
			for each2 in touches:
				ret =  gareth.line_intersection(each1[0][0], each1[0][1], each1[1][0], each1[1][1], each2[0][0], each2[0][1], each2[1][0], each2[1][1])
				if (len(ret) > 1):
					int_points.append((ret[0], ret[1]))
				
		for each in int_points:
			graphx.draw.drawCircle((each[0], each[1] + 200), 5)
				
			#graphx.draw.drawCircle(self.center, len(touches))
		
class CircleVisualisation(Visualisation):
	def __init__(self, **kwargs):
		super(CircleVisualisation, self).__init__(**kwargs)
		self.fg_color = (1.0, 1.0, 1.0)

		pm.init_pymunk()
		self.space = pm.Space()
		self.space.gravity = (0.0, 900.0)
		
		self.lines = []
		for j in xrange(0,5):
			for i in xrange(0,10):
				x1 = -200 + i * 80
				y1 = j * 100
				x2 = x1 + random.randint(-60,60)
				y2 = y1 + random.randint(-60,60)
				self.lines.append(add_static_L(self.space, x1, y1, x2, y2))
		self.balls = []
		self.off = False
 
	def visualise(self, ticks):
	
	
	
		graphx.colors.set_color(0.0,0.0,0.0)
		graphx.draw.drawRectangle((self.x,self.y), (self.width, self.height))
		graphx.colors.set_color(*self.fg_color)
		
		# First print the lines
		draw_lines(self.lines)
		
		balls_to_remove = []

		# Print the balls, and at the same time, remove those out of the screen
		for ball in self.balls:
			draw_ball(ball)
			if ball.body.position.y > 700: # 1
				balls_to_remove.append(ball) # 2
				
		for ball in balls_to_remove:
			self.space.remove(ball, ball.body) # 3
			self.balls.remove(ball) # 4
	
 
		#if its a beat change the fg colour and add more balls
		if self.stream.is_beat():
			if (self.off):
				for i in xrange(0,5):
					ball_shape = add_ball(self.space)
					self.balls.append(ball_shape)
				self.fg_color = (random.random(), random.random(), random.random())
			self.off = not self.off
			
		self.space.step(ticks/1000)
