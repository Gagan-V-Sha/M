import { useState } from 'react';
import api from '../communication/axios';

export const usePasswordChangeFormPresenter = () => {
    const [oldPassword, setOldPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [message, setMessage] = useState({ type: '', text: '' });
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage({ type: '', text: '' });

        if (newPassword !== confirmPassword) {
            setMessage({ type: 'error', text: 'New passwords do not match.' });
            return;
        }

        setLoading(true);
        try {
            await api.post('/auth/password-change', {
                old_password: oldPassword,
                new_password: newPassword
            });
            setMessage({ type: 'success', text: 'Password changed successfully!' });
            setOldPassword('');
            setNewPassword('');
            setConfirmPassword('');
        } catch (err) {
            console.error("Password change failed:", err);
            const errorMsg = err.response?.data?.detail || "Failed to change password. Please check your current password and ensure the new password meets policy requirements.";
            setMessage({ type: 'error', text: errorMsg });
        } finally {
            setLoading(false);
        }
    };

    return {
        oldPassword,
        setOldPassword,
        newPassword,
        setNewPassword,
        confirmPassword,
        setConfirmPassword,
        message,
        loading,
        handleSubmit
    };
};
