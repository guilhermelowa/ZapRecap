import React, { useState } from 'react';
import { AnalysisResponse, PremiumFeatures } from '../types/apiTypes';
import { useTranslation } from 'react-i18next';
import ReportButton from './ReportButton';
import styles from '../styles/components/AuthorSimulator.module.css';

interface AuthorSimulatorProps {
    metrics: AnalysisResponse;
    onPremiumFeaturesReceived?: (features: PremiumFeatures) => void;
    selectedModel: string;
}

const AuthorSimulator: React.FC<AuthorSimulatorProps> = ({ metrics, onPremiumFeaturesReceived, selectedModel }) => {
    const [selectedAuthor, setSelectedAuthor] = useState<string>('');
    const [prompt, setPrompt] = useState<string>('');
    const [response, setResponse] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const { t } = useTranslation();

    // Get unique authors from the conversation
    const authors = Object.keys(metrics.word_metrics.messages_per_author);

    const handleSimulation = async () => {
        if (!selectedAuthor || !prompt) return;

        setIsLoading(true);
        try {
            if (!metrics.author_messages || !metrics.author_messages[selectedAuthor]) {
                throw new Error('No messages found for the selected author');
            }

            const response = await fetch('http://localhost:8000/premium-features', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    conversation: metrics.author_messages[selectedAuthor],
                    author: selectedAuthor,
                    prompt: prompt,
                    language: 'pt',
                    model: selectedModel,
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to simulate message');
            }

            const data: PremiumFeatures = await response.json();
            setResponse(data.simulated_message);
            
            // Pass the premium features up to parent component
            if (onPremiumFeaturesReceived) {
                onPremiumFeaturesReceived(data);
            }
        } catch (error) {
            console.error('Error simulating message:', error);
            setResponse(error instanceof Error ? error.message : 'Error generating message. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <section className={styles['author-simulator']}>
            <h2 className={styles['section-title']}>
                {t('simulator.title')}
                <ReportButton 
                    sectionId="author-simulator"
                    sectionName="Author Simulator"
                    contextData={metrics.author_messages}
                />
            </h2>
            
            <div className={styles['simulator-controls']}>
                <select 
                    value={selectedAuthor}
                    onChange={(e) => setSelectedAuthor(e.target.value)}
                    className={styles['author-select']}
                >
                    <option value="">{t('simulator.selectParticipant')}</option>
                    {authors.map(author => (
                        <option key={author} value={author}>
                            {author} ({metrics.word_metrics.messages_per_author[author]} messages)
                        </option>
                    ))}
                </select>

                {selectedAuthor && (
                    <div className={styles['author-stats']}>
                        <p>{t('stats.averageWords')}: {Math.round(metrics.word_metrics.average_message_length[selectedAuthor])} words</p>
                        <p>{t('stats.totalWords')}: {metrics.word_metrics.messages_per_author[selectedAuthor]}</p>
                    </div>
                )}

                <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder={t('simulator.promptPlaceholder')}
                    className={styles['prompt-input']}
                />

                <button 
                    onClick={handleSimulation}
                    disabled={isLoading || !selectedAuthor || !prompt}
                    className={styles['simulate-button']}
                >
                    {isLoading ? t('simulator.generating') : t('simulator.generateMessage')}
                </button>
            </div>

            {response && (
                <div className={styles['simulation-response']}>
                    <h3>{t('simulator.generatedMessage')}:</h3>
                    <div className={styles['message-bubble']}>
                        <span className={styles['author-name']}>{selectedAuthor}</span>
                        <p className={styles['response-text']}>{response}</p>
                    </div>
                </div>
            )}
        </section>
    );
};

export default AuthorSimulator;