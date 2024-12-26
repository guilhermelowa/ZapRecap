import React from 'react';
import { useLocation } from 'react-router-dom';
import WordCloudComponent from '../components/WordCloud';
import Header from '../components/Header';

const ResultsPage = () => {
  const location = useLocation();
  console.log('Location state:', location.state);
  
  if (!location.state) {
    return <div>No data available</div>;
  }

  const { result } = location.state;
  console.log('Result data:', result);  // Debug result

  return (
    <div>
      <Header />
      <h1>Analysis Results</h1>
      <pre>{JSON.stringify(result, null, 2)}</pre>
      <h2>Word Cloud</h2>
      <WordCloudComponent words={result.word_cloud_data} />
    </div>
  );
};

export default ResultsPage;