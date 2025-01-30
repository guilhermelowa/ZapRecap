import React, { useState, useRef, useEffect } from 'react';
import * as Sentry from "@sentry/react";
import html2canvas from 'html2canvas';
import { useTranslation } from 'react-i18next';

const styles = `
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;

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

    useEffect(() => {
        // Add styles to document head
        const styleSheet = document.createElement("style");
        styleSheet.innerText = styles;
        document.head.appendChild(styleSheet);

        return () => {
            document.head.removeChild(styleSheet);
        };
    }, []);

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
            const sectionElement = document.getElementById(sectionId);
            if (!sectionElement) return;

            // Capture screenshot
            const canvas = await html2canvas(sectionElement);
            const screenshot = canvas.toDataURL();

            // Collect console errors (last 10)
            const consoleErrors = (window as any)._consoleErrors || [];
            
            // Create report
            Sentry.withScope((scope) => {
                scope.setExtra('section', sectionName);
                scope.setExtra('contextData', contextData);
                scope.setExtra('userAgent', navigator.userAgent);
                scope.setExtra('consoleErrors', consoleErrors);
                scope.setExtra('screenshot', screenshot);
                
                Sentry.captureMessage(`User reported issue in ${sectionName}`, 'warning');
            });

            alert(t('stats.reportSuccess'));
        } catch (error) {
            console.error('Error capturing report:', error);
            alert(t('stats.reportError'));
        }
    };

    return (
        <div style={{ position: 'relative', display: 'inline-flex' }}>
            <button
                ref={buttonRef}
                onClick={captureAndReport}
                style={{
                    marginLeft: '8px',
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: '24px',
                    height: '24px',
                    borderRadius: '50%',
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    transition: 'all 0.2s ease',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    padding: 0
                }}
                onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'scale(1.1)';
                    e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
                    updateTooltipPosition();
                    setShowTooltip(true);
                }}
                onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'scale(1)';
                    e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
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
                    style={{ color: 'rgba(255, 255, 255, 0.8)' }}
                >
                    <path d="M12 1a11 11 0 0 0-11 11c0 6.075 4.925 11 11 11s11-4.925 11-11c0-6.075-4.925-11-11-11z" />
                    <path d="M12 6a3 3 0 0 0-3 3m6 6a3 3 0 0 1-3 3" />
                    <path d="M7 10c0-2.8 2.2-5 5-5s5 2.2 5 5-2.2 5-5 5-5-2.2-5-5z" />
                    <path d="M15 9l-2 2m0 0l-2 2m2-2l2 2m-2-2l-2-2" />
                </svg>
            </button>
            {showTooltip && (
                <div 
                    style={{
                        position: 'fixed',
                        left: `${tooltipPosition.x}px`,
                        top: `${tooltipPosition.y}px`,
                        transform: 'translateX(-50%)',
                        backgroundColor: 'rgba(30, 30, 30, 0.95)',
                        border: '1px solid rgba(255, 255, 255, 0.2)',
                        borderRadius: '8px',
                        padding: '8px 12px',
                        fontSize: '12px',
                        color: 'rgba(255, 255, 255, 0.9)',
                        whiteSpace: 'nowrap',
                        zIndex: 1000,
                        pointerEvents: 'none',
                        backdropFilter: 'blur(5px)',
                        animation: 'fadeIn 0.2s ease-in-out'
                    }}
                >
                    {t('reportIssue')}
                </div>
            )}
        </div>
    );
};

export default ReportButton; 