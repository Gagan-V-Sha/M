import { theme } from '../theme';
import { Link, useNavigate } from 'react-router-dom';
import { useDashboardPresenter } from './useDashboardPresenter';
import { motion } from 'framer-motion';

const Dashboard = () => {
    const navigate = useNavigate();
    const {
        devices,
        showCreateModal,
        setShowCreateModal,
        newDevice,
        setNewDevice,
        handleCreateDevice,
        handleDeleteDevice
    } = useDashboardPresenter();

    return (
        <motion.div 
            className="dash page" 
            style={{ padding: '20px 0' }}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ type: "spring", stiffness: 260, damping: 20 }}
        >
            <div className="section-head">
                <h1 style={{ fontSize: '30px', margin: 0 }}>Dashboard</h1>
                <button
                    onClick={() => setShowCreateModal(true)}
                    className="btn-solid"
                    style={{ fontWeight: '600' }}
                >
                    + Create New Device
                </button>
            </div>

            <div className="card" style={{ marginTop: '20px' }}>
                <div className="section-head" style={{ marginBottom: '20px' }}>
                    <h3 style={{ margin: 0 }}>Available Devices</h3>
                </div>
                {devices.length === 0 ? (
                    <div className="chart-empty">No devices found. Create one to get started.</div>
                ) : (
                    <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                        {devices.map((device, index) => (
                            <motion.li 
                                key={device.id} 
                                style={{ padding: '15px 0', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ type: "spring", stiffness: 300, damping: 24, delay: index * 0.05 }}
                            >
                                <div>
                                    <Link to={`/devices/${device.id}/etd`} style={{ textDecoration: 'none', color: 'var(--text)', fontSize: '16px', fontWeight: '600' }}>
                                        {device.name}
                                    </Link>
                                    <div style={{ fontSize: '13px', color: 'var(--muted)', marginTop: '5px' }}>
                                        Attributes: {device.sterile ? 'Sterile, ' : ''}{device.implantable ? 'Implantable, ' : ''}{device.software ? 'Software' : ''}
                                    </div>
                                </div>
                                <div style={{ display: 'flex', gap: '10px' }}>
                                    <button
                                        onClick={() => navigate(`/devices/${device.id}/etd`)}
                                        className="btn-ghost"
                                        style={{ border: '1px solid var(--accent)', color: 'var(--accent)' }}
                                    >
                                        Open
                                    </button>
                                    <button
                                        onClick={() => handleDeleteDevice(device.id)}
                                        className="btn-ghost"
                                        style={{ border: '1px solid var(--red)', color: 'var(--red)' }}
                                    >
                                        Delete
                                    </button>
                                </div>
                            </motion.li>
                        ))}
                    </ul>
                )}
            </div>

            {/* Simple Modal */}
            {showCreateModal && (
                <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    style={{
                        position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                        backgroundColor: 'rgba(0,0,0,0.6)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000,
                        backdropFilter: 'blur(5px)'
                    }}
                >
                    <motion.div 
                        className="card" 
                        style={{ width: '400px', boxShadow: '0 8px 40px rgba(0,0,0,0.6)' }}
                        initial={{ scale: 0.8, opacity: 0, y: 20 }}
                        animate={{ scale: 1, opacity: 1, y: 0 }}
                        transition={{ type: "spring", stiffness: 400, damping: 25 }}
                    >
                        <h3 style={{ marginTop: 0, marginBottom: '20px' }}>Create New Device</h3>
                        <form onSubmit={handleCreateDevice} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                            <input
                                type="text"
                                placeholder="Device Name"
                                value={newDevice.name}
                                onChange={e => setNewDevice({ ...newDevice, name: e.target.value })}
                                required
                                style={{ padding: '12px 14px', border: '1px solid var(--border)', borderRadius: '10px', backgroundColor: 'var(--card2)', color: 'var(--text)', fontSize: '14px', outline: 'none' }}
                            />
                            <div style={{ display: 'flex', gap: '15px' }}>
                                <label style={{ color: 'var(--muted)', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                    <input
                                        type="checkbox"
                                        checked={newDevice.sterile}
                                        onChange={e => setNewDevice({ ...newDevice, sterile: e.target.checked })}
                                    /> Sterile
                                </label>
                                <label style={{ color: 'var(--muted)', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                    <input
                                        type="checkbox"
                                        checked={newDevice.implantable}
                                        onChange={e => setNewDevice({ ...newDevice, implantable: e.target.checked })}
                                    /> Implantable
                                </label>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '15px' }}>
                                <button type="button" onClick={() => setShowCreateModal(false)} className="btn-ghost">Cancel</button>
                                <button type="submit" className="btn-solid">Create</button>
                            </div>
                        </form>
                    </motion.div>
                </motion.div>
            )}
        </motion.div>
    );
};

export default Dashboard;
