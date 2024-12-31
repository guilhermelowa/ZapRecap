import { useLocation } from 'react-router-dom';
import { AnalysisResponse } from '../types/apiTypes';
import Header from '../components/Header';
// import Charts from '../components/Charts';
import PlotlyHeatmap from '../components/PlotlyHeatmap';

const ResultsPage = () => {
  const location = useLocation();
  console.log('Location state:', location.state);
  
  if (!location.state) {
    return <div>No data available</div>;
  }

  const { result } = location.state as { result: AnalysisResponse };
  
  try {
    return (
      <div>
        <Header />
        <h1>Analysis Results</h1>
        <PlotlyHeatmap heatmapData={result.heatmap_data} />
        {/* <Charts data={result} /> */}
      </div>
    );
  } catch (error) {
    console.error('Error rendering results:', error);
    return <div>Error displaying results</div>;
  }
};

export default ResultsPage;