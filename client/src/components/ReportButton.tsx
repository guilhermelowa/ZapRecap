import React, { useState, useRef, useEffect } from 'react';
import * as Sentry from "@sentry/react";
import html2canvas from 'html2canvas';
import { useTranslation } from 'react-i18next';
import styles from '../styles/components/ReportButton.module.css';

interface ReportButtonProps {
    sectionId: string;
    sectionName: string;
    contextData?: any;
}

const ReportButton: React.FC<ReportButtonProps> = ({ sectionId, sectionName, contextData }) => {
    const { t } = useTranslation();
    const [showTooltip, setShowTooltip] = useState(false);
    const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
    const buttonRef = useRef<HTMLButtonElement>(null);

    const updateTooltipPosition = () => {
        if (buttonRef.current) {
            const rect = buttonRef.current.getBoundingClientRect();
            setTooltipPosition({
                x: rect.left + (rect.width / 2),
                y: rect.top + rect.height + 8
            });
        }
    };

    const captureAndReport = async () => {
        try {
            const section = document.getElementById(sectionId);
            if (!section) return;

            const canvas = await html2canvas(section);
            const screenshot = canvas.toDataURL();

            Sentry.captureMessage(`User reported issue in ${sectionName}`, {
                level: 'info',
                extra: {
                    screenshot,
                    contextData,
                }
            });

            alert(t('reportSubmitted'));
        } catch (error) {
            console.error('Error capturing screenshot:', error);
        }
    };

    return (
        <div>
            <button
                ref={buttonRef}
                className={styles['report-button']}
                onClick={captureAndReport}
                onMouseEnter={(e) => {
                    updateTooltipPosition();
                    setShowTooltip(true);
                }}
                onMouseLeave={() => {
                    setShowTooltip(false);
                }}
            >
                <svg 
                    width="14" 
                    height="14" 
                    viewBox="0 0 24 24" 
                    fill="none" 
                    stroke="currentColor" 
                    strokeWidth="2"
                    strokeLinecap="round" 
                    strokeLinejoin="round"
                >
                    <path d="M12 1a11 11 0 0 0-11 11c0 6.075 4.925 11 11 11s11-4.925 11-11c0-6.075-4.925-11-11-11z" />
                    <path d="M12 6a3 3 0 0 0-3 3m6 6a3 3 0 0 1-3 3" />
                    <path d="M7 10c0-2.8 2.2-5 5-5s5 2.2 5 5-2.2 5-5 5-5-2.2-5-5z" />
                    <path d="M15 9l-2 2m0 0l-2 2m2-2l2 2m-2-2l-2-2" />
                </svg>
            </button>
            {showTooltip && (
                <div 
                    className={styles['tooltip']}
                    style={{
                        left: `${tooltipPosition.x}px`,
                        top: `${tooltipPosition.y}px`,
                    }}
                >
                    {t('reportIssue')}
                </div>
            )}
        </div>
    );
};

export default ReportButton; 