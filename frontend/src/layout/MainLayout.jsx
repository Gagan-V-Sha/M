import React, { useEffect, useState } from 'react';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import { theme } from '../theme';

const MainLayout = ({ children }) => {
    const [open, setOpen] = useState(() => localStorage.getItem('sidebarPinned') === 'true');

    useEffect(() => {
        localStorage.setItem('sidebarPinned', open ? 'true' : 'false');
    }, [open]);

    return (
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            height: '100vh',
            color: theme.colors.text
        }}>
            <div style={{ flexShrink: 0 }}>
                <Navbar
                    menuPinned={open}
                    menuOpen={open}
                    onMenuClick={() => setOpen((value) => !value)}
                />
            </div>

            <div style={{ display: 'flex', flex: 1, overflow: 'hidden', position: 'relative' }}>
                <div className={`app-sidebar-slot${open ? ' is-pinned' : ''}`}>
                    <div className="app-sidebar-flyout">
                        <Sidebar />
                    </div>
                </div>

                <div className="app-main-content" style={{
                    flex: 1,
                    minWidth: 0,
                    overflowX: 'auto',
                    overflowY: 'auto',
                    padding: '20px'
                }}>
                    {children}
                </div>
            </div>
        </div>
    );
};

export default MainLayout;
