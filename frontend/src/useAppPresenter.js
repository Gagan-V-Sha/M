import { useEffect } from 'react';
import api from './communication/axios';

export const useAppPresenter = () => {
    // Advanced Security: Inactivity Timeout (20 Minutes)
    useEffect(() => {
        let timeoutId;
        const TIMEOUT_MS = 20 * 60 * 1000; // 20 minutes

        const resetTimer = () => {
            if (timeoutId) clearTimeout(timeoutId);
            timeoutId = setTimeout(handleLogout, TIMEOUT_MS);
        };

        const handleLogout = () => {
            if (localStorage.getItem('is_authenticated') === 'true') {
                console.log("Session timed out due to inactivity.");
                localStorage.removeItem('is_authenticated');
                api.post('/auth/logout').catch(() => {});
                window.location.href = '/login?timeout=1';
            }
        };

        // Listen for common user interactions
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
        events.forEach(event => document.addEventListener(event, resetTimer));

        // Initial set
        resetTimer();

        return () => {
            if (timeoutId) clearTimeout(timeoutId);
            events.forEach(event => document.removeEventListener(event, resetTimer));
        };
    }, []);

    return {};
};
