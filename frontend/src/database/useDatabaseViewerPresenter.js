import { useState, useEffect, useRef, useCallback } from 'react';
import api from '../communication/axios';
import { useRuntimeConfig } from '../communication/useRuntimeConfig';

export const useDatabaseViewerPresenter = () => {
    const { mineruReady } = useRuntimeConfig();
    const [activeTab, setActiveTab] = useState('gspr');
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [filterText, setFilterText] = useState('');
    const [editingItem, setEditingItem] = useState(null);
    const [isAdmin, setIsAdmin] = useState(false);
    const [uploadingStandardId, setUploadingStandardId] = useState(null);
    const [scanningStandardIds, setScanningStandardIds] = useState([]);
    const [alertMessage, setAlertMessage] = useState('');
    const [alertType, setAlertType] = useState('info'); // 'info', 'success', 'error'
    const fileInputRef = useRef(null);

    const showAlert = useCallback((msg, type = 'info') => {
        setAlertMessage(msg);
        setAlertType(type);
    }, []);

    const clearAlert = useCallback(() => {
        setAlertMessage('');
    }, []);

    const checkAdminStatus = useCallback(async () => {
        try {
            const response = await api.get('/auth/me');
            if (response.data.role === 'admin' || response.data.role === 'editor') {
                setIsAdmin(true);
            }
        } catch (error) {
            console.error("Error fetching user info:", error);
        }
    }, []);

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            let endpoint = '';
            switch (activeTab) {
                case 'gspr': endpoint = '/gspr'; break;
                case 'standards': endpoint = '/standards'; break;
                case 'evidence': endpoint = '/evidence'; break;
                default: endpoint = '/gspr';
            }

            const response = await api.get(endpoint);
            setData(response.data);
        } catch (error) {
            console.error("Error fetching database data:", error);
        } finally {
            setLoading(false);
        }
    }, [activeTab]);

    useEffect(() => {
        fetchData();
        const isAuthenticated = localStorage.getItem('is_authenticated') === 'true';
        if (isAuthenticated) {
            checkAdminStatus();
        }
    }, [activeTab, fetchData, checkAdminStatus]);

    const handleUploadClick = (standardId) => {
        setUploadingStandardId(standardId);
        if (fileInputRef.current) {
            fileInputRef.current.click();
        }
    };

    // Fix 3.2: Poll the specific parse-status endpoint instead of downloading all standards
    const pollScanStatus = useCallback(async (standardId) => {
        const POLL_INTERVAL_MS = 5000;
        const MAX_ATTEMPTS = 240; // ~20 minutes

        for (let attempt = 0; attempt < MAX_ATTEMPTS; attempt++) {
            await new Promise(resolve => setTimeout(resolve, POLL_INTERVAL_MS));
            try {
                const response = await api.get(`/standards/${standardId}/parse-status`);
                const { parse_status, parse_error } = response.data;
                
                if (parse_status === 'completed' || parse_status === 'parsed') {
                    setScanningStandardIds(prev => prev.filter(id => id !== standardId));
                    fetchData();
                    showAlert(`Scan finished: GSPR mappings were extracted successfully.`, 'success');
                    return;
                }
                if (parse_status === 'failed') {
                    setScanningStandardIds(prev => prev.filter(id => id !== standardId));
                    fetchData();
                    showAlert(`Scan failed: ${parse_error || 'Unknown error'}`, 'error');
                    return;
                }
            } catch (error) {
                console.error("Error polling scan status:", error);
            }
        }
        setScanningStandardIds(prev => prev.filter(id => id !== standardId));
        showAlert(`Scan polling timed out.`, 'error');
    }, [fetchData, showAlert]);

    const handleFileChange = async (e) => {
        const file = e.target.files[0];
        if (!file || !uploadingStandardId) return;

        // Fix 3.5: Client-side file size check (50 MB limit)
        if (file.size > 50 * 1024 * 1024) {
            showAlert("File exceeds the 50 MB upload limit.", 'error');
            e.target.value = null;
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            setLoading(true);

            const isStandard = activeTab === 'standards';
            const endpoint = isStandard
                ? `/standards/${uploadingStandardId}/upload-mapping`
                : `/evidence/${uploadingStandardId}/upload-pdf`;

            await api.post(endpoint, formData, {
                headers: {
                    'Content-Type': undefined
                },
            });

            if (isStandard) {
                // MinerU runs in the background — show processing state and poll
                const standardId = uploadingStandardId;
                setScanningStandardIds(prev => [...prev, standardId]);
                showAlert("PDF uploaded. MinerU scan is running in the background — the status column will update when it finishes.", 'info');
                pollScanStatus(standardId);
            } else {
                showAlert("PDF uploaded successfully!", 'success');
            }
            fetchData(); // Refresh data to show processing status
        } catch (error) {
            console.error("Upload failed:", error);
            showAlert(`Upload failed: ${error.response?.data?.detail || error.message}`, 'error');
        } finally {
            setLoading(false);
            setUploadingStandardId(null);
            e.target.value = null; // Reset input
        }
    };

    const handleEditClick = (item) => {
        setEditingItem(item);
    };

    const handleCreateClick = () => {
        setEditingItem({}); // Empty object for new item
    };

    const handleDeleteClick = async (item) => {
        if (!window.confirm(`Are you sure you want to delete this item? This action cannot be undone.`)) {
            return;
        }

        try {
            let endpoint = '';
            switch (activeTab) {
                case 'gspr': endpoint = `/gspr/${item.id}`; break;
                case 'standards': endpoint = `/standards/${item.id}`; break;
                case 'evidence': endpoint = `/evidence/${item.id}`; break;
            }

            await api.delete(endpoint);
            fetchData(); // Refresh data
            showAlert("Item deleted successfully.", "success");
        } catch (error) {
            showAlert("Failed to delete item.", "error");
            console.error("Error deleting:", error);
        }
    };

    const handleSave = async (itemData) => {
        try {
            let endpoint = '';
            let method = 'put';

            // Determine endpoint and method
            if (itemData.id) {
                // Update existing
                switch (activeTab) {
                    case 'gspr': endpoint = `/gspr/${itemData.id}`; break;
                    case 'standards': endpoint = `/standards/${itemData.id}`; break;
                    case 'evidence': endpoint = `/evidence/${itemData.id}`; break;
                }
            } else {
                // Create new
                method = 'post';
                switch (activeTab) {
                    case 'gspr': endpoint = '/gspr'; break;
                    case 'standards': endpoint = '/standards'; break;
                    case 'evidence': endpoint = '/evidence'; break;
                }
            }

            if (method === 'put') {
                await api.put(endpoint, itemData);
            } else {
                await api.post(endpoint, itemData);
            }

            setEditingItem(null);
            fetchData();
            showAlert("Changes saved successfully.", "success");
            return true;
        } catch (error) {
            const detail = error.response?.data?.detail;
            const detailText = typeof detail === "string"
                ? detail
                : Array.isArray(detail)
                    ? detail.map((item) => item.msg || item).join(" ")
                    : (error.message || "Unknown error");
            const message = `Failed to save changes. ${detailText}`;
            console.error("Error saving:", error);
            return message;
        }
    };

    const filteredData = data.filter(item => {
        if (!filterText) return true;
        const search = filterText.toLowerCase();
        return Object.values(item).some(val =>
            item && val && String(val).toLowerCase().includes(search)
        );
    });

    return {
        activeTab,
        setActiveTab,
        loading,
        filterText,
        setFilterText,
        editingItem,
        setEditingItem,
        isAdmin,
        fileInputRef,
        scanningStandardIds,
        handleUploadClick,
        handleFileChange,
        handleEditClick,
        handleCreateClick,
        handleDeleteClick,
        handleSave,
        filteredData,
        alertMessage,
        alertType,
        clearAlert,
        mineruReady,
    };
};
