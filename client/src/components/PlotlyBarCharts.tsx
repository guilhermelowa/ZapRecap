import React from 'react';
import Plot from 'react-plotly.js';
import { AnalysisResponse } from '../types/apiTypes';

interface PlotlyBarChartsProps {
  metrics: AnalysisResponse;
}

const PlotlyBarCharts: React.FC<PlotlyBarChartsProps> = ({ metrics }) => {
  const capitalizeNames = (name: string): string => {
    return name
      .split(' ')
      .map(char => char.charAt(0).toUpperCase() + char.slice(1))
      .join(' ');
  };

  const generateColors = (length: number): string[] => {
    const startGreen = 255;
    const greenStep = 150 / length;
    const opacityStep = 0.3 / length;

    return Array.from({ length }, (_, i) => {
        const green = startGreen - (i * greenStep);
        const opacity = 1 - (i * opacityStep);
        return `rgba(37, ${green}, 102, ${opacity})`;
    });
  };

  const getContainerStyle = (dataLength: number) => {
    const baseWidth = 100;
    const widthPerItem = 50;
    const width = Math.min(350, Math.max(100, baseWidth + (dataLength * widthPerItem)));
    const leftOffset = -(width * 1.4);
    
    return {
      position: 'relative',
      left: `${leftOffset}px`,
      width: `${width}%`,
      innerHeight: '500px',
      outerHeight: '500px',
      display: 'flex',
      justifyContent: 'center',
      overflow: 'hidden',
      margin: '0 0 100px 0',
      padding: 0,
      boxSizing: 'border-box'
    } as const;
  };

  // Transform data for each chart
  const messagesPerAuthor = {
    x: Object.keys(metrics.word_metrics.messages_per_author).map(capitalizeNames),
    y: Object.values(metrics.word_metrics.messages_per_author),
    type: 'bar' as const,
    text: Object.values(metrics.word_metrics.messages_per_author),
    textposition: 'outside' as const,
    marker: {
      color: generateColors(Object.keys(metrics.word_metrics.messages_per_author).length)
    },
    width: 0.6
  };

  const averageMessageLength = {
    x: Object.keys(metrics.word_metrics.average_message_length).map(capitalizeNames),
    y: Object.values(metrics.word_metrics.average_message_length).map(Math.round),
    type: 'bar' as const,
    text: Object.values(metrics.word_metrics.average_message_length).map(Math.round),
    textposition: 'outside' as const,
    marker: {
      color: generateColors(Object.keys(metrics.word_metrics.average_message_length).length)
    },
    width: 0.6
  };

  const curseWordsPerAuthor = {
    x: Object.keys(metrics.word_metrics.curse_words_per_author).map(capitalizeNames),
    y: Object.values(metrics.word_metrics.curse_words_per_author),
    type: 'bar' as const,
    text: Object.values(metrics.word_metrics.curse_words_per_author),
    textposition: 'outside' as const,
    marker: {
      color: generateColors(Object.keys(metrics.word_metrics.curse_words_per_author).length)
    },
    width: 0.6
  };

  const curseWordsFrequency = {
      x: Object.keys(metrics.word_metrics.curse_words_frequency),
      y: Object.values(metrics.word_metrics.curse_words_frequency),
      type: 'bar' as const,
      text: Object.values(metrics.word_metrics.curse_words_frequency),
      textposition: 'outside' as const,
      marker: {
        color: generateColors(Object.keys(metrics.word_metrics.curse_words_frequency).length)
      },
      width: 0.6
  };

  const commonWords = {
    x: Object.keys(metrics.common_words),
    y: Object.values(metrics.common_words),
    type: 'bar' as const,
    text: Object.values(metrics.common_words),
    textposition: 'outside' as const,
    marker: {
      color: generateColors(Object.keys(metrics.common_words).length)
    },
    width: 0.6
  };

  const layout = {
    font: { color: '#ffffff' },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    xaxis: {
      showgrid: false,
      tickfont: { color: '#ffffff' }
    },
    yaxis: {
      showgrid: false,
      showticklabels: false,
    },
    margin: { t: 30, l: 50, r: 50, b: 60 },
  };

  return (
    <div style={{ 
        textAlign: 'center', 
        color: '#ffffff', 
        marginBottom: '20px'
    }}>
        <h2>Word metrics</h2>
        <h3>Messages per author</h3>
        <h4>
          {Object.keys(metrics.word_metrics.messages_per_author).length > 2 
            ? "📊 Let's see who's been keeping the chat alive! 🗣️" 
            : "📊 Let's see your conversation history! 🗣️"}
        </h4>
        <div style={getContainerStyle(Object.keys(metrics.word_metrics.messages_per_author).length)}>
            <Plot
                data={[messagesPerAuthor]}
                layout={{...layout,}}
                style={{ width: '100%', height: '400px' }}
                config={{ responsive: true, displayModeBar: false }}
            />
        </div>

        <h3>Average Message Length</h3>
        <h4>
          {Object.keys(metrics.word_metrics.average_message_length).length > 2 
            ? "🔍 Who's the group's chatterbox? Find out below! 💬" 
            : "🔍 Let's compare your message lengths! 💬"}
        </h4>
        <div style={getContainerStyle(Object.keys(metrics.word_metrics.average_message_length).length)}>
            <Plot
                data={[averageMessageLength]}
                layout={{...layout}}
                style={{ width: '100%', height: '400px' }}
                config={{ responsive: true, displayModeBar: false }}
            />
        </div>

        <h3>Curse Words per Author</h3>
        <h4>
          {Object.keys(metrics.word_metrics.curse_words_per_author).length > 2 
            ? "🤐 Time to see who's been keeping it spicy! 🌶️" 
            : "🤐 Let's check out the spicy vocabulary! 🌶️"}
        </h4>
        <div style={getContainerStyle(Object.keys(metrics.word_metrics.curse_words_per_author).length)}>
            <Plot
                data={[curseWordsPerAuthor]}
                layout={{...layout}}
                style={{ width: '100%', height: '400px' }}
                config={{ responsive: true, displayModeBar: false }}
            />
        </div>

        <h3>Most Used Curse Words</h3>
        <h4>
          {Object.keys(metrics.word_metrics.curse_words_frequency).length > 5 
            ? "🔥 Here's the hall of fame for spicy vocabulary! 🏆" 
            : "🔥 A peek at the spicier side of your chat! 🌶️"}
        </h4>
        <div style={getContainerStyle(Object.keys(metrics.word_metrics.curse_words_frequency).length)}>
            <Plot
                data={[curseWordsFrequency]}
                layout={{...layout}}
                style={{ width: '100%', height: '400px' }}
                config={{ responsive: true, displayModeBar: false }}
            />
        </div>

        <h2>Most Common Words</h2>
        <h4>📚 The most popular words in your conversations! 🔍</h4>
        <div style={getContainerStyle(Object.keys(metrics.common_words).length)}>
            <Plot
                data={[commonWords]}
                layout={{...layout}}
                style={{ width: '100%', height: '400px' }}
                config={{ responsive: true, displayModeBar: false }}
            />
        </div>
    </div>
  );
};

export default PlotlyBarCharts;