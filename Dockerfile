# ==========================================
# Stage 1: Build the React/TypeScript Frontend
# ==========================================
FROM node:18-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ==========================================
# Stage 2: Create the production FastAPI Backend
# ==========================================
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies for OpenCV and Healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
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

# Expose backend port
EXPOSE 8000

# Set environment variables
ENV DATABASE_URL=sqlite:///./backend/predictions.db
ENV PORT=8000
ENV HOST=0.0.0.0

# Health check to ensure API is responsive
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# Start the application
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
