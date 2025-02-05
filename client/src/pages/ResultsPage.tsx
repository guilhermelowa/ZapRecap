import { useLocation } from 'react-router-dom';
import { AnalysisResponse } from '../types/apiTypes';
import Header from '../components/Header';
import ConversationStats from '../components/ConversationStats';
import PlotlyBarCharts from '../components/PlotlyBarCharts';
import PlotlyHeatmap from '../components/PlotlyHeatmap';
import PremiumContent from '../components/PremiumContent';
import { useTranslation } from 'react-i18next';
import SuggestionBox from '../components/SuggestionBox';

const ResultsPage = () => {
  const location = useLocation();
  const { t } = useTranslation();
  
  if (!location.state) {
    return <div>No data available</div>;
  }

  const { result } = location.state as { result: AnalysisResponse };
  
  try {
    return (
      <div>
        <Header />
        <h1>{t('results.title')}</h1>
        <h2>{t('results.messageStatistics')}</h2>
        <ConversationStats stats={result.conversation_stats} />
        <PlotlyBarCharts metrics={result} />
        <PlotlyHeatmap heatmapData={result.heatmap_data} />
        <PremiumContent 
          stats={result.conversation_stats}
          metrics={result}
        />
        {result.conversation_id && (
          <SuggestionBox conversationId={result.conversation_id} />
        )}
      </div>
    );
  } catch (error) {
    console.error('Error rendering results:', error);
    return <div>Error displaying results</div>;
  }
};

export default ResultsPage;