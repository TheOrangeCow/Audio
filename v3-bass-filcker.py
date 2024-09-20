import pyaudio
import numpy as np
import tkinter as tk

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

root = tk.Tk()
root.title("Audio Bass and Treble Visualization")

canvas = tk.Canvas(root, width=800, height=600, bg='black')
canvas.pack()

particles = []

class Particle:
    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.size = size
        self.speedX = np.random.rand() * 2 - 1
        self.speedY = np.random.rand() * 2 - 1
        self.color = color
        self.original_color = color

    def update(self, treble_intensity, flicker_threshold):
        self.x += self.speedX
        self.y += self.speedY
        if self.size > 0.2:
            self.size -= 0.1
        
        if treble_intensity > flicker_threshold:
            intensity_factor = 1 + (treble_intensity - flicker_threshold) / 1000
            r = int(int(self.original_color[1:3], 16) * intensity_factor) % 255
            g = int(int(self.original_color[3:5], 16) * intensity_factor) % 255
            b = int(int(self.original_color[5:7], 16) * intensity_factor) % 255
            self.color = "#{:02x}{:02x}{:02x}".format(r, g, b)
        else:
            self.color = self.original_color

    def draw(self):
        canvas.create_oval(self.x - self.size, self.y - self.size, self.x + self.size, self.y + self.size,
                           fill=self.color, outline=self.color)

def update():
    global particles
    data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
    
    fft_data = np.fft.fft(data)
    fft_freqs = np.fft.fftfreq(len(fft_data), 1 / RATE)
    
    bass_freqs = (fft_freqs >= 20) & (fft_freqs <= 200)
    bass_amplitude = np.abs(fft_data[bass_freqs])
    bass_level = np.sum(bass_amplitude)
    
    treble_freqs = (fft_freqs >= 2000) & (fft_freqs <= 20000)
    treble_amplitude = np.abs(fft_data[treble_freqs])
    treble_level = np.sum(treble_amplitude)
    
    flicker_threshold = 1000  # Treble threshold for flickering
    particle_size = min(bass_level / 500000, 50)
    num_particles = max(1, int(bass_level / 1000000))
    
    if bass_level > 100000:
        for _ in range(num_particles):
            color = "#{:02x}{:02x}{:02x}".format(int(np.random.rand() * 255), int(np.random.rand() * 255), int(np.random.rand() * 255))
            particles.append(Particle(np.random.rand() * 800, np.random.rand() * 600, particle_size, color))
    
    canvas.delete("all")
    
    for particle in particles:
        particle.update(treble_level, flicker_threshold)
        particle.draw()
        if particle.size <= 0.2:
            particles.remove(particle)
    
    root.after(50, update)

update()
root.mainloop()

stream.stop_stream()
stream.close()
audio.terminate()
