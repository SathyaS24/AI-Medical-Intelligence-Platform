import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Paper,
  Typography,
  Box,
  Button,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  CardActions,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Assessment as AssessmentIcon,
  Timeline as TimelineIcon,
  Science as ScienceIcon,
  CheckCircleOutlined,
  ErrorOutlined,
} from '@mui/icons-material';
import { api } from '../services/api';

interface Stats {
  total_predictions: number;
  pneumonia_cases: number;
  normal_cases: number;
  average_confidence: number;
  latest_prediction_time: string | null;
}

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const res = await api.get('/dashboard/stats');
        setStats(res.data);
        setError(null);
      } catch (err: any) {
        console.error(err);
        setError('Failed to load dashboard statistics from backend database.');
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress color="primary" />
      </Box>
    );
  }

  const statCards = [
    {
      title: 'Total Scans Evaluated',
      value: stats?.total_predictions ?? 0,
      icon: <AssessmentIcon sx={{ fontSize: 40, color: '#3b82f6' }} />,
      bgColor: 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)',
    },
    {
      title: 'Pneumonia Diagnoses',
      value: stats?.pneumonia_cases ?? 0,
      icon: <ErrorOutlined sx={{ fontSize: 40, color: '#ef4444' }} />,
      bgColor: 'linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)',
    },
    {
      title: 'Normal Scan Results',
      value: stats?.normal_cases ?? 0,
      icon: <CheckCircleOutlined sx={{ fontSize: 40, color: '#22c55e' }} />,
      bgColor: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
    },
    {
      title: 'Average Model Confidence',
      value: stats ? `${(stats.average_confidence * 100).toFixed(1)}%` : '0.0%',
      icon: <TimelineIcon sx={{ fontSize: 40, color: '#0891b2' }} />,
      bgColor: 'linear-gradient(135deg, #ecfeff 0%, #cffafe 100%)',
    },
  ];

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ color: '#0f172a', fontWeight: 'bold' }}>
          Welcome to MedTool AI Medical Intelligence
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mt: 0.5 }}>
          Clinical decision support tool for chest radiograph classification and XAI region analysis.
        </Typography>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 4 }}>{error}</Alert>}

      {/* Numerical Stats Grid using CSS Grid via Box */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' },
          gap: 3,
          mb: 4,
        }}
      >
        {statCards.map((card, idx) => (
          <Paper
            key={idx}
            elevation={0}
            sx={{
              p: 3,
              borderRadius: 3,
              background: card.bgColor,
              border: '1px solid rgba(226, 232, 240, 0.8)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <Box>
              <Typography variant="subtitle2" color="text.secondary" sx={{ fontWeight: 'medium' }}>
                {card.title}
              </Typography>
              <Typography variant="h3" sx={{ mt: 1, color: '#1e293b', fontWeight: 'bold' }}>
                {card.value}
              </Typography>
            </Box>
            <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: 'rgba(255, 255, 255, 0.7)' }}>
              {card.icon}
            </Box>
          </Paper>
        ))}
      </Box>

      {/* Main Workspace Layout Grid */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', md: '1.4fr 1fr' },
          gap: 4,
        }}
      >
        {/* Quick Actions & System Info */}
        <Paper sx={{ p: 4, borderRadius: 3, border: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <Box>
            <Typography variant="h6" sx={{ mb: 2, color: '#0f172a', fontWeight: 'bold' }}>
              Initiate Patient Radiograph Screening
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Upload high-resolution frontal chest X-ray scans (PA/AP views) to perform deep learning prediction.
              The pipeline executes image standardizing, runs inference via the custom-trained EfficientNetB0 network,
              overlays a Grad-CAM localization heatmap, and calls Gemini LLM to compile a draft clinical radiology report.
            </Typography>
          </Box>
          <Box>
            <Button
              variant="contained"
              size="large"
              startIcon={<UploadIcon />}
              onClick={() => navigate('/analyze')}
              sx={{
                borderRadius: 2,
                px: 4,
                py: 1.5,
                bgcolor: '#0f172a',
                color: '#fff',
                '&:hover': { bgcolor: '#1e293b' },
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                mb: 3,
              }}
            >
              Analyze New Image
            </Button>

            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 1, color: '#1e293b', fontWeight: 'bold' }}>
                Pipeline Activity Status:
              </Typography>
              <Typography variant="body2" color="text.secondary">
                - Last Prediction Generated:{' '}
                <strong>
                  {stats?.latest_prediction_time
                    ? new Date(stats.latest_prediction_time).toLocaleString()
                    : 'No predictions recorded yet.'}
                </strong>
              </Typography>
            </Box>
          </Box>
        </Paper>

        {/* AI Model Specs Card */}
        <Card sx={{ borderRadius: 3, border: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column' }}>
          <CardContent sx={{ p: 4, flexGrow: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <ScienceIcon color="primary" />
              <Typography variant="h6" sx={{ color: '#0f172a', fontWeight: 'bold' }}>
                Model & Training Specifications
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              The classification model relies on a fine-tuned <strong>EfficientNetB0</strong> network utilizing transfer learning from ImageNet pre-trained weights.
            </Typography>
            <Box sx={{ bgcolor: '#f8fafc', p: 2, borderRadius: 2, border: '1px solid #edf2f7' }}>
              <Typography variant="caption" sx={{ display: 'block', color: 'text.secondary' }}>
                <strong>Network:</strong> EfficientNetB0 (Custom Head)
              </Typography>
              <Typography variant="caption" sx={{ display: 'block', color: 'text.secondary', mt: 0.5 }}>
                <strong>Input Size:</strong> 224 × 224 × 3 RGB
              </Typography>
              <Typography variant="caption" sx={{ display: 'block', color: 'text.secondary', mt: 0.5 }}>
                <strong>Split Ratio:</strong> 70% Train, 15% Validation, 15% Test
              </Typography>
              <Typography variant="caption" sx={{ display: 'block', color: 'text.secondary', mt: 0.5 }}>
                <strong>Confidence Limit:</strong> {(0.7 * 100).toFixed(0)}% (Below this flags low confidence)
              </Typography>
              <Typography variant="caption" sx={{ display: 'block', color: 'text.secondary', mt: 0.5 }}>
                <strong>Primary Dataset:</strong> Kaggle Chest X-ray (Pneumonia)
              </Typography>
            </Box>
          </CardContent>
          <CardActions sx={{ px: 4, pb: 4 }}>
            <Button size="small" color="primary" onClick={() => navigate('/history')} sx={{ fontWeight: 'bold' }}>
              View Prediction logs
            </Button>
          </CardActions>
        </Card>
      </Box>
    </Box>
  );
};
