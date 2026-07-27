import json
import os
from typing import Dict, Any
from backend.config import GEMINI_API_KEY, CONFIDENCE_THRESHOLD
from backend.utils.logger import logger

# Try importing google.generativeai. If not installed, we fallback gracefully.
HAS_GENAI = False
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    logger.warning("google-generativeai package not installed. Using local generator by default.")

def get_deterministic_report(prediction: str, confidence: float) -> Dict[str, str]:
    """
    Generates a high-quality, structured clinical report locally.
    Used as the default when Gemini is offline or unconfigured.
    """
    confidence_pct = f"{confidence * 100:.1f}%"
    is_low_confidence = confidence < CONFIDENCE_THRESHOLD
    
    report = {
        "prediction": prediction,
        "confidence": confidence_pct,
        "summary": "",
        "clinical_interpretation": "",
        "possible_findings": "",
        "recommended_next_steps": "",
        "disclaimer": "This platform is for educational and research purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider."
    }
    
    warning_text = ""
    if is_low_confidence:
        warning_text = " [ALERT: LOW CONFIDENCE PREDICTION] "
        
    if prediction == "PNEUMONIA":
        report["summary"] = (
            f"The deep learning model detected signs of consolidation consistent with pneumonia"
            f" with a confidence of {confidence_pct}.{warning_text}"
        )
        report["clinical_interpretation"] = (
            f"Visual inspection of the chest radiograph suggests increased opacity and potential infiltrate/consolidation "
            f"in localized lung regions. Grad-CAM visual heatmaps highlight these regions as highly influential in the prediction. "
            f"This presentation is indicative of active pulmonary infection."
        )
        if is_low_confidence:
            report["clinical_interpretation"] += (
                f"\nNOTE: The inference confidence of {confidence_pct} falls below the established clinical threshold of "
                f"{CONFIDENCE_THRESHOLD * 100:.1f}%. Findings must be interpreted with high caution."
            )
        report["possible_findings"] = "Lobary consolidation, interstitial infiltrates, airspace opacity, pleural effusion."
        report["recommended_next_steps"] = (
            "1. Urgent clinical correlation by a board-certified radiologist or primary care physician.\n"
            "2. Diagnostic confirmation using secondary clinical indicators (sputum culture, blood count, temperature).\n"
            "3. Consideration for follow-up high-resolution CT scan of the chest if symptoms persist."
        )
    else:  # NORMAL
        report["summary"] = (
            f"The deep learning model detected no significant signs of pneumonia (Normal Lung Fields)"
            f" with a confidence of {confidence_pct}.{warning_text}"
        )
        report["clinical_interpretation"] = (
            f"The lung fields appear clear and well-inflated. No clear evidence of focal consolidation, "
            f"congestive heart failure, or significant pleural effusions is identified. The cardiothoracic "
            f"ratio appears within normal physiological limits."
        )
        if is_low_confidence:
            report["clinical_interpretation"] += (
                f"\nNOTE: The inference confidence of {confidence_pct} is below the clinical threshold of "
                f"{CONFIDENCE_THRESHOLD * 100:.1f}%. Normal lung classification should be validated clinically."
            )
        report["possible_findings"] = "Clear lung fields, no active cardiopulmonary disease."
        report["recommended_next_steps"] = (
            "1. Standard clinical monitoring. No immediate radiology follow-up is recommended based on this screen.\n"
            "2. If clinical symptoms (e.g., persistent cough, fever, dyspnea) are present, seek professional clinical correlation regardless of the screen result."
        )
        
    return report

async def generate_medical_report(prediction: str, confidence: float) -> Dict[str, str]:
    """
    Generates a structured medical report. Tries to use Gemini API,
    falling back to the deterministic local report generator on error or absence of API key.
    """
    is_low_confidence = confidence < CONFIDENCE_THRESHOLD
    confidence_pct = f"{confidence * 100:.1f}%"
    
    # 1. Fallback immediately if no key or library
    if not GEMINI_API_KEY or not HAS_GENAI:
        logger.info("Gemini API key not configured or package missing. Generating local report.")
        return get_deterministic_report(prediction, confidence)
        
    try:
        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Build prompt
        prompt = f"""
        You are a board-certified radiologist and AI clinical advisor assistant.
        Generate a structured chest radiograph (X-ray) medical report based on the following AI classification results:
        - Predicted Condition: {prediction}
        - Confidence Score: {confidence_pct}
        - Clinical Threshold: {CONFIDENCE_THRESHOLD * 100:.1f}%
        - Is Low Confidence: {is_low_confidence}
        
        Provide the report strictly as a valid JSON object matching the following structure. Do not output markdown other than the JSON block. Do not write any conversational text before or after the JSON.
        
        {{
          "prediction": "{prediction}",
          "confidence": "{confidence_pct}",
          "summary": "Short 1-2 sentence AI-generated summary of findings.",
          "clinical_interpretation": "A professional clinical description of what features (opacities, infiltration, consolidation, or clear fields) are associated with the prediction. Mention Grad-CAM highlighting if applicable. {"Flag this prediction as Low Confidence and urge caution because it is below the threshold of " + str(CONFIDENCE_THRESHOLD*100) + "%" if is_low_confidence else ""}",
          "possible_findings": "List of possible radiologic findings (comma separated).",
          "recommended_next_steps": "Numbered clinical suggestions for next steps (e.g. clinical correlation, PCR test, physician consult, chest CT).",
          "disclaimer": "This platform is for educational and research purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider."
        }}
        """
        
        # Use gemini-1.5-flash as the fast, lightweight model
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Parse JSON response
        report_data = json.loads(response.text.strip())
        
        # Verify keys are present
        required_keys = ["prediction", "confidence", "summary", "clinical_interpretation", "possible_findings", "recommended_next_steps", "disclaimer"]
        if all(k in report_data for k in required_keys):
            logger.info("Successfully generated report using Gemini API.")
            return report_data
        else:
            raise ValueError("Gemini response missing required JSON fields.")
            
    except Exception as e:
        logger.error(f"Failed to generate report with Gemini API: {e}. Falling back to local report.")
        return get_deterministic_report(prediction, confidence)
