import { useLocation } from 'react-router-dom';
import { AnalysisResponse } from '../types/apiTypes';
import Header from '../components/Header';
import ConversationStats from '../components/ConversationStats';
import PlotlyHeatmap from '../components/PlotlyHeatmap';
import PlotlyBarCharts from '../components/PlotlyBarCharts';

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
        <PlotlyBarCharts metrics={result} />
        <h2>Message statistics</h2>
        <ConversationStats stats={result.conversation_stats} />
        <PlotlyHeatmap heatmapData={result.heatmap_data} />
      </div>
    );
  } catch (error) {
    console.error('Error rendering results:', error);
    return <div>Error displaying results</div>;
  }
};

export default ResultsPage;