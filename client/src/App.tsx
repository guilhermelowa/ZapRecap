import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import ResultsPage from './pages/ResultsPage'
import './styles/global.css'
import './styles/App.css'

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