import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import api from '../communication/axios';
import { useRuntimeConfig } from '../communication/useRuntimeConfig';

export const useSidebarPresenter = () => {
    const [chapters, setChapters] = useState([]);
    const navigate = useNavigate();
    const location = useLocation();
    const { mineruReady } = useRuntimeConfig();

    // Check if we are on Dashboard
    const isDashboard = location.pathname.includes('/dashboard');
    const isDatabaseViewer = location.pathname.includes('/database-viewer');
    const isScanReview = location.pathname.includes('/scan-review');
    const isEtd = /\/devices\/\d+\/etd/.test(location.pathname);
    const activeChapter = new URLSearchParams(location.search).get('chapter');

    // Check if we are in a device-specific route using location
    const deviceIdMatch = location.pathname.match(/\/devices\/(\d+)/);
    const urlDeviceId = deviceIdMatch ? deviceIdMatch[1] : null;

    useEffect(() => {
        if (urlDeviceId) {
            sessionStorage.setItem('activeDeviceId', urlDeviceId);
        } else if (isDashboard) {
            sessionStorage.removeItem('activeDeviceId');
        }
    }, [urlDeviceId, isDashboard]);

    const activeDeviceId = sessionStorage.getItem('activeDeviceId') || urlDeviceId;
    const shouldShowChapters = activeDeviceId && !isDashboard;

    useEffect(() => {
        const fetchChapters = async () => {
            try {
                const response = await api.get('/gspr/chapters');
                setChapters(response.data);
            } catch (error) {
                console.error("Failed to fetch chapters", error);
            }
        };
        fetchChapters();
    }, []);

    return {
        chapters,
        navigate,
        activeDeviceId,
        shouldShowChapters,
        isDashboard,
        isDatabaseViewer,
        isScanReview,
        showScanReview: mineruReady,
        isEtd,
        activeChapter
    };
};
