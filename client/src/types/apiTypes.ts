export interface ConversationStats {
  average_length: number;
  longest_conversation_length: number;
  longest_conversation_start: Date;
  longest_conversation_end: Date;
}

export interface WordMetrics {
  messages_per_author: {
    [author: string]: number;
  };
  average_message_length: {
    [author: string]: number;
  };
  curse_words_per_author: {
    [author: string]: number;
  };
  curse_words_by_author: {
    [author: string]: {
      [word: string]: number;
    };
  };
  curse_words_frequency: {
    [word: string]: number;
  };
}

export interface CommonWord {
  word: string;
  count: number;
}

// export interface HeatmapPoint {
//   x: number;  // week number (0-52)
//   y: number;  // weekday (0-6)
//   v: number;  // normalized value (0-100)
// }

export interface HeatmapData {
  z: number[][];         // 7x53 matrix
  x: string[];          // week labels
  y: string[];          // weekday labels
  zmin: number;
  zmax: number;
  dates: string[][];      // date strings
}

export interface AnalysisResponse {
  heatmap_data: HeatmapData;
  conversation_stats: ConversationStats;
  word_metrics: WordMetrics;
  common_words: CommonWord[];
}