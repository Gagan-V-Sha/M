import { useState, useEffect } from 'react';
import api from '../communication/axios';

export const useDashboardPresenter = () => {
    const [devices, setDevices] = useState([]);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [newDevice, setNewDevice] = useState({ name: '', sterile: false, implantable: false });

    useEffect(() => {
        let cancelled = false;
        api.get('/device-profiles')
            .then((response) => {
                if (!cancelled) setDevices(response.data);
            })
            .catch((error) => {
                if (!cancelled) console.error("Failed to load devices", error);
            });
        return () => { cancelled = true; };
    }, []);

    const handleCreateDevice = async (e) => {
        e.preventDefault();
        try {
            // send the new device details to the backend
            const response = await api.post('/device-profiles', newDevice);
            setDevices([...devices, response.data]);
            setShowCreateModal(false);
            setNewDevice({ name: '', sterile: false, implantable: false });
        } catch (error) {
            console.error("Failed to create device", error);
            alert("Failed to create device");
        }
    };

    const handleDeleteDevice = async (deviceId) => {
        // ask for confirmation before deleting
        if (!window.confirm("Are you sure you want to delete this device? This action cannot be undone and will delete all associated ETD data.")) {
            return;
        }

        try {
            await api.delete(`/device-profiles/${deviceId}`);
            setDevices(devices.filter(d => d.id !== deviceId));
        } catch (error) {
            console.error("Failed to delete device", error);
            alert("Failed to delete device. " + (error.response?.data?.detail || ""));
        }
    };

    return {
        devices,
        showCreateModal,
        setShowCreateModal,
        newDevice,
        setNewDevice,
        handleCreateDevice,
        handleDeleteDevice
    };
};
