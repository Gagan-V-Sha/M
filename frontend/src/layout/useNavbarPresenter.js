import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../communication/axios';

export const useNavbarPresenter = () => {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);

    useEffect(() => {
        const fetchUser = async () => {
            try {
                const response = await api.get('/auth/me');
                setUser(response.data);
            } catch (err) {
                console.error("Failed to fetch user data", err);
            }
        };
        const isAuthenticated = localStorage.getItem('is_authenticated') === 'true';
        if (isAuthenticated) {
            fetchUser();
        }
    }, []);

    const handleLogout = async () => {
        try {
            await api.post('/auth/logout');
        } catch (error) {
            console.error("Logout failed", error);
        } finally {
            localStorage.removeItem('is_authenticated');
            navigate('/login');
        }
    };

    return {
        user,
        navigate,
        handleLogout
    };
};
