import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../communication/axios';

export const useSignupPagePresenter = () => {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [gdprConsent, setGdprConsent] = useState(false); // Fix 8.2
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        if (!gdprConsent) {
            setError('You must agree to the Terms of Service and Privacy Policy to register.');
            return;
        }

        setLoading(true);
        try {
            // Register the user
            await api.post('/auth/register', {
                email,
                password,
                name: name || undefined,
                role: 'editor', // Default role
                is_active: true,
                gdpr_consent_accepted: gdprConsent // Fix 8.2
            });

            // Auto login after successful registration
            await api.post('/auth/login', { email, password });
            localStorage.setItem('is_authenticated', 'true'); // Fix 8.1
            navigate('/dashboard');
        } catch (err) {
            console.error("Registration failed:", err);
            if (err.response) {
                const message = err.response.data?.detail || "Registration failed. Please try again.";
                setError(message);
            } else if (err.request) {
                setError('Registration failed: Cannot connect to server');
            } else {
                setError('Registration failed: An unexpected error occurred');
            }
        } finally {
            setLoading(false);
        }
    };

    return {
        name,
        setName,
        email,
        setEmail,
        password,
        setPassword,
        confirmPassword,
        setConfirmPassword,
        gdprConsent,
        setGdprConsent,
        error,
        loading,
        handleSubmit
    };
};
