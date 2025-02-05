import React, { useState, useEffect, useRef } from 'react';
import { ConversationStats as Stats, AnalysisResponse, ConversationThemesResponse } from '../types/apiTypes';
import ConversationThemes from './ConversationThemes';
import AuthorSimulator from './AuthorSimulator';
import { useTranslation } from 'react-i18next';

interface PremiumContentProps {
    stats: Stats;
    metrics: AnalysisResponse;
}

const PRICE = 0.99;

const PremiumContent: React.FC<PremiumContentProps> = ({ metrics }) => {
    const [isPaid, setIsPaid] = useState<boolean>(false);
    const [pixQRCode, setPixQRCode] = useState<string>('');
    const [pixCopyCola, setPixCopyCola] = useState<string>('');
    const [paymentId, setPaymentId] = useState<string>('');
    const [themes, setThemes] = useState<{ [theme: string]: string }>();
    const hasInitialized = useRef(false);
    const { t } = useTranslation();

    const initializePayment = async () => {
        try {
            const response = await fetch('http://localhost:8000/create-pix-payment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    amount: PRICE,
                    description: 'WhatsApp Recap Premium Features'
                })
            });

            const data = await response.json();
            setPixQRCode(`data:image/png;base64,${data.qr_code}`);
            setPixCopyCola(data.copy_cola);
            setPaymentId(data.payment_id);
            checkPaymentStatus(String(data.payment_id));
        } catch (error) {
            console.error('Error creating payment:', error);
        }
    };

    const checkPaymentStatus = async (id: string) => {
        const checkStatus = async () => {
            try {
                const response = await fetch(`http://localhost:8000/check-payment-status/${id}`);
                const data = await response.json();
                
                if (data.status === 'approved') {
                    setIsPaid(true);
                    localStorage.setItem('whatsapp_recap_premium', 'true');
                    return true;
                }
                return false;
            } catch (error) {
                console.error('Error checking payment status:', error);
                return false;
            }
        };

        // Check every 5 seconds until payment is confirmed
        const interval = setInterval(async () => {
            const isConfirmed = await checkStatus();
            if (isConfirmed) {
                clearInterval(interval);
            }
        }, 2000);
        return interval;
    };

    useEffect(() => {
        if (!hasInitialized.current) {
            hasInitialized.current = true;
            initializePayment();
        }

        // For testing: Show premium content after 5 seconds
        const timer = setTimeout(() => {
            setIsPaid(true);
            console.log('isPaid value:', isPaid);
        }, 5000);

        return () => {
            if (paymentId) {
                clearInterval(Number(paymentId));
            }
            clearTimeout(timer); // Clean up the timer
        };
    }, []);

    useEffect(() => {
        console.log('isPaid value updated:', isPaid);
    }, [isPaid]);

    useEffect(() => {
        if (isPaid) {
            const fetchThemes = async () => {
                try {
                    const whatsappContent = localStorage.getItem('whatsapp_chat_content');
                    if (!whatsappContent) {
                        console.error('No chat content found in localStorage');
                        return;
                    }
                    console.log('Fetching themes with content length:', whatsappContent.length);

                    const response = await fetch('http://localhost:8000/conversation-themes', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ 
                            content: whatsappContent
                        })
                    });

                    if (!response.ok) {
                        const errorText = await response.text();
                        console.error('Error response:', response.status, errorText);
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const data: ConversationThemesResponse = await response.json();
                    console.log('Received themes:', data.themes);
                    setThemes(data.themes);
                } catch (error) {
                    console.error('Error fetching themes:', error);
                }
            };
            fetchThemes();
        }
    }, [isPaid]);

    if (isPaid) {
        return (
            <div className="premium-content">
                <ConversationThemes themes={themes} />
                <AuthorSimulator metrics={metrics} />
            </div>
        );
    }

    return (
        <div className="premium-content-gate" style={{
            padding: '20px',
            backgroundColor: 'rgba(0, 0, 0, 0.2)',
            borderRadius: '10px',
            margin: '20px 0'
        }}>
            <h2>{t('premium.unlockFeatures')}</h2>
            <p>{t('premium.description')}</p>
            <div className="premium-features" style={{
                marginBottom: '20px'
            }}>
                <p>{t('premium.feature1')}</p>
                <p>{t('premium.feature2')}</p>
            </div>
            
            <div className="payment-section" style={{
                textAlign: 'center',
                marginTop: '20px'
            }}>
                <h3 style={{ marginBottom: '20px' }}>{t('premium.price') + PRICE}</h3>
                
                <div className="pix-options" style={{
                    display: 'flex',
                    justifyContent: 'center',
                    gap: '20px',
                    flexWrap: 'wrap'
                }}>
                    <div className="qr-code-section" style={{
                        width: '200px'
                    }}>
                        <h4 style={{ marginBottom: '10px' }}>{t('premium.scanQRCode')}</h4>
                        {pixQRCode && (
                            <img 
                                src={pixQRCode} 
                                alt="Pix QR Code"
                                style={{
                                    width: '200px',
                                    height: '200px'
                                }}
                            />
                        )}
                    </div>

                    {pixCopyCola && (
                        <div className="copy-cola-section" style={{
                            width: '200px'
                        }}>
                            <h4 style={{ marginBottom: '10px' }}>{t('premium.pixCopyCola')}</h4>
                            <div style={{
                                position: 'relative',
                                height: '200px'
                            }}>
                                <textarea
                                    value={pixCopyCola}
                                    readOnly
                                    style={{
                                        width: '100%',
                                        height: '89%',
                                        padding: '10px',
                                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                                        color: 'white',
                                        border: '1px solid rgba(255, 255, 255, 0.2)',
                                        borderRadius: '5px',
                                        resize: 'none'
                                    }}
                                />
                                <button
                                    onClick={() => navigator.clipboard.writeText(pixCopyCola)}
                                    style={{
                                        position: 'absolute',
                                        right: '10px',
                                        bottom: '10px',
                                        padding: '5px 10px',
                                        backgroundColor: '#25d366',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '3px',
                                        cursor: 'pointer'
                                    }}
                                >
                                    {t('premium.copy')}
                                </button>
                            </div>
                        </div>
                    )}
                </div>
                
                <p style={{ marginTop: '20px' }}>
                    {!paymentId 
                        ? t('premium.generatingPayment')
                        : t('premium.waitingPayment')
                    }
                </p>
            </div>
        </div>
    );
};

export default PremiumContent; 