# MedTool AI Medical Intelligence Platform

A production-quality, end-to-end medical image analysis platform designed for front-line clinical decision support. The platform performs deep learning-based frontal chest radiograph classification (Pneumonia Detection), generates spatial explainability heatmaps (Grad-CAM), and automates clinical reporting using the Gemini API.

---

## 1. Project Overview & System Architecture

This platform provides a complete clinical workflow bridging deep learning models, explainability maps, and generative reporting. 

### End-to-End Inference Pipeline

```text
Image Upload
      │
      ▼
File Validation (Type: JPG/JPEG/PNG, Size: < 10MB)
      │
      ▼
Image Preprocessing (RGB conversion, Resize to 224x224, Pixel normalization, NumPy array, Batch padding)
      │
      ▼
EfficientNetB0 Prediction (In-memory model loaded at startup)
      │
      ▼
Confidence Score Calculation & Threshold Evaluation (Configurable threshold, default 70%)
      │
      ▼
Grad-CAM Generation (Heatmap overlay on original image)
      │
      ▼
LLM Medical Report (Gemini API or Deterministic Local Report)
      │
      ▼
Save Prediction to Database (SQLAlchemy ORM + SQLite default)
      │
      ▼
Display Results in Frontend (React + TS dashboard)
```

---

## 2. Technology Stack

* **Frontend:** React, Vite, TypeScript, React Router, Axios, Material UI (MUI), jsPDF.
* **Backend:** FastAPI, Uvicorn, SQLAlchemy ORM, Pydantic, Python-Multipart.
* **AI/ML & XAI:** TensorFlow/Keras, EfficientNetB0, OpenCV, NumPy, Pillow, Scikit-learn, Matplotlib.
* **LLM Integration:** Gemini API (via `google-generativeai`) with deterministic local templates.
* **Database:** SQLite (default local development), architected database-agnostically via SQLAlchemy ORM (compatible with PostgreSQL/MySQL).
* **Containerization:** Multi-stage Docker, Docker Compose, container health checks.

---

## 3. Directory Structure

```text
medical-ai-platform/
├── frontend/
│   ├── src/
│   │   ├── components/         # Layout, GradCamSlider
│   │   ├── pages/              # Dashboard, Analyze, History
│   │   ├── services/           # Axios api client
│   │   ├── App.tsx             # Clinical theme provider and routes
│   │   ├── index.css
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── backend/
│   ├── api/
│   │   └── routes.py           # /predict, /history, /health
│   ├── database/
│   │   └── connection.py       # SQLAlchemy setup, session injection
│   ├── models/
│   │   └── prediction.py       # SQL database entities
│   ├── schemas/
│   │   └── prediction.py       # Pydantic validation schemas
│   ├── xai/
│   │   └── gradcam.py          # TF gradient tape Grad-CAM generator
│   ├── llm/
│   │   └── generator.py        # Gemini API report compiler
│   ├── utils/
│   │   └── logger.py           # Rotating file handler configuration
│   ├── static/                 # Served output assets
│   ├── uploads/                # Temporary raw uploads
│   ├── config.py               # Env configurations and directories
│   └── main.py                 # FastAPI application and lifespan caching
├── trained_model/
│   ├── train.py                # EfficientNetB0 training pipeline
│   ├── best_model.keras        # Generated trained model weights
│   └── model_metadata.json     # Model version and hyperparameter history
├── logs/
│   └── application.log         # Rotated server activity logs
├── evaluation/                 # Metrics graphs and reports
│   ├── classification_report.txt
│   ├── confusion_matrix.png
│   └── training_history.png
├── Dockerfile                  # Multi-stage production build
├── docker-compose.yml          # Container stack orchestrator
├── requirements.txt            # Python dependencies
├── README.md
├── Project_Report.pdf          # Full technical design documentation
└── generate_report_pdf.py      # Report PDF compiler script
```

---

## 4. Local Installation & Configuration

### Prerequisites
* Python 3.10+
* Node.js 18+
* npm 9+
* (Optional) Docker & Docker Compose

### Step 1: Environment Variables
Create a `.env` file in the root directory (based on `.env.example`):
```bash
DATABASE_URL=sqlite:///./predictions.db
GEMINI_API_KEY=your_gemini_api_key_here
CONFIDENCE_THRESHOLD=0.70
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
FRONTEND_URL=http://localhost:5173
```
*Note: If `GEMINI_API_KEY` is omitted, the backend falls back to the **deterministic local report generator**.*

