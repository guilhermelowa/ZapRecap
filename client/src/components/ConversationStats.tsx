import React, { useState, useRef } from 'react';
import { ConversationStats as Stats } from '../types/apiTypes';
import { format } from 'date-fns';
import { useTranslation } from 'react-i18next';
import ReportButton from './ReportButton';

interface ConversationStatsProps {
    stats: Stats;
}

const styles = `
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;

const styleSheet = document.createElement("style");
styleSheet.innerText = styles;
document.head.appendChild(styleSheet);

const ConversationStats: React.FC<ConversationStatsProps> = ({ stats }) => {
    const { t } = useTranslation();
    const weekdays = t('weekdays', { returnObjects: true }) as string[];
    const months = t('months', { returnObjects: true }) as string[];
    const [showTooltip, setShowTooltip] = useState(false);
    const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
    const questionMarkRef = useRef<HTMLSpanElement>(null);

    const updateTooltipPosition = () => {
        if (questionMarkRef.current) {
            const rect = questionMarkRef.current.getBoundingClientRect();
            setTooltipPosition({
                x: rect.left,
                y: rect.bottom + window.scrollY + 8 // 8px below the question mark
            });
        }
    };

    return (
        <div className="stats-container" style={{ color: '#ffffff', padding: '20px' }}>
            <section id="conversation-length" className="conversation-length">
                <h3>
                    {t('stats.conversationPatterns')}
                    <ReportButton 
                        sectionId="conversation-length" 
                        sectionName="Conversation Length"
                        contextData={stats}
                    />
                    <span 
                        ref={questionMarkRef}
                        style={{ 
                            marginLeft: '8px',
                            cursor: 'help',
                            display: 'inline-flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            width: '20px',
                            height: '20px',
                            borderRadius: '50%',
                            backgroundColor: 'rgba(255, 255, 255, 0.1)',
                            fontSize: '14px',
                            transition: 'all 0.2s ease',
                            border: '1px solid rgba(255, 255, 255, 0.2)',
                            position: 'relative'
                        }}
                        onMouseEnter={(e) => {
                            const target = e.currentTarget;
                            target.style.transform = 'scale(1.1)';
                            target.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
                            updateTooltipPosition();
                            setShowTooltip(true);
                        }}
                        onMouseLeave={(e) => {
                            const target = e.currentTarget;
                            target.style.transform = 'scale(1)';
                            target.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
                            setShowTooltip(false);
                        }}
                    >
                        ?
                    </span>
                </h3>
                {showTooltip && (
                    <div 
                        style={{
                            position: 'absolute',
                            left: `${tooltipPosition.x}px`,
                            top: `${tooltipPosition.y}px`,
                            backgroundColor: 'rgba(30, 30, 30, 0.95)',
                            border: '1px solid rgba(255, 255, 255, 0.2)',
                            borderRadius: '8px',
                            padding: '12px 16px',
                            maxWidth: '300px',
                            zIndex: 1000,
                            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                            fontSize: '14px',
                            lineHeight: '1.5',
                            color: 'rgba(255, 255, 255, 0.9)',
                            backdropFilter: 'blur(5px)',
                            animation: 'fadeIn 0.2s ease-in-out'
                        }}
                    >
                        {t('stats.conversationDefinition')}
                    </div>
                )}
                <p>
                    {t('stats.averageConversationLength')} <b>{stats.average_length}</b> {t('stats.messages') + " "}
                    {stats.average_length > 10 ? t('stats.chattersComment') : t('stats.shortSweetComment')}
                </p>
                <p>
                    {t('stats.longestConversation')} <b>{stats.longest_conversation_length}</b> {t('stats.messages') + " "}
                    {t('stats.startingOn')} {format(new Date(stats.longest_conversation_start), 'PPP')}{' '}
                    {t('stats.endingOn')} {format(new Date(stats.longest_conversation_end), 'PPP')}. 
                    {" " + t('stats.epicComment')}
                </p>
            </section>

            <section id="active-periods" className="active-periods">
                <h3>
                    {t('stats.timePatterns')}
                    <ReportButton 
                        sectionId="active-periods" 
                        sectionName="Active Periods"
                        contextData={stats}
                    />
                </h3>
                <p>
                    {weekdays[stats.most_active_weekday.period]} {t('stats.powerDay')}
                    {' '}<b>{stats.most_active_weekday.count}</b> {t('stats.messagesLastYear')}
                </p>
                <p>
                    {weekdays[stats.least_active_weekday.period]} {t('stats.quietDay') + " "}
                    <b>{stats.least_active_weekday.count}</b>.
                    {" " + (stats.least_active_weekday.period === 1 ? t('stats.mondayBlues') : t('stats.takingBreak'))}
                </p>
            </section>

            <section id="monthly-patterns" className="monthly-patterns">
                <h3>
                    {t('stats.monthlyReview')}
                    <ReportButton 
                        sectionId="monthly-patterns" 
                        sectionName="Monthly Patterns"
                        contextData={stats}
                    />
                </h3>
                <p>
                    {t(`months.${stats.most_active_month.period}`)} {t('stats.chattiestMonth')}
                    {' '}<b>{stats.most_active_month.count}</b> {t('stats.messages')}! 
                    {' ' + (stats.most_active_month.period >= 6 && stats.most_active_month.period <= 8 ? 
                    t('stats.summerVibes') : t('stats.normalVibes'))}
                </p>
                <p>
                    {t(`months.${stats.least_active_month.period}`)} {t('stats.quietMonth')}
                    {' '}<b>{stats.least_active_month.count}</b> {t('stats.messages')}. 
                    {stats.least_active_month.period === 12 ? t('stats.holidayBreak') : t('stats.quietVibes')}
                </p>
            </section>

            <section id="weekly-insights" className="weekly-insights">
                <h3>
                    {t('stats.weeklyRhythms')}
                    <ReportButton 
                        sectionId="weekly-insights" 
                        sectionName="Weekly Insights"
                        contextData={stats}
                    />
                </h3>
                <p>
                    {t('stats.intenseWeek')} <b>{stats.most_active_week.period + 1}</b> {t('stats.wasIntense')}
                    {' '}<b>{stats.most_active_week.count}</b> {t('stats.whatHappened')}
                </p>
                <p>
                    {t('stats.intenseWeek')} <b>{stats.least_active_week.period + 1}</b> {t('stats.quietestWeek')}
                    {' '}<b>{stats.least_active_week.count}</b> {t('stats.vacationTime')}
                </p>
            </section>

            <section id="theme-patterns" className="theme-patterns">
                <h3>
                    {t('stats.themesFromBusiestDay')}
                    <ReportButton 
                        sectionId="theme-patterns" 
                        sectionName="Theme Patterns"
                        contextData={stats}
                    />
                </h3>
                <p>{t('stats.commonThemes')}</p>
                <div style={{ 
                    padding: '10px', 
                    borderRadius: '5px',
                    marginTop: '10px',
                    backgroundColor: 'rgba(255, 255, 255, 0.1)'
                }}>
                    {Object.entries(stats.themes).map(([theme, example], index) => (
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
        </div>
    );
};

export default ConversationStats;