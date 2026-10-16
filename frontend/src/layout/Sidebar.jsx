import React from 'react';
import { theme } from '../theme';
import { useSidebarPresenter } from './useSidebarPresenter';

const Sidebar = () => {
    const {
        chapters,
        navigate,
        activeDeviceId,
        shouldShowChapters,
        isDashboard,
        isDatabaseViewer,
        isScanReview,
        showScanReview,
        isEtd,
        activeChapter
    } = useSidebarPresenter();

    const navItemStyle = (active) => ({
        padding: '12px 20px',
        backgroundColor: active ? 'var(--card)' : 'transparent',
        borderLeft: active ? '4px solid var(--accent)' : '4px solid transparent',
        cursor: 'pointer',
        color: active ? 'var(--text)' : 'var(--muted)',
        fontSize: '14px'
    });

    return (
        <div className="app-sidebar" style={{
            width: '100%',
            minWidth: 0,
            backgroundColor: 'var(--card2)',
            borderRight: '1px solid var(--border)',
            display: 'flex',
            flexDirection: 'column',
            padding: '20px 0',
            height: '100%', // Take full height of parent
            boxSizing: 'border-box',
            overflowY: 'auto', // Allow scrolling
            backdropFilter: 'blur(16px)',
            WebkitBackdropFilter: 'blur(16px)'
        }}>
            <div style={{
                padding: '0 20px 10px 20px',
                fontSize: '11px',
                fontWeight: '600',
                color: 'var(--muted)',
                textTransform: 'uppercase',
                letterSpacing: '1.4px'
            }}>
                Navigation
            </div>

            <div style={{ display: 'flex', flexDirection: 'column' }}>
                <div
                    style={navItemStyle(isDashboard)}
                    onClick={() => navigate('/dashboard')}
                >
                    Dashboard
                </div>

                <div
                    style={navItemStyle(isDatabaseViewer)}
                    onClick={() => navigate('/database-viewer')}
                >
                    Database Viewer
                </div>

                {showScanReview && (
                    <div
                        style={navItemStyle(isScanReview)}
                        onClick={() => navigate('/scan-review')}
                    >
                        Scan review
                    </div>
                )}

                {/* Dynamic Chapters - Only show if a device has been selected and we aren't at the dashboard */}
                {shouldShowChapters && (
                    <>
                        <div style={{ marginTop: '20px', padding: '0 20px 10px 20px', fontSize: '11px', color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '1.4px', borderTop: '1px solid var(--border)', paddingTop: '15px' }}>
                            Annex 1
                        </div>
                        {chapters.map((chapter, index) => {
                            const chapterTitles = {
                                "Chapter I": "General requirements",
                                "Chapter II": "Requirements regarding design and manufacture",
                                "Chapter III": "Information supplied with the device"
                            };
                            const title = chapterTitles[chapter] || "";

                            const isActiveChapter = isEtd && (activeChapter === chapter || (!activeChapter && index === 0));

                            return (
                                <div key={index} style={{
                                    padding: '10px 20px',
                                    cursor: 'pointer',
                                    color: isActiveChapter ? 'var(--text)' : 'var(--muted)',
                                    backgroundColor: isActiveChapter ? 'var(--card)' : 'transparent',
                                    borderLeft: isActiveChapter ? '4px solid var(--accent)' : '4px solid transparent',
                                    display: 'flex',
                                    flexDirection: 'column'
                                }}
                                    onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--text)'; e.currentTarget.style.backgroundColor = 'var(--card)'; }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.color = isActiveChapter ? 'var(--text)' : 'var(--muted)';
                                        e.currentTarget.style.backgroundColor = isActiveChapter ? 'var(--card)' : 'transparent';
                                    }}
                                    onClick={() => navigate(`/devices/${activeDeviceId}/etd?chapter=${chapter}`)}
                                >
                                    <span style={{ fontWeight: '600', fontSize: '13px' }}>{chapter}</span>
                                    {title && <span style={{ fontSize: '11px', opacity: 0.6, marginTop: '2px' }}>{title}</span>}
                                </div>
                            );
                        })}
                    </>
                )}
            </div>
        </div>
    );
};

export default Sidebar;
