import pygame
import sounddevice as sd
import numpy as np
import pyaudio

pygame.init()

win = pygame.display.set_mode((800, 600))
image = pygame.image.load('guitar.jpg')
win.fill((255,255,255))

class button(): 
	def __init__(self, color, x, y, width, height, text=''): 
		self.color = color 
		self.x = x 
		self.y = y 
		self.width = width 
		self.height = height 
		self.text = text

	def draw(self,win,outline=None):
		if outline:
			pygame.draw.rect(win, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)

		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0) 
		if self.text != '': 
			font = pygame.font.SysFont('comicsans', 60) 
			text = font.render(self.text, 1, (0,0,0)) 
			win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

	def isOver(self, pos):
		if pos[0] > self.x and pos[0] < self.x + self.width: 
			if pos[1] > self.y and pos[1] < self.y + self.height: 
				return True
		return False

class note_window():
	def __init__(self, color, x, y, width, height, text=''):
		self.color = color
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.text = text
	def draw(self, win):
		if self.text != '':
			pygame.draw.rect(win, self.color, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)
			font = pygame.font.SysFont('comicsans', 60)
			text = font.render(self.text, 1, (0,0,0))
			win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

def readWindow():
	win.fill((255,255,255))
	win.blit(image, [0,0])
	E2_Button.draw(win, (0,0,0))
	A2_Button.draw(win, (0,0,0))
	D3_Button.draw(win, (0,0,0))
	G3_Button.draw(win, (0,0,0))
	B3_Button.draw(win, (0,0,0))
	E4_Button.draw(win, (0,0,0))
	
E2_Button = button((0,255,0), 100, 330, 100, 50, 'E2')
A2_Button = button((0,255,0), 100, 212, 100, 50, 'A2')
D3_Button = button((0,255,0), 100, 100, 100, 50, 'D3')
G3_Button = button((0,255,0), 600, 100, 100, 50, 'G3')
B3_Button = button((0,255,0), 600, 212, 100, 50, 'B3')
E4_Button = button((0,255,0), 600, 330, 100, 50, 'E4')

NOTE_MIN = 40       # E2
NOTE_MAX = 64       # E4
FSAMP = 44100       # Sampling frequency in Hz
FRAME_SIZE = 2048   # samples per frame
FRAMES_PER_FFT = 16 

SAMPLES_PER_FFT = FRAME_SIZE * FRAMES_PER_FFT
FREQ_STEP = float(FSAMP) / SAMPLES_PER_FFT

NOTE_NAMES = 'E F F# G G# A A# B C C# D D#'.split()

def freq_to_number(f): 
    return 64 + 12 * np.log2(f / 329.63)

def number_to_freq(n): 
    return 329.63 * 2.0**((n - 64) / 12.0)

def note_name(n):
    return NOTE_NAMES[n % NOTE_MIN % len(NOTE_NAMES)] + str(int(n / 12 - 1))

def note_to_fftbin(n): 
    return number_to_freq(n) / FREQ_STEP

imin = max(0, int(np.floor(note_to_fftbin(NOTE_MIN - 1))))
imax = min(SAMPLES_PER_FFT, int(np.ceil(note_to_fftbin(NOTE_MAX + 1))))

buf = np.zeros(SAMPLES_PER_FFT, dtype=np.float32)
num_frames = 0

stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=FSAMP, input=True, frames_per_buffer=FRAME_SIZE)
stream.start_stream()

window = 0.5 * (1 - np.cos(np.linspace(0, 2 * np.pi, SAMPLES_PER_FFT, False)))

while stream.is_active():
	buf[:-FRAME_SIZE] = buf[FRAME_SIZE:]
	buf[-FRAME_SIZE:] = np.fromstring(stream.read(FRAME_SIZE), np.int16)
	fft = np.fft.rfft(buf * window)
	freq = (np.abs(fft[imin:imax]).argmax() + imin) * FREQ_STEP
	n = freq_to_number(freq)
	n0 = int(round(n))
	num_frames += 1
	if num_frames >= FRAMES_PER_FFT:
		print('number {:7.2f}     freq: {:7.2f} Hz     note: {:>3s} {:+.2f}'.format(n, freq, note_name(n0), n - n0))
	readWindow()
	pygame.display.update()
	note = note_window((0,255,0), 350, 50, 100, 50, note_name(n0))
	note.draw(win)
	pygame.display.update()
	for event in pygame.event.get():
		pos = pygame.mouse.get_pos()
		if event.type == pygame.QUIT:
			run = False
			pygame.quit()
			quit()
		if event.type == pygame.MOUSEBUTTONDOWN:
			if E2_Button.isOver(pos):
				sd.play(2.0*np.sin(2*np.pi*82.41*np.arange(44100)/44100), samplerate=44100, blocking=True)
				print("E2 Button clicked")
			elif A2_Button.isOver(pos):
				sd.play(2.0*np.sin(2*np.pi*110.00*np.arange(44100)/44100), samplerate=44100, blocking=True)
				print("A2 Button clicked")
			elif D3_Button.isOver(pos):
				sd.play(2.0*np.sin(2*np.pi*146.83*np.arange(44100)/44100), samplerate=44100, blocking=True)
				print("D3 Button clicked")
			elif G3_Button.isOver(pos):
				sd.play(2.0*np.sin(2*np.pi*196.00*np.arange(44100)/44100), samplerate=44100, blocking=True)
				print("G3 Button clicked")
			elif B3_Button.isOver(pos):
				sd.play(2.0*np.sin(2*np.pi*246.94*np.arange(44100)/44100), samplerate=44100, blocking=True)
				print("B3 Button clicked")
			elif E4_Button.isOver(pos):
				sd.play(2.0*np.sin(2*np.pi*329.63*np.arange(44100)/44100), samplerate=44100, blocking=True)
				print("E4 Button clicked")
		if event.type == pygame.MOUSEMOTION:
			if E2_Button.isOver(pos):
				E2_Button.color = (255,0,0)
			elif A2_Button.isOver(pos):
				A2_Button.color = (255,0,0)
			elif D3_Button.isOver(pos):
				D3_Button.color = (255,0,0)
			elif G3_Button.isOver(pos):
				G3_Button.color = (255,0,0)
			elif B3_Button.isOver(pos):
				B3_Button.color = (255,0,0)
			elif E4_Button.isOver(pos):
				E4_Button.color = (255,0,0)
			else:
				E2_Button.color = (0,204,204)
				A2_Button.color = (0,204,204)
				D3_Button.color = (0,204,204)
				G3_Button.color = (0,204,204)
				B3_Button.color = (0,204,204)
				E4_Button.color = (0,204,204)