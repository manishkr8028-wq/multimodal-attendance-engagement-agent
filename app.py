import os
import uuid
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, Response, send_file
from flask_cors import CORS

from config import PORT, DEBUG, SECRET_KEY, SUSTAINED_PRESENCE_SECONDS, ATTENTION_THRESHOLD, GEMINI_API_KEY
import database as db
from modules.vision_module import vision_engine
from modules.audio_module import audio_engine
from modules.multimodal_fusion import fusion_engine
from modules.gemini_agent import gemini_agent
from modules.analytics_engine import analytics_engine

app = Flask(__name__)
app.secret_key = SECRET_KEY
CORS(app)

# Ensure database is initialized
db.init_db()

# --- Web Page Views ---

@app.route('/')
def index():
    """Live Classroom Monitor and Real-Time HUD."""
    sessions = db.list_sessions(limit=5)
    active_session = sessions[0] if sessions else None
    return render_template('index.html', active_session=active_session, sessions=sessions)

@app.route('/attendance')
def attendance_view():
    """Automated Attendance Register and Sustained Presence Logs."""
    sessions = db.list_sessions(limit=10)
    current_sess_id = request.args.get('session_id', sessions[0]['id'] if sessions else 'sess_demo_2026')
    attendance = db.get_session_attendance(current_sess_id)
    session = db.get_session(current_sess_id)
    return render_template('attendance.html', attendance=attendance, session=session, sessions=sessions, current_sess_id=current_sess_id)

@app.route('/analytics')
def analytics_view():
    """Deep-Dive Engagement Analytics and Session Dynamics."""
    sessions = db.list_sessions(limit=10)
    current_sess_id = request.args.get('session_id', sessions[0]['id'] if sessions else 'sess_demo_2026')
    data = analytics_engine.compute_session_statistics(current_sess_id)
    return render_template('analytics.html', data=data, sessions=sessions, current_sess_id=current_sess_id)

@app.route('/suggestions')
def suggestions_view():
    """AI-Driven Teaching Suggestions and Real-Time Decision Support."""
    sessions = db.list_sessions(limit=10)
    current_sess_id = request.args.get('session_id', sessions[0]['id'] if sessions else 'sess_demo_2026')
    suggestions = db.get_teaching_suggestions(current_sess_id)
    session = db.get_session(current_sess_id)
    return render_template('ai_suggestions.html', suggestions=suggestions, session=session, sessions=sessions, current_sess_id=current_sess_id)

@app.route('/settings')
def settings_view():
    """System Configuration and Model Settings."""
    return render_template('settings.html', gemini_key=gemini_agent.api_key, model=gemini_agent.model_name)


# --- REST API Endpoints ---

@app.route('/api/sessions/create', methods=['POST'])
def api_create_session():
    """Create a new classroom intelligence monitoring session."""
    data = request.json or {}
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    title = data.get('title', 'AI Classroom Lecture')
    class_name = data.get('class_name', 'Computer Science & AI')
    instructor = data.get('instructor', 'Course Instructor')

    session = db.create_session(session_id, title, class_name, instructor)
    return jsonify({"success": True, "session": session})

@app.route('/api/sessions/<session_id>/end', methods=['POST'])
def api_end_session(session_id):
    """End and finalize classroom session."""
    stats = analytics_engine.compute_session_statistics(session_id)
    summary = stats.get('summary', {})
    avg_eng = summary.get('avg_engagement', 75.0)
    present_cnt = summary.get('present_count', 0)
    total_stu = summary.get('total_students', 0)

    db.update_session_summary(session_id, avg_eng, present_cnt, total_stu)
    return jsonify({"success": True, "message": "Session finalized", "summary": summary})

@app.route('/api/sessions', methods=['GET'])
def api_list_sessions():
    sessions = db.list_sessions()
    return jsonify({"success": True, "sessions": sessions})

@app.route('/api/vision/process_frame', methods=['POST'])
def api_process_frame():
    """Process a single base64 camera frame for face detection, tracking, and pose."""
    payload = request.json or {}
    frame_b64 = payload.get('frame', '')
    if not frame_b64:
        return jsonify({"success": False, "error": "No frame data provided"}), 400

    result = vision_engine.process_frame(frame_b64)
    return jsonify(result)

@app.route('/api/audio/process_metrics', methods=['POST'])
def api_process_audio_metrics():
    """Process real-time audio loudness/RMS metrics from frontend Web Audio."""
    payload = request.json or {}
    rms = float(payload.get('rms', 0.0))
    peak = float(payload.get('peak', 0.0))

    result = audio_engine.process_live_audio_metrics(rms, peak)
    return jsonify(result)

