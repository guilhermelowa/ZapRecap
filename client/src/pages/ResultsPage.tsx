import { useLocation } from 'react-router-dom';
import { AnalysisResponse } from '../types/apiTypes';
import Header from '../components/Header';
import ConversationStats from '../components/ConversationStats';
import PlotlyHeatmap from '../components/PlotlyHeatmap';
import PlotlyBarCharts from '../components/PlotlyBarCharts';
import AuthorSimulator from '../components/AuthorSimulator';
import { useTranslation } from 'react-i18next';

const ResultsPage = () => {
  const location = useLocation();
  const { t } = useTranslation();
  console.log('Location state:', location.state);
  
  if (!location.state) {
    return <div>No data available</div>;
  }

  const { result } = location.state as { result: AnalysisResponse };
  
  try {
    return (
      <div>
        <Header />
        <h1>{t('results.title')}</h1>
        <PlotlyBarCharts metrics={result} />
        <h2>{t('results.messageStatistics')}</h2>
        <ConversationStats stats={result.conversation_stats} />
        <PlotlyHeatmap heatmapData={result.heatmap_data} />
        <AuthorSimulator metrics={result} />
      </div>
    );
  } catch (error) {
    console.error('Error rendering results:', error);
    return <div>Error displaying results</div>;
  }
};

export default ResultsPage;