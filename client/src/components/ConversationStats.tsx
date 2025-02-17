import React, { useState, useRef } from 'react';
import { ConversationStats as Stats } from '../types/apiTypes';
import { format } from 'date-fns';
import { useTranslation } from 'react-i18next';
import ReportButton from './ReportButton';
import styles from '../styles/components/ConversationStats.module.css';

interface ConversationStatsProps {
    stats: Stats;
}

const ConversationStats: React.FC<ConversationStatsProps> = ({ stats }) => {
    const { t } = useTranslation();
    const weekdays = t('weekdays', { returnObjects: true }) as string[];
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
        <div className="stats-container">
            <section className={styles['stats-section']}>
                <h3 className={styles['stats-title']}>
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
                <p className={styles['stats-text']}>
                    {t('stats.averageConversationLength') + ' '} 
                    <span className={styles['stats-highlight']}>{stats.average_length}</span> 
                    {' ' + t('stats.messages') + ' '}
                    {stats.average_length > 10 ? t('stats.chattersComment') : t('stats.shortSweetComment')}
                </p>
                <p className={styles['stats-text']}>
                    {t('stats.longestConversation')} <span className={styles['stats-highlight']}>{stats.longest_conversation_length}</span> {t('stats.messages') + " "}
                    {t('stats.startingOn')} {format(new Date(stats.longest_conversation_start), 'PPP')}{' '}
                    {t('stats.endingOn')} {format(new Date(stats.longest_conversation_end), 'PPP')}. 
                    {" " + t('stats.epicComment')}
                </p>
            </section>

            <section className={styles['stats-section']}>
                <h3 className={styles['stats-title']}>
                    {t('stats.timePatterns')}
                    <ReportButton 
                        sectionId="active-periods" 
                        sectionName="Active Periods"
                        contextData={stats}
                    />
                </h3>
                <p className={styles['stats-text']}>
                    {weekdays[stats.most_active_weekday.period]} {t('stats.powerDay')}
                    {' '}<span className={styles['stats-highlight']}>{stats.most_active_weekday.count}</span> {t('stats.messagesLastYear')}
                </p>
                <p className={styles['stats-text']}>
                    {weekdays[stats.least_active_weekday.period]} {t('stats.quietDay') + " "}
                    <span className={styles['stats-highlight']}>{stats.least_active_weekday.count}</span>.
                    {" " + (stats.least_active_weekday.period === 1 ? t('stats.mondayBlues') : t('stats.takingBreak'))}
                </p>
            </section>

            <section className={styles['stats-section']}>
                <h3 className={styles['stats-title']}>
                    {t('stats.monthlyReview')}
                    <ReportButton 
                        sectionId="monthly-patterns" 
                        sectionName="Monthly Patterns"
                        contextData={stats}
                    />
                </h3>
                <p className={styles['stats-text']}>
                    {t(`months.${stats.most_active_month.period}`)} {t('stats.chattiestMonth')}
                    {' '}<span className={styles['stats-highlight']}>{stats.most_active_month.count}</span> {t('stats.messages')}! 
                    {' ' + (stats.most_active_month.period >= 6 && stats.most_active_month.period <= 8 ? 
                    t('stats.summerVibes') : t('stats.normalVibes'))}
                </p>
                <p className={styles['stats-text']}>
                    {t(`months.${stats.least_active_month.period}`)} {t('stats.quietMonth')}
                    {' '}<span className={styles['stats-highlight']}>{stats.least_active_month.count}</span> {t('stats.messages')}. 
                    {stats.least_active_month.period === 12 ? t('stats.holidayBreak') : t('stats.quietVibes')}
                </p>
            </section>

            <section className={styles['stats-section']}>
                <h3 className={styles['stats-title']}>
                    {t('stats.weeklyRhythms')}
                    <ReportButton 
                        sectionId="weekly-insights" 
                        sectionName="Weekly Insights"
                        contextData={stats}
                    />
                </h3>
                <p className={styles['stats-text']}>
                    {t('stats.intenseWeek')} <span className={styles['stats-highlight']}>{stats.most_active_week.period + 1}</span> {t('stats.wasIntense')}
                    {' '}<span className={styles['stats-highlight']}>{stats.most_active_week.count}</span> {t('stats.whatHappened')}
                </p>
                <p className={styles['stats-text']}>
                    {t('stats.intenseWeek')} <span className={styles['stats-highlight']}>{stats.least_active_week.period + 1}</span> {t('stats.quietestWeek')}
                    {' '}<span className={styles['stats-highlight']}>{stats.least_active_week.count}</span> {t('stats.vacationTime')}
                </p>
            </section>
        </div>
    );
};

export default ConversationStats;