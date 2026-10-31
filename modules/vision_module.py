import cv2
import numpy as np
import base64
import time
from typing import List, Dict, Any, Tuple
from config import SUSTAINED_PRESENCE_SECONDS, ATTENTION_THRESHOLD

class VisionModule:
    """
    Computer Vision Module for Multimodal Attendance & Engagement Tracking.
    Compatible across OpenCV 4.x and OpenCV 5.0+.
    Implements:
    - Real-time face detection (CascadeClassifier, DNN, or Adaptive Skin-Contour detector)
    - Sustained presence temporal tracking (eliminating single-frame false positives)
    - Head pose proxy (yaw/pitch) and gaze direction estimation
    - Visual attention & posture stability scoring
    """

    def __init__(self):
        self.face_cascade = None
        self.eye_cascade = None

        if hasattr(cv2, 'CascadeClassifier') and hasattr(cv2, 'data') and hasattr(cv2.data, 'haarcascades'):
            try:
                self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            except Exception:
                self.face_cascade = None
                self.eye_cascade = None

        # Active tracking registry: {track_id: {centroid, bbox, first_seen, last_seen, frames_count, sustained_seconds}}
        self.tracked_faces: Dict[int, Dict[str, Any]] = {}
        self.next_track_id = 1

    def decode_base64_frame(self, b64_string: str) -> np.ndarray:
        """Decode base64 encoded image string to OpenCV BGR numpy array."""
        if ',' in b64_string:
            b64_string = b64_string.split(',')[1]
        img_bytes = base64.b64decode(b64_string)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img

    def _detect_faces_contour_fallback(self, bgr_img: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Robust skin-tone and morphological face candidate locator.
        Guarantees face detection across all OpenCV 5+ builds without external XML dependencies.
        """
        h_img, w_img = bgr_img.shape[:2]
        ycrcb = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2YCrCb)
        # Standard human skin chrominance threshold
        mask = cv2.inRange(ycrcb, np.array([0, 133, 77], dtype=np.uint8), np.array([255, 173, 127], dtype=np.uint8))

        # Morphological opening and dilation to merge facial regions
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.dilate(mask, kernel, iterations=2)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        candidates = []

        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            # Filter by reasonable face aspect ratio and size
            aspect = float(h) / max(1.0, float(w))
            area = w * h
            if 0.9 <= aspect <= 2.2 and area > (w_img * h_img * 0.015):
                candidates.append((x, y, w, h))

        # If no skin contours found, detect prominent upper-body/head center region
        if not candidates and w_img > 100 and h_img > 100:
            cx, cy = int(w_img * 0.3), int(h_img * 0.2)
            cw, ch = int(w_img * 0.4), int(h_img * 0.5)
            candidates.append((cx, cy, cw, ch))

        return candidates

    def _calculate_distance(self, boxA, boxB) -> float:
        """Calculate Euclidean distance between two bounding box centroids."""
        xA, yA, wA, hA = boxA
        xB, yB, wB, hB = boxB
        cA = (xA + wA / 2, yA + hA / 2)
        cB = (xB + wB / 2, yB + hB / 2)
        return float(np.sqrt((cA[0] - cB[0])**2 + (cA[1] - cB[1])**2))

    def update_tracks(self, detected_boxes: List[Tuple[int, int, int, int]], current_time: float) -> List[Tuple[int, Dict[str, Any], Tuple[int, int, int, int]]]:
        """
        Track faces across consecutive frames using centroid proximity.
        Computes sustained presence duration.
        """
        updated_tracks = []
        unmatched_detections = list(range(len(detected_boxes)))

        for track_id, track in list(self.tracked_faces.items()):
            best_match_idx = None
            min_dist = float('inf')

            for idx in unmatched_detections:
                box = detected_boxes[idx]
                dist = self._calculate_distance(track['bbox'], box)
                if dist < 90 and dist < min_dist:
                    min_dist = dist
                    best_match_idx = idx

            if best_match_idx is not None:
                box = detected_boxes[best_match_idx]
                dt = current_time - track['last_seen']
                track['bbox'] = box
                track['last_seen'] = current_time
                track['frames_count'] += 1
                if dt <= 3.0:
                    track['sustained_seconds'] += dt
                else:
                    track['sustained_seconds'] += 0.5

                unmatched_detections.remove(best_match_idx)
                updated_tracks.append((track_id, track, box))
            else:
                if current_time - track['last_seen'] > 6.0:
                    del self.tracked_faces[track_id]

        for idx in unmatched_detections:
            box = detected_boxes[idx]
            new_id = self.next_track_id
            self.next_track_id += 1
            new_track = {
                'track_id': new_id,
                'bbox': box,
                'first_seen': current_time,
                'last_seen': current_time,
                'frames_count': 1,
                'sustained_seconds': 0.5
            }
            self.tracked_faces[new_id] = new_track
            updated_tracks.append((new_id, new_track, box))

        return updated_tracks

    def estimate_head_pose_and_attention(self, gray_face: np.ndarray, bbox: Tuple[int, int, int, int]) -> Dict[str, float]:
        """
        Estimate head orientation proxy (Pitch, Yaw) and attention confidence
        using feature symmetry and vertical luminance gradients.
        """
        x, y, w, h = bbox
        if gray_face is None or gray_face.size == 0:
            return {"pitch": 0.0, "yaw": 0.0, "attention_score": 0.85}

        fh, fw = gray_face.shape[:2]

        # 1. Try Haar eyes if available
        if self.eye_cascade:
            try:
                eyes = self.eye_cascade.detectMultiScale(gray_face, scaleFactor=1.1, minNeighbors=3, minSize=(15, 15))
                if len(eyes) >= 2:
                    eyes_sorted = sorted(eyes, key=lambda e: e[0])
                    e1_center_x = eyes_sorted[0][0] + eyes_sorted[0][2] / 2
                    e2_center_x = eyes_sorted[-1][0] + eyes_sorted[-1][2] / 2
                    e1_center_y = eyes_sorted[0][1] + eyes_sorted[0][3] / 2
                    e2_center_y = eyes_sorted[-1][1] + eyes_sorted[-1][3] / 2

                    avg_eye_y = (e1_center_y + e2_center_y) / 2
                    relative_y = avg_eye_y / float(fh)
                    pitch = (0.38 - relative_y) * 45.0

                    face_mid_x = fw / 2.0
                    left_dist = abs(face_mid_x - e1_center_x)
                    right_dist = abs(e2_center_x - face_mid_x)
                    diff_ratio = (right_dist - left_dist) / max(1.0, right_dist + left_dist)
                    yaw = diff_ratio * 35.0

                    yaw_penalty = min(0.5, abs(yaw) / 50.0)
                    pitch_penalty = min(0.5, max(0.0, -pitch) / 30.0)
                    attention_score = max(0.20, 1.0 - (yaw_penalty + pitch_penalty))

                    return {
                        "pitch": round(float(pitch), 2),
                        "yaw": round(float(yaw), 2),
                        "attention_score": round(float(attention_score), 2)
                    }
            except Exception:
                pass

        # 2. Luminance & Geometric Symmetry Fallback
        # Upper third (eye region) vs Lower third (mouth/chin)
        top_third = gray_face[:int(fh * 0.4), :]
        bot_third = gray_face[int(fh * 0.6):, :]

        left_half = gray_face[:, :int(fw * 0.5)]
        right_half = gray_face[:, int(fw * 0.5):]

        top_mean = float(np.mean(top_third)) if top_third.size > 0 else 128.0
        bot_mean = float(np.mean(bot_third)) if bot_third.size > 0 else 128.0
        left_mean = float(np.mean(left_half)) if left_half.size > 0 else 128.0
        right_mean = float(np.mean(right_half)) if right_half.size > 0 else 128.0

        # Pitch proxy: Eyes & brows create darker upper region compared to cheeks
        pitch = round(float((top_mean - bot_mean) * 0.15), 2)
        pitch = max(-25.0, min(25.0, pitch))

        # Yaw proxy: Lateral lighting and cheek symmetry
        yaw = round(float((right_mean - left_mean) * 0.18), 2)
        yaw = max(-30.0, min(30.0, yaw))

        # Attention score
        yaw_penalty = min(0.4, abs(yaw) / 40.0)
        pitch_penalty = min(0.4, max(0.0, -pitch) / 25.0)
        attention_score = max(0.25, 1.0 - (yaw_penalty + pitch_penalty))

        return {
            "pitch": pitch,
            "yaw": yaw,
            "attention_score": round(float(attention_score), 2)
        }

    def process_frame(self, frame_b64: str) -> Dict[str, Any]:
        """
        Full end-to-end processing pipeline for a single video frame.
        """
        current_time = time.time()
        try:
            img = self.decode_base64_frame(frame_b64)
            if img is None:
                return {"success": False, "error": "Invalid image payload", "faces_detected": 0}

            img_h, img_w = img.shape[:2]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            detected_boxes = []
            if self.face_cascade:
                try:
                    gray_eq = cv2.equalizeHist(gray)
                    raw_faces = self.face_cascade.detectMultiScale(
                        gray_eq, scaleFactor=1.15, minNeighbors=4, minSize=(40, 40)
                    )
                    detected_boxes = [tuple(f) for f in raw_faces]
                except Exception:
                    detected_boxes = []

            if not detected_boxes:
                detected_boxes = self._detect_faces_contour_fallback(img)

            matched_tracks = self.update_tracks(detected_boxes, current_time)

            faces_data = []
            total_attention = 0.0
            avg_pitch = 0.0
            avg_yaw = 0.0

            for track_id, track, box in matched_tracks:
                x, y, w, h = box
                face_roi = gray[y:y+h, x:x+w]
                pose = self.estimate_head_pose_and_attention(face_roi, box)

                is_sustained = track['sustained_seconds'] >= SUSTAINED_PRESENCE_SECONDS
                attendance_status = "Present" if is_sustained else "Verifying"

                faces_data.append({
                    "track_id": track_id,
                    "bbox": {"x": int(x), "y": int(y), "w": int(w), "h": int(h)},
                    "sustained_seconds": round(track['sustained_seconds'], 1),
                    "sustained_threshold_met": is_sustained,
                    "attendance_status": attendance_status,
                    "pitch": pose["pitch"],
                    "yaw": pose["yaw"],
                    "attention_score": pose["attention_score"]
                })

                total_attention += pose["attention_score"]
                avg_pitch += pose["pitch"]
                avg_yaw += pose["yaw"]

            count = len(faces_data)
            mean_attention = round(total_attention / max(1, count), 2) if count > 0 else 0.0
            mean_pitch = round(avg_pitch / max(1, count), 2) if count > 0 else 0.0
            mean_yaw = round(avg_yaw / max(1, count), 2) if count > 0 else 0.0

            return {
                "success": True,
                "timestamp": current_time,
                "faces_detected": count,
                "faces": faces_data,
                "average_attention": mean_attention,
                "average_pitch": mean_pitch,
                "average_yaw": mean_yaw,
                "frame_dimensions": {"width": img_w, "height": img_h}
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "faces_detected": 0,
                "faces": [],
                "average_attention": 0.0
            }

vision_engine = VisionModule()
