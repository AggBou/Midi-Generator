# gui.py
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QGridLayout, QTextEdit, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from sequencer import Pattern
from playback import MidiPlayer
from midi_export import export_pattern
from presets import save_presets, load_presets
import os

class DrumGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drum Sequencer")
        self.patterns = []
        self.current_pattern = Pattern(16)
        self.patterns.append(self.current_pattern)
        self.bpm = 120
        self.player = MidiPlayer()
        self.steps_options = [16, 32, 64]
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # LEFT: Tools / Presets
        self.step_selector = QComboBox()
        for s in self.steps_options:
            self.step_selector.addItem(str(s))
        self.step_selector.currentIndexChanged.connect(self.change_steps)
        left_layout.addWidget(QLabel("Steps per pattern:"))
        left_layout.addWidget(self.step_selector)

        self.bpm_selector = QComboBox()
        for bpm in range(60, 201, 10):
            self.bpm_selector.addItem(str(bpm))
        self.bpm_selector.setCurrentText(str(self.bpm))
        self.bpm_selector.currentIndexChanged.connect(self.change_bpm)
        left_layout.addWidget(QLabel("BPM:"))
        left_layout.addWidget(self.bpm_selector)

        btn_random = QPushButton("Random Pattern")
        btn_random.clicked.connect(self.random_pattern)
        left_layout.addWidget(btn_random)

        btn_euclidean = QPushButton("Euclidean Kick")
        btn_euclidean.clicked.connect(self.euclidean_pattern)
        left_layout.addWidget(btn_euclidean)

        btn_fill = QPushButton("Generate Fill")
        btn_fill.clicked.connect(self.generate_fill)
        left_layout.addWidget(btn_fill)

        btn_save = QPushButton("Save Presets")
        btn_save.clicked.connect(self.save_presets)
        left_layout.addWidget(btn_save)

        btn_load = QPushButton("Load Presets")
        btn_load.clicked.connect(self.load_presets)
        left_layout.addWidget(btn_load)

        left_layout.addStretch()
        main_layout.addLayout(left_layout)

        # RIGHT: Step grid + text
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_widget.setLayout(self.grid_layout)
        right_layout.addWidget(self.grid_widget)

        self.text_edit = QTextEdit()
        self.text_edit.setFixedHeight(80)
        right_layout.addWidget(QLabel("Pattern Text (k=s/h):"))
        right_layout.addWidget(self.text_edit)

        btn_update_text = QPushButton("Update Grid from Text")
        btn_update_text.clicked.connect(self.update_grid_from_text)
        right_layout.addWidget(btn_update_text)

        # Playback controls
        btn_play = QPushButton("Play")
        btn_play.clicked.connect(self.play_pattern)
        btn_stop = QPushButton("Stop")
        btn_stop.clicked.connect(self.stop_pattern)
        btn_export = QPushButton("Export MIDI")
        btn_export.clicked.connect(self.export_midi)

        pb_layout = QHBoxLayout()
        pb_layout.addWidget(btn_play)
        pb_layout.addWidget(btn_stop)
        pb_layout.addWidget(btn_export)
        right_layout.addLayout(pb_layout)

        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

        self.update_grid()

    def update_grid(self):
        # Clear existing
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)

        self.buttons = []
        rows = ["Kick", "Snare", "Hi-hat"]
        for r in range(3):
            row_buttons = []
            for c in range(self.current_pattern.steps):
                btn = QPushButton(".")
                btn.setCheckable(True)
                btn.setFixedSize(40, 40)
                btn.setStyleSheet("background-color: lightgray;")
                btn.setChecked(self.current_pattern.grid[r][c])
                btn.clicked.connect(lambda _, x=r, y=c: self.toggle_step(x, y))
                self.grid_layout.addWidget(btn, r, c)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

        # Update text edit
        text_rows = self.current_pattern.to_text()
        self.text_edit.setText("\n".join(text_rows))

    def toggle_step(self, r, c):
        self.current_pattern.toggle(r, c)
        self.update_grid()

    def update_grid_from_text(self):
        text = self.text_edit.toPlainText().splitlines()
        self.current_pattern.from_text(text)
        self.update_grid()

    def change_steps(self, index):
        steps = self.steps_options[index]
        self.current_pattern.steps = steps
        self.current_pattern.grid = [[False]*steps for _ in range(3)]
        self.update_grid()

    def change_bpm(self, index):
        self.bpm = int(self.bpm_selector.currentText())

    def random_pattern(self):
        self.current_pattern.generate_random()
        self.update_grid()

    def euclidean_pattern(self):
        self.current_pattern.generate_euclidean(5, self.current_pattern.steps, 0)  # Kick
        self.update_grid()

    def generate_fill(self):
        self.current_pattern.generate_fill()
        self.update_grid()

    def play_pattern(self):
        self.player.play_pattern(self.current_pattern, self.bpm)

    def stop_pattern(self):
        self.player.stop()

    def export_midi(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Export MIDI", "", "MIDI Files (*.mid)")
        if fname:
            if not fname.endswith(".mid"):
                fname += ".mid"
            export_pattern([self.current_pattern], self.bpm, fname)
            QMessageBox.information(self, "Export", f"MIDI exported to {fname}")

    def save_presets(self):
        save_presets(self.patterns)
        QMessageBox.information(self, "Save", "Presets saved.")

    def load_presets(self):
        loaded = load_presets()
        if loaded:
            self.patterns = loaded
            self.current_pattern = self.patterns[0]
            self.update_grid()
            QMessageBox.information(self, "Load", "Presets loaded.")
        else:
            QMessageBox.warning(self, "Load", "No presets found.")
