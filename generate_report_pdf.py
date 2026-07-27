import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Suppress headers/footers on cover page
        if self._pageNumber == 1:
            self.restoreState()
            return
            
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header
        self.drawString(54, 750, "AI Medical Intelligence Platform — Technical Project Report")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 742, 612 - 54, 742)
        
        # Footer
        self.line(54, 55, 612 - 54, 55)
        self.drawString(54, 42, "CONFIDENTIAL — CLINICAL EVALUATION WORK")
        self.drawRightString(612 - 54, 42, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def create_project_report(output_filename="Project_Report.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54,  # 0.75 in
        rightMargin=54,
        topMargin=72,   # 1.0 in
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=colors.HexColor("#0f172a"),
        alignment=0,
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=colors.HexColor("#0891b2"),
        alignment=0,
        spaceAfter=40
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=20,
        spaceAfter=12,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0891b2"),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=10
    )
    
    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f8fafc"),
        borderColor=colors.HexColor("#e2e8f0"),
        borderWidth=0.5,
        borderPadding=6,
        spaceAfter=12
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=6
    )

    story = []
    
    # ------------------ COVER PAGE ------------------
    story.append(Spacer(1, 100))
    story.append(Paragraph("AI MEDICAL INTELLIGENCE PLATFORM", title_style))
    story.append(Paragraph("Production-Grade Chest X-Ray Pneumonia Detection System<br/>incorporating EfficientNetB0, Grad-CAM Explainable AI (XAI), and Gemini LLM reporting.", subtitle_style))
    
    story.append(Spacer(1, 120))
    
    metadata_data = [
        [Paragraph("<b>Candidate Role:</b>", body_style), Paragraph("Senior AI/ML & Full-Stack Engineer", body_style)],
        [Paragraph("<b>Target Domain:</b>", body_style), Paragraph("Digital Health & Intelligent Radiology Diagnostics", body_style)],
        [Paragraph("<b>Core Stack:</b>", body_style), Paragraph("FastAPI, React, TypeScript, TensorFlow, SQLAlchemy, SQLite, Docker", body_style)],
        [Paragraph("<b>Document Version:</b>", body_style), Paragraph("1.0.0 (Production Release)", body_style)],
        [Paragraph("<b>Submission Date:</b>", body_style), Paragraph("July 22, 2026", body_style)]
    ]
    metadata_table = Table(metadata_data, colWidths=[1.5*inch, 4.5*inch])
    metadata_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(metadata_table)
    story.append(PageBreak())
    
    # ------------------ SECTION 1 ------------------
    story.append(Paragraph("1. Executive Summary & Objectives", h1_style))
    story.append(Paragraph(
        "This project reports on the technical design and architectural execution of the MedTool AI Medical Intelligence Platform. "
        "The system provides a production-grade, end-to-end intelligent pipeline that accepts frontal chest radiographs, "
        "performs deep learning classification to identify features associated with active pulmonary pneumonia, generates "
        "a visual heatmap highlighting diagnostic focal areas using Grad-CAM, and orchestrates Gemini API to generate structured clinical reports.",
        body_style
    ))
    story.append(Paragraph("Key engineering objectives achieved include:", h2_style))
    story.append(Paragraph("• <b>Deep Learning Model Excellence:</b> Fine-tuned an EfficientNetB0 network using transfer learning to classify Normal vs. Pneumonia radiographs.", bullet_style))
    story.append(Paragraph("• <b>Explainable AI (XAI):</b> Developed custom Grad-CAM visualization to highlight specific spatial features that influenced network decisions, satisfying crucial clinical explainability constraints.", bullet_style))
    story.append(Paragraph("• <b>FastAPI REST Server:</b> Engineered a highly responsive async REST API, exposing endpoints for inference, database logs, and granular status checks.", bullet_style))
    story.append(Paragraph("• <b>Robust Frontend UI:</b> Built an interactive React dashboard with Vite and TypeScript, featuring a dual-layer cross-fade slider for original/Grad-CAM overlays, historical log inspection, and PDF report downloads.", bullet_style))
    
    # ------------------ SECTION 2 ------------------
    story.append(Paragraph("2. Dataset & Preprocessing Pipeline", h1_style))
    story.append(Paragraph(
        "The model is developed on the chest radiograph pneumonia dataset, consisting of anterior-posterior (AP) and posterior-anterior (PA) view X-ray scans of pediatric patients. "
        "Images are cataloged into NORMAL (no active infiltrates) and PNEUMONIA (visible pulmonary consolidation).",
        body_style
    ))
    story.append(Paragraph("To ensure zero bias and robust evaluation, we implement the following pipeline steps:", h2_style))
    story.append(Paragraph("1. <b>Strict 70:15:15 Split Strategy:</b> The dataset is partitioned into Training (70%), Validation (15%), and Testing (15%) splits. The test partition is held strictly separate and is never loaded during fitting or callback operations.", bullet_style))
    story.append(Paragraph("2. <b>Input Matrix Standardization:</b> Images are dynamically loaded, converted to 3-channel RGB, resized to 224x224 pixels, and normalized by dividing color channel values by 255.0 to map input pixel scalars to a [0.0, 1.0] float range.", bullet_style))
    story.append(Paragraph("3. <b>Online Augmentation:</b> During training, images are randomly subjected to horizontal flips and slight intensity adjustments to build structural invariance.", bullet_style))

    # ------------------ SECTION 3 ------------------
    story.append(Paragraph("3. Deep Learning Model Architecture", h1_style))
    story.append(Paragraph(
        "We implement <b>EfficientNetB0</b> as the primary classifier. It uses compound scaling to balance depth, width, and resolution, yielding superior feature representation with minimal model parameters. "
        "The architecture begins with pre-trained ImageNet weights, freezing the convolutional base during initial cycles. "
        "A customized classification head is appended:",
        body_style
    ))
    story.append(Paragraph(
        "<i>Input (224x224x3) → EfficientNetB0 Base → GlobalAveragePooling2D → Dense (128, ReLU) → Dropout (0.3) → Dense (1, Sigmoid)</i>",
        code_style
    ))
    story.append(Paragraph(
        "<b>Model Versioning & Version Control:</b> The training script outputs the optimized weights as <code>best_model.keras</code> alongside a structured <code>model_metadata.json</code>. "
        "This JSON files acts as a version-control log, tracking metrics (accuracy, recall, precision, F1), training timestamps, hyperparameters, and dataset parameters. "
        "<b>In-Memory Caching:</b> The FastAPI server imports the model once during lifespan startup. The cached model is held in memory and shared across requests, preventing redundant disk loads.",
        body_style
    ))
    
    story.append(PageBreak())

    # ------------------ SECTION 4 ------------------
    story.append(Paragraph("4. Explainable AI (Grad-CAM)", h1_style))
    story.append(Paragraph(
        "Medical AI systems require auditability. We implement <b>Gradient-weighted Class Activation Mapping (Grad-CAM)</b>. "
        "Grad-CAM uses the gradients of the target class score flowing into the final convolutional layer of the network "
        "(<code>top_activation</code> in EfficientNetB0) to produce a coarse localization map highlighting the regions in the image most relevant for prediction.",
        body_style
    ))
    story.append(Paragraph("The mathematical process is structured as follows:", h2_style))
    story.append(Paragraph("1. Extract the feature map activations \(A^k\) of the final conv layer and compute gradients of the class output score \(y^c\) with respect to the activations.", bullet_style))
    story.append(Paragraph("2. Compute the channel-wise importance weights: \(\alpha_k^c = \\frac{1}{Z} \sum_{i} \sum_{j} \\frac{\partial y^c}{\partial A_{i,j}^k}\).", bullet_style))
    story.append(Paragraph("3. Generate the heatmap via a weighted combination of feature maps filtered through a ReLU activation: \(L_{Grad-CAM}^c = ReLU(\sum_{k} \alpha_k^c A^k)\).", bullet_style))
    story.append(Paragraph("4. Resize the heatmap to the original image dimensions, normalize, and overlay using a JET colormap blend.", bullet_style))

    # ------------------ SECTION 5 ------------------
    story.append(Paragraph("5. LLM Clinical Reporting & Fallback", h1_style))
    story.append(Paragraph(
        "To compile findings into actionable clinical reports, the API hooks into the <b>Gemini API</b> (<code>gemini-1.5-flash</code>) using structured JSON prompts. "
        "If the API key is not configured, or if rate limits block the request, the backend automatically transitions to a "
        "<b>deterministic local report generator</b>. This generator utilizes pre-defined clinical templates based on the predicted class "
        "and confidence score, guaranteeing full pipeline reliability without breaking.",
        body_style
    ))
    story.append(Paragraph("<b>Confidence Threshold Constraint:</b> The application supports a configurable confidence threshold (default 70%). If a prediction falls below this setting, the report is annotated with a warning flagging it as a 'Low Confidence Prediction' and advising immediate physician verification.", body_style))

    # ------------------ SECTION 6 ------------------
    story.append(Paragraph("6. REST API Design & Database Schema", h1_style))
    story.append(Paragraph(
        "The backend is developed with <b>FastAPI</b>, offering asynchronous non-blocking routes and auto-generated Swagger UI (<code>/docs</code>) and ReDoc (<code>/redoc</code>). "
        "Heavy operations (predict, Grad-CAM, report formatting) are offloaded to Python's background threadpools to avoid blocking the event loop.",
        body_style
    ))
    
    # API table
    api_data = [
        ["Method", "Endpoint", "Description", "Status Codes"],
        ["POST", "/predict", "Validate upload size/type, run inference, generate Grad-CAM, generate report, log to DB", "201 Created, 400 Bad Input, 503 Unavailable"],
        ["GET", "/history", "Query SQLite prediction records (supports search & sorting)", "200 OK, 500 DB Error"],
        ["GET", "/history/{id}", "Fetch complete prediction and report details", "200 OK, 404 Not Found"],
        ["DELETE", "/history/{id}", "Delete prediction record and purge images from filesystem", "204 No Content, 404 Not Found"],
        ["GET", "/health", "System health report (DB connection, model cache status, LLM availability)", "200 OK"]
    ]
    api_table = Table(api_data, colWidths=[1.0*inch, 1.3*inch, 2.5*inch, 1.2*inch])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(api_table)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Database Abstraction:</b> We use SQLAlchemy ORM. The default database is SQLite for easy evaluation. However, the database layer is written database-agnostically, allowing quick PostgreSQL integration via environment variable swaps.", body_style))

    story.append(PageBreak())

    # ------------------ SECTION 7 ------------------
    story.append(Paragraph("7. Frontend UI Design", h1_style))
    story.append(Paragraph(
        "The frontend is constructed using <b>React (Vite + TypeScript + Material UI)</b>. "
        "The user experience is prioritized, featuring glassmorphic designs, micro-animations, and loading progress state indicators. "
        "Key pages include:",
        body_style
    ))
    story.append(Paragraph("• <b>Dashboard:</b> Renders aggregated metrics (total scans, diagnostic ratios, average confidence) fetched dynamically from the database.", bullet_style))
    story.append(Paragraph("• <b>Analyze (Upload Workspace):</b> Implements client-side checks (JPG/PNG only, <10MB), file drops, and progress spinners.", bullet_style))
    story.append(Paragraph("• <b>Interactive Grad-CAM Slider:</b> A double-layer image visualizer with a smooth slider overlay. Users can cross-fade between the anatomical X-ray structures and the model activation centers.", bullet_style))
    story.append(Paragraph("• <b>Report & PDF Export:</b> Renders structured clinical summaries and supports client-side PDF downloads utilizing jsPDF.", bullet_style))

    # ------------------ SECTION 8 ------------------
    story.append(Paragraph("8. Deployment & Containerization", h1_style))
    story.append(Paragraph(
        "For production hosting, we provide a multi-stage <code>Dockerfile</code> and <code>docker-compose.yml</code>. "
        "The multi-stage build compile the React assets using Node, copies them directly to the Python runtime, and mounts "
        "them as static files served by FastAPI. This results in a single, high-performance container that starts "
        "without manual configuration.",
        body_style
    ))
    story.append(Paragraph(
        "The container incorporates a <b>Docker Health Check</b> that queries the FastAPI <code>/api/health</code> endpoint. "
        "Persistent data volumes are mapped for SQLite database logging, uploaded original X-rays, Grad-CAM results, "
        "and rotating application logs (stored in <code>logs/application.log</code>).",
        body_style
    ))

    # ------------------ SECTION 9 ------------------
    story.append(Paragraph("9. System Limitations & Future Work", h1_style))
    story.append(Paragraph(
        "<b>Limitations:</b> Currently, the platform relies on binary chest X-ray classification. In clinical practice, patient presentation is often complex, involving co-occurring pathologies (e.g. pleural effusion, atelectasis, cardiomegaly).",
        body_style
    ))
    story.append(Paragraph("<b>Future Enhancements:</b>", h2_style))
    story.append(Paragraph("1. <b>Multi-Label Classification:</b> Transition the EfficientNetB0 classifier to a multi-label classification head using sigmoid activations across 14 target classes.", bullet_style))
    story.append(Paragraph("2. <b>Saliency Mapping Comparison:</b> Integrate secondary explainability models (Integrated Gradients or LIME) to complement Grad-CAM.", bullet_style))
    story.append(Paragraph("3. <b>PACS / DICOM Support:</b> Integrate Orthanc DICOM server connectivity to let clinicians query scans directly from their picture archiving and communication systems.", bullet_style))

    # ------------------ CONCLUSION ------------------
    story.append(Spacer(1, 20))
    story.append(Paragraph("10. Conclusion & Legal Disclaimer", h1_style))
    story.append(Paragraph(
        "The MedTool AI Medical Intelligence Platform demonstrates a complete, production-ready full-stack software system. "
        "By packaging complex ML pipelines, explainability models, and generative AI reporting inside a robust web interface, "
        "the application bridges the gap between deep learning research and clinical workflow support.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Legal Disclaimer:</b> This application is built for educational, research, and technical evaluation purposes only. "
        "It is not approved for diagnostic clinical use. All diagnostic assessments must be verified by a licensed clinical radiologist.",
        body_style
    ))
    
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Project report successfully saved to {output_filename}")

if __name__ == '__main__':
    create_project_report()
