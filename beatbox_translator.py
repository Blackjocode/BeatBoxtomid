"""
This module provides functions for translating beatbox sequences into instrument sequences.
"""
from midiutil import MIDIFile

TIME_STEP = 0.25
REST_TOKEN = "."

SOUND_MAP = {
    "b": "bass_drum",
    "t": "closed_hi_hat",
    "k": "snare_drum",
    "s": "open_hi_hat",
    "ch": "crash_cymbal",
    "p": "clap",
    "f": "rimshot",
    "c": "cowbell",
    "tm": "tambourine",
}

INSTRUMENT_TO_MIDI_NOTE = {
    "bass_drum": 36,
    "snare_drum": 38,
    "closed_hi_hat": 42,
    "open_hi_hat": 46,
    "crash_cymbal": 49,
    "clap": 39,
    "rimshot": 37,  # Side Stick in General MIDI
    "cowbell": 56,
    "tambourine": 54,
    # Add other instruments from SOUND_MAP if they have a clear MIDI percussion equivalent
}

def parse_beatbox_sequence(sequence_string):
    """
    Parses a beatbox sequence string into a list of instrument events with timing.

    Each token in the input string is mapped to an instrument and assigned a time
    based on its position and the TIME_STEP. Unknown tokens are skipped with a warning.

    Args:
        sequence_string: A string representing the beatbox sequence, with tokens
                         separated by spaces.

    Returns:
        A list of dictionaries, where each dictionary represents an instrument event
        and contains 'time', 'instrument', and 'token' keys.
    """
    tokens = sequence_string.split(' ')
    parsed_sequence = []
    current_time = 0.0
    for token in tokens:
        if not token: # Skip empty strings that can result from split
            continue

        if token == REST_TOKEN:
            current_time += TIME_STEP
            continue

        mapped_instrument_name = SOUND_MAP.get(token)
        if mapped_instrument_name:
            parsed_sequence.append({
                'time': current_time,
                'instrument': mapped_instrument_name,
                'token': token
            })
            current_time += TIME_STEP
        else:
            # We already checked for empty strings, so 'token' here is guaranteed to be non-empty.
            print(f"Warning: Unknown beatbox token '{token}' encountered. Skipping.")
            # Note: Time is NOT incremented for unknown sound tokens as per previous logic.
            # If unknown tokens should also take up time, current_time += TIME_STEP would be here too.
    return parsed_sequence

def generate_instrument_output(parsed_sequence):
    """
    Generates a list of human-readable strings describing instrument playback.

    Args:
        parsed_sequence: A list of instrument event dictionaries, typically from
                         `parse_beatbox_sequence`. Each dictionary should have
                         'time', 'instrument', and 'token' keys.

    Returns:
        A list of strings, where each string describes an instrument playback event.
    """
    output_lines = []
    for event in parsed_sequence:
        output_lines.append(
            f"Time {event['time']:.2f}: Play {event['instrument']} (from token '{event['token']}')"
        )
    return output_lines

def generate_midi_file(parsed_sequence, tempo=120, output_filename="output.mid"):
    """
    Generates a MIDI file from a parsed beatbox sequence.

    Args:
        parsed_sequence: A list of instrument event dictionaries from parse_beatbox_sequence.
        tempo: The tempo for the MIDI track in beats per minute.
        output_filename: The name of the MIDI file to create.
    """
    midi_file = MIDIFile(1)  # 1 track
    midi_file.addTrackName(track=0, time=0, trackName="Beatbox Track")
    midi_file.addTempo(track=0, time=0, tempo=tempo)

    for event in parsed_sequence:
        instrument = event['instrument']
        time = event['time']  # Time in beats (assuming TIME_STEP relates to beat subdivisions)

        midi_note = INSTRUMENT_TO_MIDI_NOTE.get(instrument)

        if midi_note is not None:
            channel = 9  # General MIDI percussion channel (0-indexed for MIDIUtil)
            duration = 1  # Duration in beats. Adjust if TIME_STEP implies different note lengths.
            volume = 100  # MIDI velocity (0-127)
            midi_file.addNote(track=0, channel=channel, pitch=midi_note, time=time, duration=duration, volume=volume)
        else:
            if instrument: # Only print warning if instrument is not empty
                print(f"Warning: No MIDI note defined for instrument '{instrument}'. Skipping in MIDI output.")

    with open(output_filename, "wb") as output_f:
        midi_file.writeFile(output_f)
    print(f"MIDI file saved as {output_filename}")


if __name__ == "__main__":
    sample_beatbox = "b . k c . tm f"
    print(f"Processing sequence: '{sample_beatbox}'")
    parsed_sample = parse_beatbox_sequence(sample_beatbox)
    output_sample = generate_instrument_output(parsed_sample)
    for line in output_sample:
        print(line)
    generate_midi_file(parsed_sample, tempo=120, output_filename="demonstration_1.mid")

    print("\n--- Example with unknown tokens and rests ---")
    sample_beatbox_with_unknown = "b x . k t y . c"
    print(f"Processing sequence: '{sample_beatbox_with_unknown}'")
    parsed_unknown = parse_beatbox_sequence(sample_beatbox_with_unknown)
    output_unknown = generate_instrument_output(parsed_unknown)
    for line in output_unknown:
        print(line)
    generate_midi_file(parsed_unknown, tempo=100, output_filename="demonstration_2.mid")


    print("\n--- Example with leading/trailing rests and spaces ---")
    sample_beatbox_complex = "  . b  .   k . tm  . "
    print(f"Processing sequence: '{sample_beatbox_complex}'")
    parsed_complex = parse_beatbox_sequence(sample_beatbox_complex)
    output_complex = generate_instrument_output(parsed_complex)
    for line in output_complex:
        print(line)
    generate_midi_file(parsed_complex, tempo=140, output_filename="demonstration_3.mid")
