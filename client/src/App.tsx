import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import ResultsPage from './pages/ResultsPage'
import './styles/global.css'
import './styles/App.css'
import * as Sentry from "@sentry/react";

// Initialize Sentry
Sentry.init({
  dsn: "https://2437468a195476f97044567a63c189f2@o4508733083549696.ingest.de.sentry.io/4508733086826576", // You'll get this from Sentry dashboard
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration(),
    Sentry.captureConsoleIntegration()
  ],
  tracesSampleRate: 1.0,
  replaysOnErrorSampleRate: 1.0,
  environment: process.env.NODE_ENV
});


// Store last 10 console errors
(window as any)._consoleErrors = [];
const originalConsoleError = console.error;
console.error = (...args) => {
    (window as any)._consoleErrors = [...(window as any)._consoleErrors.slice(-9), args.join(' ')];
    originalConsoleError.apply(console, args);
};

function App() {

  return (
    <BrowserRouter>
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/results" element={<ResultsPage />} />
    </Routes>
    </BrowserRouter>
  );
}

export default App