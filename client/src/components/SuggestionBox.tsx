import React, { useState } from 'react';
import apiClient from '../services/axiosConfig';
import { useTranslation } from 'react-i18next';
import styles from '../styles/components/SuggestionBox.module.css';

interface SuggestionBoxProps {
  conversationId?: string;
}

const SuggestionBox: React.FC<SuggestionBoxProps> = ({ conversationId }) => {
  const [suggestion, setSuggestion] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const { t } = useTranslation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      const { _data } = await apiClient.post(
        '/suggestions',
        {
          suggestion,
          conversationId: conversationId || null,
          timestamp: new Date().toISOString(),
        }
      );

      setSubmitStatus('success');
      setSuggestion('');
    } catch (error) {
      setSubmitStatus('error');
      console.error('Error submitting suggestion:', error);
    } finally {
      setIsSubmitting(false);
      setTimeout(() => setSubmitStatus('idle'), 3000);
    }
  };

  return (
    <section className={styles['suggestion-box']}>
      <h2 className={styles['section-title']}>
        {t('suggestions.title')}
      </h2>
      
      <div className={styles['suggestion-controls']}>
        <form onSubmit={handleSubmit}>
          <textarea
            value={suggestion}
            onChange={(e) => setSuggestion(e.target.value)}
            placeholder={t('suggestions.placeholder')}
            className={styles['suggestion-input']}
          />
          <div className={styles['button-container']}>
            <button 
              type="submit"
              disabled={isSubmitting || !suggestion.trim()}
              className={styles['submit-button']}
            >
              {isSubmitting ? t('suggestions.submitting') : t('suggestions.submit')}
            </button>
            {submitStatus !== 'idle' && (
              <span className={`${styles['status-message']} ${styles[submitStatus]}`}>
                {t('suggestions.success')}
              </span>
            )}
          </div>
        </form>
      </div>
    </section>
  );
};

export default SuggestionBox; 