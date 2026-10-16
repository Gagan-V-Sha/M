import { useEffect, useState } from 'react';
import api from '../communication/axios';

export const useScanReviewPresenter = () => {
    const [jobs, setJobs] = useState([]);
    const [selectedId, setSelectedId] = useState(null);
    const [detail, setDetail] = useState(null);
    const [loadingList, setLoadingList] = useState(true);
    const [loadingDetail, setLoadingDetail] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        let cancelled = false;

        const loadJobs = async () => {
            try {
                const response = await api.get('/imports/scan-review');
                if (cancelled) return;
                setJobs(response.data || []);
                setError(null);
            } catch (err) {
                if (!cancelled) {
                    setError(err.response?.data?.detail || 'Could not load scan jobs.');
                }
            } finally {
                if (!cancelled) setLoadingList(false);
            }
        };

        loadJobs();
        const timer = setInterval(loadJobs, 4000);
        return () => {
            cancelled = true;
            clearInterval(timer);
        };
    }, []);

    useEffect(() => {
        if (!selectedId) {
            setDetail(null);
            return undefined;
        }

        let cancelled = false;
        const loadDetail = async () => {
            setLoadingDetail(true);
            try {
                const response = await api.get(`/imports/scan-review/${selectedId}`);
                if (cancelled) return;
                setDetail(response.data);
                setError(null);
            } catch (err) {
                if (!cancelled) {
                    setError(err.response?.data?.detail || 'Could not load scan result.');
                }
            } finally {
                if (!cancelled) setLoadingDetail(false);
            }
        };

        loadDetail();
        const selected = jobs.find((job) => job.standard_id === selectedId);
        const busy = selected && ['pending', 'processing'].includes((selected.parse_status || '').toLowerCase());
        const timer = busy ? setInterval(loadDetail, 3000) : null;
        return () => {
            cancelled = true;
            if (timer) clearInterval(timer);
        };
    }, [selectedId, jobs]);

    return {
        jobs,
        selectedId,
        setSelectedId,
        detail,
        loadingList,
        loadingDetail,
        error,
    };
};
