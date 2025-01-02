import React from 'react';
import { format } from 'date-fns';
import { Bar, Line, Scatter } from 'react-chartjs-2';
import { 
    Chart as ChartJS,
    BarElement,
    CategoryScale,
    Legend,
    LinearScale,
    LineElement,
    PointElement,
    Title,
    Tooltip
} from 'chart.js';
import { MatrixController, MatrixElement } from 'chartjs-chart-matrix';
import { COLORS, CHART_OPTIONS, HEATMAP_OPTIONS } from '../styles/theme';
import { AnalysisResponse, HeatmapPoint } from '../types/apiTypes';

ChartJS.register(
    BarElement,
    CategoryScale,
    Legend,
    LinearScale,
    LineElement,
    PointElement,
    Title,
    Tooltip
);

interface ChartProps {
  data: AnalysisResponse;
}

const Charts: React.FC<ChartProps> = ({ data }) => {
    console.log(data.heatmap_data)
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

const scatterData = {
    datasets: [{
        label: 'Message Activity',
        data: data.heatmap_data.map((point: HeatmapPoint) => ({
            x: point.x,
            y: point.y,
            value: point.v
        })),
        backgroundColor: (context: any) => {
            const value = context.raw?.value || 0;
            const alpha = Math.min(value / 100, 1);
            return `rgba(18, 140, 126, ${alpha})`;
        },
        pointStyle: 'rect',
        pointRadius: 15,
    }],
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
    <h2>Message Activity</h2>
    <Scatter data={scatterData} options={HEATMAP_OPTIONS} />
      <h2>Messages per Author</h2>
      <Bar data={barData} options={CHART_OPTIONS} />
      <h2>Curse Words Frequency</h2>
      <Line data={lineData} options={CHART_OPTIONS} />
    </div>
  );
};

export default Charts;