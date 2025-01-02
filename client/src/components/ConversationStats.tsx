import React from 'react';
import { ConversationStats as Stats } from '../types/apiTypes';
import { format } from 'date-fns';

interface ConversationStatsProps {
    stats: Stats;
}

const ConversationStats: React.FC<ConversationStatsProps> = ({ stats }) => {
    const weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const months = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December'];

    return (
        <div className="stats-container" style={{ color: '#ffffff', padding: '20px' }}>
            <section className="conversation-length">
                <h3>📊 Conversation Patterns</h3>
                <p>
                    On average, your conversations last about {stats.average_length} messages! 
                    {stats.average_length > 10 ? " You're quite the chatters! 🗣️" : " Short and sweet! 💝"}
                </p>
                <p>
                    Your longest conversation had {stats.longest_conversation_length} messages! 
                    Starting on {format(new Date(stats.longest_conversation_start), 'PPP')} 
                    and ending on {format(new Date(stats.longest_conversation_end), 'PPP')}. 
                    That was epic! 🚀
                </p>
            </section>

            <section className="active-periods">
                <h3>⏰ Time Patterns</h3>
                <p>
                    {weekdays[stats.most_active_weekday.period]} is your power day with 
                    {stats.most_active_weekday.count} messages last year! 
                    {stats.most_active_weekday.period === 0 ? " Sunday funday! 🎉" : 
                     stats.most_active_weekday.period === 1 ? " Starting the week strong! 💪" :
                     stats.most_active_weekday.period === 2 ? " Taco Tuesday! 🌮" :
                     stats.most_active_weekday.period === 3 ? " Midweek motivation! 🎯" :
                     stats.most_active_weekday.period === 4 ? " Almost there! 🚀" :
                     stats.most_active_weekday.period === 5 ? " TGIF! 🎊" :
                     " Weekend vibes! 🎸"}
                </p>
                <p>
                    {weekdays[stats.least_active_weekday.period]} seems to be your quiet day... 
                    Only {stats.least_active_weekday.count} messages. 
                    {stats.least_active_weekday.period === 1 ? " Monday blues? 😴" : " Taking a break? 🌅"}
                </p>
            </section>

            <section className="monthly-patterns">
                <h3>📅 Monthly Review</h3>
                <p>
                    {months[stats.most_active_month.period - 1]} was your chattiest month with 
                    {stats.most_active_month.count} messages! 
                    {stats.most_active_month.period >= 6 && stats.most_active_month.period <= 8 ? 
                    " Summer vibes! ☀️" : " 💫"}
                </p>
                <p>
                    {months[stats.least_active_month.period - 1]} was pretty quiet with only 
                    {stats.least_active_month.count} messages. 
                    {stats.least_active_month.period === 12 ? " Holiday break? 🎄" : " 🌙"}
                </p>
            </section>

            <section className="weekly-insights">
                <h3>🗓️ Weekly Rhythms</h3>
                <p>
                    Week {stats.most_active_week.period + 1} was intense with 
                    {stats.most_active_week.count} messages! What happened there? 🤔
                </p>
                <p>
                    Week {stats.least_active_week.period + 1} was your quietest with just 
                    {stats.least_active_week.count} messages. Vacation time? ✈️
                </p>
            </section>
        </div>
    );
};

export default ConversationStats;