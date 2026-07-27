import React, { useState } from 'react';
import { Box, Slider, Typography, Paper } from '@mui/material';
import { Compare, Image as ImageIcon } from '@mui/icons-material';

interface GradCamSliderProps {
  originalUrl: string;
  gradcamUrl: string;
  maxHeight?: string | number;
}

export const GradCamSlider: React.FC<GradCamSliderProps> = ({
  originalUrl,
  gradcamUrl,
  maxHeight = 450,
}) => {
  const [opacity, setOpacity] = useState<number>(0.5);

  const handleSliderChange = (_event: Event, newValue: number | number[]) => {
    setOpacity(newValue as number);
  };

  return (
    <Paper
      elevation={3}
      sx={{
        p: 2,
        borderRadius: 2,
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(224, 224, 224, 0.4)',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, gap: 1 }}>
        <Compare color="primary" />
        <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
          Grad-CAM XAI Visualizer
        </Typography>
      </Box>

      {/* Double Layer Image Container */}
      <Box
        sx={{
          position: 'relative',
          width: '100%',
          maxHeight: maxHeight,
          height: maxHeight,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: '#121212',
          borderRadius: 2,
          overflow: 'hidden',
          boxShadow: 'inset 0 0 10px rgba(0,0,0,0.8)',
          mb: 2,
        }}
      >
        {/* Original Chest X-Ray (Bottom Layer) */}
        <Box
          component="img"
          src={originalUrl}
          alt="Original Chest X-Ray"
          sx={{
            maxWidth: '100%',
            maxHeight: '100%',
            objectFit: 'contain',
            width: 'auto',
            height: 'auto',
            display: 'block',
          }}
        />

        {/* Grad-CAM Heatmap Overlay (Top Layer) */}
        <Box
          component="img"
          src={gradcamUrl}
          alt="Grad-CAM Activation Heatmap"
          sx={{
            position: 'absolute',
            maxWidth: '100%',
            maxHeight: '100%',
            objectFit: 'contain',
            width: 'auto',
            height: 'auto',
            opacity: opacity,
            transition: 'opacity 0.05s linear',
            pointerEvents: 'none', // Allow clicking/dragging on the container if needed
          }}
        />
      </Box>

      {/* Control Slider */}
      <Box sx={{ px: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box>
            <Typography variant="body2" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <ImageIcon fontSize="small" /> X-Ray Only
            </Typography>
          </Box>
          <Box sx={{ flexGrow: 1 }}>
            <Slider
              value={opacity}
              onChange={handleSliderChange}
              min={0}
              max={1}
              step={0.01}
              aria-label="Grad-CAM Opacity Slider"
              valueLabelFormat={(val) => `${Math.round(val * 100)}% Heatmap`}
              valueLabelDisplay="auto"
              sx={{
                color: 'primary.main',
                '& .MuiSlider-thumb': {
                  width: 16,
                  height: 16,
                  backgroundColor: '#fff',
                  border: '3px solid currentColor',
                  '&:focus, &:hover, &.Mui-active, &.Mui-focusVisible': {
                    boxShadow: 'inherit',
                  },
                },
                '& .MuiSlider-track': {
                  height: 4,
                },
                '& .MuiSlider-rail': {
                  height: 4,
                  opacity: 0.28,
                },
              }}
            />
          </Box>
          <Box>
            <Typography variant="body2" color="primary" sx={{ fontWeight: 'medium' }}>
              Heatmap Overlay
            </Typography>
          </Box>
        </Box>
      </Box>

      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1, textAlign: 'center', fontStyle: 'italic' }}>
        Drag the slider to cross-fade between the original anatomical structures and the model activation centers.
      </Typography>
    </Paper>
  );
};
