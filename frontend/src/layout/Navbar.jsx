import React from 'react';
import Logo from '../ui/Logo';
import { theme } from '../theme';
import { useNavbarPresenter } from './useNavbarPresenter';

const Navbar = ({ onMenuClick, menuPinned, menuOpen }) => {
    const {
        user,
        navigate,
        handleLogout
    } = useNavbarPresenter();

    return (
        <nav className="topbar">
            {onMenuClick && (
                <button
                    type="button"
                    id="app-nav-toggle"
                    className="app-sidebar-toggle"
                    aria-label={menuPinned ? 'Hide navigation' : 'Show navigation'}
                    aria-expanded={!!menuOpen}
                    title={menuPinned ? 'Hide navigation' : 'Show navigation'}
                    onClick={onMenuClick}
                >
                    ☰
                </button>
            )}
            {/* Left: Logo */}
            <div className="brand" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{ width: '120px' }}>
                    <Logo />
                </div>
            </div>

            {/* Center: Title */}
            <div style={{ flex: 1, textAlign: 'center', fontWeight: '700', fontSize: '15px', color: 'var(--text)' }}>
                Technical Documentation Generator
            </div>

            {/* Right: User / Logout */}
            <div className="topbar-right">
                <span className="small muted" title="Current User" style={{ marginRight: '10px' }}>
                    {user ? (user.name || user.email) : '...'}
                </span>
                <div className="nav-links">
                    <button onClick={() => navigate('/settings')} className="btn-ghost">
                        Settings
                    </button>
                    <button onClick={handleLogout} className="btn-solid" title="Logout">
                        Logout
                    </button>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
