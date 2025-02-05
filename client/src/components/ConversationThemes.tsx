import React from 'react';
import { useTranslation } from 'react-i18next';
import ReportButton from './ReportButton';

interface ConversationThemesProps {
    themes?: { [theme: string]: string };
}

const ConversationThemes: React.FC<ConversationThemesProps> = ({ themes }) => {
    const { t } = useTranslation();

    if (!themes || Object.keys(themes).length === 0) {
        return (
            <section id="theme-patterns" className="theme-patterns">
                <h3>{t('stats.themesFromBusiestDay')}</h3>
                <p>No themes available</p>
            </section>
        );
    }

    return (
        <section id="theme-patterns" className="theme-patterns">
            <h3>
                {t('stats.themesFromBusiestDay')}
                <ReportButton 
                    sectionId="theme-patterns" 
                    sectionName="Theme Patterns"
                    contextData={themes}
                />
            </h3>
            <p>{t('stats.commonThemes')}</p>
            <div style={{ 
                padding: '10px', 
                borderRadius: '5px',
                marginTop: '10px',
                backgroundColor: 'rgba(255, 255, 255, 0.1)'
            }}>
                {Object.entries(themes).map(([theme, example], index) => (
                    <div key={index} style={{ 
                        marginBottom: '12px',
                        padding: '8px 12px',
                        borderRadius: '4px',
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        border: '1px solid rgba(255, 255, 255, 0.1)'
                    }}>
                        <div>{theme}</div>
                        {example && (
                            <div style={{
                                marginTop: '4px',
                                marginLeft: '20px',
                                fontSize: '0.95em',
                                color: 'rgba(255, 255, 255, 0.8)'
                            }}>
                                - {example}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </section>
    );
};

export default ConversationThemes; 