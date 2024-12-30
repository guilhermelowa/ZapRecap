import { useLocation } from 'react-router-dom';
import Header from '../components/Header';
import Charts from '../components/Charts';

const ResultsPage = () => {
  const location = useLocation();
  console.log('Location state:', location.state);
  
  if (!location.state) {
    return <div>No data available</div>;
  }

  const { result } = location.state;
  try {
    return (
      <div>
        <Header />
        <h1>Analysis Results</h1>
        <Charts data={result} />
      </div>
    );
  } catch (error) {
    console.error('Render error:', error);
    return <div>Error rendering results. Check console for details.</div>;
  }
};

export default ResultsPage;