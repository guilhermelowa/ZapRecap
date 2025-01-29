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
            tickvals: [1, 5, 9, 13, 18, 22, 26, 31, 35, 39, 44, 48]
        },
        yaxis: {
            showgrid: false,
            scaleanchor: 'x',  
            scaleratio: 1,
            autorange: 'reversed'
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: {
            l: 50,
            r: 50,
            b: 50,
            t: 50,
            pad: 4
        }
    };
};