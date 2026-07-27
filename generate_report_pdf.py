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
        self.drawString(54, 750, "MedTool AI — Technical Project Report")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 742, 612 - 54, 742)
        
        # Footer
        self.line(54, 55, 612 - 54, 55)
        self.drawString(54, 42, "TECHNICAL EVALUATION REPORT — SUBMISSION DOCUMENT")
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
        fontSize=26,
        leading=32,
        textColor=colors.HexColor("#0f172a"),
        alignment=0,
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0891b2"),
        alignment=0,
        spaceAfter=40
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#0891b2"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=8
    )
    
    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f8fafc"),
        borderColor=colors.HexColor("#e2e8f0"),
        borderWidth=0.5,
        borderPadding=6,
        spaceAfter=10
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    # Styles specifically for table cell auto-wrapping
    table_hdr_style = ParagraphStyle(
        'TableHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        textColor=colors.white
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#334155")
    )
    
    table_code_style = ParagraphStyle(
        'TableCode',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#0f172a")
    )

    story = []
    
    # ------------------ COVER PAGE ------------------
    story.append(Spacer(1, 100))
    story.append(Paragraph("DEVELOPMENT AND DEPLOYMENT OF AN EXPLAINABLE DEEP LEARNING SYSTEM FOR PNEUMONIA SCREENING", title_style))
    story.append(Paragraph("Technical Report on a Clinical Decision Support System (CDSS) utilizing MobileNetV2 Transfer Learning, Grad-CAM Saliency Mapping, and Automated LLM Reporting.", subtitle_style))
    
    story.append(Spacer(1, 120))
    
    metadata_data = [
        [Paragraph("<b>Submitted By:</b>", body_style), Paragraph("Sathya S", body_style)],
        [Paragraph("<b>GitHub Repository:</b>", body_style), Paragraph("github.com/SathyaS24/AI-Medical-Intelligence-Platform", body_style)],
        [Paragraph("<b>Live Application URL:</b>", body_style), Paragraph("ai-medical-intelligence-platform-fjeb.onrender.com", body_style)],
        [Paragraph("<b>Core Stack:</b>", body_style), Paragraph("FastAPI, React, TypeScript, TensorFlow/Keras, SQLite, Docker, Render", body_style)],
        [Paragraph("<b>Submission Date:</b>", body_style), Paragraph("July 27, 2026", body_style)]
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
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(Paragraph(
        "Chest radiographs (CXRs) represent the primary imaging modality for diagnosing respiratory infections in pediatric settings. "
        "However, interpreting pediatric radiographs is complicated by anatomical variations, patient movement, and subjective differences between observers. "
        "This project reports on the technical implementation of MedTool AI, a clinical decision support system designed to assist radiologists "
        "by classifying frontal chest radiographs, highlighting focal zones of consolidation using Explainable AI (XAI) overlays, and generating "
        "structured draft clinical reports utilizing the Google Gemini API.",
        body_style
    ))
    story.append(Paragraph(
        "The system integrates a deep learning pipeline (MobileNetV2, fine-tuned on pediatric CXR scans) with a FastAPI backend server and "
        "an interactive web interface. To bridge the trust gap common in clinical AI tools, the system implements Gradient-weighted Class "
        "Activation Mapping (Grad-CAM), enabling clinicians to inspect the spatial features that influenced the model's diagnostic classification.",
        body_style
    ))
    
    # ------------------ SECTION 2 ------------------
    story.append(Paragraph("2. Dataset & Preprocessing Pipeline", h1_style))
    story.append(Paragraph(
        "The classification model was trained and evaluated on pediatric chest radiograph datasets containing anterior-posterior (AP) and posterior-anterior (PA) "
        "scans. Images are categorized into normal lungs (clear lung fields without active consolidations) and pneumonia (containing visible pulmonary consolidations, "
        "interstitial patterns, or pleural abnormalities).",
        body_style
    ))
    story.append(Paragraph(
        "To ensure robust evaluation and prevent data leakage, we implemented a strict 70:15:15 data partitioning strategy. "
        "The held-out testing partition is stored in a separate directory structure and is never exposed to the model during training or parameter optimization. "
        "A key challenge in multi-center radiograph analysis is the variation in exposure, contrast, and quality across imaging hardware. "
        "To address this, we integrated Contrast Limited Adaptive Histogram Equalization (CLAHE) into the preprocessing pipeline. "
        "CLAHE standardizes the contrast profiles of the lung fields, highlighting subtle consolidations while avoiding the amplification of background noise in soft tissues.",
        body_style
    ))
    story.append(Paragraph(
        "Input matrices are standardized as follows: image files are parsed, converted to 3-channel matrices, resized to 224x224 pixels, "
        "subjected to CLAHE contrast normalization, and normalized to floating-point values in the range [0.0, 1.0]. During local training, "
        "we apply online data augmentation—including random rotations, zooms, and horizontal flips—to improve the model's generalization.",
        body_style
    ))

    # ------------------ SECTION 3 ------------------
    story.append(Paragraph("3. Convolutional Neural Network Architecture", h1_style))
    story.append(Paragraph(
        "We selected the MobileNetV2 architecture as the core convolutional neural network. MobileNetV2 utilizes depthwise separable convolutions "
        "to dramatically reduce the number of parameters and computational complexity, making it ideal for clinical edge servers without dedicated GPUs. "
        "The base model is initialized with weights pre-trained on ImageNet. During the initial training phase, the convolutional base is frozen to retain "
        "general edge-detection features, and a customized classification head is appended to learn chest radiograph patterns:",
        body_style
    ))
    story.append(Paragraph(
        "<i>Input Tensor (224x224x3) → MobileNetV2 Base → GlobalAveragePooling2D → Dense (128, ReLU) → Dropout (40%) → Dense (1, Sigmoid)</i>",
        code_style
    ))
    story.append(Paragraph(
        "To address class distribution skew in the training set, we compute and apply inverse-frequency class weights during optimization, "
        "preventing the loss function from biasing toward the majority class. The final model is saved as a native Keras `.keras` checkpoint, "
        "accompanied by a metadata JSON file tracking its validation history, hyperparameters, input parameters, and performance metrics (accuracy, loss, sensitivity). "
        "FastAPI loads this model in-memory during application startup, holding the weights cached to guarantee sub-second API response times.",
        body_style
    ))
    
    story.append(PageBreak())

    # ------------------ SECTION 4 ------------------
    story.append(Paragraph("4. Explainable AI (Grad-CAM) Implementation", h1_style))
    story.append(Paragraph(
        "Clinical adoption of deep learning tools depends heavily on transparency. To resolve the 'black-box' nature of neural networks, we "
        "implemented Gradient-weighted Class Activation Mapping (Grad-CAM). Grad-CAM tracks the gradients of the diagnostic output score "
        "with respect to the feature map activations of the final convolutional layer (`out_relu` in MobileNetV2). This highlights the spatial regions "
        "in the radiograph that most heavily influenced the network's prediction.",
        body_style
    ))
    story.append(Paragraph("The mathematical process is structured as follows:", h2_style))
    story.append(Paragraph("• <b>Feature Map Activation:</b> Extract the activation maps <i>A<sup>k</sup></i> of the final convolutional layer, and calculate the gradient of the class score <i>y<sup>c</sup></i> with respect to the activations, denoted as <i>&part;y<sup>c</sup> / &part;A<sup>k</sup></i>.", bullet_style))
    story.append(Paragraph("• <b>Channel-Wise Importance:</b> Compute the importance weights by average-pooling the gradients over the spatial dimensions: <i>&alpha;<sub>k</sub><sup>c</sup> = (1 / Z) * &Sigma;<sub>i</sub> &Sigma;<sub>j</sub> (&part;y<sup>c</sup> / &part;A<sub>i,j</sub><sup>k</sup>)</i>.", bullet_style))
    story.append(Paragraph("• <b>Rectified Linear Combination:</b> Perform a weighted summation of feature maps and filter through a ReLU activation to focus only on features that positively contribute to the class: <i>L<sub>Grad-CAM</sub> = ReLU(&Sigma;<sub>k</sub> &alpha;<sub>k</sub><sup>c</sup> A<sup>k</sup>)</i>.", bullet_style))
    story.append(Paragraph("• <b>Heatmap Synthesis:</b> Bilinearly interpolate the resulting activation map to match the input scan dimensions and blend using a JET colormap overlay.", bullet_style))

    # ------------------ SECTION 5 ------------------
    story.append(Paragraph("5. LLM Integration & Deterministic Fallbacks", h1_style))
    story.append(Paragraph(
        "To assist clinicians with documentation, the platform connects to the Google Gemini API (`gemini-1.5-flash`) using structured JSON prompting. "
        "The model parses the diagnostic output and confidence intervals to draft a clinical report outlining findings, suspected pathologies, and "
        "recommended follow-up actions. "
        "To guarantee high reliability in environments with strict firewalls or API rate limits, we built a deterministic local fallback report generator. "
        "If the connection fails, the backend immediately transitions to generating reports from structured medical templates, ensuring the system remains fully functional.",
        body_style
    ))
    story.append(Paragraph(
        "The system also enforces a configurable confidence threshold (default 70%). If a prediction falls below this threshold, the API flags the result "
        "with a warning label ('Low Confidence Prediction') in both the user interface and the exported PDFs, indicating that immediate clinician review is required.",
        body_style
    ))

    # ------------------ SECTION 6 ------------------
    story.append(Paragraph("6. REST API Design & Database Schema", h1_style))
    story.append(Paragraph(
        "The backend application is developed using FastAPI. FastAPI provides an asynchronous event loop that allows non-blocking operations. "
        "Heavy operations (image decoding, model inference, and Grad-CAM matrix math) are offloaded to separate background threads to prevent "
        "blocking incoming requests. The API includes automatically documented Swagger UI (`/docs`) and ReDoc (`/redoc`) endpoints.",
        body_style
    ))
    
    # API table with auto-wrapping Paragraph elements in each cell
    api_data = [
        [
            Paragraph("Method", table_hdr_style), 
            Paragraph("Endpoint", table_hdr_style), 
            Paragraph("Description", table_hdr_style), 
            Paragraph("Status Codes", table_hdr_style)
        ],
        [
            Paragraph("POST", table_cell_style), 
            Paragraph("/api/predict", table_code_style), 
            Paragraph("Validate and process upload, run inference, generate Grad-CAM and PDF, log to DB", table_cell_style), 
            Paragraph("201, 400, 503", table_cell_style)
        ],
        [
            Paragraph("GET", table_cell_style), 
            Paragraph("/api/history", table_code_style), 
            Paragraph("Query SQLite prediction records (supports search and sorting)", table_cell_style), 
            Paragraph("200, 500", table_cell_style)
        ],
        [
            Paragraph("GET", table_cell_style), 
            Paragraph("/api/history/{id}", table_code_style), 
            Paragraph("Fetch complete prediction and clinical report details", table_cell_style), 
            Paragraph("200, 404", table_cell_style)
        ],
        [
            Paragraph("DELETE", table_cell_style), 
            Paragraph("/api/history/{id}", table_code_style), 
            Paragraph("Delete prediction record and purge images from filesystem", table_cell_style), 
            Paragraph("204, 404", table_cell_style)
        ],
        [
            Paragraph("GET", table_cell_style), 
            Paragraph("/api/health", table_code_style), 
            Paragraph("System health report (DB connection and model cache status)", table_cell_style), 
            Paragraph("200", table_cell_style)
        ]
    ]
    api_table = Table(api_data, colWidths=[0.8*inch, 1.4*inch, 2.8*inch, 1.0*inch])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(api_table)
    story.append(Spacer(1, 10))
    story.append(Paragraph("We use SQLAlchemy ORM to manage database logs. By default, the service uses an SQLite backend for easy evaluation. However, the database connection is abstracted, allowing a seamless switch to PostgreSQL by changing the database connection string environment variable.", body_style))

    story.append(PageBreak())

    # ------------------ SECTION 7 ------------------
    story.append(Paragraph("7. Frontend UI Implementation", h1_style))
    story.append(Paragraph(
        "The client-side dashboard is built with React 19, TypeScript, and Vite. The user interface prioritizes utility and responsiveness, "
        "offering a clinical dashboard, a dedicated history view, and a workspaces area for analysis. "
        "Key interface components include:",
        body_style
    ))
    story.append(Paragraph("• <b>Clinical Dashboard:</b> Renders aggregated metrics (total scans, diagnostic ratios, average confidence) fetched dynamically from the database API.", bullet_style))
    story.append(Paragraph("• <b>Workspaces:</b> Implements drag-and-drop file uploaders, client-side validation (file size limit and formats), and live progress indicators.", bullet_style))
    story.append(Paragraph("• <b>Interactive Grad-CAM Slider:</b> A double-layer image visualizer with a cross-fade slider. Clinicians can adjust the slider to smoothly transition between the raw anatomical X-ray structures and the model activation heatmaps.", bullet_style))
    story.append(Paragraph("• <b>Report & PDF Export:</b> Renders structured clinical summaries and supports direct client-side PDF downloads utilizing jsPDF.", bullet_style))

    # ------------------ SECTION 8 ------------------
    story.append(Paragraph("8. Deployment & Containerization", h1_style))
    story.append(Paragraph(
        "For hosting, we configured a multi-stage Dockerfile and docker-compose.yml. "
        "The builder stage utilizes Node 20 to compile the React static assets, which are copied directly into the Python 3.10-slim runtime container. "
        "This design aggregates both backend routes and frontend static files under a single port (8000), making deployment clean and simple. "
        "The container is configured with health checks targeting the `/api/health` endpoint, and volumes are mapped to persist uploaded assets, databases, and application logs.",
        body_style
    ))

    # ------------------ SECTION 9 ------------------
    story.append(Paragraph("9. Limitations & Future Work", h1_style))
    story.append(Paragraph(
        "<b>Limitations:</b> Currently, the classifier handles binary normal-vs-pneumonia screening. In real clinical scenarios, pediatric patients often present with multiple co-occurring pathologies (e.g., pleural effusion, atelectasis, cardiomegaly).",
        body_style
    ))
    story.append(Paragraph("<b>Future Work:</b>", h2_style))
    story.append(Paragraph("• <b>Multi-Label Classification:</b> Transition the model to a multi-label classification head using sigmoid activations across 14 target classes.", bullet_style))
    story.append(Paragraph("• <b>Comparative Saliency Mapping:</b> Integrate secondary explainability models (like Integrated Gradients or LIME) to complement Grad-CAM.", bullet_style))
    story.append(Paragraph("• <b>PACS Connectivity:</b> Implement DICOM routing to allow the application to query and retrieve scans directly from clinical Picture Archiving and Communication Systems (PACS).", bullet_style))

    # ------------------ SECTION 10 ------------------
    story.append(Spacer(1, 10))
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
