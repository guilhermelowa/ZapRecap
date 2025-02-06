import React, { useState } from 'react';
import { AnalysisResponse, PremiumFeatures } from '../types/apiTypes';
import { useTranslation } from 'react-i18next';
import ReportButton from './ReportButton';

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
        <section className="author-simulator">
            <h2 style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {t('simulator.title')}
                <ReportButton 
                    sectionId="author-simulator"
                    sectionName="Author Simulator"
                    contextData={metrics.author_messages}
                />
            </h2>
            <p>{t('simulator.selectParticipant')}</p>
            
            <div className="simulator-controls">
                <select 
                    value={selectedAuthor}
                    onChange={(e) => setSelectedAuthor(e.target.value)}
                    className="author-select"
                >
                    <option value="">{t('simulator.selectParticipant')}</option>
                    {authors.map(author => (
                        <option key={author} value={author}>
                            {author} ({metrics.word_metrics.messages_per_author[author]} messages)
                        </option>
                    ))}
                </select>

                {selectedAuthor && (
                    <div className="author-stats">
                        <p>{t('stats.averageWords')}: {Math.round(metrics.word_metrics.average_message_length[selectedAuthor])} words</p>
                        <p>{t('stats.totalWords')}: {metrics.word_metrics.messages_per_author[selectedAuthor]}</p>
                    </div>
                )}

                <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder={t('simulator.promptPlaceholder')}
                    className="prompt-input"
                />

                <button 
                    onClick={handleSimulation}
                    disabled={isLoading || !selectedAuthor || !prompt}
                    className="simulate-button"
                >
                    {isLoading ? t('simulator.generating') : t('simulator.generateMessage')}
                </button>
            </div>

            {response && (
                <div className="simulation-response">
                    <h3>{t('simulator.generatedMessage')}:</h3>
                    <div className="message-bubble">
                        <span className="author-name">{selectedAuthor}</span>
                        <p className="response-text">{response}</p>
                    </div>
                </div>
            )}

            <style jsx>{`
                .author-simulator {
                    background: rgba(0, 0, 0, 0.2);
                    padding: 20px;
                    border-radius: 10px;
                    margin: 20px 0;
                }

                .simulator-controls {
                    display: flex;
                    flex-direction: column;
                    gap: 15px;
                    margin: 20px 0;
                }

                .author-select {
                    padding: 10px;
                    border-radius: 5px;
                    background: rgba(255, 255, 255, 0.1);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }

                .author-stats {
                    background: rgba(255, 255, 255, 0.1);
                    padding: 10px;
                    border-radius: 5px;
                    margin-top: -10px;
                }

                .author-stats p {
                    margin: 5px 0;
                    font-size: 0.9em;
                    color: rgba(255, 255, 255, 0.8);
                }

                .prompt-input {
                    padding: 10px;
                    border-radius: 5px;
                    background: rgba(255, 255, 255, 0.1);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    min-height: 100px;
                    resize: vertical;
                }

                .simulate-button {
                    padding: 10px 20px;
                    border-radius: 5px;
                    background: #25d366;
                    color: white;
                    border: none;
                    cursor: pointer;
                    font-weight: bold;
                }

                .simulate-button:disabled {
                    background: rgba(37, 211, 102, 0.5);
                    cursor: not-allowed;
                }

                .simulation-response {
                    margin-top: 20px;
                }

                .message-bubble {
                    background: #025C4C;
                    padding: 10px 15px;
                    border-radius: 10px;
                    margin-top: 10px;
                    position: relative;
                }

                .author-name {
                    color: #25d366;
                    font-weight: bold;
                    font-size: 0.9em;
                    display: block;
                    margin-bottom: 5px;
                }

                .response-text {
                    white-space: pre-wrap;
                    word-break: break-word;
                    margin: 0;
                }
            `}</style>
        </section>
    );
};

export default AuthorSimulator;