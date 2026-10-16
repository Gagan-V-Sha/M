import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../communication/axios';

export const useLoginPagePresenter = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [mfaToken, setMfaToken] = useState('');
    const [mfaRequired, setMfaRequired] = useState(false);
    const location = useMemo(() => new URLSearchParams(window.location.search), []);
    const [error, setError] = useState(() =>
        location.get('timeout') ? 'Your session has timed out due to inactivity.' : ''
    );
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            const payload = { email, password };
            if (mfaRequired) {
                payload.mfa_token = mfaToken;
            }
            const response = await api.post('/auth/login', payload);
            // Fix 8.1: Token is now HTTP-only cookie. Just set UI auth flag.
            localStorage.setItem('is_authenticated', 'true');
            navigate('/dashboard');
        } catch (err) {
            console.error("Login failed:", err);
            if (err.response) {
                if (err.response.data?.detail === "mfa_required") {
                    setMfaRequired(true);
                } else {
                    const message = err.response.data?.detail || "Incorrect email or password.";
                    setError(message);
                }
            } else if (err.request) {
                setError('Login failed: Cannot connect to server');
            } else {
                setError('Login failed: An unexpected error occurred');
            }
        }
    };

    return {
        email,
        setEmail,
        password,
        setPassword,
        mfaToken,
        setMfaToken,
        mfaRequired,
        error,
        handleSubmit
    };
};
