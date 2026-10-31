# Multimodal Attendance & Engagement Agent

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1%2B-black?logo=flask&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer_Vision-red?logo=opencv&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google_Gemini-2.0_Flash-orange?logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Program](https://img.shields.io/badge/Program-Generative_AI_with_Google_Cloud-indigo)

**An AI-powered, privacy-preserving classroom intelligence system integrating Computer Vision, Audio Signal Processing, and Gemini 2.0 Flash agent-based reasoning for automated attendance and real-time engagement analytics.**

[Live Monitor](#live-monitor-hud) • [Architecture](#technical-architecture) • [Core Scenarios](#core-scenarios) • [Epics Breakdown](#project-workflow--epics) • [Quick Start](#quick-start-guide) • [API Documentation](#rest-api-documentation)

---

</div>

## 📌 Executive Summary

In educational institutions and professional training environments, attendance tracking remains largely manual or limited to basic biometric systems that fail to capture meaningful engagement and participation context. These traditional approaches are time-consuming, prone to inaccuracies, and provide no insight into learner attention, interaction patterns, or session effectiveness.

As classrooms increasingly adopt digital tools, there is a growing need for intelligent systems that can move beyond simple presence detection. The **Multimodal Attendance & Engagement Agent** was engineered as an **AI-powered, privacy-preserving classroom intelligence system**. The project fuses **computer vision**, **audio signal processing**, and **agent-based reasoning** to:
1. Automatically track attendance via **sustained presence verification**.
2. Analyze multi-dimensional **temporal engagement trends**.
3. Generate **AI-driven, context-aware teaching suggestions** via Google Gemini 2.0 Flash.
4. Provide deep **student session analytics and compliance audit logs**.
5. Operate **entirely offline at the edge** to safeguard learner privacy and ethical standards.

---

## 🎯 Core Scenarios

### Scenario 1: Automated Attendance Tracking
* **The Challenge:** Conventional face detection marks attendance on single snapshots, causing false positives from transient passersby or brief head movements.
* **Our Solution:** The agent tracks participants over time using spatial overlap and centroid persistence counters. Attendance is officially marked only after **sustained presence** meets a configurable threshold (e.g., $\ge 10\text{ seconds}$). Timestamped attendance logs are generated automatically with high precision confidence metrics.

### Scenario 2: Engagement and Session Dynamics Analysis
* **The Challenge:** Passive check-ins do not reveal when students experience cognitive fatigue or disengagement.
* **Our Solution:** The system continuously monitors behavioral indicators:
  * **Head Pose & Attention Proxy:** Vertical pitch and horizontal yaw derived from facial symmetry and eye-level geometry to detect board-gaze vs. phone/desk downward drift.
  * **Acoustic Participation:** Root Mean Square (RMS) energy, Zero Crossing Rate (ZCR), and Voice Activity Detection (VAD) to distinguish silence, lecturer monologues, and collaborative peer discussions.
  * **Multimodal Fusion Engine:** Integrates visual attention and vocal participation via temporal Exponential Moving Average (EMA) into a normalized **Engagement Index (0–100%)**.

### Scenario 3: AI-Driven Teaching Suggestions
* **The Challenge:** Educators often lack objective real-time indicators to adjust classroom pacing or re-engage quieter cohorts.
* **Our Solution:** Powered by **Google Gemini 2.0 Flash**, the agent acts as an assistive decision-support tool. When attention drops or prolonged monologues are identified, the agent generates non-intrusive micro-interventions (e.g., *Think-Pair-Share*, concept verification polls, or pacing resets). A conversational **"Ask the Agent"** chat assistant allows educators to interrogate classroom telemetry in natural language.

---

## 🏗️ Technical Architecture

The system implements a decoupled, high-performance layered architecture:

<div align="center">
  <img src="static/images/architecture.svg" alt="Technical Architecture Diagram" width="100%">
</div>

### Layer-by-Layer Breakdown:

1. **Frontend Presentation Layer (`templates/`, `static/`):**
   * **HTML5 Semantic Templates:** Dashboard, Attendance Register, Session Analytics, and AI Insights.
   * **Vanilla CSS3 Design System:** Sleek, modern dark glassmorphic interface with HSL tailored color palettes, subtle glowing borders, and fluid responsive layouts.
   * **JavaScript Controllers:**
     * `camera_stream.js`: HTML5 `<video>` and `<canvas>` real-time HUD bounding box and gaze overlay. Includes a simulated classroom video mode when webcams are offline.
     * `audio_stream.js`: Web Audio API real-time acoustic RMS analyzer and 24-band dynamic visualizer waveform.
     * `app.js`: Telemetry synchronization, circular SVG gauge animation, and session lifecycle management.

2. **Backend & API Gateway Layer (`app.py`, `config.py`):**
   * **Flask API Gateway:** High-throughput lightweight RESTful endpoints for frame ingestion, audio telemetry, and report downloads.
   * **Route Handlers:** Synchronized endpoint `/api/telemetry/multimodal_step` ensuring sub-200ms roundtrip analysis.

3. **Computer Vision & Audio Signal Processing Layer (`modules/`):**
   * `vision_module.py`: Dual-pipeline face detection (OpenCV Cascade / DNN with adaptive skin-chrominance morphological contour fallback) guaranteeing zero crashing across OpenCV 4.x and OpenCV 5.0+.
   * `audio_module.py`: Fast NumPy-based acoustic energy computation, VAD indicator, and conversational state classification.
   * `multimodal_fusion.py`: Temporal smoothing and dynamic weighting engine ($W_{visual} = 0.65$, $W_{audio} = 0.35$).

4. **AI Reasoning Service Layer (`modules/gemini_agent.py`):**
   * Native integration with **Google Gemini 2.0 Flash** via the official `google.genai` SDK.
   * Built-in expert pedagogical rule engine providing offline fallback if an API key is not configured.

5. **Storage & Utility Layer (`database.py`, `modules/analytics_engine.py`):**
   * Thread-safe **SQLite database** managing sessions, enrolled students, timestamped sustained attendance, and engagement logs.
   * Export engines producing CSV attendance registries, CSV engagement timelines, and compliant JSON audit summaries.

---

## 📋 Project Workflow & Epics

| Epic | Scope & Implementation Details | Status |
|---|---|:---:|
| **EPIC 1: Requirements & Environment Setup** | Requirements specification, Python 3.10+ virtual environment, dependencies configuration, `.env.example`, database initialization scripts. | **Completed (100%)** |
| **EPIC 2: Vision Module Development** | Real-time face detection, centroid tracking, temporal sustained presence verification ($\ge 10\text{s}$), and head pose pitch/yaw estimation. | **Completed (100%)** |
| **EPIC 3: Audio Module Development** | Web Audio API mic streaming, RMS energy calculation, Voice Activity Detection (VAD), silence ratio calculation, and discussion classification. | **Completed (100%)** |
| **EPIC 4: AI Implementation** | Multimodal signal fusion algorithm, Google Gemini 2.0 Flash prompt engineering, proactive pedagogical recommendations, and conversational teacher chat. | **Completed (100%)** |
| **EPIC 5: Analytics & Recommendation Engine** | Time-series engagement aggregation, statistical peak/dip indicators, Chart.js timeline and tier distribution, CSV and JSON export routines. | **Completed (100%)** |
| **EPIC 6: Interface, Testing, and Deployment** | Dark glassmorphism frontend HUD, circular SVG gauge, 9 comprehensive unit tests (`tests/`), Windows quick-start `run.bat`, and GitHub repository setup. | **Completed (100%)** |

---

## 📂 Repository Structure

```
multimodal-attendance-engagement-agent/
├── .env.example                    # Environment variable configuration template
├── .gitignore                      # Git ignore rules for Python, virtualenv, and local caches
├── requirements.txt                # Production dependency list
├── config.py                       # Global settings, paths, and detection thresholds
├── database.py                     # SQLite data access layer and schema management
├── app.py                          # Flask API Gateway and web application entrypoint
├── run.bat                         # One-click Windows launch script
├── README.md                       # Comprehensive project documentation
├── modules/
│   ├── __init__.py
│   ├── vision_module.py            # Computer Vision, face tracking, sustained presence, head pose
│   ├── audio_module.py             # Audio signal processing, RMS energy, and VAD
│   ├── multimodal_fusion.py        # Signal fusion engine and temporal engagement scoring
│   ├── gemini_agent.py             # Google Gemini 2.0 Flash integration and teaching suggestions
│   └── analytics_engine.py         # Metrics aggregation, statistical analysis, and CSV/JSON exports
├── templates/
│   ├── base.html                   # Master layout with top navigation, banners, and status pills
│   ├── index.html                  # Live Classroom Monitor & Real-Time Engagement HUD
│   ├── attendance.html             # Automated Attendance Register with sustained presence logs
│   ├── analytics.html              # Deep-Dive Engagement Analytics & Session Dynamics (Chart.js)
│   ├── ai_suggestions.html         # Gemini 2.0 Flash Teaching Suggestions & Interactive Chat
│   └── settings.html               # System calibration, Gemini API key, and privacy options
├── static/
│   ├── css/
│   │   └── style.css               # Vanilla CSS3 Design System with dark glassmorphic styling
│   ├── js/
│   │   ├── camera_stream.js        # Webcam capture, canvas HUD overlay, and simulation fallback
│   │   ├── audio_stream.js         # Web Audio API mic analysis and 24-band waveform visualizer
│   │   └── app.js                  # Main client-side telemetry loop and session manager
│   ├── images/
│   │   └── architecture.svg        # Scalable Vector Graphics system architecture diagram
│   └── samples/
│       └── sample_classroom.json   # Benchmark classroom metadata and metrics
└── tests/
    ├── test_vision.py              # Unit tests for face detection, tracking, and pose
    ├── test_audio.py               # Unit tests for RMS energy and speech classification
    ├── test_multimodal.py          # Unit tests for signal fusion and anomaly alerts
    └── test_api.py                 # Unit tests for Flask web routes and data export endpoints
```

---

## ⚡ Quick Start Guide

### 1. Prerequisites
* **Python 3.10+** (Tested on Python 3.10, 3.11, 3.12, 3.14)
* **Git** installed on your operating system
* Modern Web Browser (Chrome, Edge, Firefox, Brave)

### 2. Clone the Repository
```bash
git clone https://github.com/manishkr8028-wq/multimodal-attendance-engagement-agent.git
cd multimodal-attendance-engagement-agent
```

### 3. Install Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment (Optional)
Copy the example environment configuration:
```bash
cp .env.example .env
```
Open `.env` and set your `GEMINI_API_KEY`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
PORT=5000
DEBUG=True
SUSTAINED_PRESENCE_SECONDS=10
```
> **Note:** If no Gemini API key is provided, the application runs automatically in **Offline Mode** utilizing its built-in rule-based expert pedagogical engine!

### 5. Launch the Application

#### Option A: Windows Quick-Start
Simply double-click `run.bat` or run:
```powershell
.\run.bat
```

#### Option B: Terminal
```bash
python app.py
```
Open your browser to: **[http://localhost:5000](http://localhost:5000)**

---

## 🧪 Running Automated Tests

All core algorithms (vision, audio, multimodal fusion, and web endpoints) are covered by automated unit tests:

```bash
python -m unittest discover tests -v
```

Expected output:
```
test_pages_load (test_api.TestFlaskEndpoints) ... ok
test_api_session_lifecycle (test_api.TestFlaskEndpoints) ... ok
test_live_metrics_processing (test_audio.TestAudioModule) ... ok
test_silence_detection (test_audio.TestAudioModule) ... ok
test_sine_wave_activity (test_audio.TestAudioModule) ... ok
test_high_engagement_fusion (test_multimodal.TestMultimodalFusion) ... ok
test_low_engagement_alert (test_multimodal.TestMultimodalFusion) ... ok
test_head_pose_estimation (test_vision.TestVisionModule) ... ok
test_track_updates (test_vision.TestVisionModule) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.133s

OK
```

---

## 🌐 REST API Documentation

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Live Classroom Monitor and Real-Time HUD |
| `GET` | `/attendance` | Automated Attendance Register and Sustained Presence logs |
| `GET` | `/analytics` | Deep-Dive Engagement Analytics and Session Dynamics |
| `GET` | `/suggestions` | AI-Driven Teaching Suggestions & "Ask the Agent" Chat |
| `GET` | `/settings` | System settings, Gemini Model, and privacy calibration |
| `POST` | `/api/sessions/create` | Initialize a new classroom intelligence monitoring session |
| `POST` | `/api/sessions/<id>/end` | Finalize session and calculate summary metrics |
| `POST` | `/api/vision/process_frame` | Ingest base64 camera frame; returns tracked faces and pose |
| `POST` | `/api/audio/process_metrics`| Ingest live RMS loudness and audio peaks |
| `POST` | `/api/telemetry/multimodal_step` | Synchronized multimodal telemetry cycle (fuses vision + audio) |
| `POST` | `/api/ai/ask` | Query the Gemini 2.0 Flash Classroom Assistant |
| `POST` | `/api/ai/suggest` | Trigger proactive context-aware pedagogical recommendation |
| `GET` | `/api/export/attendance/<id>` | Download Attendance Register as CSV file |
| `GET` | `/api/export/engagement/<id>` | Download Engagement Dynamics Timeline as CSV file |
| `GET` | `/api/export/json/<id>` | Download complete session compliance audit as JSON |

---

## 🔒 Privacy & Ethical Deployment

* **Edge Processing:** Face detection and audio feature extraction occur locally on the machine.
* **Zero Raw Video Retention:** Raw video frames and camera feeds are evaluated strictly in ephemeral memory buffers; no video footage is stored permanently.
* **Non-Enforcing Assistive Nature:** AI-driven suggestions are presented strictly as decision-support insights for educators without enforcing automated disciplinary actions.

---

## 👨‍💻 Author & Acknowledgements

* **Author:** Manish Kumar ([@manishkr8028-wq](https://github.com/manishkr8028-wq))
* **Email:** manishkr8028@gmail.com
* **Program:** Generative AI with Google Cloud
* **Project:** Multimodal Attendance & Engagement Agent

---

<div align="center">
  <sub>Developed for the Generative AI with Google Cloud Internship &bull; 2026</sub>
</div>
