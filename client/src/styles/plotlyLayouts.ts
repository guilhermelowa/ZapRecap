import { Layout } from 'plotly.js';
import { HeatmapData } from '../types/apiTypes';

export const createLayout = (heatmapData: HeatmapData): Partial<Layout> => ({
    title: {
        text: 'Message Activity Heatmap',
    },
    font: {
        color: '#ffffff'
    },
    xaxis: {
        showgrid: false,
        rangemode: 'nonnegative' as const,
        // Find first week with data
        range: [
            Math.min(...heatmapData.z.map(row => 
                row.findIndex(val => val > 0)
            ).filter(i => i !== -1)),
            52
        ],
        tickmode: 'array',
        ticktext: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
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
});