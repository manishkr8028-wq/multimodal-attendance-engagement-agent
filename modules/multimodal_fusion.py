from typing import Dict, Any, List
import numpy as np

class MultimodalFusionEngine:
    """
    Multimodal Signal Fusion & Real-Time Engagement Scoring Engine.
    Fuses:
    1. Computer Vision indicators: Gaze/Head pose attention, face counts, sustained presence
    2. Audio Processing indicators: RMS volume, speech ratio, silence/dialogue dynamics
    3. Temporal Smoothing: Rolling exponential moving average to filter transient noise
    """

    def __init__(self, visual_weight: float = 0.65, audio_weight: float = 0.35):
        self.visual_weight = visual_weight
        self.audio_weight = audio_weight
        self.smoothed_score = 75.0  # initial baseline
        self.history: List[float] = []

    def compute_engagement_index(
        self,
        visual_attention: float,      # 0.0 to 1.0 (from VisionModule)
        vocal_activity_score: float,  # 0.0 to 100.0 (from AudioModule)
        active_faces: int = 1,
        silence_seconds: float = 0.0
    ) -> Dict[str, Any]:
        """
        Synthesizes visual and auditory signals into a holistic classroom engagement index.
        """
        # Normalize visual attention to 0 - 100 scale
        vis_score = max(0.0, min(100.0, visual_attention * 100.0))

        # Contextual modulation:
        # If active discussion is underway, audio activity carries higher weight.
        # If quiet lecture/study, visual attention carries dominant weight.
        if vocal_activity_score > 60.0:
            effective_vis_w = 0.45
            effective_aud_w = 0.55
        else:
            effective_vis_w = 0.70
            effective_aud_w = 0.30

        # Raw combined score
        raw_score = (vis_score * effective_vis_w) + (vocal_activity_score * effective_aud_w)

        # Presence penalty: if 0 faces detected, drop score
        if active_faces == 0:
            raw_score = max(10.0, raw_score * 0.3)

        # Temporal smoothing (EMA with alpha = 0.3)
        alpha = 0.3
        self.smoothed_score = alpha * raw_score + (1.0 - alpha) * self.smoothed_score
        final_score = round(float(self.smoothed_score), 1)

        # Maintain history
        self.history.append(final_score)
        if len(self.history) > 60:
            self.history.pop(0)

        # Engagement Level Classification
        if final_score >= 78.0:
            level = "Optimal Engagement"
            badge_color = "success"
        elif final_score >= 60.0:
            level = "Attentive / Receptive"
            badge_color = "info"
        elif final_score >= 45.0:
            level = "Moderate / Pacing Dip"
            badge_color = "warning"
        else:
            level = "Disengaged / Distraction Drift"
            badge_color = "danger"

        # Alert evaluation
        alert = "Normal"
        if final_score < 45.0:
            alert = "Attention Drop"
        elif silence_seconds > 18.0:
            alert = "Prolonged Silence"
        elif vocal_activity_score > 85.0:
            alert = "High Discussion Peak"

        return {
            "engagement_score": final_score,
            "raw_score": round(float(raw_score), 1),
            "visual_score": round(float(vis_score), 1),
            "vocal_score": round(float(vocal_activity_score), 1),
            "engagement_level": level,
            "badge_color": badge_color,
            "alert_flag": alert,
            "active_faces": active_faces
        }

fusion_engine = MultimodalFusionEngine()
