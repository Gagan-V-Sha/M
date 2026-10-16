import React from 'react';
import { Link } from 'react-router-dom';
import Logo from '../ui/Logo';
import { theme } from '../theme';
import { useForgotPasswordPagePresenter } from './useForgotPasswordPagePresenter';

const ForgotPasswordPage = () => {
    const {
        email,
        setEmail,
        message,
        loading,
        navigate,
        handleSubmit
    } = useForgotPasswordPagePresenter();

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
                <h2>Forgot Password</h2>
                <p style={{ fontSize: '0.9rem', color: theme.colors.muted }}>
                    Enter your email address and we'll send you a token to reset your password.
                </p>

                {message.text && (
                    <div style={{
                        padding: '10px',
                        borderRadius: '4px',
                        backgroundColor: message.type === 'error' ? 'rgba(255,0,0,0.1)' : 'rgba(0,255,0,0.1)',
                        color: message.type === 'error' ? '#ff6b6b' : '#51cf66',
                        border: `1px solid ${message.type === 'error' ? '#ff6b6b' : '#51cf66'}`,
                        fontSize: '0.9rem'
                    }}>
                        {message.text}
                    </div>
                )}

                <input
                    type="email"
                    placeholder="Email Address"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
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
                    {loading ? 'Sending...' : 'Request Reset Token'}
                </button>

                {message.type === 'success' && (
                    <button
                        type="button"
                        onClick={() => navigate('/reset-password')}
                        style={{
                            padding: '10px',
                            backgroundColor: 'transparent',
                            color: theme.colors.primary,
                            border: `1px solid ${theme.colors.primary}`,
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontWeight: 'bold',
                            marginTop: '0.5rem'
                        }}
                    >
                        I have a token, proceed to reset
                    </button>
                )}

                <div style={{ textAlign: 'center', marginTop: '1rem', fontSize: '0.9rem' }}>
                    Remember your password? <Link to="/login" style={{ color: theme.colors.secondary, textDecoration: 'none' }}>Log in</Link>
                </div>
            </form>
        </div>
    );
};

export default ForgotPasswordPage;
