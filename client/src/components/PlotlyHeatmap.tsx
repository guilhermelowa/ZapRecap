import React from 'react';
import Plotly from 'plotly.js-dist';
import createPlotlyComponent from 'react-plotly.js/factory';
import { HeatmapData } from '../types/apiTypes';
import { createLayout } from '../styles/plotlyLayouts';
import { useTranslation } from 'react-i18next';

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
    const { t } = useTranslation();

    const data: PlotlyHeatmapData[] = [{
        ...heatmapData,
        type: 'heatmap',
        colorscale: [
            [0, 'rgba(37, 211, 102, 0)'],       // transparent whatsapp green
            [0.1, 'rgba(37, 211, 102, 0.1)'],   // light whatsapp green
            [0.3, 'rgba(37, 211, 102, 0.3)'],   // medium whatsapp green
            [0.5, 'rgba(37, 211, 102, 0.5)'],   // medium-dark whatsapp green
            [0.7, 'rgba(37, 211, 102, 0.7)'],   // dark whatsapp green
            [1, 'rgba(37, 211, 102, 1)']        // solid whatsapp green
        ],
        showscale: true,
        customdata: heatmapData.dates,
        hovertemplate: 'Date: %{customdata}<br>Messages: %{z}<extra></extra>'
    }];

    return (
        <div style={{
            position: 'relative',
            width: '100%',
            maxWidth: '90vw',
            display: 'flex',
            justifyContent: 'center',
            overflow: 'hidden',
            margin: '0 auto',
            padding: 0,
            boxSizing: 'border-box'
        }}>
            <Plot
                data={data}
                layout={{
                    ...createLayout(heatmapData, t),
                    title: t('messageActivityHeatmap'),
                    width: typeof window !== 'undefined' ? Math.min(window.innerWidth * 0.9, 1200) : 1024,
                    height: 500,
                    margin: { t: 30, l: 50, r: 50, b: 60 }
                }}
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