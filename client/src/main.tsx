import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import './i18n/i18n.ts'

// Add this to help debug startup memory usage
if (process.env.NODE_ENV === 'production') {
  console.log('Initial memory usage:', process.memoryUsage());

  const reportMemory = () => {
    const used = process.memoryUsage();
    console.log('Memory usage:');
    for (let key in used) {
      console.log(`${key}: ${Math.round(used[key] / 1024 / 1024 * 100) / 100} MB`);
    }
  };
  
  // Report memory usage every 30 seconds
  setInterval(reportMemory, 30000);
  // Initial report
  reportMemory();
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
//console.log(import.meta.env);