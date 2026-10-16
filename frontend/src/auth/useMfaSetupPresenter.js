import { useState, useEffect } from 'react';
import api from '../communication/axios';

export const useMfaSetupPresenter = () => {
    const [secret, setSecret] = useState('');
    const [qrUri, setQrUri] = useState('');
    const [token, setToken] = useState('');
    const [message, setMessage] = useState({ type: '', text: '' });
    const [isSettingUp, setIsSettingUp] = useState(false);
    const [isEnabled, setIsEnabled] = useState(false);
    const [showDisableForm, setShowDisableForm] = useState(false);

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const response = await api.get('/auth/me');
                setIsEnabled(response.data.mfa_enabled);
            } catch (err) {
                console.error("Failed to fetch MFA status", err);
            }
        };
        fetchStatus();
    }, []);

    const handleSetup = async () => {
        setIsSettingUp(true);
        setMessage({ type: '', text: '' });
        try {
            const response = await api.post('/auth/mfa/setup');
            setSecret(response.data.secret);
            setQrUri(response.data.qr_uri);
        } catch (err) {
            console.error("MFA setup failed:", err);
            setMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to initialize MFA setup.' });
        } finally {
            setIsSettingUp(false);
        }
    };

    const handleEnable = async (e) => {
        e.preventDefault();
        setMessage({ type: '', text: '' });
        try {
            await api.post('/auth/mfa/enable', { token });
            setIsEnabled(true);
            setMessage({ type: 'success', text: 'MFA has been successfully enabled!' });
            setSecret('');
            setQrUri('');
            setToken('');
        } catch (err) {
            console.error("MFA enable failed:", err);
            setMessage({ type: 'error', text: err.response?.data?.detail || 'Invalid code. Please try again.' });
        }
    };

    const handleDisable = async (e) => {
        e.preventDefault();
        setMessage({ type: '', text: '' });
        try {
            await api.post('/auth/mfa/disable', { token });
            setIsEnabled(false);
            setShowDisableForm(false);
            setToken('');
            setMessage({ type: 'success', text: 'MFA has been successfully disabled.' });
        } catch (err) {
            console.error("MFA disable failed:", err);
            setMessage({ type: 'error', text: err.response?.data?.detail || 'Invalid code. Please try again.' });
        }
    };

    return {
        secret,
        qrUri,
        token,
        setToken,
        message,
        isSettingUp,
        isEnabled,
        showDisableForm,
        setShowDisableForm,
        handleSetup,
        handleEnable,
        handleDisable
    };
};
