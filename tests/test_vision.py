import unittest
import numpy as np
import cv2
import time
from modules.vision_module import VisionModule

class TestVisionModule(unittest.TestCase):
    def setUp(self):
        self.vision = VisionModule()

    def test_track_updates(self):
        # Create synthetic bounding boxes
        box1 = (100, 100, 80, 80)
        current_time = time.time()
        
        # Frame 1: Register new track
        tracks1 = self.vision.update_tracks([box1], current_time)
        self.assertEqual(len(tracks1), 1)
        track_id = tracks1[0][0]

        # Frame 2: Same track slightly moved
        box2 = (105, 102, 80, 80)
        tracks2 = self.vision.update_tracks([box2], current_time + 1.0)
        self.assertEqual(len(tracks2), 1)
        self.assertEqual(tracks2[0][0], track_id)
        self.assertGreater(tracks2[0][1]['sustained_seconds'], 1.0)

    def test_head_pose_estimation(self):
        # Create a synthetic face ROI
        face_roi = np.zeros((100, 100), dtype=np.uint8)
        # Add synthetic eye spots
        cv2.circle(face_roi, (30, 35), 6, 255, -1)
        cv2.circle(face_roi, (70, 35), 6, 255, -1)

        pose = self.vision.estimate_head_pose_and_attention(face_roi, (10, 10, 100, 100))
        self.assertIn("pitch", pose)
        self.assertIn("yaw", pose)
        self.assertIn("attention_score", pose)
        self.assertGreaterEqual(pose["attention_score"], 0.0)
        self.assertLessEqual(pose["attention_score"], 1.0)

if __name__ == '__main__':
    unittest.main()
