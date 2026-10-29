import sys, numpy as np, sounddevice as sd, soundfile as sf
from pynput import keyboard

DEVICE = sys.argv[1] if len(sys.argv) > 1 else None  # es. "MacBook Pro Speakers"
data, sr = sf.read("click.wav", dtype="float32")
if data.ndim == 1:
    data = np.stack([data, data], axis=1)

playing = []  # posizioni di riproduzione attive (permette click sovrapposti)

def callback(out, frames, t, status):
    out[:] = 0
    for p in playing[:]:
        chunk = data[p[0]:p[0] + frames]
        out[:len(chunk)] += chunk
        p[0] += frames
        if p[0] >= len(data):
            playing.remove(p)
    np.clip(out, -1, 1, out=out)

down = set()
def on_press(key):
    if key not in down:          # ignora l'auto-repeat
        down.add(key)
        playing.append([0])
def on_release(key):
    down.discard(key)

with sd.OutputStream(samplerate=sr, channels=2, device=DEVICE,
                     callback=callback, latency="low"):
    with keyboard.Listener(on_press=on_press, on_release=on_release) as l:
        l.join()
