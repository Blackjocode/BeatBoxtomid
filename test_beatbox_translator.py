import unittest
import os
from beatbox_translator import (
    parse_beatbox_sequence,
    generate_instrument_output,
    generate_midi_file,
    SOUND_MAP,
    INSTRUMENT_TO_MIDI_NOTE,
    TIME_STEP,
    REST_TOKEN
)

class TestBeatboxTranslator(unittest.TestCase):
    TEST_MIDI_FILENAME = "test_output.mid"

    def tearDown(self):
        # Clean up any MIDI files created during tests
        if os.path.exists(self.TEST_MIDI_FILENAME):
            os.remove(self.TEST_MIDI_FILENAME)
        # Add other specific test filenames if necessary
        # For demonstration files from __main__, it's tricky as tests usually import, not run __main__
        # We will ensure the main block's output files have distinct names from test files.

    def test_sound_map_contents(self):
        self.assertIsInstance(SOUND_MAP, dict)
        self.assertEqual(SOUND_MAP['b'], 'bass_drum')
        self.assertEqual(SOUND_MAP['t'], 'closed_hi_hat')
        self.assertEqual(SOUND_MAP['k'], 'snare_drum')
        self.assertEqual(SOUND_MAP['s'], 'open_hi_hat')
        self.assertEqual(SOUND_MAP['ch'], 'crash_cymbal')
        self.assertEqual(SOUND_MAP['p'], 'clap')
        self.assertEqual(SOUND_MAP['f'], 'rimshot')
        self.assertEqual(SOUND_MAP['c'], 'cowbell')
        self.assertEqual(SOUND_MAP['tm'], 'tambourine')
        self.assertIsNotNone(REST_TOKEN) # Check it's defined

    def test_parse_beatbox_sequence_basic(self):
        sequence = "b k t"
        expected = [
            {'time': 0.0 * TIME_STEP, 'instrument': 'bass_drum', 'token': 'b'},
            {'time': 1.0 * TIME_STEP, 'instrument': 'snare_drum', 'token': 'k'},
            {'time': 2.0 * TIME_STEP, 'instrument': 'closed_hi_hat', 'token': 't'}
        ]
        # The implementation increments current_time for each token processed,
        # so the time for 'k' is 0.0 + TIME_STEP, and for 't' is (0.0 + TIME_STEP) + TIME_STEP
        # The problem description for the test case had a slight error in expected times.
        # Corrected expected times:
        expected_corrected = [
            {'time': 0.0, 'instrument': 'bass_drum', 'token': 'b'},
            {'time': 0.25, 'instrument': 'snare_drum', 'token': 'k'},
            {'time': 0.50, 'instrument': 'closed_hi_hat', 'token': 't'}
        ]
        self.assertEqual(parse_beatbox_sequence(sequence), expected_corrected) # Corrected name from previous step

    def test_parse_beatbox_sequence_empty(self):
        # An empty string splits into [''], which is now explicitly skipped.
        self.assertEqual(parse_beatbox_sequence(""), [])

    def test_parse_beatbox_sequence_with_extra_spaces(self):
        # "b  k   t" -> ["b", "", "k", "", "", "t"]. Empty strings are skipped.
        sequence = "b  k   t"
        expected = [
            {'time': 0.0, 'instrument': 'bass_drum', 'token': 'b'},
            {'time': 0.25, 'instrument': 'snare_drum', 'token': 'k'},
            {'time': 0.50, 'instrument': 'closed_hi_hat', 'token': 't'}
        ]
        self.assertEqual(parse_beatbox_sequence(sequence), expected)

    def test_parse_beatbox_sequence_with_leading_trailing_spaces(self):
        # " b k t " -> ["", "b", "k", "t", ""]. Empty strings are skipped.
        sequence = " b k t "
        expected = [
            {'time': 0.0, 'instrument': 'bass_drum', 'token': 'b'},
            {'time': 0.25, 'instrument': 'snare_drum', 'token': 'k'},
            {'time': 0.50, 'instrument': 'closed_hi_hat', 'token': 't'}
        ]
        self.assertEqual(parse_beatbox_sequence(sequence), expected)

    def test_parse_beatbox_sequence_with_unknown_tokens(self):
        sequence = "b x k y t"
        # Unknown tokens 'x' and 'y' are skipped, time is not incremented for them.
        expected = [
            {'time': 0.0, 'instrument': 'bass_drum', 'token': 'b'},
            {'time': 0.25, 'instrument': 'snare_drum', 'token': 'k'}, # x is skipped
            {'time': 0.50, 'instrument': 'closed_hi_hat', 'token': 't'}  # y is skipped
        ]
        self.assertEqual(parse_beatbox_sequence(sequence), expected)

    def test_parse_beatbox_sequence_with_only_unknown_tokens(self):
        self.assertEqual(parse_beatbox_sequence("x y z"), [])

    def test_parse_beatbox_sequence_with_rests(self):
        sequence = "b . k . t"
        expected = [
            {'time': 0.0 * TIME_STEP, 'instrument': 'bass_drum', 'token': 'b'},
            # Rest at 0.25
            {'time': 2.0 * TIME_STEP, 'instrument': 'snare_drum', 'token': 'k'}, # k is after b and 1 rest
            # Rest at 0.75
            {'time': 4.0 * TIME_STEP, 'instrument': 'closed_hi_hat', 'token': 't'} # t is after k and 1 rest
        ]
        self.assertEqual(parse_beatbox_sequence(sequence), expected)

    def test_parse_beatbox_sequence_starting_and_ending_with_rests(self):
        sequence = ". b . k ."
        expected = [
            # Rest at 0.0
            {'time': 1.0 * TIME_STEP, 'instrument': 'bass_drum', 'token': 'b'},
            # Rest at 0.50
            {'time': 3.0 * TIME_STEP, 'instrument': 'snare_drum', 'token': 'k'},
            # Rest at 0.75
        ]
        self.assertEqual(parse_beatbox_sequence(sequence), expected)

    def test_parse_beatbox_sequence_with_new_instruments(self):
        sequence = "c b tm k"
        expected = [
            {'time': 0.0, 'instrument': 'cowbell', 'token': 'c'},
            {'time': 0.25, 'instrument': 'bass_drum', 'token': 'b'},
            {'time': 0.50, 'instrument': 'tambourine', 'token': 'tm'},
            {'time': 0.75, 'instrument': 'snare_drum', 'token': 'k'}
        ]
        self.assertEqual(parse_beatbox_sequence(sequence), expected)

    def test_instrument_to_midi_note_mapping(self):
        self.assertIsInstance(INSTRUMENT_TO_MIDI_NOTE, dict)
        self.assertEqual(INSTRUMENT_TO_MIDI_NOTE['bass_drum'], 36)
        self.assertEqual(INSTRUMENT_TO_MIDI_NOTE['snare_drum'], 38)
        self.assertEqual(INSTRUMENT_TO_MIDI_NOTE['closed_hi_hat'], 42)
        self.assertEqual(INSTRUMENT_TO_MIDI_NOTE['cowbell'], 56)
        # Check if all SOUND_MAP instruments that should be in MIDI map are present
        for key in SOUND_MAP.keys():
            if key in ["p", "s", "ch"]: # Example: these might not have direct common drum MIDI notes or are complex
                if SOUND_MAP[key] in INSTRUMENT_TO_MIDI_NOTE:
                     print(f"Note: '{SOUND_MAP[key]}' from SOUND_MAP has a MIDI mapping, verify if intended.")
            elif key not in [REST_TOKEN]: # REST_TOKEN should not be in INSTRUMENT_TO_MIDI_NOTE
                 self.assertIn(SOUND_MAP[key], INSTRUMENT_TO_MIDI_NOTE,
                               f"Instrument {SOUND_MAP[key]} (token '{key}') from SOUND_MAP is missing in INSTRUMENT_TO_MIDI_NOTE")


    def test_generate_instrument_output_basic(self):
        parsed_sequence = [
            {'time': 0.0, 'instrument': 'bass_drum', 'token': 'b'},
            {'time': 0.25, 'instrument': 'snare_drum', 'token': 'k'}
        ]
        expected = [
            "Time 0.00: Play bass_drum (from token 'b')",
            "Time 0.25: Play snare_drum (from token 'k')"
        ]
        self.assertEqual(generate_instrument_output(parsed_sequence), expected)

    def test_generate_instrument_output_empty_input(self):
        self.assertEqual(generate_instrument_output([]), [])

    def test_generate_instrument_output_with_new_instruments(self):
        parsed_sequence = [
            {'time': 0.0, 'instrument': 'cowbell', 'token': 'c'},
            {'time': 0.25, 'instrument': 'tambourine', 'token': 'tm'}
        ]
        expected = [
            "Time 0.00: Play cowbell (from token 'c')",
            "Time 0.25: Play tambourine (from token 'tm')"
        ]
        self.assertEqual(generate_instrument_output(parsed_sequence), expected)

    def test_generate_midi_file_runs(self):
        sample_sequence = [
            {'time': 0.0, 'instrument': 'bass_drum', 'token': 'b'},
            {'time': 0.25, 'instrument': 'snare_drum', 'token': 'k'},
            {'time': 0.50, 'instrument': 'cowbell', 'token': 'c'}, # New instrument
            {'time': 0.75, 'instrument': 'some_unknown_sound', 'token': 'unknown'} # Test missing MIDI mapping
        ]
        generate_midi_file(sample_sequence, output_filename=self.TEST_MIDI_FILENAME)
        self.assertTrue(os.path.exists(self.TEST_MIDI_FILENAME))
        self.assertGreater(os.path.getsize(self.TEST_MIDI_FILENAME), 0)
        # The tearDown method will handle removal


if __name__ == '__main__':
    unittest.main()
