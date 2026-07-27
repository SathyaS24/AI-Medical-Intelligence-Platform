import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./predictions.db")

# LLM Config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ML Config
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.70"))
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
PORT = int(os.getenv("PORT", "8000"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Ensure directories exist
for directory in [UPLOAD_DIR, STATIC_DIR, GRADCAM_DIR, ORIGINAL_DIR, LOG_DIR]:
    os.makedirs(directory, exist_ok=True)
