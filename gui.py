import flet as ft
from sequencer import Pattern
from playback import MidiPlayer
from midi_export import export_pattern
from presets import save_presets, load_presets

class DrumApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Drum Sequencer"
        self.page.scroll = "auto"

        self.patterns = []
        self.current_pattern = Pattern(16)
        self.patterns.append(self.current_pattern)
        self.bpm = 120
        self.player = MidiPlayer()
        self.steps_options = [16, 32, 64]

        self.init_ui()

    def init_ui(self):
        # Layouts
        self.left_column = ft.Column()
        self.right_column = ft.Column()
        self.grid_buttons = []

        # Step selector
        self.step_selector = ft.Dropdown(
            options=[ft.dropdown.Option(str(s)) for s in self.steps_options],
            value=str(self.steps_options[0]),
            on_change=self.change_steps
        )
        self.left_column.controls.append(ft.Text("Steps per pattern:"))
        self.left_column.controls.append(self.step_selector)

        # BPM selector
        self.bpm_selector = ft.Dropdown(
            options=[ft.dropdown.Option(str(bpm)) for bpm in range(60, 201, 10)],
            value=str(self.bpm),
            on_change=self.change_bpm
        )
        self.left_column.controls.append(ft.Text("BPM:"))
        self.left_column.controls.append(self.bpm_selector)

        # Buttons
        self.left_column.controls.extend([
            ft.ElevatedButton("Random Pattern", on_click=self.random_pattern),
            ft.ElevatedButton("Euclidean Kick", on_click=self.euclidean_pattern),
            ft.ElevatedButton("Generate Fill", on_click=self.generate_fill),
            ft.ElevatedButton("Save Presets", on_click=self.save_presets),
            ft.ElevatedButton("Load Presets", on_click=self.load_presets),
        ])

        # Grid and text area
        self.grid_container = ft.Column()
        self.text_area = ft.TextField(multiline=True, height=100)
        self.right_column.controls.append(self.grid_container)
        self.right_column.controls.append(ft.Text("Pattern Text (k=s/h):"))
        self.right_column.controls.append(self.text_area)
        self.right_column.controls.append(ft.ElevatedButton("Update Grid from Text", on_click=self.update_grid_from_text))

        # Playback controls
        self.right_column.controls.append(
            ft.Row([
                ft.ElevatedButton("Play", on_click=self.play_pattern),
                ft.ElevatedButton("Stop", on_click=self.stop_pattern),
                ft.ElevatedButton("Export MIDI", on_click=self.export_midi),
            ])
        )

        # Add to page
        self.page.add(ft.Row([self.left_column, self.right_column]))
        self.update_grid()

    def update_grid(self, _=None):
        self.grid_container.controls.clear()
        self.grid_buttons = []
        rows = ["Kick", "Snare", "Hi-hat"]
        for r in range(3):
            row_buttons = []
            row = ft.Row()
            for c in range(self.current_pattern.steps):
                btn = ft.Checkbox(value=self.current_pattern.grid[r][c], on_change=lambda e, x=r, y=c: self.toggle_step(x, y))
                row.controls.append(btn)
                row_buttons.append(btn)
            self.grid_container.controls.append(row)
            self.grid_buttons.append(row_buttons)
        self.text_area.value = "\n".join(self.current_pattern.to_text())
        self.page.update()

    def toggle_step(self, r, c):
        self.current_pattern.toggle(r, c)
        self.update_grid()

    def update_grid_from_text(self, _):
        text = self.text_area.value.splitlines()
        self.current_pattern.from_text(text)
        self.update_grid()

    def change_steps(self, e):
        steps = int(e.control.value)
        self.current_pattern.steps = steps
        self.current_pattern.grid = [[False] * steps for _ in range(3)]
        self.update_grid()

    def change_bpm(self, e):
        self.bpm = int(e.control.value)

    def random_pattern(self, _):
        self.current_pattern.generate_random()
        self.update_grid()

    def euclidean_pattern(self, _):
        self.current_pattern.generate_euclidean(5, self.current_pattern.steps, 0)  # Kick
        self.update_grid()

    def generate_fill(self, _):
        self.current_pattern.generate_fill()
        self.update_grid()

    def play_pattern(self, _):
        self.player.play_pattern(self.current_pattern, self.bpm)

    def stop_pattern(self, _):
        self.player.stop()

    def export_midi(self, _):
        fname = ft.dialogs.save_file_dialog("Export MIDI", "MIDI Files (*.mid)")
        if fname:
            if not fname.endswith(".mid"):
                fname += ".mid"
            export_pattern([self.current_pattern], self.bpm, fname)

    def save_presets(self, _):
        save_presets(self.patterns)

    def load_presets(self, _):
        loaded = load_presets()
        if loaded:
            self.patterns = loaded
            self.current_pattern = self.patterns[0]
            self.update_grid()


def main(page: ft.Page):
    DrumApp(page)

ft.app(target=main)