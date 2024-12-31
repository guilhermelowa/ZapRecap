import React from 'react';
import Plotly from 'plotly.js-dist';
import createPlotlyComponent from 'react-plotly.js/factory';
import { HeatmapData } from '../types/apiTypes';
import { Layout } from 'plotly.js';

const Plot = createPlotlyComponent(Plotly);

interface PlotlyHeatmapData {
    z: number[][];
    type: 'heatmap';
    x: string[];
    y: string[];
    colorscale: Array<[number, string]>;
    showscale: boolean;
    zmin: number;    
    zmax: number;
    hovertemplate: string;
    customdata: string[][]; // Dates for hover template
}

interface PlotlyHeatmapProps {
    heatmapData: HeatmapData;
}

const PlotlyHeatmap: React.FC<PlotlyHeatmapProps> = ({ heatmapData }) => {
    console.log('Heatmap Data:', heatmapData); // Debug data

    const data: PlotlyHeatmapData[] = [{
        ...heatmapData,
        type: 'heatmap',
        colorscale: [
            [0, 'rgba(37, 211, 102, 0)'],       // transparent whatsapp green
            [0.1, 'rgba(37, 211, 102, 0.2)'],   // light whatsapp green
            [0.3, 'rgba(37, 211, 102, 0.4)'],   // medium whatsapp green
            [0.5, 'rgba(37, 211, 102, 0.6)'],   // medium-dark whatsapp green
            [0.7, 'rgba(37, 211, 102, 0.8)'],   // dark whatsapp green
            [1, 'rgba(37, 211, 102, 1)']        // solid whatsapp green
        ],
        showscale: true,
        customdata: heatmapData.dates,
        hovertemplate: 'Date: %{customdata}<br>Messages: %{z}<extra></extra>'
    }];

    const layout: Partial<Layout> = {
        title: {
            text: 'Message Activity Heatmap',
            font: { color: '#ffffff' }
        },
        xaxis: {
            showgrid: false,
            tickfont: { color: '#ffffff' },
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
            tickfont: { color: '#ffffff' },
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

    return (
        <div style={{
            position: 'relative',
            left: '-490px',  
            width: '350%',
            display: 'flex',
            justifyContent: 'center',
            overflow: 'hidden',
            margin: 0,
            padding: 0,
            boxSizing: 'border-box'
        }}>
            <Plot
                data={data}
                layout={layout}
                style={{
                    width: '100%',
                    height: '500px',
                    margin: 0,
                    padding: 0
                }}
                config={{
                    responsive: true,
                    displayModeBar: false
                }}
            />
        </div>
    );
};

export default PlotlyHeatmap;