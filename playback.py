# playback.py
import time
import threading
import mido
import rtmidi

NOTE_KICK = 36
NOTE_SNARE = 38
NOTE_HH = 42

class MidiPlayer:
    def __init__(self):
        self.midi_out = rtmidi.MidiOut()
        ports = self.midi_out.get_ports()
        if ports:
            self.midi_out.open_port(0)
        else:
            self.midi_out.open_virtual_port("DrumSequencer")

        self.playing = False
        self.thread = None

    def send_note(self, note, vel=100):
        self.midi_out.send_message([0x99, note, vel])
        self.midi_out.send_message([0x89, note, 0])

    def play_pattern(self, pattern, bpm):
        if self.playing:
            return

        self.playing = True
        step_time = 60.0 / bpm / 4.0  # 16 steps per bar

        events = pattern.get_events()
        steps = pattern.steps

        def run():
            while self.playing:
                for step in range(steps):
                    if not self.playing:
                        break
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
