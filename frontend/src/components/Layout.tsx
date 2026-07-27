import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Container,
  CssBaseline,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  CloudUpload as UploadIcon,
  History as HistoryIcon,
  MedicalServices as MedicalIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

const drawerWidth = 260;

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Analyze Chest X-Ray', icon: <UploadIcon />, path: '/analyze' },
    { text: 'Prediction History', icon: <HistoryIcon />, path: '/history' },
  ];

  const drawerContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', bgcolor: '#0f172a', color: '#fff' }}>
      <Toolbar sx={{ display: 'flex', alignItems: 'center', gap: 1, px: 2, bgcolor: '#1e293b' }}>
        <MedicalIcon sx={{ color: '#06b6d4', fontSize: 28 }} />
        <Typography variant="h6" noWrap sx={{ fontWeight: 'bold', letterSpacing: 0.5, color: '#f8fafc' }}>
          MedTool AI
        </Typography>
      </Toolbar>
      <Divider sx={{ borderColor: 'rgba(255,255,255,0.08)' }} />
      <List sx={{ px: 1, py: 2, flexGrow: 1 }}>
        {menuItems.map((item) => {
          const active = location.pathname === item.path;
          return (
            <ListItem key={item.text} disablePadding sx={{ mb: 1 }}>
              <ListItemButton
                onClick={() => {
                  navigate(item.path);
                  setMobileOpen(false);
                }}
                sx={{
                  borderRadius: 2,
                  bgcolor: active ? 'rgba(6, 182, 212, 0.15)' : 'transparent',
                  color: active ? '#06b6d4' : '#94a3b8',
                  '&:hover': {
                    bgcolor: 'rgba(255, 255, 255, 0.05)',
                    color: '#fff',
                    '& .MuiListItemIcon-root': { color: '#fff' },
                  },
                  transition: 'all 0.2s',
                }}
              >
                <ListItemIcon sx={{ color: active ? '#06b6d4' : '#64748b', minWidth: 40 }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography sx={{ fontWeight: active ? 'bold' : 'medium', fontSize: 14 }}>
                      {item.text}
                    </Typography>
                  }
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
      <Box sx={{ p: 2, bgcolor: '#1e293b', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
          <InfoIcon sx={{ color: '#06b6d4', fontSize: 16 }} />
          <Typography variant="caption" sx={{ fontWeight: 'bold', color: '#e2e8f0' }}>
            System Status
          </Typography>
        </Box>
        <Typography variant="caption" sx={{ display: 'block', color: '#94a3b8' }}>
          Model: EfficientNetB0
        </Typography>
        <Typography variant="caption" sx={{ display: 'block', color: '#94a3b8' }}>
          API Status: Healthy
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#f8fafc' }}>
      <CssBaseline />
      
      {/* Header AppBar */}
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          bgcolor: 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(10px)',
          boxShadow: 'none',
          borderBottom: '1px solid #e2e8f0',
          color: '#1e293b',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          
          <Box sx={{ display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
            <Typography variant="subtitle2" color="primary" sx={{ fontWeight: 'bold', textTransform: 'uppercase', letterSpacing: 1, fontSize: 10 }}>
              Clinical Decision Support System
            </Typography>
            <Typography variant="h6" sx={{ fontWeight: 'bold', mt: -0.5 }}>
              Medical Intelligence Platform
            </Typography>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Navigation Drawers */}
      <Box component="nav" sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }} aria-label="mailbox folders">
        {/* Mobile Drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawerContent}
        </Drawer>
        {/* Desktop Permanent Drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth, border: 'none' },
          }}
          open
        >
          {drawerContent}
        </Drawer>
      </Box>

      {/* Main Content Area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Toolbar /> {/* Spacer below header */}
        <Container maxWidth="xl" sx={{ mt: 2, mb: 4, flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
          {children}
        </Container>
        
        {/* Footer */}
        <Box component="footer" sx={{ py: 3, px: 2, mt: 'auto', borderTop: '1px solid #e2e8f0', textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            © {new Date().getFullYear()} MedTool AI. All rights reserved.
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};
