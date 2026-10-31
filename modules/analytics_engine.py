import io
import csv
import json
from typing import Dict, Any, List
import numpy as np
from database import get_session, get_session_attendance, get_engagement_timeline, get_teaching_suggestions

class AnalyticsEngine:
    """
    Classroom Session Analytics, Metrics Aggregation, and Export Engine.
    """

    def compute_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """
        Calculates deep statistical indicators for a given classroom session.
        """
        timeline = get_engagement_timeline(session_id, limit=500)
        attendance = get_session_attendance(session_id)
        session = get_session(session_id) or {}

        if not timeline:
            return {
                "session": session,
                "attendance": attendance,
                "timeline": [],
                "summary": {
                    "avg_engagement": 0.0,
                    "peak_engagement": 0.0,
                    "lowest_engagement": 0.0,
                    "peak_minute": 0,
                    "low_minute": 0,
                    "avg_visual": 0.0,
                    "avg_vocal": 0.0,
                    "present_percentage": 0.0,
                    "engagement_distribution": {"optimal": 0, "attentive": 0, "moderate": 0, "disengaged": 0}
                }
            }

        scores = [item["overall_score"] for item in timeline]
        visuals = [item["visual_attention"] for item in timeline]
        vocals = [item["vocal_activity"] for item in timeline]

        avg_score = float(np.mean(scores))
        max_idx = int(np.argmax(scores))
        min_idx = int(np.argmin(scores))

        peak_minute = round(timeline[max_idx]["elapsed_seconds"] / 60.0, 1)
        low_minute = round(timeline[min_idx]["elapsed_seconds"] / 60.0, 1)

        # Engagement distribution
        optimal_cnt = sum(1 for s in scores if s >= 78.0)
        attentive_cnt = sum(1 for s in scores if 60.0 <= s < 78.0)
        moderate_cnt = sum(1 for s in scores if 45.0 <= s < 60.0)
        disengaged_cnt = sum(1 for s in scores if s < 45.0)
        total_pts = max(1, len(scores))

        # Attendance percentages
        total_students = len(attendance)
        present_count = sum(1 for a in attendance if a.get("attendance_status") in ("Present", "Late"))
        present_pct = round((present_count / max(1, total_students)) * 100.0, 1)

        summary = {
            "avg_engagement": round(avg_score, 1),
            "peak_engagement": round(float(scores[max_idx]), 1),
            "lowest_engagement": round(float(scores[min_idx]), 1),
            "peak_minute": peak_minute,
            "low_minute": low_minute,
            "avg_visual": round(float(np.mean(visuals)), 1),
            "avg_vocal": round(float(np.mean(vocals)), 1),
            "total_students": total_students,
            "present_count": present_count,
            "present_percentage": present_pct,
            "engagement_distribution": {
                "optimal": round((optimal_cnt / total_pts) * 100.0, 1),
                "attentive": round((attentive_cnt / total_pts) * 100.0, 1),
                "moderate": round((moderate_cnt / total_pts) * 100.0, 1),
                "disengaged": round((disengaged_cnt / total_pts) * 100.0, 1)
            }
        }

        return {
            "session": session,
            "attendance": attendance,
            "timeline": timeline,
            "summary": summary
        }

    def generate_attendance_csv(self, session_id: str) -> str:
        """Export session attendance report as CSV string."""
        attendance = get_session_attendance(session_id)
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["Student ID", "Roll Number", "Student Name", "Department", "Attendance Status", "Sustained Time (Seconds)", "Confidence", "First Seen", "Last Seen"])
        for row in attendance:
            writer.writerow([
                row.get("id", ""),
                row.get("roll_no", ""),
                row.get("name", ""),
                row.get("department", ""),
                row.get("attendance_status", "Absent"),
                round(row.get("sustained_seconds", 0), 1),
                round(row.get("confidence", 0.0), 2),
                row.get("first_seen", "N/A"),
                row.get("last_seen", "N/A")
            ])

        return output.getvalue()

    def generate_engagement_csv(self, session_id: str) -> str:
        """Export session engagement timeline as CSV string."""
        timeline = get_engagement_timeline(session_id, limit=1000)
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["Elapsed Seconds", "Elapsed Minutes", "Overall Engagement (%)", "Visual Attention (%)", "Vocal Activity (%)", "Active Faces", "Head Pitch", "Head Yaw", "Alert Status", "Timestamp"])
        for item in timeline:
            sec = item.get("elapsed_seconds", 0)
            writer.writerow([
                sec,
                round(sec / 60.0, 2),
                item.get("overall_score", 0.0),
                item.get("visual_attention", 0.0),
                item.get("vocal_activity", 0.0),
                item.get("active_faces_count", 0),
                item.get("head_pitch", 0.0),
                item.get("head_yaw", 0.0),
                item.get("alert_flag", "Normal"),
                item.get("timestamp", "")
            ])

        return output.getvalue()

analytics_engine = AnalyticsEngine()
