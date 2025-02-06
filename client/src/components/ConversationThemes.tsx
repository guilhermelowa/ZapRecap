import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import ReportButton from './ReportButton';
import styles from '../styles/components/ConversationThemes.module.css';

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
        <section id="theme-patterns" className={styles['theme-patterns']}>
            <h2 className={styles['section-title']}>
                <span>{t('premium.themesTitle')}</span>
                <ReportButton 
                    sectionId="theme-patterns" 
                    sectionName="Theme Patterns"
                    contextData={themes}
                />
            </h2>
            <button 
                onClick={handleGenerateThemes}
                disabled={isLoading}
                className={styles['generate-button']}
            >
                {isLoading ? t('premium.generating') : t('premium.generateThemes')}
            </button>

            {themes && Object.keys(themes).length > 0 && (
                <>
                    <p className={styles['themes-description']}>{t('stats.commonThemes')}</p>
                    <div className={styles['themes-container']}>
                        {Object.entries(themes).map(([theme, example], index) => (
                            <div key={index} className={styles['theme-item']}>
                                <div className={styles['theme-title']}>{theme}</div>
                                {example && (
                                    <div className={styles['theme-example']}>
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