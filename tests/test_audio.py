import unittest
import numpy as np
from modules.audio_module import AudioModule

class TestAudioModule(unittest.TestCase):
    def setUp(self):
        self.audio = AudioModule()

    def test_silence_detection(self):
        # Generate silence
        silence = np.zeros(16000, dtype=np.float32)
        res = self.audio.analyze_audio_chunk(silence, 16000)
        self.assertEqual(res["rms_energy"], 0.0)
        self.assertFalse(res["is_speech"])

    def test_sine_wave_activity(self):
        # Generate 440 Hz audio tone
        t = np.linspace(0, 1.0, 16000, endpoint=False)
        tone = 0.5 * np.sin(2 * np.pi * 440 * t).astype(np.float32)
        res = self.audio.analyze_audio_chunk(tone, 16000)
        self.assertGreater(res["rms_energy"], 0.1)
        self.assertTrue(res["is_speech"])
        self.assertGreater(res["vocal_activity_score"], 20.0)

    def test_live_metrics_processing(self):
        res = self.audio.process_live_audio_metrics(0.04, 0.08)
        self.assertTrue(res["is_speech"])
        self.assertIn("interaction_state", res)

if __name__ == '__main__':
    unittest.main()
