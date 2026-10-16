import React from 'react';
import { theme } from '../theme';
import { usePasswordChangeFormPresenter } from './usePasswordChangeFormPresenter';

const PasswordChangeForm = () => {
    const {
        oldPassword,
        setOldPassword,
        newPassword,
        setNewPassword,
        confirmPassword,
        setConfirmPassword,
        message,
        loading,
        handleSubmit
    } = usePasswordChangeFormPresenter();

    return (
        <div style={{
            padding: '2rem',
            border: `1px solid ${theme.colors.border}`,
            borderRadius: '8px',
            backgroundColor: theme.colors.surface,
            width: '100%',
            maxWidth: '500px'
        }}>
            <h2 style={{ marginTop: 0, marginBottom: '1.5rem' }}>Change Password</h2>

            {message.text && (
                <div style={{
                    padding: '10px',
                    marginBottom: '1rem',
                    borderRadius: '4px',
                    backgroundColor: message.type === 'error' ? 'rgba(255,0,0,0.1)' : 'rgba(0,255,0,0.1)',
                    color: message.type === 'error' ? '#ff6b6b' : '#51cf66',
                    border: `1px solid ${message.type === 'error' ? '#ff6b6b' : '#51cf66'}`
                }}>
                    {message.text}
                </div>
            )}

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: theme.colors.muted }}>Current Password</label>
                    <input
                        type="password"
                        required
                        value={oldPassword}
                        onChange={(e) => setOldPassword(e.target.value)}
                        style={{ width: '100%', padding: '10px', backgroundColor: theme.colors.background, color: theme.colors.text, border: `1px solid ${theme.colors.border}`, borderRadius: '4px', boxSizing: 'border-box' }}
                    />
                </div>
                <div>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: theme.colors.muted }}>New Password</label>
                    <input
                        type="password"
                        required
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        style={{ width: '100%', padding: '10px', backgroundColor: theme.colors.background, color: theme.colors.text, border: `1px solid ${theme.colors.border}`, borderRadius: '4px', boxSizing: 'border-box' }}
                    />
                    <div style={{ fontSize: '0.75rem', color: theme.colors.muted, marginTop: '4px' }}>
                        Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special character.
                    </div>
                </div>
                <div>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: theme.colors.muted }}>Confirm New Password</label>
                    <input
                        type="password"
                        required
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        style={{ width: '100%', padding: '10px', backgroundColor: theme.colors.background, color: theme.colors.text, border: `1px solid ${theme.colors.border}`, borderRadius: '4px', boxSizing: 'border-box' }}
                    />
                </div>
                <button type="submit" disabled={loading} style={{
                    marginTop: '1rem',
                    padding: '10px',
                    backgroundColor: theme.colors.primary,
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    fontWeight: 'bold',
                    opacity: loading ? 0.7 : 1
                }}>
                    {loading ? 'Changing Password...' : 'Update Password'}
                </button>
            </form>
        </div>
    );
};

export default PasswordChangeForm;
