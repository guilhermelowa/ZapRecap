import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Suspense, lazy } from 'react'
import LandingPage from './pages/LandingPage'
import './styles/global.css'
import './styles/App.css'
import * as Sentry from "@sentry/react";

// Lazy load heavy components
const ResultsPage = lazy(() => import('./pages/ResultsPage'));

// Initialize Sentry 
Sentry.init({
  dsn: "https://2437468a195476f97044567a63c189f2@o4508733083549696.ingest.de.sentry.io/4508733086826576",
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration(),
    Sentry.captureConsoleIntegration(),
  ],
  tracesSampleRate: 1.0,
  replaysOnErrorSampleRate: 1.0,
  environment: process.env.NODE_ENV
});

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

export default App;