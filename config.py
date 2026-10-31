import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# Server Settings
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "multimodal-agent-secret-key-2026")

# Database & Storage
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DATABASE_PATH = str(DATA_DIR / "classroom_intelligence.db")

UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

REPORTS_DIR = BASE_DIR / "static" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Google Gemini API Settings (Gemini 2.0 Flash)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Presence & Engagement Thresholds
SUSTAINED_PRESENCE_SECONDS = int(os.getenv("SUSTAINED_PRESENCE_SECONDS", 10))
ATTENTION_THRESHOLD = float(os.getenv("ATTENTION_THRESHOLD", 0.60))
AUDIO_RMS_THRESHOLD = float(os.getenv("AUDIO_RMS_THRESHOLD", 0.015))
ENGAGEMENT_UPDATE_INTERVAL = int(os.getenv("ENGAGEMENT_UPDATE_INTERVAL", 2))

# Offline and Ethical Privacy Preserving Settings
ENABLE_OFFLINE_MODE = os.getenv("ENABLE_OFFLINE_MODE", "True").lower() == "true"
PRIVACY_PRESERVE_BLUR = False  # Option to blur raw faces in logs
