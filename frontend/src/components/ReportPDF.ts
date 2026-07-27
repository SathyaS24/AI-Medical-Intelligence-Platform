import jsPDF from 'jspdf';

interface ReportData {
  filename: string;
  prediction: string;
  confidence: number;
  confidence_rating: string;
  inference_time: number;
  created_at: string;
  report: {
    prediction: string;
    confidence: string;
    summary: string;
    clinical_interpretation: string;
    possible_findings: string;
    recommended_next_steps: string;
    disclaimer: string;
  };
}

export const downloadReportPDF = (data: ReportData) => {
  const doc = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4'
  });

  const pageWidth = doc.internal.pageSize.getWidth();
  const margin = 20;
  const contentWidth = pageWidth - 2 * margin;
  let y = 20;

  // Header Brand
  doc.setFont('Helvetica', 'bold');
  doc.setFontSize(22);
  doc.setTextColor(24, 76, 120); // Deep Teal/Blue
  doc.text('MEDTOOL AI MEDICAL INTELLIGENCE', margin, y);
  
  y += 6;
  doc.setFont('Helvetica', 'normal');
  doc.setFontSize(10);
  doc.setTextColor(100, 100, 100);
  doc.text('Advanced Radiology AI Diagnostics & Analytics Platform', margin, y);

  y += 4;
  // Border line
  doc.setDrawColor(200, 200, 200);
  doc.setLineWidth(0.5);
  doc.line(margin, y, pageWidth - margin, y);

  y += 10;
  
  // Title
  doc.setFont('Helvetica', 'bold');
  doc.setFontSize(14);
  doc.setTextColor(33, 33, 33);
  doc.text('CLINICAL RADIOLOGY REPORT', margin, y);

  y += 8;

  // Metadata Table
  doc.setFont('Helvetica', 'bold');
  doc.setFontSize(9);
  doc.setTextColor(80, 80, 80);
  doc.text('Report ID:', margin, y);
  doc.text('Date/Time:', margin + 80, y);
  
  doc.setFont('Helvetica', 'normal');
  doc.setTextColor(33, 33, 33);
  doc.text(`MED-${Math.floor(100000 + Math.random() * 900000)}`, margin + 25, y);
  doc.text(new Date(data.created_at).toLocaleString(), margin + 105, y);
  
  y += 6;
  
  doc.setFont('Helvetica', 'bold');
  doc.setTextColor(80, 80, 80);
  doc.text('Filename:', margin, y);
  doc.text('Inference Time:', margin + 80, y);
  
  doc.setFont('Helvetica', 'normal');
  doc.setTextColor(33, 33, 33);
  // Truncate filename if too long
  const filename = data.filename.length > 25 ? data.filename.substring(0, 22) + '...' : data.filename;
  doc.text(filename, margin + 25, y);
  doc.text(`${data.inference_time.toFixed(3)} seconds`, margin + 105, y);
  
  y += 10;
  
  // Diagnostic Result Box
  const isPneumonia = data.prediction === 'PNEUMONIA';
  const boxHeight = 22;
  
  // Fill color
  if (isPneumonia) {
    doc.setFillColor(254, 242, 242); // Soft red
    doc.setDrawColor(239, 68, 68); // Red border
  } else {
    doc.setFillColor(240, 253, 244); // Soft green
    doc.setDrawColor(34, 197, 94); // Green border
  }
  
  doc.rect(margin, y, contentWidth, boxHeight, 'FD');
  
  // Result text
  doc.setFont('Helvetica', 'bold');
  doc.setFontSize(11);
  doc.setTextColor(isPneumonia ? 185 : 21, isPneumonia ? 28 : 128, isPneumonia ? 28 : 61);
  doc.text('PRIMARY DIAGNOSTIC PREDICTION', margin + 5, y + 6);
  
  doc.setFontSize(18);
  doc.text(data.prediction, margin + 5, y + 15);
  
  doc.setFontSize(10);
  doc.setTextColor(80, 80, 80);
  doc.text('Confidence Score:', margin + 100, y + 6);
  doc.setFont('Helvetica', 'bold');
  doc.setFontSize(16);
  doc.setTextColor(33, 33, 33);
  doc.text(`${(data.confidence * 100).toFixed(1)}%`, margin + 100, y + 14);
  
  doc.setFont('Helvetica', 'normal');
  doc.setFontSize(9);
  doc.setTextColor(data.confidence_rating === 'High Confidence' ? 21 : 185, data.confidence_rating === 'High Confidence' ? 128 : 28, data.confidence_rating === 'High Confidence' ? 61 : 28);
  doc.text(`(${data.confidence_rating})`, margin + 122, y + 14);

  y += boxHeight + 10;

  // Render text blocks helper
  const renderSection = (title: string, content: string) => {
    // Check page height
    if (y > 250) {
      doc.addPage();
      y = 20;
    }
    
    doc.setFont('Helvetica', 'bold');
    doc.setFontSize(11);
    doc.setTextColor(24, 76, 120);
    doc.text(title, margin, y);
    
    y += 5;
    
    doc.setFont('Helvetica', 'normal');
    doc.setFontSize(9.5);
    doc.setTextColor(50, 50, 50);
    
    // Split text to fit inside the width
    const lines = doc.splitTextToSize(content, contentWidth);
    doc.text(lines, margin, y);
    
    y += (lines.length * 4.5) + 8;
  };

  // Render individual sections
  renderSection('AI FINDINGS SUMMARY', data.report.summary);
  renderSection('CLINICAL INTERPRETATION', data.report.clinical_interpretation);
  renderSection('POSSIBLE DIFFERENTIAL FINDINGS', data.report.possible_findings);
  renderSection('RECOMMENDED CLINICAL NEXT STEPS', data.report.recommended_next_steps);

  // Footer Disclaimer
  doc.setDrawColor(220, 220, 220);
  doc.line(margin, 268, pageWidth - margin, 268);
  
  doc.setFont('Helvetica', 'bold');
  doc.setFontSize(8);
  doc.setTextColor(120, 120, 120);
  doc.text('IMPORTANT CLINICAL DISCLAIMER:', margin, 273);
  
  doc.setFont('Helvetica', 'normal');
  doc.setFontSize(7.5);
  const disclaimerText = data.report.disclaimer;
  const disclaimerLines = doc.splitTextToSize(disclaimerText, contentWidth);
  doc.text(disclaimerLines, margin, 277);

  // Save report
  doc.save(`MED_Radiology_Report_${data.prediction}_${Date.now()}.pdf`);
};
