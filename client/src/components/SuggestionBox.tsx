import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

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
      const response = await fetch('/api/suggestions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          suggestion,
          conversationId: conversationId || null,
          timestamp: new Date().toISOString(),
        }),
      });

      if (!response.ok) throw new Error('Failed to submit');
      
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
    <section className="suggestion-box">
      <h2 style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        {t('suggestions.title')}
      </h2>
      
      <div className="suggestion-controls">
        <form onSubmit={handleSubmit}>
          <textarea
            value={suggestion}
            onChange={(e) => setSuggestion(e.target.value)}
            placeholder={t('suggestions.placeholder')}
            className="suggestion-input"
            disabled={isSubmitting}
          />
          
          <div className="button-container">
            <button
              type="submit"
              disabled={isSubmitting || !suggestion.trim()}
              className="submit-button"
            >
              {isSubmitting ? t('common.submitting') : t('suggestions.submit')}
            </button>
            {submitStatus === 'success' && (
              <span className="status-message success">{t('suggestions.thankYou')}</span>
            )}
            {submitStatus === 'error' && (
              <span className="status-message error">{t('suggestions.error')}</span>
            )}
          </div>
        </form>
      </div>

      <style jsx>{`
        .suggestion-box {
          background: rgba(0, 0, 0, 0.2);
          padding: 20px;
          border-radius: 10px;
          margin: 20px 0;
        }

        .suggestion-controls {
          display: flex;
          flex-direction: column;
          gap: 15px;
          margin: 20px 0;
        }

        .suggestion-input {
          width: 100%;
          padding: 10px;
          border-radius: 5px;
          background: rgba(255, 255, 255, 0.1);
          color: white;
          border: 1px solid rgba(255, 255, 255, 0.2);
          min-height: 100px;
          resize: vertical;
          margin-bottom: 15px;
        }

        .button-container {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .submit-button {
          padding: 10px 20px;
          border-radius: 5px;
          background: #25d366;
          color: white;
          border: none;
          cursor: pointer;
          font-weight: bold;
        }

        .submit-button:disabled {
          background: rgba(37, 211, 102, 0.5);
          cursor: not-allowed;
        }

        .status-message {
          padding: 5px 10px;
          border-radius: 5px;
          font-size: 0.9em;
        }

        .success {
          color: #25d366;
        }

        .error {
          color: #ff4444;
        }
      `}</style>
    </section>
  );
};

export default SuggestionBox; 