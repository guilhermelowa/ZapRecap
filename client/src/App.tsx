import { useState } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import ResultsPage from './pages/ResultsPage'
import './styles/global.css'
import './styles/App.css'
import axios from 'axios'

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleSubmit = async () => {
    if (!selectedFile) return;

    setIsLoading(true);
    const reader = new FileReader();

    reader.onload = async (e) => {
      const content = e.target?.result as string;
      
      try {
        const response = await axios.post('http://localhost:8000/analyze', {
          content: content
        }, {
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        console.log(response.data);
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setIsLoading(false);
      }
    };

    reader.readAsText(selectedFile);
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/results" element={<ResultsPage />} />
      </Routes>
      <div className="container">
        <input 
          type="file" 
          accept=".txt" 
          onChange={handleFileSelect} 
        />
        <button 
          onClick={handleSubmit}
          disabled={!selectedFile || isLoading}
        >
          {isLoading ? 'Processing...' : 'Analyze File'}
        </button>
        {isLoading && <div>Loading...</div>}
      </div>
    </BrowserRouter>
  );
}

export default App