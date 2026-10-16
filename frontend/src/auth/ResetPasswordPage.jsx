import React from 'react';
import { Link } from 'react-router-dom';
import Logo from '../ui/Logo';
import { theme } from '../theme';
import { useResetPasswordPagePresenter } from './useResetPasswordPagePresenter';

const ResetPasswordPage = () => {
    const {
        token,
        setToken,
        newPassword,
        setNewPassword,
        confirmPassword,
        setConfirmPassword,
        error,
        success,
        loading,
        handleSubmit
    } = useResetPasswordPagePresenter();

    return (
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100vh',
            backgroundColor: theme.colors.background,
            color: theme.colors.text
        }}>
            <div style={{ marginBottom: '2rem' }}>
                <Logo />
            </div>

            <form onSubmit={handleSubmit} style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '1rem',
                padding: '2rem',
                border: `1px solid ${theme.colors.secondary}`,
                borderRadius: '8px',
                width: '320px'
            }}>
                <h2>Reset Password</h2>

                {success ? (
                    <div style={{
                        padding: '15px',
                        borderRadius: '4px',
                        backgroundColor: 'rgba(0,255,0,0.1)',
                        color: '#51cf66',
                        border: '1px solid #51cf66',
                        textAlign: 'center'
                    }}>
                        <p style={{ margin: '0 0 10px 0', fontWeight: 'bold' }}>Password reset successful!</p>
                        <p style={{ margin: 0, fontSize: '0.9rem' }}>Redirecting to login...</p>
                    </div>
                ) : (
                    <>
                        {error && <div style={{ color: '#ff6b6b', fontSize: '0.9rem', padding: '10px', backgroundColor: 'rgba(255,0,0,0.1)', border: '1px solid #ff6b6b44', borderRadius: '4px' }}>{error}</div>}

                        <input
                            type="text"
                            placeholder="Reset Token"
                            required
                            value={token}
                            onChange={(e) => setToken(e.target.value)}
                            style={{ padding: '10px', backgroundColor: theme.colors.surface, color: theme.colors.text, border: `1px solid ${theme.colors.border}`, borderRadius: '4px' }}
                        />

                        <input
                            type="password"
                            placeholder="New Password"
                            required
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                            style={{ padding: '10px', backgroundColor: theme.colors.surface, color: theme.colors.text, border: `1px solid ${theme.colors.border}`, borderRadius: '4px' }}
                        />
                        <div style={{ fontSize: '0.75rem', color: theme.colors.muted, marginTop: '-5px' }}>
                            Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special character.
                        </div>

                        <input
                            type="password"
                            placeholder="Confirm New Password"
                            required
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            style={{ padding: '10px', backgroundColor: theme.colors.surface, color: theme.colors.text, border: `1px solid ${theme.colors.border}`, borderRadius: '4px' }}
                        />

                        <button type="submit" disabled={loading} style={{
                            padding: '12px',
                            backgroundColor: theme.colors.secondary,
                            color: theme.colors.background,
                            border: 'none',
                            borderRadius: '4px',
                            cursor: loading ? 'not-allowed' : 'pointer',
                            fontWeight: 'bold',
                            opacity: loading ? 0.7 : 1,
                            marginTop: '0.5rem'
                        }}>
                            {loading ? 'Resetting...' : 'Set New Password'}
                        </button>
                    </>
                )}

                <div style={{ textAlign: 'center', marginTop: '1rem', fontSize: '0.9rem' }}>
                    <Link to="/login" style={{ color: theme.colors.secondary, textDecoration: 'none' }}>Back to Login</Link>
                </div>
            </form>
        </div>
    );
};

export default ResetPasswordPage;
