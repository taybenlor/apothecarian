import pyaudio
import sys
import audioop
from numpy import zeros, linspace, short, fromstring, hstack, transpose, mean, absolute, max, median
from numpy import fft, concatenate, array
fft = fft.fft
from threading import Thread
import random, time, math
 
class InputStream(Thread):
	FORMAT = pyaudio.paInt16
	SPECTROGRAM_LENGTH = 100
	NUM_SAMPLES = 1024
	SAMPLING_RATE = 11025
	SPECTROGRAM_LENGTH = 100
	def __init__(self, **kwargs):
		super(InputStream, self).__init__(**kwargs)
		self.audio_data = None
		self.history = None
		self.closed = False
		self.beat = False
		self.beats = []
		self.max = -1
		self.last = time.time()
		self.last_beat = time.time()
		self.last_avg = -1
		self.legit_bpm = 0
		self.iscand = False
		self.next_beats = []
		self.expected_dist = -1
		self.max_bucket = 0
		self.max_normal_bucket = 0
		self.max_ben = 0
 
	def is_a_beat(self, samples, time_offset):
		avg = mean(absolute(samples))
		if (avg > self.max):
			self.max = avg
 
 
		self.max = self.max * 0.9997
 
		isa_beat = False
 
 
		if (avg < self.last_avg and self.last_avg > (self.max * 0.85) and self.iscand):
			isa_beat = True
			self.iscand = False
			self.candidates.append((avg, time_offset))
 
			#now = time.time() - time_offset
			#dist = now - self.last_beat
			#self.last_beat = now
			#self.beats.append(dist)
			#print (1/median(self.beats))*60
 
		else:
			if (avg > self.last_avg):
				self.iscand = True
			else:
				self.iscand = False
 
 
		self.last_avg = avg
		return isa_beat
 
	def run(self):
		pa = pyaudio.PyAudio()
		stream = pa.open(format=pyaudio.paInt16, channels=1,
						  rate=InputStream.SAMPLING_RATE,
						  input=True, frames_per_buffer=InputStream.NUM_SAMPLES)
 
		while not self.closed:
 
			self.audio_data = fromstring(stream.read(InputStream.NUM_SAMPLES), dtype=short)/32768.0
			now = time.time()
			dist = now - self.last			
			self.last = now
 
			self.candidates = []
 
			sample_divisor = 8
			for i in xrange(0,sample_divisor):
				cur = self.audio_data[i * (1024/sample_divisor):((i+1)*(1024/sample_divisor))-1]
				avg = mean(absolute(cur))
				#for j in xrange(0, int(avg*100)):
				#	print  "*",
				#print  ""
				if (self.is_a_beat(cur, (dist/sample_divisor) * (sample_divisor-i))):
					pass
			local_max = -1
			local_offset = -1
 
			for each in self.candidates:
				if (each[0] > local_max):
					local_max = each[0]
					local_offset = each[1]
 
			self.expected_dist = median(self.beats)
 
			if (local_max != -1):
				now = time.time() - local_offset
				dist = now - self.last_beat
				self.last_beat = now
				self.beats.append(dist)
				# If this is a good beat
				if (abs(dist - self.expected_dist) < 0.04):
					self.next_beats = []
					self.next_beats.append(now + self.expected_dist)
 
 
			energy = self.get_average_energy()
 
 
			if self.history != None:
				#print self.history
				self.history = concatenate((self.history, [absolute(energy)]))
				if len(self.history) > InputStream.NUM_SAMPLES * 120:
					self.history = self.history[(len(self.history) - (InputStream.NUM_SAMPLES * 120)):]
			else:
				self.history = [absolute(energy)]
 
			if len(self.beats) > 100:
				self.beats = self.beats[10:]			
			#hist = mean(self.history)
 
			bpm = self.get_bpm()
 
 
 
			p_bpm = 80
			if len(self.beats) >=10:
				p_bpm = 2/((now - self.beats[-1])/60)
 
			#if self.get_average_energy() > 1.3*hist:
			#if self.get_average_energy() > (0.75 * self.max):
			#	self.beat = True
			#	self.beats.append(dist)
 
			#print self.beats
 
 
		stream.close()
 
	def close(self):
		self.closed = True
 
	def get_bpm(self):
		return -1
 
	def get_audio_spectrum(self, buckets=100):
		if self.audio_data == None:
			return [0]*buckets
		return abs(fft(self.audio_data, 2*buckets))[:buckets]
		
	def get_normal_audio_spectrum(self, buckets=10):
		fft_data = self.get_audio_spectrum(buckets)
		self.max_normal_bucket -= 0.001
		self.max_normal_bucket = max([self.max_normal_bucket, max(fft_data)])
		return fft_data/(self.max_normal_bucket+0.01)
	
	#normalised audio spectrum between 0.0 and 1.0 each bucket contains twice as many frequency buckets as the previous as per the way the ear works
	def get_log_audio_spectrum(self, buckets=7):
		fft_data = self.get_audio_spectrum((2**buckets)-(buckets+1))
		log_fft_data = []
		low = 1
		high = 2
		for i in xrange(buckets):
			log_fft_data.append(sum(fft_data[(low):(high)]))
			low = high + 1
			high *= 2
			high += 1
		
		self.max_bucket -= 0.01
		self.max_bucket = max([self.max_bucket, max(log_fft_data)])
		return array(log_fft_data)/(self.max_bucket+0.001)
		
	

	def get_average_energy(self):
		if self.audio_data == None:
			return 0
		return mean(absolute(self.audio_data))
 
	def is_beat(self):
		if (len(self.next_beats) == 0):
			return False
		if (time.time() > (self.next_beats[0]-0.10)):
			last = self.next_beats[0]
			self.next_beats = self.next_beats[1:]
			if (len(self.next_beats) == 0):
				self.next_beats.append(last + self.expected_dist)
			return True
		else:
			return False