import numpy as np
import time
from typing import Dict, Any, List
from config import AUDIO_RMS_THRESHOLD

class AudioModule:
    """
    Audio Signal Processing Module for Classroom Intelligence.
    Analyzes:
    - Root Mean Square (RMS) energy & audio loudness levels
    - Voice Activity Detection (VAD) indicator & speech confidence
    - Classroom interaction dynamics (Monologue vs Peer Discussion vs Silence)
    - Audio-level temporal timeline & anomaly triggers
    """

    def __init__(self):
        self.noise_floor = 0.005
        self.silence_threshold = AUDIO_RMS_THRESHOLD
        self.last_speech_time = time.time()
        self.recent_energy_history: List[float] = []

    def analyze_audio_chunk(self, audio_samples: np.ndarray, sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Analyze a raw numpy array of PCM audio samples.
        """
        if len(audio_samples) == 0:
            return self._empty_result()

        # Normalize samples
        if np.issubdtype(audio_samples.dtype, np.integer):
            max_val = float(np.iinfo(audio_samples.dtype).max)
            samples = audio_samples.astype(np.float32) / max_val
        else:
            samples = audio_samples.astype(np.float32)

        # 1. RMS Energy
        rms = float(np.sqrt(np.mean(samples**2)))

        # 2. Zero-Crossing Rate (ZCR)
        zero_crossings = np.sum(np.abs(np.diff(np.sign(samples)))) / (2.0 * len(samples))
        zcr = float(zero_crossings)

        # 3. Peak amplitude
        peak = float(np.max(np.abs(samples)))

        # 4. Voice Activity Detection (VAD) logic
        is_speech = rms > self.silence_threshold and (0.02 < zcr < 0.40)
        vad_confidence = min(1.0, max(0.0, (rms - self.silence_threshold) / 0.05)) if is_speech else 0.0

        current_time = time.time()
        if is_speech:
            self.last_speech_time = current_time

        silence_duration = current_time - self.last_speech_time

        # Track rolling history for interaction classification
        self.recent_energy_history.append(rms)
        if len(self.recent_energy_history) > 30:
            self.recent_energy_history.pop(0)

        # Interaction classification
        avg_recent = np.mean(self.recent_energy_history) if self.recent_energy_history else rms
        std_recent = np.std(self.recent_energy_history) if self.recent_energy_history else 0.0

        if silence_duration > 15.0:
            interaction_state = "Prolonged Silence"
        elif avg_recent > 0.08 and std_recent > 0.02:
            interaction_state = "Lively Discussion / Q&A"
        elif is_speech:
            interaction_state = "Active Speech / Lecture"
        else:
            interaction_state = "Quiet Study / Listening"

        # Normalized vocal activity score (0 - 100)
        vocal_activity_score = min(100.0, max(0.0, rms * 1500.0))

        return {
            "rms_energy": round(rms, 4),
            "peak_amplitude": round(peak, 4),
            "zero_crossing_rate": round(zcr, 4),
            "is_speech": bool(is_speech),
            "vad_confidence": round(vad_confidence, 2),
            "silence_duration_seconds": round(silence_duration, 1),
            "interaction_state": interaction_state,
            "vocal_activity_score": round(vocal_activity_score, 1)
        }

    def process_live_audio_metrics(self, rms_input: float, peak_input: float = 0.0) -> Dict[str, Any]:
        """
        Process pre-calculated audio level metrics streamed from Web Audio API (Frontend).
        """
        current_time = time.time()
        rms = max(0.0, min(1.0, float(rms_input)))
        peak = max(rms, float(peak_input))

        is_speech = rms > self.silence_threshold
        vad_confidence = min(1.0, max(0.0, (rms - self.silence_threshold) / 0.05)) if is_speech else 0.0

        if is_speech:
            self.last_speech_time = current_time

        silence_duration = current_time - self.last_speech_time

        self.recent_energy_history.append(rms)
        if len(self.recent_energy_history) > 20:
            self.recent_energy_history.pop(0)

        avg_recent = float(np.mean(self.recent_energy_history)) if self.recent_energy_history else rms

        if silence_duration > 12.0:
            interaction_state = "Prolonged Silence"
        elif avg_recent > 0.06:
            interaction_state = "Interactive Discussion"
        elif is_speech:
            interaction_state = "Active Lecture / Dialogue"
        else:
            interaction_state = "Attentive Listening"

        vocal_score = min(100.0, max(10.0, rms * 800.0))

        return {
            "rms_energy": round(rms, 4),
            "peak_amplitude": round(peak, 4),
            "is_speech": is_speech,
            "vad_confidence": round(vad_confidence, 2),
            "silence_duration_seconds": round(silence_duration, 1),
            "interaction_state": interaction_state,
            "vocal_activity_score": round(vocal_score, 1)
        }

    def _empty_result(self) -> Dict[str, Any]:
        return {
            "rms_energy": 0.0,
            "peak_amplitude": 0.0,
            "zero_crossing_rate": 0.0,
            "is_speech": False,
            "vad_confidence": 0.0,
            "silence_duration_seconds": 0.0,
            "interaction_state": "Quiet",
            "vocal_activity_score": 0.0
        }

audio_engine = AudioModule()
