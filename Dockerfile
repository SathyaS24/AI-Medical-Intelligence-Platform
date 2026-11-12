# ==========================================
# Stage 1: Build the React/TypeScript Frontend
# ==========================================
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npx vite build

# ==========================================
# Stage 2: Create the production FastAPI Backend
# ==========================================
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies for OpenCV and Healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ ./backend

# Copy pre-trained model and metadata
COPY trained_model/ ./trained_model

# Copy built frontend assets to be served by FastAPI
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Expose default backend port
EXPOSE 8000

# Set default production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL=sqlite:///./backend/database/predictions.db \
    PORT=8000 \
    HOST=0.0.0.0 \
    CONFIDENCE_THRESHOLD=0.70 \
    LOG_LEVEL=INFO

# Health check dynamically bound to $PORT (supporting both local Docker and Render)
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8000}/api/health || exit 1

# Start the application dynamically evaluating Render's assigned $PORT
CMD ["sh", "-c", "python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
