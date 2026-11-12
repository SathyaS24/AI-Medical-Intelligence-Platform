# Production Deployment Guide: AI Medical Intelligence Platform (MedTool)

This guide provides end-to-end instructions for deploying the **AI Medical Intelligence Platform (MedTool)** to production on [Render](https://render.com) using Docker, with support for deep learning inference, Grad-CAM visual explainability, Gemini LLM clinical report generation, and persistent database storage.

---

## 1. Project Architecture

The platform is designed as a unified single-container production architecture:

```mermaid
flowchart TD
    User([User Browser]) -->|HTTPS / Port 443| RenderProxy[Render Edge TLS Proxy]
    RenderProxy -->|HTTP / Dynamic $PORT| FastAPIApp[FastAPI Production Server]
    
    subgraph Container [Docker Production Container]
        FastAPIApp -->|Serves Static Dist| ReactUI[React + Vite SPA Frontend]
        FastAPIApp -->|API Routes /api/*| APIRouter[FastAPI REST API]
        APIRouter -->|Inference Pass| KerasModel[MobileNetV2 / EfficientNetB0 Keras 3 Model]
        APIRouter -->|Gradient Calculation| GradCAM[Grad-CAM Heatmap Engine]
        APIRouter -->|Async Clinical Summary| GeminiLLM[Gemini 1.5 Pro / Flash API]
        APIRouter -->|ORM Operations| Database[(PostgreSQL or SQLite)]
    end

    GeminiLLM -.->|External API Call| GoogleAI[Google Gemini AI Cloud]
    Database -.->|Persistent Storage| ManagedDB[(Render Managed PostgreSQL or Persistent Disk)]
```

- **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS + Lucide Icons. Built into static assets (`frontend/dist`) and served directly by FastAPI via custom `SPAStaticFiles` routing.
- **Backend:** Python 3.10 + FastAPI + Uvicorn + SQLAlchemy 2.0.
- **Deep Learning Model:** Pre-trained binary classification model (`best_model.keras`) trained on chest radiographs for normal vs. pneumonia classification.
- **Explainable AI (XAI):** Custom Grad-CAM engine supporting Keras 3 / TensorFlow 2.16+ Sequential architectures with nested convolutional backbones.
- **Clinical Report Engine:** Google Gemini API integration (`gemini-1.5-flash`) with automatic fallback to a deterministic medical report generator.
- **Database & Persistence:** SQLite for local development; Render Managed PostgreSQL (recommended for free tier) or Render Persistent Disks for production data retention.

---

## 2. Prerequisites

Before deploying to Render, ensure you have:

1. **GitHub Account:** Access to your GitHub repository ([SathyaS24/AI-Medical-Intelligence-Platform](https://github.com/SathyaS24/AI-Medical-Intelligence-Platform)).
2. **Render Account:** Sign up for free at [render.com](https://render.com).
3. **Google Gemini API Key:** Obtain an API key from [Google AI Studio](https://aistudio.google.com/).
4. **Git:** Installed on your local machine to commit and push changes.
5. **(Optional) Docker Desktop:** If you wish to build and test the container locally.

---

## 3. Environment Variables Reference

Configure the following environment variables. In Render, sensitive secrets (`GEMINI_API_KEY`, `DATABASE_URL`) are entered securely via the dashboard and are never committed to Git.

| Variable Name | Type | Required | Default Value | Description |
| :--- | :--- | :--- | :--- | :--- |
| `GEMINI_API_KEY` | Secret | Optional | *Empty* | Google Gemini API key for dynamic clinical reports. If omitted, the deterministic medical report generator is used. |
| `DATABASE_URL` | Config/Secret | Optional | `sqlite:///./backend/database/predictions.db` | SQLAlchemy connection string. Set to Render PostgreSQL `postgresql://...` for persistent history. |
| `CONFIDENCE_THRESHOLD` | Config | Optional | `0.70` | Threshold (0.0 - 1.0) defining high vs. low confidence predictions. |
| `PORT` | Config | Auto | `10000` (Render) / `8000` (Local) | Dynamic port assigned by Render. The container binds dynamically to `${PORT:-8000}`. |
| `HOST` | Config | Optional | `0.0.0.0` | Container host binding address. |
| `FRONTEND_URL` | Config | Optional | `*` | Allowed CORS origins (comma-separated or `*` for public access). |
| `LOG_LEVEL` | Config | Optional | `INFO` | Application log verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |

---

## 4. Local Deployment Instructions

### Option A: Using Docker & Docker Compose (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SathyaS24/AI-Medical-Intelligence-Platform.git
   cd AI-Medical-Intelligence-Platform
   ```

2. **Configure local environment:**
   ```bash
   cp .env.example .env
   # Edit .env and set your GEMINI_API_KEY if available
   ```

3. **Build and launch with Docker Compose:**
   ```bash
   docker compose up --build
   ```

4. **Access the application:**
   - Web Platform: [http://localhost:8000](http://localhost:8000)
   - Swagger API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Health Check: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### Option B: Using Standalone Docker Build

1. **Build Docker image:**
   ```bash
   docker build -t medical-ai-platform:latest .
   ```

2. **Run container:**
   ```bash
   docker run -d -p 8000:8000 \
     -e GEMINI_API_KEY="your_gemini_api_key_here" \
     --name medtool-app \
     medical-ai-platform:latest
   ```

---

## 5. Render Account Setup

1. Navigate to [dashboard.render.com](https://dashboard.render.com/) and register or sign in.
2. Link your **GitHub** account to Render in **Account Settings > Connected Accounts** with permissions to access your repository.

---

## 6. GitHub Repository Connection

1. On your local machine, ensure all production changes are committed and pushed to GitHub:
   ```bash
   git status
   git add .
   git commit -m "Configure production Dockerfile, render.yaml, and persistence for Render deployment"
   git push origin main
   ```
2. In the Render Dashboard, click **New +** in the top navigation bar.
3. Select **Web Service**.
4. Choose **Build and deploy from a Git repository**.
5. Select `SathyaS24/AI-Medical-Intelligence-Platform` from your repository list and click **Connect**.

---

## 7. Render Web Service Configuration

Configure the web service with the following settings:

| Setting | Value |
| :--- | :--- |
| **Name** | `ai-medical-intelligence-platform` (or your preferred name) |
| **Region** | `Oregon (US West)` or `Frankfurt (EU Central)` |
| **Branch** | `main` |
| **Root Directory** | *(Leave empty)* |
| **Runtime** | **Docker** |
| **Dockerfile Path** | `./Dockerfile` |
| **Docker Build Context** | `.` |
| **Instance Type** | **Starter** (recommended: 1 GB RAM minimum for TensorFlow) or **Free** |

> [!IMPORTANT]
> **Memory Requirements:** TensorFlow 2.16+ and Keras model inference require approximately 450 MB – 650 MB of RAM during image analysis and Grad-CAM generation. The Render **Free Tier** provides 512 MB RAM, which may run close to memory limits under peak loads. For production reliability, the **Starter Plan** (512 MB – 1 GB RAM) is recommended.

---

## 8. Secrets and Environment Variables Configuration

In the Render Dashboard under **Environment Variables**, add:

1. `GEMINI_API_KEY` = `your_actual_google_gemini_api_key`
2. `CONFIDENCE_THRESHOLD` = `0.70`
3. `FRONTEND_URL` = `*`
4. `LOG_LEVEL` = `INFO`
5. `PORT` = `10000` *(Render sets this automatically, but defining it ensures consistency)*
6. `HOST` = `0.0.0.0`

Click **Save Changes**.

---

## 9. Persistent Storage Configuration

### Strategy A: Free Tier Persistent Database (Render Managed PostgreSQL)

Render Free Tier Web Services do **not** support Persistent Disks. When a free web service restarts or sleeps, its local filesystem (including SQLite files) resets. 

To achieve 100% persistent prediction history on the Free Tier:
1. In Render Dashboard, click **New +** > **PostgreSQL**.
2. Set Name to `medical-platform-db` and select the **Free** instance type.
3. Once provisioned, copy the **Internal Database URL** (e.g., `postgres://user:pass@host/dbname`).
4. In your Web Service settings, add the environment variable:
   - `DATABASE_URL` = `<Internal Database URL>`
   *(Note: The platform automatically converts `postgres://` to `postgresql://` for SQLAlchemy 2.0 compatibility).*

### Strategy B: Paid Plan Persistent Disk (SQLite Storage)

If you use a Render Paid Plan (Starter or higher), you can attach a Persistent Disk:
1. In your Web Service settings, go to the **Disks** section.
2. Click **Add Disk**:
   - **Name:** `medical-storage`
   - **Mount Path:** `/app/backend/database`
   - **Size:** `1 GB` (or more)
3. Keep default `DATABASE_URL=sqlite:///./backend/database/predictions.db`. All SQLite database records will persist across redeployments and restarts.

---

## 10. Automated Deployment via Blueprint (render.yaml)

Alternatively, you can deploy using Render's Infrastructure-as-Code:
1. In Render Dashboard, click **New +** > **Blueprint**.
2. Connect your repository `SathyaS24/AI-Medical-Intelligence-Platform`.
3. Render will automatically detect `render.yaml` located in the root of the repository.
4. Fill in the prompted secret `GEMINI_API_KEY` and click **Apply**.

---

## 11. Post-Deployment Verification Tests

Once Render shows **Deploy Succeeded** and the service URL becomes active (`https://<service-name>.onrender.com`):

1. **Verify Health Endpoint:**
   ```bash
   curl -i https://<service-name>.onrender.com/api/health
   ```
   *Expected response:*
   ```json
   {
     "status": "healthy",
     "model_loaded": true,
     "database_connected": true,
     "llm_available": true,
     "version": "1.0.0"
   }
   ```

2. **Verify Interactive API Documentation:**
   Open `https://<service-name>.onrender.com/docs` in your browser. Verify that all endpoints (`/api/predict`, `/api/history`, `/api/dashboard/stats`, `/api/health`) are documented.

3. **Verify Web User Interface:**
   Navigate to `https://<service-name>.onrender.com`:
   - Verify the homepage loads with dashboard statistics.
   - Click **Analyze X-Ray** (`/analyze`).
   - Upload a sample chest X-ray image (`.jpg`, `.jpeg`, or `.png`).
   - Verify that:
     1. Prediction class (`NORMAL` or `PNEUMONIA`) appears with confidence percentage.
     2. Grad-CAM visual heatmap overlay renders alongside the original radiograph.
     3. Clinical report displays the AI interpretation, possible findings, and recommendations.
     4. Prominent clinical disclaimer is displayed at the bottom of the page.
   - Navigate to **Prediction History** (`/history`) and verify the scan record is saved.

---

## 12. Troubleshooting Common Issues

### Issue 1: Port Scan Timeout on Render
- **Symptom:** Render build succeeds, but deployment fails with `Timed out waiting for port 10000 to respond`.
- **Cause:** Application hardcoded to port 8000 instead of listening on Render's dynamic `$PORT`.
- **Resolution:** The updated `Dockerfile` dynamically launches uvicorn using:
  ```dockerfile
  CMD ["sh", "-c", "python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
  ```

### Issue 2: Health Check Returns 500 (`SELECT 1` Error)
- **Symptom:** `/api/health` throws `ArgumentError: Textual SQL expression 'SELECT 1' should be explicitly declared as text('SELECT 1')`.
- **Cause:** SQLAlchemy 2.0 requires raw SQL strings to be wrapped with `text()`.
- **Resolution:** Fixed in `backend/api/routes.py` with `from sqlalchemy import text` and `db.execute(text("SELECT 1"))`.

### Issue 3: Grad-CAM Fails with Keras 3 Sequential Models
- **Symptom:** Logs show `AttributeError: The layer sequential has never been called and thus has no defined output`.
- **Cause:** Keras 3 changes multi-output model extraction for Sequential wrappers containing nested functional backbones.
- **Resolution:** Fixed in `backend/xai/gradcam.py` by using dual-stage forward passes on the convolutional backbone and classification head.

### Issue 4: 404 on Direct Navigation / Refresh to React Routes (`/analyze`, `/history`)
- **Symptom:** Navigating directly to `https://<service-name>.onrender.com/analyze` gives a `404 Not Found` error.
- **Cause:** Client-side SPA routing requires non-asset paths to serve `index.html`.
- **Resolution:** Implemented `SPAStaticFiles` in `backend/main.py` which transparently falls back to `index.html` for deep links.

### Issue 5: Render Free Tier Web Service Sleeps
- **Symptom:** First request after 15 minutes of inactivity takes 30-50 seconds to respond.
- **Cause:** Render Free Tier spins down inactive web services.
- **Resolution:** This is standard behavior on Render's free tier. The container will automatically spin up on the first inbound HTTP request. For 24/7 instant response, upgrade the web service to Render's **Starter Plan** ($7/mo).

---

## 13. Clinical Safety Notice

> [!CAUTION]
> **Medical Diagnostic Disclaimer:** The AI Medical Intelligence Platform is intended strictly for experimental, research, and educational purposes. It is **not** an FDA-approved diagnostic medical device and must never be used as a substitute for professional clinical judgment, radiology consultation, or laboratory diagnosis.
