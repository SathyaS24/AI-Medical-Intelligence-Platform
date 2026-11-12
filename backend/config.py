import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Database Configuration
DEFAULT_DB_DIR = os.path.join(BASE_DIR, "database")
DEFAULT_DB_PATH = os.path.join(DEFAULT_DB_DIR, "predictions.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# Render provides postgres:// connection URLs which SQLAlchemy 1.4+ / 2.0 rejects; convert to postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# LLM Config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ML Config
try:
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.70"))
    if not (0.0 <= CONFIDENCE_THRESHOLD <= 1.0):
        CONFIDENCE_THRESHOLD = 0.70
except (ValueError, TypeError):
    CONFIDENCE_THRESHOLD = 0.70

MODEL_PATH = os.path.join(PROJECT_ROOT, "trained_model", "best_model.keras")
METADATA_PATH = os.path.join(PROJECT_ROOT, "trained_model", "model_metadata.json")

# Directories
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
STATIC_DIR = os.path.join(BASE_DIR, "static")
GRADCAM_DIR = os.path.join(STATIC_DIR, "gradcam")
ORIGINAL_DIR = os.path.join(STATIC_DIR, "original")
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")

# Server Config
HOST = os.getenv("HOST", "0.0.0.0")
try:
    PORT = int(os.getenv("PORT", "8000"))
except (ValueError, TypeError):
    PORT = 8000

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Ensure directories exist
for directory in [UPLOAD_DIR, STATIC_DIR, GRADCAM_DIR, ORIGINAL_DIR, LOG_DIR, DEFAULT_DB_DIR]:
    os.makedirs(directory, exist_ok=True)
