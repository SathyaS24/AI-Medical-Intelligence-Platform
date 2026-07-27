from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, Optional

class ReportContentSchema(BaseModel):
    prediction: str
    confidence: str
    summary: str
    clinical_interpretation: str
    possible_findings: str
    recommended_next_steps: str
    disclaimer: str

class PredictionResponse(BaseModel):
    id: int
    filename: str
    prediction: str = Field(..., description="NORMAL or PNEUMONIA")
    confidence: float
    confidence_rating: str = Field(..., description="High Confidence or Low Confidence")
    inference_time: float
    gradcam_image: str
    original_image: str
    report: ReportContentSchema
    created_at: datetime

    class Config:
        from_attributes = True

class PredictionHistoryItem(BaseModel):
    id: int
    filename: str
    prediction: str
    confidence: float
    confidence_rating: str
    inference_time: float
    created_at: datetime

    class Config:
        from_attributes = True

class DashboardStatsResponse(BaseModel):
    total_predictions: int
    pneumonia_cases: int
    normal_cases: int
    average_confidence: float
    latest_prediction_time: Optional[datetime] = None

class HealthCheckResponse(BaseModel):
    status: str
    model_loaded: bool
    database_connected: bool
    llm_available: bool
    version: str
