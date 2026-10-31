import unittest
from modules.multimodal_fusion import MultimodalFusionEngine

class TestMultimodalFusion(unittest.TestCase):
    def setUp(self):
        self.engine = MultimodalFusionEngine()

    def test_high_engagement_fusion(self):
        result = self.engine.compute_engagement_index(
            visual_attention=0.92,
            vocal_activity_score=75.0,
            active_faces=1,
            silence_seconds=2.0
        )
        self.assertGreater(result["engagement_score"], 65.0)
        self.assertEqual(result["alert_flag"], "Normal")

    def test_low_engagement_alert(self):
        result = self.engine.compute_engagement_index(
            visual_attention=0.20,
            vocal_activity_score=10.0,
            active_faces=1,
            silence_seconds=25.0
        )
        # Should flag attention drop or prolonged silence
        self.assertIn(result["alert_flag"], ["Attention Drop", "Prolonged Silence"])

if __name__ == '__main__':
    unittest.main()
