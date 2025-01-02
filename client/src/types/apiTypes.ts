export interface PeriodStats {
  period: number;
  count: number;
}

export interface ConversationSample {
  start_date: Date;
  messages: string[];
}

export interface ConversationStats {
  total_messages: number;
  participant_count: number;
  average_length: number;
  longest_conversation_length: number;
  longest_conversation_start: Date;
  longest_conversation_end: Date;
  conversation_samples: ConversationSample[];
  most_active_weekday: PeriodStats;
  least_active_weekday: PeriodStats;
  most_active_week: PeriodStats;
  least_active_week: PeriodStats;
  most_active_month: PeriodStats;
  least_active_month: PeriodStats;
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
  common_words: {
    [word: string]: number;
  }
}