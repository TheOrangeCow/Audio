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
root.title("Audio Visualization")

canvas = tk.Canvas(root, width=800, height=600, bg='black')
canvas.pack()

particles = []

class Particle:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.speedX = np.random.rand() * 2 - 1
        self.speedY = np.random.rand() * 2 - 1
        self.color = "#{:02x}{:02x}{:02x}".format(int(np.random.rand() * 255), int(np.random.rand() * 255), int(np.random.rand() * 255))

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
    fft_data = np.fft.fft(data)
    fft_freqs = np.fft.fftfreq(len(fft_data), 1 / RATE)

    low_freqs = (fft_freqs >= 20) & (fft_freqs <= 200)
    mid_freqs = (fft_freqs > 200) & (fft_freqs <= 2000)
    high_freqs = (fft_freqs > 2000) & (fft_freqs <= 5000)

    low_amplitude = np.sum(np.abs(fft_data[low_freqs]))
    mid_amplitude = np.sum(np.abs(fft_data[mid_freqs]))
    high_amplitude = np.sum(np.abs(fft_data[high_freqs]))

    total_amplitude = low_amplitude + mid_amplitude + high_amplitude
    num_particles = max(1, int(total_amplitude / 1000000))

    fft_data = np.fft.fft(data)
    fft_freqs = np.fft.fftfreq(len(fft_data), 1 / RATE)
    
    # Focus on bass frequencies (e.g., 20 to 200 Hz)
    bass_freqs = (fft_freqs >= 15) & (fft_freqs <= 200)
    bass_amplitude = np.abs(fft_data[bass_freqs])
    bass_level = np.sum(bass_amplitude)
    
    # Scale particle size and number based on bass level
    particle_size = min(bass_level / 500000, 500)  # Adjust scaling as needed

    if total_amplitude > 100000:
        for _ in range(num_particles):
            particles.append(Particle(np.random.rand() * 800, np.random.rand() * 600, particle_size))

    canvas.delete("all")
    
    for particle in particles:
        particle.update()
        particle.draw()
        if particle.size <= 0.2:
            particles.remove(particle)
    
    root.after(50, update)

update()
root.mainloop()

stream.stop_stream()
stream.close()
audio.terminate()
