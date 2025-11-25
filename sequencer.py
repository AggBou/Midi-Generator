# sequencer.py
import random
import math

NOTE_KICK = 36
NOTE_SNARE = 38
NOTE_HH = 42

NOTE_MAP = {
    "k": NOTE_KICK,
    "s": NOTE_SNARE,
    "h": NOTE_HH
}

class Pattern:
    def __init__(self, steps=16):
        self.steps = steps
        self.grid = [[False]*steps for _ in range(3)]

    def to_text(self):
        rows = []
        for r in range(3):
            row = ""
            for c in range(self.steps):
                row += "ksh"[r] if self.grid[r][c] else "."
            rows.append(row)
        return rows

    def from_text(self, text_rows):
        for r, row in enumerate(text_rows):
            for c, ch in enumerate(row[:self.steps]):
                self.grid[r][c] = (ch.lower() in ["k","s","h"] and "ksh".index(ch.lower())==r)

    def toggle(self, row, col):
        self.grid[row][col] = not self.grid[row][col]

    def generate_random(self):
        for r in range(3):
            for c in range(self.steps):
                self.grid[r][c] = (random.random() < 0.25)

    def generate_fill(self):
        for r in range(3):
            for c in range(self.steps):
                self.grid[r][c] = (random.random() < (0.5 if r==1 else 0.3))

    def generate_euclidean(self, pulses, total, row):
        pattern = []
        counts = []
        remainders = []
        divisor = total - pulses
        remainders.append(pulses)
        level = 0

        while True:
            counts.append(divisor // remainders[level])
            remainders.append(divisor % remainders[level])
            divisor = remainders[level]
            level += 1
            if remainders[level] == 0:
                break

        def build(level):
            if level == -1:
                return [0]
            if level == -2:
                return [1]
            res = []
            for _ in range(counts[level]):
                res.extend(build(level-1))
            if remainders[level]:
                res.extend(build(level-2))
            return res

        pattern = build(level)
        while len(pattern) < total:
            pattern.append(0)
        pattern = pattern[:total]

        for c in range(total):
            self.grid[row][c] = (pattern[c] == 1)

    def get_events(self):
        """Return list of (note, step_index)."""
        events = []
        for r, note in enumerate([NOTE_KICK, NOTE_SNARE, NOTE_HH]):
            for c in range(self.steps):
                if self.grid[r][c]:
                    events.append((note, c))
        return events
