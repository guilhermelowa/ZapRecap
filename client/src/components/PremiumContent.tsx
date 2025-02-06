import React, { useState, useEffect, useRef } from 'react';
import { ConversationStats as Stats, AnalysisResponse } from '../types/apiTypes';
import ConversationThemes from './ConversationThemes';
import AuthorSimulator from './AuthorSimulator';
import { useTranslation } from 'react-i18next';
import styles from '../styles/components/PremiumContent.module.css';

interface PremiumContentProps {
    stats: Stats;
    metrics: AnalysisResponse;
}

const PRICE = 0.99;

const AVAILABLE_MODELS = [
    { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
    { value: 'gpt-4', label: 'GPT-4' },
    { value: 'gpt-4o', label: 'GPT-4o' },
    { value: 'gpt-4o-mini', label: 'GPT-4o-mini' },
    { value: 'o1', label: 'o1' },
    { value: 'o3-mini', label: 'o3-mini' },
];


const PremiumContent: React.FC<PremiumContentProps> = ({ metrics }) => {
    const [isPaid, setIsPaid] = useState<boolean>(false);
    const [pixQRCode, setPixQRCode] = useState<string>('');
    const [pixCopyCola, setPixCopyCola] = useState<string>('');
    const [paymentId, setPaymentId] = useState<string>('');
    const [themes, setThemes] = useState<{ [theme: string]: string }>();
    const hasInitialized = useRef(false);
    const { t } = useTranslation();
    const [selectedModel, setSelectedModel] = useState<string>(AVAILABLE_MODELS[0].value);

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

    if (isPaid) {
        return (
            <div className={styles['premium-content']}>
                <h2>{t('premium.sectionTitle')}</h2>
                <div className={styles['model-selector']}>
                    <label htmlFor="model-select" className={styles['model-label']}>
                        {t('premium.selectModel')}:
                    </label>
                    <select
                        id="model-select"
                        value={selectedModel}
                        onChange={(e) => setSelectedModel(e.target.value)}
                        className={styles['model-select']}
                    >
                        {AVAILABLE_MODELS.map(model => (
                            <option key={model.value} value={model.value}>
                                {model.label}
                            </option>
                        ))}
                    </select>
                </div>
                <ConversationThemes 
                    themes={themes} 
                    conversationId={metrics.conversation_id}
                    selectedModel={selectedModel}
                    onThemesGenerated={setThemes}
                />
                <AuthorSimulator 
                    metrics={metrics} 
                    selectedModel={selectedModel}
                />
            </div>
        );
    }

    return (
        <div className={styles['premium-content-gate']}>
            <h2>{t('premium.unlockFeatures')}</h2>
            <p>{t('premium.description')}</p>
            <div className={styles['premium-features']}>
                <p>{t('premium.feature1')}</p>
                <p>{t('premium.feature2')}</p>
            </div>
            
            <div className={styles['payment-section']}>
                <h3>{t('premium.price') + PRICE}</h3>
                
                <div className={styles['pix-options']}>
                    <div className={styles['qr-code-section']}>
                        <h4>{t('premium.scanQRCode')}</h4>
                        {pixQRCode && (
                            <img 
                                src={pixQRCode} 
                                alt="Pix QR Code"
                                className={styles['qr-code']}
                            />
                        )}
                    </div>

                    {pixCopyCola && (
                        <div className={styles['copy-cola-section']}>
                            <h4>{t('premium.pixCopyCola')}</h4>
                            <div className={styles['copy-cola-container']}>
                                <textarea
                                    value={pixCopyCola}
                                    readOnly
                                    className={styles['copy-cola-input']}
                                />
                                <button
                                    onClick={() => navigator.clipboard.writeText(pixCopyCola)}
                                    className={styles['copy-button']}
                                >
                                    {t('premium.copy')}
                                </button>
                            </div>
                        </div>
                    )}
                </div>
                
                <p className={styles['payment-status']}>
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