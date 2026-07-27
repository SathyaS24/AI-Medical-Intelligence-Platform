import React, { useState, useRef } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Chip,
  Divider,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  GetApp as DownloadIcon,
  Refresh as RefreshIcon,
  PriorityHigh,
  CheckCircle,
} from '@mui/icons-material';
import { api, getStaticUrl } from '../services/api';
import { GradCamSlider } from '../components/GradCamSlider';
import { downloadReportPDF } from '../components/ReportPDF';

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png'];

interface ReportData {
  id: number;
  filename: string;
  prediction: string;
  confidence: number;
  confidence_rating: string;
  inference_time: number;
  gradcam_image: string;
  original_image: string;
  report: {
    prediction: string;
    confidence: string;
    summary: string;
    clinical_interpretation: string;
    possible_findings: string;
    recommended_next_steps: string;
    disclaimer: string;
  };
  created_at: string;
}

export const Analyze: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ReportData | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = (file: File) => {
    setError(null);
    setResult(null);

    // Validate type
    if (!ALLOWED_TYPES.includes(file.type)) {
      setError('Invalid file type. Only JPG, JPEG, and PNG images are accepted.');
      setSelectedFile(null);
      setPreviewUrl(null);
      return;
    }

    // Validate size
    if (file.size > MAX_FILE_SIZE) {
      setError('File size too large. Maximum size allowed is 10 MB.');
      setSelectedFile(null);
      setPreviewUrl(null);
      return;
    }

    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const runInference = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      setLoading(true);
      setError(null);
      
      const res = await api.post('/predict', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(res.data);
    } catch (err: any) {
      console.error(err);
      const detail = err.response?.data?.detail || 'Inference pipeline failure. Please try again.';
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  const resetState = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ color: '#0f172a', fontWeight: 'bold' }}>
          Evaluate Chest Radiograph
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mt: 0.5 }}>
          Upload a frontal chest X-ray image to identify features associated with pulmonary pneumonia.
        </Typography>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      {!result && !loading && (
        <Paper
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          sx={{
            p: 5,
            border: '2px dashed #cbd5e1',
            borderRadius: 4,
            bgcolor: 'rgba(255, 255, 255, 0.4)',
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'all 0.2s',
            '&:hover': {
              borderColor: 'primary.main',
              bgcolor: 'rgba(255, 255, 255, 0.7)',
            },
          }}
          onClick={handleUploadClick}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            style={{ display: 'none' }}
            accept=".jpg,.jpeg,.png"
          />
          <UploadIcon sx={{ fontSize: 60, color: '#94a3b8', mb: 2 }} />
          <Typography variant="h6" sx={{ color: '#334155', mb: 1, fontWeight: 'bold' }}>
            Drag and drop chest X-ray image here
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Supports JPG, JPEG, and PNG files up to 10 MB
          </Typography>
          <Button variant="outlined" color="primary" sx={{ borderRadius: 2 }}>
            Browse Local Files
          </Button>
        </Paper>
      )}

      {/* Preview and Upload Action State */}
      {previewUrl && !result && !loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 1 }}>
          <Paper sx={{ p: 2, borderRadius: 3, border: '1px solid #e2e8f0', textAlign: 'center', width: '100%', maxWidth: 500 }}>
            <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
              Selected Image Preview:
            </Typography>
            <Box
              component="img"
              src={previewUrl}
              alt="Selected Chest X-Ray Preview"
              sx={{
                width: '100%',
                maxHeight: 350,
                objectFit: 'contain',
                borderRadius: 2,
                bgcolor: '#f1f5f9',
                border: '1px solid #e2e8f0',
                mb: 2,
              }}
            />
            <Typography variant="body2" color="text.primary" sx={{ mb: 2, fontWeight: 'bold' }}>
              {selectedFile?.name} ({(selectedFile ? selectedFile.size / (1024 * 1024) : 0).toFixed(2)} MB)
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
              <Button variant="outlined" color="error" onClick={resetState} sx={{ borderRadius: 2 }}>
                Cancel
              </Button>
              <Button variant="contained" color="primary" onClick={runInference} sx={{ borderRadius: 2, px: 4 }}>
                Analyze Radiograph
              </Button>
            </Box>
          </Paper>
        </Box>
      )}

      {/* Loading Indicator */}
      {loading && (
        <Paper sx={{ p: 5, borderRadius: 3, textAlign: 'center', border: '1px solid #e2e8f0', mt: 2 }}>
          <CircularProgress size={50} sx={{ mb: 3 }} />
          <Typography variant="h6" color="text.primary" sx={{ mb: 1, fontWeight: 'bold' }}>
            Running Deep Learning Pipeline...
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Standardizing image matrix, calculating network predictions, generating Grad-CAM gradients, and fetching clinical reports.
          </Typography>
        </Paper>
      )}

      {/* Results View */}
      {result && (
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' },
            gap: 4,
            mt: 1,
          }}
        >
          {/* Grad-CAM Blending Overlay Slider */}
          <Box>
            <GradCamSlider
              originalUrl={getStaticUrl(result.original_image)}
              gradcamUrl={getStaticUrl(result.gradcam_image)}
            />
          </Box>

          {/* Diagnosis Stats and AI Report */}
          <Box>
            {/* Primary Diagnostic Verdict Card */}
            <Card
              sx={{
                borderRadius: 3,
                border: '1px solid #e2e8f0',
                mb: 3,
                background:
                  result.prediction === 'PNEUMONIA'
                    ? 'linear-gradient(135deg, #fff 50%, #fef2f2 100%)'
                    : 'linear-gradient(135deg, #fff 50%, #f0fdf4 100%)',
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary" sx={{ fontWeight: 'bold' }}>
                    Primary Verdict:
                  </Typography>
                  <Chip
                    icon={result.prediction === 'PNEUMONIA' ? <PriorityHigh /> : <CheckCircle />}
                    label={result.prediction}
                    color={result.prediction === 'PNEUMONIA' ? 'error' : 'success'}
                    sx={{ fontWeight: 'bold', fontSize: 13 }}
                  />
                </Box>

                <Box sx={{ display: 'flex', gap: 4, mb: 1 }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="caption" sx={{ display: 'block', color: 'text.secondary' }}>
                      Inference Confidence
                    </Typography>
                    <Typography variant="h5" sx={{ color: 'text.primary', fontWeight: 'bold' }}>
                      {(result.confidence * 100).toFixed(1)}%
                    </Typography>
                    <Typography
                      variant="caption"
                      sx={{
                        fontWeight: 'bold',
                        color: result.confidence_rating === 'High Confidence' ? 'success.main' : 'error.main',
                      }}
                    >
                      {result.confidence_rating}
                    </Typography>
                  </Box>

                  <Box sx={{ flex: 1 }}>
                    <Typography variant="caption" sx={{ display: 'block', color: 'text.secondary' }}>
                      Inference Duration
                    </Typography>
                    <Typography variant="h5" sx={{ color: 'text.primary', fontWeight: 'bold' }}>
                      {result.inference_time.toFixed(3)}s
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      GPU-Optimized Threadpool
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>

            {/* AI Report Card */}
            <Paper sx={{ p: 4, borderRadius: 3, border: '1px solid #e2e8f0', bgcolor: '#fff' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" color="primary" sx={{ fontWeight: 'bold' }}>
                  Clinical Radiology Report
                </Typography>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<DownloadIcon />}
                  onClick={() => downloadReportPDF(result)}
                  sx={{ borderRadius: 2 }}
                >
                  Download PDF
                </Button>
              </Box>

              <Typography variant="subtitle2" sx={{ mt: 2, mb: 0.5, color: '#334155', fontWeight: 'bold' }}>
                1. AI Summary:
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ pl: 1, borderLeft: '3px solid #0891b2' }}>
                {result.report.summary}
              </Typography>

              <Typography variant="subtitle2" sx={{ mt: 3, mb: 0.5, color: '#334155', fontWeight: 'bold' }}>
                2. Clinical Interpretation:
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {result.report.clinical_interpretation}
              </Typography>

              <Typography variant="subtitle2" sx={{ mt: 3, mb: 0.5, color: '#334155', fontWeight: 'bold' }}>
                3. Possible Differential Findings:
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {result.report.possible_findings}
              </Typography>

              <Typography variant="subtitle2" sx={{ mt: 3, mb: 0.5, color: '#334155', fontWeight: 'bold' }}>
                4. Recommended Next Steps:
              </Typography>
              <Typography variant="body2" color="text.secondary" style={{ whiteSpace: 'pre-line' }}>
                {result.report.recommended_next_steps}
              </Typography>

              <Divider sx={{ my: 3 }} />
              
              <Box sx={{ bgcolor: '#fef3c7', p: 2, borderRadius: 2, border: '1px solid #fde68a' }}>
                <Typography variant="caption" color="amber.900" sx={{ fontWeight: 'bold', textTransform: 'uppercase', mb: 0.5, display: 'block' }}>
                  Medical Disclaimer:
                </Typography>
                <Typography variant="caption" color="amber.900" sx={{ display: 'block' }}>
                  {result.report.disclaimer}
                </Typography>
              </Box>
            </Paper>

            {/* Reload button for another scan */}
            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
              <Button
                variant="contained"
                startIcon={<RefreshIcon />}
                onClick={resetState}
                sx={{ borderRadius: 2, bgcolor: '#0f172a', color: '#fff', '&:hover': { bgcolor: '#1e293b' } }}
              >
                Analyze Another Image
              </Button>
            </Box>
          </Box>
        </Box>
      )}
    </Box>
  );
};