@app.route('/api/telemetry/multimodal_step', methods=['POST'])
def api_multimodal_step():
    """
    Combined multimodal telemetry update step.
    Receives synchronized vision + audio data, calculates fused engagement,
    updates sustained presence attendance records, and logs time series.
    """
    payload = request.json or {}
    session_id = payload.get('session_id', 'sess_demo_2026')
    elapsed_seconds = int(payload.get('elapsed_seconds', 0))

    frame_b64 = payload.get('frame', '')
    rms = float(payload.get('rms', 0.0))
    peak = float(payload.get('peak', 0.0))

    # 1. Process Vision
    if frame_b64:
        vision_res = vision_engine.process_frame(frame_b64)
    else:
        vision_res = {"faces_detected": 1, "average_attention": 0.82, "average_pitch": 0.0, "average_yaw": 0.0, "faces": []}

    # 2. Process Audio
    audio_res = audio_engine.process_live_audio_metrics(rms, peak)

    # 3. Multimodal Fusion
    active_faces = vision_res.get("faces_detected", 0)
    avg_attention = vision_res.get("average_attention", 0.75)
    vocal_score = audio_res.get("vocal_activity_score", 40.0)
    silence = audio_res.get("silence_duration_seconds", 0.0)

    fused = fusion_engine.compute_engagement_index(
        visual_attention=avg_attention,
        vocal_activity_score=vocal_score,
        active_faces=active_faces,
        silence_seconds=silence
    )

    # 4. Sustained Presence Tracking (Update attendance logs)
    # If face detected, map track to student presence
    if active_faces > 0:
        # For classroom demo, map detected tracks to registered students
        students = db.get_session_attendance(session_id)
        if students:
            # Mark presence for the active participant
            db.record_presence(session_id, students[0]['id'], confidence=0.96)

    # 5. Log engagement time-point in database
    db.log_engagement(
        session_id=session_id,
        elapsed_seconds=elapsed_seconds,
        score=fused["engagement_score"],
        visual=fused["visual_score"],
        vocal=fused["vocal_score"],
        faces=active_faces,
        pitch=vision_res.get("average_pitch", 0.0),
        yaw=vision_res.get("average_yaw", 0.0),
        alert=fused["alert_flag"]
    )

    # 6. Check if AI Teaching Suggestion should be generated
    new_suggestion = None
    if fused["alert_flag"] in ("Attention Drop", "Prolonged Silence") or (elapsed_seconds > 0 and elapsed_seconds % 60 == 0):
        sug_payload = {
            "engagement_score": fused["engagement_score"],
            "visual_score": fused["visual_score"],
            "vocal_score": fused["vocal_score"],
            "silence_duration_seconds": silence,
            "alert_flag": fused["alert_flag"]
        }
        ai_res = gemini_agent.generate_realtime_suggestion(sug_payload)
        db.add_teaching_suggestion(
            session_id=session_id,
            elapsed_seconds=elapsed_seconds,
            trigger=ai_res.get("trigger_reason", "Telemetry threshold"),
            category=ai_res.get("category", "General"),
            suggestion=ai_res.get("suggestion_text", ""),
            action=ai_res.get("action_item", "")
        )
        new_suggestion = ai_res

    return jsonify({
        "success": True,
        "vision": vision_res,
        "audio": audio_res,
        "fusion": fused,
        "new_suggestion": new_suggestion
    })

@app.route('/api/analytics/<session_id>', methods=['GET'])
def api_get_analytics(session_id):
    """Retrieve full analytics statistics and timeline for Chart.js."""
    data = analytics_engine.compute_session_statistics(session_id)
    return jsonify({"success": True, "data": data})

@app.route('/api/ai/ask', methods=['POST'])
def api_ai_ask():
    """Ask the Gemini Decision Support Assistant a question."""
    payload = request.json or {}
    query = payload.get('query', '')
    session_id = payload.get('session_id', 'sess_demo_2026')

    if not query:
        return jsonify({"success": False, "error": "Query required"}), 400

    stats = analytics_engine.compute_session_statistics(session_id)
    context = stats.get('summary', {})
    context['session_id'] = session_id

    answer = gemini_agent.answer_teacher_query(query, context)
    return jsonify({"success": True, "answer": answer})

@app.route('/api/ai/suggest', methods=['POST'])
def api_ai_suggest():
    """Explicitly trigger an AI teaching suggestion."""
    payload = request.json or {}
    metrics = payload.get('metrics', {
        "engagement_score": 68.0,
        "visual_score": 62.0,
        "vocal_score": 45.0,
        "silence_duration_seconds": 12.0,
        "alert_flag": "Pacing Check"
    })
    suggestion = gemini_agent.generate_realtime_suggestion(metrics)
    return jsonify({"success": True, "suggestion": suggestion})

@app.route('/api/settings/update', methods=['POST'])
def api_update_settings():
    """Update Gemini API Key or settings dynamically."""
    payload = request.json or {}
    new_key = payload.get('gemini_key', '').strip()
    if new_key:
        gemini_agent.update_api_key(new_key)
    return jsonify({"success": True, "message": "Settings updated successfully"})

@app.route('/api/export/attendance/<session_id>', methods=['GET'])
def api_export_attendance_csv(session_id):
    """Download attendance CSV."""
    csv_data = analytics_engine.generate_attendance_csv(session_id)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=attendance_{session_id}.csv"}
    )

@app.route('/api/export/engagement/<session_id>', methods=['GET'])
def api_export_engagement_csv(session_id):
    """Download engagement timeline CSV."""
    csv_data = analytics_engine.generate_engagement_csv(session_id)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=engagement_timeline_{session_id}.csv"}
    )

@app.route('/api/export/json/<session_id>', methods=['GET'])
def api_export_json(session_id):
    """Download full session audit report as JSON."""
    data = analytics_engine.compute_session_statistics(session_id)
    data["suggestions"] = db.get_teaching_suggestions(session_id)
    return Response(
        json.dumps(data, indent=2),
        mimetype="application/json",
        headers={"Content-disposition": f"attachment; filename=classroom_intelligence_{session_id}.json"}
    )

if __name__ == '__main__':
    print(f"Starting Multimodal Attendance & Engagement Agent on http://localhost:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
