import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import ReportButton from './ReportButton';

interface ConversationThemesProps {
    themes?: { [theme: string]: string };
    conversationId?: string;
    selectedModel: string;
    onThemesGenerated: (themes: { [theme: string]: string }) => void;
}

const ConversationThemes: React.FC<ConversationThemesProps> = ({ 
    themes, 
    conversationId,
    selectedModel,
    onThemesGenerated 
}) => {
    const { t } = useTranslation();
    const [isLoading, setIsLoading] = useState<boolean>(false);

    const handleGenerateThemes = async () => {
        if (!conversationId || isLoading) return;
        
        setIsLoading(true);
        try {
            const response = await fetch('http://localhost:8000/conversation-themes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    conversation_id: conversationId,
                    model: selectedModel
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            onThemesGenerated(data.themes);
        } catch (error) {
            console.error('Error generating themes:', error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <section id="theme-patterns" className="theme-patterns" style={{
            backgroundColor: 'rgba(0, 0, 0, 0.2)',
            padding: '20px',
            borderRadius: '10px',
            margin: '20px 0'
        }}>
            <h3>
                {t('premium.themesTitle')}
                <ReportButton 
                    sectionId="theme-patterns" 
                    sectionName="Theme Patterns"
                    contextData={themes}
                />
            </h3>
            <button 
                onClick={handleGenerateThemes}
                disabled={isLoading}
                className="green-button"
            >
                {isLoading ? t('premium.generating') : t('premium.generateThemes')}
            </button>

            {themes && Object.keys(themes).length > 0 && (
                <>
                    <p>{t('stats.commonThemes')}</p>
                    <div className="themes-container">
                        {Object.entries(themes).map(([theme, example], index) => (
                            <div key={index} className="theme-item">
                                <div>{theme}</div>
                                {example && (
                                    <div className="theme-example">
                                        - {example}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </>
            )}
        </section>
    );
};

export default ConversationThemes; 