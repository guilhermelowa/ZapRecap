import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Suspense, lazy } from 'react'
import LandingPage from './pages/LandingPage'
import './styles/global.css'
import './styles/App.css'
import * as Sentry from "@sentry/react";

// Lazy load heavy components
const ResultsPage = lazy(() => import('./pages/ResultsPage'));

// Initialize Sentry with memory monitoring
Sentry.init({
  dsn: "https://2437468a195476f97044567a63c189f2@o4508733083549696.ingest.de.sentry.io/4508733086826576",
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration(),
    Sentry.captureConsoleIntegration(),
    {
      name: 'memoryMonitoring',
      setupOnce: () => {
        setInterval(() => {
          if ('performance' in window && 'memory' in (performance as any)) {
            const memory = (performance as any).memory;
            Sentry.setContext("memory", {
              usedJSHeapSize: `${(memory.usedJSHeapSize / 1024 / 1024).toFixed(2)} MB`,
              totalJSHeapSize: `${(memory.totalJSHeapSize / 1024 / 1024).toFixed(2)} MB`,
              jsHeapSizeLimit: `${(memory.jsHeapSizeLimit / 1024 / 1024).toFixed(2)} MB`,
            });
          }
        }, 30000); // Check every 30 seconds
      },
    },
  ],
  tracesSampleRate: 1.0,
  replaysOnErrorSampleRate: 1.0,
  environment: process.env.NODE_ENV
});

// Enhanced error logging with memory info
(window as any)._consoleErrors = [];
const originalConsoleError = console.error;
console.error = (...args) => {
    const memory = ('performance' in window && 'memory' in (performance as any)) 
      ? (performance as any).memory 
      : null;
    
    const errorInfo = {
      message: args.join(' '),
      timestamp: new Date().toISOString(),
      memoryUsage: memory ? {
        used: `${(memory.usedJSHeapSize / 1024 / 1024).toFixed(2)} MB`,
        total: `${(memory.totalJSHeapSize / 1024 / 1024).toFixed(2)} MB`,
      } : 'Not available'
    };

    (window as any)._consoleErrors = [
      ...((window as any)._consoleErrors.slice(-9)), 
      errorInfo
    ];
    
    originalConsoleError.apply(console, args);
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/results" element={
          <Suspense fallback={<div>Loading...</div>}>
            <ResultsPage />
          </Suspense>
        } />
      </Routes>
    </BrowserRouter>
  );
}

// Add cleanup on unmount
window.addEventListener('unload', () => {
  // Clear any cached data
  (window as any)._consoleErrors = [];
  
  // Force garbage collection if available
  if (window.gc) {
    window.gc();
  }
});

export default App;