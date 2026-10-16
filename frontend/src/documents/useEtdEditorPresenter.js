import { useState, useEffect, useRef } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import api from '../communication/axios';

export const useEtdEditorPresenter = () => {
    const { id } = useParams();
    const location = useLocation();
    const navigate = useNavigate();
    const queryParams = new URLSearchParams(location.search);
    const selectedChapter = queryParams.get('chapter');

    const [rows, setRows] = useState([]);
    const [loading, setLoading] = useState(true);
    const [standardsOptions, setStandardsOptions] = useState([]);
    const [evidenceOptions, setEvidenceOptions] = useState([]);

    // Filters
    const [filterText, setFilterText] = useState('');
    const [hideNotApplicable, setHideNotApplicable] = useState(false);
    const [allChapters, setAllChapters] = useState([]);
    const [device, setDevice] = useState(null);

    // Auto-save state
    const [isSaving, setIsSaving] = useState(false);
    const [lastSaved, setLastSaved] = useState(null);
    const [saveError, setSaveError] = useState(null);
    
    // Fix 2.6: Prevent double-clicks on export
    const [isExporting, setIsExporting] = useState(false);

    // Batch save state
    const pendingChangesRef = useRef({ device_meta: {}, row_updates: {} });
    const saveTimeoutRef = useRef(null);

    const queueSave = () => {
        if (saveTimeoutRef.current) {
            clearTimeout(saveTimeoutRef.current);
        }
        saveTimeoutRef.current = setTimeout(flushChanges, 1000);
    };

    const flushChanges = async () => {
        const changesToSave = pendingChangesRef.current;
        if (Object.keys(changesToSave.device_meta).length === 0 && Object.keys(changesToSave.row_updates).length === 0) {
            return;
        }

        const payload = {
            device_id: parseInt(id),
            device_meta: Object.keys(changesToSave.device_meta).length > 0 ? changesToSave.device_meta : null,
            row_updates: Object.values(changesToSave.row_updates)
        };

        // Clear buffer so user can keep typing, but hold onto changesToSave in case of failure
        pendingChangesRef.current = { device_meta: {}, row_updates: {} };

        setIsSaving(true);
        setSaveError(null);
        try {
            await api.post('/etd/batch-update', payload);
            setLastSaved(new Date());
        } catch (err) {
            console.error("Batch update failed", err);
            // Fix 1.3: Restore changes if they failed, merging with anything typed during the request
            const current = pendingChangesRef.current;
            pendingChangesRef.current = {
                device_meta: { ...changesToSave.device_meta, ...current.device_meta },
                row_updates: { ...changesToSave.row_updates, ...current.row_updates }
            };
            setSaveError("Auto-save failed - retrying...");
            queueSave(); // Retry automatically
        } finally {
            setIsSaving(false);
        }
    };

    useEffect(() => {
        const fetchData = async () => {
            try {
                // fetch all the data needed for the editor in one go
                const [rowsResp, stdResp, evidResp, chaptersResp, deviceResp] = await Promise.all([
                    api.get(`/etd?device_id=${id}`),
                    api.get('/standards'),
                    api.get('/evidence'),
                    api.get('/gspr/chapters'),
                    api.get(`/device-profiles/${id}`) // Fix 3.1: Direct fetch
                ]);

                setRows(rowsResp.data);
                setAllChapters(chaptersResp.data);
                setDevice(deviceResp.data);

                // Format options for react-select
                setStandardsOptions(stdResp.data.map(s => ({
                    value: s.id,
                    label: s.code + (s.title ? ` - ${s.title}` : '')
                })));

                setEvidenceOptions(evidResp.data.map(e => ({
                    value: e.id,
                    label: e.tdd_number + ' ' + (e.title || '')
                })));

            } catch (err) {
                console.error("Failed to load ETD data", err);
                alert("Error loading data. Please check console.");
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [id]);

    // Update Handlers
    const updateRow = (rowId, field, value) => {
        setRows(prev => prev.map(r => r.id === rowId ? { ...r, [field]: value } : r));
        if (!pendingChangesRef.current.row_updates[rowId]) {
            pendingChangesRef.current.row_updates[rowId] = { id: rowId };
        }
        pendingChangesRef.current.row_updates[rowId][field] = value;
        queueSave();
    };

    const updateRowStandards = (rowId, selectedOptions) => {
        const standardIds = selectedOptions.map(o => o.value);
        setRows(prev => prev.map(r => r.id === rowId ? {
            ...r,
            standards: selectedOptions.map(o => ({ id: o.value, code: o.label.split(' - ')[0] }))
        } : r));
        if (!pendingChangesRef.current.row_updates[rowId]) {
            pendingChangesRef.current.row_updates[rowId] = { id: rowId };
        }
        pendingChangesRef.current.row_updates[rowId].standard_ids = standardIds;
        queueSave();
    };

    const updateRowEvidence = (rowId, selectedOptions) => {
        const evidenceIds = selectedOptions.map(o => o.value);
        setRows(prev => prev.map(r => r.id === rowId ? {
            ...r,
            evidence_documents: selectedOptions.map(o => ({ id: o.value, tdd_number: o.label.split(' ')[0] }))
        } : r));
        if (!pendingChangesRef.current.row_updates[rowId]) {
            pendingChangesRef.current.row_updates[rowId] = { id: rowId };
        }
        pendingChangesRef.current.row_updates[rowId].evidence_ids = evidenceIds;
        queueSave();
    };

    const updateDeviceMeta = (field, value) => {
        if (!device) return;
        setDevice({ ...device, [field]: value });
        pendingChangesRef.current.device_meta[field] = value;
        queueSave();
    };

    const handleExportPdf = async () => {
        if (isExporting) return; // Fix 2.6: Prevent double click
        setIsExporting(true);
        try {
            // trigger the pdf generation on the backend
            const response = await api.post(`/etd/export/pdf?device_id=${id}`, {}, { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `etd_device_${id}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error("PDF Export failed", err);
            let message = "PDF Export failed.";
            const detail = err.response?.data?.detail;
            if (typeof detail === "string") {
                message = detail;
            } else if (err.response?.data instanceof Blob) {
                try {
                    const text = await err.response.data.text();
                    const parsed = JSON.parse(text);
                    if (parsed.detail) message = parsed.detail;
                } catch {
                    // keep default message
                }
            }
            alert(message);
        } finally {
            setIsExporting(false); // Fix 2.6
        }
    };

    // Filter Logic
    const filteredRows = rows.filter(row => {
        if (hideNotApplicable && row.applicability === 'not_applicable') return false;

        // New Chapter Filter
        if (selectedChapter && row.gspr_requirement?.chapter !== selectedChapter) {
            return false;
        }

        if (filterText) {
            const text = (row.gspr_requirement?.text || '').toLowerCase();
            const ref = (row.gspr_requirement?.full_reference || '').toLowerCase();
            const notes = (row.notes || '').toLowerCase();
            const search = filterText.toLowerCase();
            return text.includes(search) || ref.includes(search) || notes.includes(search);
        }
        return true;
    });

    return {
        id,
        navigate,
        selectedChapter,
        loading,
        device,
        isSaving,
        lastSaved,
        saveError,
        allChapters,
        filterText,
        setFilterText,
        hideNotApplicable,
        setHideNotApplicable,
        filteredRows,
        standardsOptions,
        evidenceOptions,
        updateRow,
        updateRowStandards,
        updateRowEvidence,
        updateDeviceMeta,
        handleExportPdf,
        isExporting // Fix 2.6: expose to UI
    };
};
