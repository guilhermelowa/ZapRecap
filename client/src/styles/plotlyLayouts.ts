import { Layout } from 'plotly.js';
import { HeatmapData } from '../types/apiTypes';
import { TFunction } from 'i18next';

export const createLayout = (heatmapData: HeatmapData, t: TFunction): Partial<Layout> => {
    return {
        font: {
            color: '#ffffff'
        },
        xaxis: {
            showgrid: false,
            rangemode: 'nonnegative' as const,
            range: [
                Math.min(...heatmapData.z.map(row => 
                    row.findIndex(val => val > 0)
                ).filter(i => i !== -1)),
                52
            ],
            tickmode: 'array',
            ticktext: [
                t('months.1'), t('months.2'), t('months.3'),
                t('months.4'), t('months.5'), t('months.6'),
                t('months.7'), t('months.8'), t('months.9'),
                t('months.10'), t('months.11'), t('months.12')
            ],
            tickvals: [1, 5, 9, 13, 18, 22, 26, 31, 35, 39, 44, 48],
            constrain: 'domain'
        },
        yaxis: {
            showgrid: false,
            autorange: 'reversed',
            type: 'category',
            tickmode: 'array',
            tickvals: [0, 1, 2, 3, 4, 5, 6],
            ticktext: [
                t('weekdays-short.0'), t('weekdays-short.1'),
                t('weekdays-short.2'), t('weekdays-short.3'),
                t('weekdays-short.4'), t('weekdays-short.5'), t('weekdays-short.6')
            ],
            range: [-0.5, 6.5],
            fixedrange: true,
            constrain: 'domain'
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: {
            l: 50,
            r: 50,
            b: 50,
            t: 50,
            pad: 4
        },
    };
};