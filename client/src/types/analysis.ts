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

export interface AnalysisResponse {
  conversation_stats: ConversationStats;
  word_metrics: WordMetrics;
  common_words: CommonWord[];
}