### Step 2: Model Setup
1. **Dataset Location:** Download the official [Chest X-ray Images (Pneumonia) dataset from Kaggle](https://www.kaggle.com/datasets/paultimothymccarty/chest-xray-pneumonia) and extract it to `trained_model/dataset/`.
2. **Train Model:** Run the training script:
   ```bash
   python trained_model/train.py
   ```
   *Note: If the dataset is not found in `trained_model/dataset`, the training script will halt gracefully, print instructions, and initialize a baseline model at `trained_model/best_model.keras` so the application runs immediately.*

### Step 3: Run Backend
```bash
pip install -r requirements.txt
python backend/main.py
```
The backend API is now running at `http://localhost:8000`. Exposes:
* Swagger Documentation: `http://localhost:8000/docs`
* ReDoc Documentation: `http://localhost:8000/redoc`

### Step 4: Run Frontend
```bash
cd frontend
npm install
npm run dev
```
Open your browser and navigate to `http://localhost:5173` to access the platform.

---

## 5. Docker Deployment

To run the entire system inside Docker containers with single-command startup:
```bash
docker-compose up --build
```
This builds a multi-stage production container:
1. Builds the React frontend using Node.js.
2. Packages the backend using a slim Python image, mounting the static React files to be served directly from FastAPI.
3. Incorporates a database volume for SQLite persistence, directory bindings for uploaded files, and rotating log exports.
4. Activates a `HEALTHCHECK` matching the API `/health` route.

Visit `http://localhost:8000` to view the running app.

---

## 6. Deep Learning Training & Evaluation Details

The training pipeline uses transfer learning via **EfficientNetB0**.
* **Split Strategy:** Strict 70:15:15 partitioning (Training, Validation, Testing). The test set is fully isolated.
* **Callbacks:** Early Stopping (patience=4), ReduceLROnPlateau (patience=2, decay=0.5), and ModelCheckpoint tracking `val_loss`.
* **Outputs:** Training outputs evaluation graphs (history, confusion matrices) and reports directly into the `evaluation/` directory.

---

## 7. API Endpoints

### `POST /api/predict`
Accepts a chest radiograph image, performs inference, generates Grad-CAM overlays, calls Gemini (or local templates), and logs findings.
* **Request Validation:** Only accepts JPG, JPEG, and PNG images under 10 MB.
* **Response Format:**
```json
{
  "id": 15,
  "filename": "chest_xray_sample.jpeg",
  "prediction": "PNEUMONIA",
  "confidence": 0.982,
  "confidence_rating": "High Confidence",
  "inference_time": 0.642,
  "gradcam_image": "/static/gradcam/abc123.png",
  "original_image": "/static/original/abc123.png",
  "report": {
    "prediction": "PNEUMONIA",
    "confidence": "98.2%",
    "summary": "AI prediction indicates signs of consolidation in the lungs.",
    "clinical_interpretation": "Increased opacities observed in lower lobes...",
    "possible_findings": "Consolidation, infiltrate.",
    "recommended_next_steps": "1. Radiologist validation...",
    "disclaimer": "For educational purposes only..."
  },
  "created_at": "2026-07-22T18:40:00.123456Z"
}
```

### `GET /api/history`
Returns a list of all past predictions, orderable by timestamp, supporting string filters for filename and prediction class.

### `DELETE /api/history/{id}`
Removes the database log and purges associated image files from disk.

### `GET /api/health`
Returns system component states:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "database_connected": true,
  "llm_available": true,
  "version": "1.0.0"
}
```

---

## 8. Troubleshooting Guide

* **Model Loading Errors:** Ensure `trained_model/best_model.keras` is generated. If missing, run `python trained_model/train.py` to trigger the baseline model builder.
* **OpenCV Errors (Linux/Docker):** If you run in a custom Linux environment, use `pip install opencv-python-headless` instead of standard OpenCV to avoid graphical library dependencies.
* **Database Locked Warnings:** Because SQLite is a file-based database, FastAPI configuration sets `check_same_thread=False` to handle concurrent async requests. For high-volume multi-user environments, update `DATABASE_URL` in `.env` to point to a dedicated PostgreSQL instance.
