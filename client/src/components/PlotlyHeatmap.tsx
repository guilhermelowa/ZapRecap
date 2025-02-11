import React, { useEffect, useRef } from 'react';
import createPlotlyComponent from '../fixPlotlyComponent';
import Plotly from 'plotly.js';
import { HeatmapData } from '../types/apiTypes';
import { createLayout } from '../styles/plotlyLayouts';
import { useTranslation } from 'react-i18next';
import ReportButton from './ReportButton';

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
    const plotRef = useRef<any>(null);

    // Cleanup function to prevent memory leaks
    useEffect(() => {
        return () => {
            if (plotRef.current) {
                Plotly.purge(plotRef.current);
            }
        };
    }, []);

    // Calculate the aspect ratio based on the data dimensions
    // 7 rows (days) and ~52 columns (weeks)
    const aspectRatio = 7 / 52;
    // Use a larger portion of the viewport width (95% instead of 90%)
    const width = typeof window !== 'undefined' ? Math.min(window.innerWidth * 0.95, 1300) : 1024;
    // Calculate height to maintain square cells
    const height = width * aspectRatio;


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
        <div>
            <h3 style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                color: '#ffffff'
            }}>
                {t('messageActivityHeatmap')}
                <ReportButton 
                    sectionId="heatmap-container"
                    sectionName="Message Activity Heatmap"
                    contextData={heatmapData}
                />
            </h3>
            <div id="heatmap-container" style={{
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
                    ref={plotRef}
                    data={data}
                    layout={{
                        ...createLayout(heatmapData, t),
                        width: width,
                        height: height + 100, // Add some padding for labels
                        margin: { t: 30, l: 50, r: 50, b: 60 }
                    }}
                    style={{
                        width: '100%',
                        height: `${height + 100}px`,
                        margin: 0,
                        padding: 0
                    }}
                    config={{
                        responsive: true,
                        displayModeBar: false
                    }}
                />
            </div>
        </div>
    );
};

export default PlotlyHeatmap;