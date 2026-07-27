import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  TextField,
  InputAdornment,
  CircularProgress,
  Alert,
  Chip,
  Button,
  Divider,
} from '@mui/material';
import {
  Search as SearchIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  GetApp as DownloadIcon,
  Close as CloseIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { api, getStaticUrl } from '../services/api';
import { downloadReportPDF } from '../components/ReportPDF';
import { GradCamSlider } from '../components/GradCamSlider';

interface HistoryItem {
  id: number;
  filename: string;
  prediction: string;
  confidence: number;
  confidence_rating: string;
  inference_time: number;
  created_at: string;
}

interface ReportDetails extends HistoryItem {
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
}

export const History: React.FC = () => {
  const [historyList, setHistoryList] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  
  // Selected Detail View
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [selectedDetails, setSelectedDetails] = useState<ReportDetails | null>(null);
  const [detailsLoading, setDetailsLoading] = useState(false);

  const fetchHistory = async (query = '') => {
    try {
      setLoading(true);
      const res = await api.get('/history', {
        params: query ? { search: query } : {},
      });
      setHistoryList(res.data);
      setError(null);
    } catch (err: any) {
      console.error(err);
      setError('Failed to fetch prediction history from server.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchHistory(search);
  };

  const loadDetails = async (id: number) => {
    try {
      setSelectedId(id);
      setDetailsLoading(true);
      const res = await api.get(`/history/${id}`);
      setSelectedDetails(res.data);
    } catch (err: any) {
      console.error(err);
      alert('Failed to load complete historical report details.');
    } finally {
      setDetailsLoading(false);
    }
  };

  const handleDelete = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation(); // Avoid triggering row click selection
    if (!confirm('Are you sure you want to delete this prediction log? All image files on disk will be deleted.')) {
      return;
    }
    
    try {
      await api.delete(`/history/${id}`);
      setHistoryList((prev) => prev.filter((item) => item.id !== id));
      if (selectedId === id) {
        setSelectedId(null);
        setSelectedDetails(null);
      }
    } catch (err: any) {
      console.error(err);
      alert('Failed to delete prediction record.');
    }
  };

  const handlePdfDownload = (record: ReportDetails) => {
    downloadReportPDF(record);
  };

  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" sx={{ color: '#0f172a', fontWeight: 'bold' }}>
            Prediction Logs & History
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mt: 0.5 }}>
            Audit past scans, clinical interpretations, and download reports.
          </Typography>
        </Box>
        <IconButton onClick={() => fetchHistory(search)} color="primary" sx={{ border: '1px solid #cbd5e1' }}>
          <RefreshIcon />
        </IconButton>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      {/* Grid container replaced with flexible Box display Grid */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: selectedDetails ? { xs: '1fr', lg: '1.2fr 1fr' } : '1fr',
          gap: 4,
          alignItems: 'start',
        }}
      >
        {/* Logs Table (Left Panel / Full Panel) */}
        <Box sx={{ minWidth: 0 }}>
          <Paper sx={{ p: 3, borderRadius: 3, border: '1px solid #e2e8f0' }}>
            {/* Search Bar */}
            <form onSubmit={handleSearchSubmit}>
              <TextField
                fullWidth
                size="small"
                variant="outlined"
                value={search}
                onChange={handleSearchChange}
                placeholder="Search scans by file name or diagnosis (e.g. pneumonia, normal)..."
                sx={{ mb: 3 }}
                slotProps={{
                  input: {
                    startAdornment: (
                      <InputAdornment position="start">
                        <SearchIcon color="action" />
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <Button type="submit" variant="text" size="small" sx={{ fontWeight: 'bold' }}>
                          Search
                        </Button>
                      </InputAdornment>
                    ),
                  }
                }}
              />
            </form>

            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
                <CircularProgress />
              </Box>
            ) : historyList.length === 0 ? (
              <Box sx={{ p: 5, textAlign: 'center' }}>
                <Typography variant="body1" color="text.secondary">
                  No prediction records found matching the search criteria.
                </Typography>
              </Box>
            ) : (
              <TableContainer>
                <Table sx={{ minWidth: 400 }}>
                  <TableHead sx={{ bgcolor: '#f8fafc' }}>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Scan File</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Verdict</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Confidence</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Timestamp</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 'bold' }}>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {historyList.map((item) => {
                      const isSelected = selectedId === item.id;
                      return (
                        <TableRow
                          key={item.id}
                          onClick={() => loadDetails(item.id)}
                          hover
                          selected={isSelected}
                          sx={{
                            cursor: 'pointer',
                            bgcolor: isSelected ? 'rgba(6, 182, 212, 0.05) !important' : 'inherit',
                            transition: 'background-color 0.2s',
                          }}
                        >
                          <TableCell sx={{ fontWeight: 'medium' }}>
                            {item.filename.length > 20 ? item.filename.substring(0, 17) + '...' : item.filename}
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={item.prediction}
                              color={item.prediction === 'PNEUMONIA' ? 'error' : 'success'}
                              size="small"
                              sx={{ fontWeight: 'bold' }}
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                              {(item.confidence * 100).toFixed(1)}%
                            </Typography>
                            <Typography
                              variant="caption"
                              sx={{
                                fontWeight: 'bold',
                                color: item.confidence_rating === 'High Confidence' ? 'success.main' : 'error.main',
                              }}
                            >
                              {item.confidence_rating}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="caption" color="text.secondary">
                              {new Date(item.created_at).toLocaleDateString()}
                            </Typography>
                            <Typography variant="caption" sx={{ display: 'block', color: 'text.secondary', mt: -0.5 }}>
                              {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </Typography>
                          </TableCell>
                          <TableCell align="right" onClick={(e) => e.stopPropagation()}>
                            <IconButton color="primary" onClick={() => loadDetails(item.id)} size="small">
                              <ViewIcon />
                            </IconButton>
                            <IconButton color="error" onClick={(e) => handleDelete(item.id, e)} size="small" sx={{ ml: 0.5 }}>
                              <DeleteIcon />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Paper>
        </Box>

        {/* Historical Record Detailed View Panel (Right Panel) */}
        {selectedDetails && (
          <Box sx={{ minWidth: 0 }}>
            <Paper sx={{ p: 4, borderRadius: 3, border: '1px solid #cbd5e1', position: 'sticky', top: 90 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Box>
                  <Typography variant="h6" color="text.primary" sx={{ fontWeight: 'bold' }}>
                    Record ID: AGY-{selectedDetails.id}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Logged: {new Date(selectedDetails.created_at).toLocaleString()}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', gap: 0.5 }}>
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<DownloadIcon />}
                    onClick={() => handlePdfDownload(selectedDetails)}
                  >
                    PDF
                  </Button>
                  <IconButton onClick={() => { setSelectedDetails(null); setSelectedId(null); }} size="small">
                    <CloseIcon />
                  </IconButton>
                </Box>
              </Box>

              <Divider sx={{ my: 2 }} />

              {/* Slider for history details */}
              <Box sx={{ my: 3 }}>
                <GradCamSlider
                  originalUrl={getStaticUrl(selectedDetails.original_image)}
                  gradcamUrl={getStaticUrl(selectedDetails.gradcam_image)}
                  maxHeight={280}
                />
              </Box>

              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="subtitle2" color="text.secondary" sx={{ fontWeight: 'bold' }}>
                  File: {selectedDetails.filename}
                </Typography>
                <Chip
                  label={selectedDetails.prediction}
                  color={selectedDetails.prediction === 'PNEUMONIA' ? 'error' : 'success'}
                  sx={{ fontWeight: 'bold' }}
                />
              </Box>

              {/* Report Text Sections */}
              <Box sx={{ maxHeight: 300, overflowY: 'auto', pr: 1 }}>
                <Typography variant="subtitle2" color="primary" sx={{ mt: 2, fontWeight: 'bold' }}>
                  AI Summary:
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ pl: 1, borderLeft: '3px solid #0891b2' }}>
                  {selectedDetails.report.summary}
                </Typography>

                <Typography variant="subtitle2" color="primary" sx={{ mt: 2, fontWeight: 'bold' }}>
                  Clinical Interpretation:
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {selectedDetails.report.clinical_interpretation}
                </Typography>

                <Typography variant="subtitle2" color="primary" sx={{ mt: 2, fontWeight: 'bold' }}>
                  Possible Differential Findings:
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {selectedDetails.report.possible_findings}
                </Typography>

                <Typography variant="subtitle2" color="primary" sx={{ mt: 2, fontWeight: 'bold' }}>
                  Recommended Next Steps:
                </Typography>
                <Typography variant="body2" color="text.secondary" style={{ whiteSpace: 'pre-line' }}>
                  {selectedDetails.report.recommended_next_steps}
                </Typography>

                <Divider sx={{ my: 2 }} />
                
                <Box sx={{ bgcolor: '#fef3c7', p: 1.5, borderRadius: 2, border: '1px solid #fde68a' }}>
                  <Typography variant="caption" color="amber.900" sx={{ fontWeight: 'bold', display: 'block' }}>
                    Disclaimer:
                  </Typography>
                  <Typography variant="caption" color="amber.900" sx={{ display: 'block' }}>
                    {selectedDetails.report.disclaimer}
                  </Typography>
                </Box>
              </Box>
            </Paper>
          </Box>
        )}

        {/* Loading details state */}
        {detailsLoading && !selectedDetails && (
          <Box sx={{ minWidth: 0 }}>
            <Paper sx={{ p: 5, borderRadius: 3, textAlign: 'center', border: '1px solid #cbd5e1' }}>
              <CircularProgress />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                Loading complete radiograph report details...
              </Typography>
            </Paper>
          </Box>
        )}
      </Box>
    </Box>
  );
};
