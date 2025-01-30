import React from 'react';
import Plot from 'react-plotly.js';
import { AnalysisResponse } from '../types/apiTypes';
import { useTranslation } from 'react-i18next';
import ReportButton from './ReportButton';

interface PlotlyBarChartsProps {
  metrics: AnalysisResponse;
}

const PlotlyBarCharts: React.FC<PlotlyBarChartsProps> = ({ metrics }) => {
  const { t, i18n } = useTranslation();

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
    // Base width per bar in pixels
    const widthPerBar = 100;
    // Calculate total width based on number of bars
    const calculatedWidth = dataLength * widthPerBar;
    // Get viewport width
    const viewportWidth = typeof window !== 'undefined' ? window.innerWidth : 1024;
    // Maximum width should be 90% of viewport
    const maxWidth = viewportWidth * 0.9;
    // Final width in pixels (minimum 300px, maximum maxWidth)
    const finalWidth = Math.max(300, Math.min(calculatedWidth, maxWidth));
    
    return {
      position: 'relative' as const,
      width: `${finalWidth}px`,
      maxWidth: '90vw',
      innerHeight: '500px',
      outerHeight: '500px',
      display: 'flex',
      justifyContent: 'center',
      overflow: 'hidden',
      margin: '0 auto 100px auto',
      padding: 0,
      boxSizing: 'border-box' as const
    };
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
    <div style={{ textAlign: 'center', color: '#ffffff', marginBottom: '20px' }}>
      <h2 style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        {t('results.wordMetrics')}
      </h2>
      <div id="word-metrics">
        <h3 style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          {t('results.messagesPerAuthor')}
          <ReportButton 
            sectionId="messages-per-author"
            sectionName="Messages per Author"
            contextData={messagesPerAuthor}
          />
        </h3>
        <h4>
          {Object.keys(metrics.word_metrics.messages_per_author).length > 2 
            ? t('charts.messageDistributionHigh') 
            : t('charts.messageDistributionLow')}
        </h4>
        <div style={getContainerStyle(Object.keys(metrics.word_metrics.messages_per_author).length)}>
          <Plot
            data={[messagesPerAuthor]}
            layout={{...layout,}}
            style={{ width: '100%', height: '400px' }}
            config={{ responsive: true, displayModeBar: false }}
          />
        </div>

        <h3 style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          {t('results.averageMessageLength')}
          <ReportButton 
            sectionId="average-message-length"
            sectionName="Average Message Length"
            contextData={averageMessageLength}
          />
        </h3>
        <h4>
          {Object.keys(metrics.word_metrics.average_message_length).length > 2 
            ? t('charts.averageMessageLengthHigh')
            : t('charts.averageMessageLengthLow')}
        </h4>
        <div style={getContainerStyle(Object.keys(metrics.word_metrics.average_message_length).length)}>
          <Plot
            data={[averageMessageLength]}
            layout={{...layout}}
            style={{ width: '100%', height: '400px' }}
            config={{ responsive: true, displayModeBar: false }}
          />
        </div>

        <h3 style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          {t('results.curseWordsPerAuthor')}
          <ReportButton 
            sectionId="curse-words-per-author"
            sectionName="Curse Words per Author"
            contextData={curseWordsPerAuthor}
          />
        </h3>
        <h4>
          {Object.keys(metrics.word_metrics.curse_words_per_author).length > 2 
            ? t('results.curseWordsHighParticipants')
            : t('results.curseWordsLowParticipants')}
        </h4>
        <div style={getContainerStyle(Object.keys(metrics.word_metrics.curse_words_per_author).length)}>
          <Plot
            data={[curseWordsPerAuthor]}
            layout={{...layout}}
            style={{ width: '100%', height: '400px' }}
            config={{ responsive: true, displayModeBar: false }}
          />
        </div>

        <h3 style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          {t('results.curseWordsFrequency')}
          <ReportButton 
            sectionId="curse-words-frequency"
            sectionName="Curse Words Frequency"
            contextData={curseWordsFrequency}
          />
        </h3>
        <h4>
          {Object.keys(metrics.word_metrics.curse_words_frequency).length > 5 
            ? t('results.curseWordsHighFrequency')
            : t('results.curseWordsLowFrequency')}
        </h4>
        <div style={getContainerStyle(Object.keys(metrics.word_metrics.curse_words_frequency).length)}>
          <Plot
            data={[curseWordsFrequency]}
            layout={{...layout}}
            style={{ width: '100%', height: '400px' }}
            config={{ responsive: true, displayModeBar: false }}
          />
        </div>

        <h3 style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          {t('results.mostCommonWords')}
          <ReportButton 
            sectionId="most-common-words"
            sectionName="Most Common Words"
            contextData={curseWordsFrequency}
          />
        </h3>
        <h4>{t('results.mostCommonWordsDescription')}</h4>
        <div style={getContainerStyle(Object.keys(metrics.common_words).length)}>
          <Plot
            data={[commonWords]}
            layout={{...layout}}
            style={{ width: '100%', height: '400px' }}
            config={{ responsive: true, displayModeBar: false }}
          />
        </div>
      </div>
    </div>
  );
};

export default PlotlyBarCharts;