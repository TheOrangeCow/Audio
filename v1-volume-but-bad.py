import pyaudio
import numpy as np
import tkinter as tk
from PIL import Image, ImageDraw

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Initialize PyAudio
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

# Initialize tkinter
root = tk.Tk()
root.title("Audio Visualization")

canvas = tk.Canvas(root, width=800, height=400, bg='black')
canvas.pack()

particles = []

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = np.random.rand() * 5 + 1
        self.speedX = np.random.rand() * 3 - 1.5
        self.speedY = np.random.rand() * 3 - 1.5
        self.color = "#{:02x}{:02x}{:02x}".format(int(np.random.rand()*255), int(np.random.rand()*255), int(np.random.rand()*255))

    def update(self):
        self.x += self.speedX
        self.y += self.speedY
        if self.size > 0.2:
            self.size -= 0.1

    def draw(self):
        canvas.create_oval(self.x - self.size, self.y - self.size, self.x + self.size, self.y + self.size,
                           fill=self.color, outline=self.color)

def update():
    global particles
    data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
    
    max_val = np.max(np.abs(data))
    if max_val > 1000:
        for _ in range(5):
            particles.append(Particle(np.random.rand() * 800, np.random.rand() * 400))
    
    canvas.delete("all")
    for particle in particles:
        particle.update()
        particle.draw()
        if particle.size <= 0.2:
            particles.remove(particle)
    
    root.after(50, update)

update()
root.mainloop()

# Clean up
stream.stop_stream()
stream.close()
audio.terminate()
