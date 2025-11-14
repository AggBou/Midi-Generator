# playback.py (WAV enabled)
import time
import threading
from PyQt5.QtMultimedia import QSound
import os

NOTE_KICK = 36
NOTE_SNARE = 38
NOTE_HH = 42

SOUND_MAP = {
    NOTE_KICK: "sounds/kick.wav",
    NOTE_SNARE: "sounds/snare.wav",
    NOTE_HH: "sounds/hihat.wav"
}

class MidiPlayer:
    def __init__(self):
        self.playing = False
        self.thread = None

    def send_note(self, note):
        path = SOUND_MAP.get(note)
        if path and os.path.exists(path):
            QSound.play(path)

    def play_pattern(self, pattern, bpm):
        if self.playing:
            return

        self.playing = True
        step_time = 60.0 / bpm / 4.0  # 16 steps per bar
        steps = pattern.steps
        events = pattern.get_events()

        def run():
            while self.playing:
                for step in range(steps):
                    if not self.playing:
                        break
                    # Play all notes in this step
                    for note, c in events:
                        if c == step:
                            self.send_note(note)
                    time.sleep(step_time)

        self.thread = threading.Thread(target=run)
        self.thread.start()

    def stop(self):
        self.playing = False
        if self.thread:
            self.thread.join()
            self.thread = None
