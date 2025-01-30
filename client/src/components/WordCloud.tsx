import React, { useEffect, useRef } from 'react';
import WordCloud from 'wordcloud';

interface Word {
  text: string;
  value: number;
}

interface WordCloudComponentProps {
  words: Word[];
}

const WordCloudComponent: React.FC<WordCloudComponentProps> = ({ words }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (canvasRef.current) {
      WordCloud(canvasRef.current, {
        list: words.map(word => [word.text, word.value]),
        gridSize: 16,
        weightFactor: 3,
        fontFamily: 'Times, serif',
        color: 'random-dark',
        rotateRatio: 0.5,
        rotationSteps: 2,
        backgroundColor: '#ffffff',
      });
    }
  }, [words]);

  return (
    <canvas ref={canvasRef}></canvas>
  );
};

export default WordCloudComponent;