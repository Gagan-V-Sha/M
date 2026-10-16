import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../communication/axios';

export const useResetPasswordPagePresenter = () => {
    const [token, setToken] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (newPassword !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        setLoading(true);
        try {
            await api.post('/auth/password-reset-confirm', {
                token: token,
                new_password: newPassword
            });
            setSuccess(true);
            setTimeout(() => {
                navigate('/login');
            }, 3000); // Redirect after 3 seconds
        } catch (err) {
            console.error("Password reset failed:", err);
            if (err.response) {
                setError(err.response.data?.detail || "Invalid or expired token, or password does not meet requirements.");
            } else {
                setError("An unexpected error occurred.");
            }
        } finally {
            setLoading(false);
        }
    };

    return {
        token,
        setToken,
        newPassword,
        setNewPassword,
        confirmPassword,
        setConfirmPassword,
        error,
        success,
        loading,
        handleSubmit
    };
};
