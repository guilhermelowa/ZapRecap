import React from 'react';
import { ConversationStats as Stats } from '../types/apiTypes';
import { format } from 'date-fns';
import { useTranslation } from 'react-i18next';

interface ConversationStatsProps {
    stats: Stats;
}

const ConversationStats: React.FC<ConversationStatsProps> = ({ stats }) => {
    const { t } = useTranslation();
    const weekdays = t('weekdays', { returnObjects: true }) as string[];
    const months = t('months', { returnObjects: true }) as string[];

    return (
        <div className="stats-container" style={{ color: '#ffffff', padding: '20px' }}>
            <section className="conversation-length">
                <h3>{t('stats.conversationPatterns')}</h3>
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

            <section className="active-periods">
                <h3>{t('stats.timePatterns')}</h3>
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

            <section className="monthly-patterns">
                <h3>{t('stats.monthlyReview')}</h3>
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

            <section className="weekly-insights">
                <h3>{t('stats.weeklyRhythms')}</h3>
                <p>
                    {t('stats.intenseWeek')} <b>{stats.most_active_week.period + 1}</b> {t('stats.wasIntense')}
                    {' '}<b>{stats.most_active_week.count}</b> {t('stats.whatHappened')}
                </p>
                <p>
                    {t('stats.intenseWeek')} <b>{stats.least_active_week.period + 1}</b> {t('stats.quietestWeek')}
                    {' '}<b>{stats.least_active_week.count}</b> {t('stats.vacationTime')}
                </p>
            </section>

            <section className="theme-patterns">
                <h3>{t('stats.themesFromBusiestDay')}</h3>
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