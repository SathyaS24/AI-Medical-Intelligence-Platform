from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from datetime import datetime, timezone
from backend.database.connection import Base

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    prediction_class = Column(String, nullable=False)  # 'PNEUMONIA' or 'NORMAL'
    confidence = Column(Float, nullable=False)
    inference_time = Column(Float, nullable=False)  # In seconds
    report_content = Column(Text, nullable=False)  # JSON-serialized report dictionary
    gradcam_path = Column(String, nullable=False)  # Path to saved Grad-CAM image
    original_path = Column(String, nullable=False)  # Path to saved original uploaded image
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
