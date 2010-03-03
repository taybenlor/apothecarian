from __future__ import division
from VideoCapture import Device
import Image
from time import sleep
import gareth
from threading import Thread
import colorsys


class InImage:
		def __init__(self, filename):
				self.inim = Image.open(filename)
				self.nx,self.ny = self.inim.size
				self.inmat = self.inim.load()
		def __getitem__(self, (x, y)):
				return self.inmat[x % self.nx, y % self.ny]
		def all_coords(self):
				for y in xrange(self.ny):
						for x in xrange(self.nx):
								yield x, y

class OutImage:
		def __init__(self, in_image):
				self.nx,self.ny = in_image.nx, in_image.ny
				self.outim = in_image.inim.copy()
				self.outmat = self.outim.load()
		def __setitem__(self, (x, y), value):
				self.outmat[x % self.nx, y % self.ny] = value
		def save(self, filename, *args, **kwds):
				self.outim.save(filename, *args, **kwds)



class TouchStream(Thread):
	def __init__(self, **kwargs):
		super(TouchStream, self).__init__(**kwargs)
		self.cam1 = Device(devnum=0)
		self.cam2 = Device(devnum=1)

		# For using a different filename each time... not needed for now
		self.count = 0

		self.return_lines = []
		
	
		
		
	def run(self):
	
		avgs1 = []
		avgs2 = []
		
		for i in xrange(0,640):
			avgs1.append((0,0,0))
			avgs2.append((0,0,0))
		
		startdone = 0
		
		while 1:
			self.count += 1
			self.cam2.saveSnapshot('temp/image' + str(self.count) + '.jpg', timestamp=3, boldfont=1)
			self.cam1.saveSnapshot('temp/2image' + str(self.count) + '.jpg', timestamp=3, boldfont=1)
			
			img1 = InImage("temp/image" + str(self.count) + ".jpg")
			img2 = InImage("temp/2image" + str(self.count) + ".jpg")

			red1 = 0
			green1 = 0
			blue1 = 0
			
			red2 = 0
			green2 = 0
			blue2 = 0

			row = 100
			row2 = 100


			lines = gareth.generate_lines(100,100,100, img1.nx)
			lines2 = gareth.generate_lines(100,100,100, img1.nx)
			
			touch_lines = []
			
			for x in xrange(0,(img1.nx/2)):
				for y in xrange(row,row+1):
					red1 += img1[x,y][0]
					green1 += img1[x,y][1]
					blue1 += img1[x,y][2]
			for x in xrange((img1.nx/2), img1.nx):
				for y in xrange(row,row+1):
					red2 += img1[x,y][0]
					green2 += img1[x,y][1]
					blue2 += img1[x,y][2]
					
			red1 /= (img1.nx/2)
			green1 /= (img1.nx/2)
			blue1  /= (img1.nx/2)
			
			red2 /= (img1.nx/2)
			green2 /= (img1.nx/2)
			blue2  /= (img1.nx/2)

			
			smallest = 10000
			biggest = -1
			
			found = False
			

			for x in xrange(0,img1.nx):
				if x > (img1.nx / 2):
					red = red2
					blue = blue2
					green = green2
				else:
					red = red1
					blue = blue1
					green = green1
				reda = avgs1[x][0]
				greena = avgs1[x][1]
				bluea = avgs1[x][2]
				for y in xrange(row,row+1):
					ored,ogreen,oblue = img1[x,y]
					diff = abs(ored - reda) + abs(ogreen - greena) + abs(oblue - bluea)
					found = False
					
					hue, sat, var = colorsys.rgb_to_hsv(red, green, blue)
					hue2, sat2, var2 = colorsys.rgb_to_hsv(ored, ogreen, oblue)
					
					
					a,b,c = colorsys.rgb_to_yiq(red, green, blue)
					a1,b1,c1 = colorsys.rgb_to_yiq(ored, ogreen, oblue)
					
					diff = abs(hue - hue2) + abs(sat - sat2) + abs(var - var2)
					diff += abs(a - a1) + abs(b - b1) + abs(c - 1)
					
					if (diff > (100 + (abs(x - (img1.nx / 2)) / 600))):
						found = True
					#if (diff > 80):
					
					#	found = True
					diff = abs(ored - red) + abs(ogreen - green) + abs(oblue - blue)
					if (found and (diff > (65 + (abs(x - (img1.nx / 2)) / 600)))):
						touch_lines.append(((0,-100), lines[img1.nx - 1 - x]))
					else:
						avgs1[x] = (ored, ogreen,oblue)

							
			startdone += 1
						

			red1 = 0
			green1 = 0
			blue1 = 0
			
			red2 = 0
			green2 = 0
			blue2 = 0						
					
			for x in xrange(0,(img2.nx/2)):
				for y in xrange(row2,row2+1):
					red1 += img2[x,y][0]
					green1 += img2[x,y][1]
					blue1 += img2[x,y][2]
			for x in xrange((img2.nx/2), img2.nx):
				for y in xrange(row2,row2+1):
					red2 += img2[x,y][0]
					green2 += img2[x,y][1]
					blue2 += img2[x,y][2]
					
					

					
			red1 /= (img2.nx/2)
			green1 /= (img2.nx/2)
			blue1  /= (img2.nx/2)
			
			red2 /= (img2.nx/2)
			green2 /= (img2.nx/2)
			blue2  /= (img2.nx/2)

			print red,green,blue

			for x in xrange(0,img2.nx):
				if x > (img2.nx / 2):
					red = red2
					blue = blue2
					green = green2
				else:
					red = red1
					blue = blue1
					green = green1
				reda = avgs2[x][0]
				greena = avgs2[x][1]
				bluea = avgs2[x][2]
				for y in xrange(row2,row2+1):
					ored,ogreen,oblue = img2[x,y]
					diff = abs(ored - reda) + abs(ogreen - greena) + abs(oblue - bluea)
					found = False
					
					hue, sat, var = colorsys.rgb_to_hsv(red, green, blue)
					hue2, sat2, var2 = colorsys.rgb_to_hsv(ored, ogreen, oblue)
					
					
					a,b,c = colorsys.rgb_to_yiq(red, green, blue)
					a1,b1,c1 = colorsys.rgb_to_yiq(ored, ogreen, oblue)
					
					diff = abs(hue - hue2) + abs(sat - sat2) + abs(var - var2)
					diff += abs(a - a1) + abs(b - b1) + abs(c - 1)
					
					if (diff > (100 + (abs(x - (img2.nx / 2)) / 500))):
						found = True
					#if (diff > 80):
					#	found = True
					diff = abs(ored - red) + abs(ogreen - green) + abs(oblue - blue)
					if (found and (diff > (65 + (abs(x - (img2.nx / 2)) / 500)))):
						touch_lines.append(((100,-100), (100 - lines[x][0], lines[x][1])))	
					else:
						avgs2[x] = (ored, ogreen,oblue)
						
								
			
						
			self.return_lines = touch_lines

			
			#print str(num_diff), str(smallest), str(biggest)
		
	def isTouch(self):
		return self.return_lines
