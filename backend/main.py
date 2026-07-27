import os
import tensorflow as tf
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from backend.config import FRONTEND_URL, MODEL_PATH, STATIC_DIR, HOST, PORT, METADATA_PATH, PROJECT_ROOT
from backend.database.connection import engine, Base
from backend.api.routes import router
from backend.utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    logger.info("Application starting up...")
    
    # 1. Initialize Database Tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified/created successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize database tables: {e}", exc_info=True)
        
    # 2. Load Deep Learning Model once in memory
    app.state.model = None
    if os.path.exists(MODEL_PATH):
        try:
            logger.info(f"Loading Keras deep learning model from: {MODEL_PATH}")
            # Ensure TensorFlow does not allocate all GPU memory (if running on GPU)
            gpus = tf.config.experimental.list_physical_devices('GPU')
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
                
            app.state.model = tf.keras.models.load_model(MODEL_PATH)
            
            # Read metadata for dynamic naming
            import json
            arch = "Keras"
            if os.path.exists(METADATA_PATH):
                try:
                    with open(METADATA_PATH, "r") as f:
                        meta = json.load(f)
                        arch = meta.get("model_architecture", "Keras")
                except Exception:
                    pass
            logger.info(f"{arch} model loaded successfully.")
        except Exception as e:
            logger.critical(f"Failed to load Keras model from {MODEL_PATH}: {e}", exc_info=True)
    else:
        logger.warning(
            f"Trained model not found at '{MODEL_PATH}'. "
            "Please run trained_model/train.py to generate it, or check installation directory. "
            "Inference requests will fail until model is placed."
        )
        
    yield
    
    # --- Shutdown ---
    logger.info("Application shutting down...")

app = FastAPI(
    title="AI Medical Intelligence Platform API",
    description="Production-grade API for Chest X-ray Pneumonia Detection with Grad-CAM and Gemini report generation.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
# Standard CORS middleware enabling cross-origin requests from the React frontend
origins = [
    FRONTEND_URL,
    "http://localhost:5173",  # fallback local Vite port
    "http://127.0.0.1:5173",  # 127.0.0.1 loopback Vite port
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Directory
# Used to serve original uploads and Grad-CAM results
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Register API Router
app.include_router(router, prefix="/api")

# Serve Frontend Static Files (Vite Production Build)
FRONTEND_DIST_DIR = os.path.join(PROJECT_ROOT, "frontend", "dist")
if os.path.exists(FRONTEND_DIST_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST_DIR, html=True), name="frontend")

# Global Exception Handlers for Robust Error Responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception in request {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please check application logs."}
    )

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Running uvicorn server on {HOST}:{PORT}")
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)
