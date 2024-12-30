import React from 'react';
import { format } from 'date-fns';
import { Bar, Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, PointElement, LineElement } from 'chart.js';
import { COLORS, CHART_OPTIONS } from '../styles/theme';
import { AnalysisResponse } from '../types/analysis';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, PointElement, LineElement);

interface ChartProps {
  data: AnalysisResponse;
}

const Charts: React.FC<ChartProps> = ({ data }) => {
  const barData = {
    labels: Object.keys(data.word_metrics.messages_per_author),
    datasets: [
      {
        label: 'Messages per Author',
        data: Object.values(data.word_metrics.messages_per_author),
        backgroundColor: COLORS.whatsappLightGreen,
        borderColor: COLORS.whatsappDarkGreen,
        borderWidth: 1,
      },
    ],
  };

  const lineData = {
    labels: Object.keys(data.word_metrics.curse_words_frequency),
    datasets: [
      {
        label: 'Curse Words Frequency',
        data: Object.values(data.word_metrics.curse_words_frequency),
        fill: false,
        backgroundColor: COLORS.whatsappLightGreen,
        borderColor: COLORS.whatsappDarkGreen,
      },
    ],
  };

  return (
    <div>
      <h2>Conversations</h2>
        <div>
            <p><strong>Average Conversation Length:</strong> {data.conversation_stats.average_length} messages</p>
            <p><strong>Longest Conversation:</strong> {data.conversation_stats.longest_conversation_length} messages</p>
            <p><strong>Longest Conversation Period:</strong>{' '}
                {format(new Date(data.conversation_stats.longest_conversation_start), 'PPP')} to{' '}
                {format(new Date(data.conversation_stats.longest_conversation_end), 'PPP')}
            </p>
        </div>
      <h2>Messages per Author</h2>
      <Bar data={barData} options={CHART_OPTIONS} />
      <h2>Curse Words Frequency</h2>
      <Line data={lineData} options={CHART_OPTIONS} />
    </div>
  );
};

export default Charts;