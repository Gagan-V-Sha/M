import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../communication/axios';

export const useForgotPasswordPagePresenter = () => {
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState({ type: '', text: '' });
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage({ type: '', text: '' });
        setLoading(true);

        try {
            await api.post('/auth/password-reset-request', { email });
            setMessage({
                type: 'success',
                text: 'If that email is registered, a password reset token has been generated. Please check your admin console (or email) for the token.'
            });
        } catch (err) {
            console.error("Password reset request failed:", err);
            // Always show success to prevent email enumeration, but log the error internally
            setMessage({
                type: 'success',
                text: 'If that email is registered, a password reset token has been sent.'
            });
        } finally {
            setLoading(false);
        }
    };

    return {
        email,
        setEmail,
        message,
        loading,
        navigate,
        handleSubmit
    };
};
