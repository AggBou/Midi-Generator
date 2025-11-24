from mido import MidiFile, MidiTrack, Message
import mido

def export_pattern(patterns, bpm, filename):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    tempo = int(60_000_000 / bpm)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))

    ppq = mid.ticks_per_beat
    step_ticks = ppq // 4

    for pat in patterns:
        events = pat.get_events()
        steps = pat.steps
        for step in range(steps):
            notes = [note for note, c in events if c == step]
            for n in notes:
                track.append(Message('note_on', channel=9, note=n, velocity=100, time=0))
                track.append(Message('note_off', channel=9, note=n, velocity=0, time=step_ticks))
            if not notes:
                track.append(Message('note_on', channel=9, note=36, velocity=0, time=step_ticks))

    mid.save(filename)
