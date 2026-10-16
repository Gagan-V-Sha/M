import React from 'react';
import { Link } from 'react-router-dom';
import Logo from '../ui/Logo';
import { theme } from '../theme';
import { useLoginPagePresenter } from './useLoginPagePresenter';

const LoginPage = () => {
    const {
        email,
        setEmail,
        password,
        setPassword,
        mfaToken,
        setMfaToken,
        mfaRequired,
        error,
        handleSubmit
    } = useLoginPagePresenter();

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
                width: '300px'
            }}>
                <h2>Login</h2>
                {error && <div style={{ color: '#ff6b6b', fontSize: '0.9rem', padding: '10px', backgroundColor: 'rgba(255,0,0,0.1)', border: '1px solid #ff6b6b44', borderRadius: '4px' }}>{error}</div>}

                {!mfaRequired ? (
                    <>
                        <input
                            type="email"
                            placeholder="Email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            style={{ padding: '10px', backgroundColor: theme.colors.surface, color: theme.colors.text, border: `1px solid ${theme.colors.border}`, borderRadius: '4px' }}
                            required
                        />
                        <input
                            type="password"
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            style={{ padding: '10px', backgroundColor: theme.colors.surface, color: theme.colors.text, border: `1px solid ${theme.colors.border}`, borderRadius: '4px' }}
                            required
                        />
                    </>
                ) : (
                    <>
                        <p style={{ fontSize: '0.9rem', color: theme.colors.muted }}>
                            Please open your Authenticator app and enter the 6-digit code for <strong>{email}</strong>.
                        </p>
                        <input
                            type="text"
                            placeholder="000000"
                            maxLength="6"
                            value={mfaToken}
                            onChange={(e) => setMfaToken(e.target.value.replace(/\D/g, ''))}
                            style={{
                                padding: '10px',
                                backgroundColor: theme.colors.background,
                                color: theme.colors.text,
                                border: `1px solid ${theme.colors.border}`,
                                borderRadius: '4px',
                                fontSize: '1.2rem',
                                letterSpacing: '4px',
                                textAlign: 'center'
                            }}
                            required
                        />
                    </>
                )}

                <button type="submit" style={{
                    padding: '10px',
                    backgroundColor: theme.colors.secondary,
                    color: theme.colors.background,
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontWeight: 'bold'
                }}>
                    Sign In
                </button>
                <div style={{ textAlign: 'center', marginTop: '0.5rem', fontSize: '0.9rem' }}>
                    <Link to="/forgot-password" style={{ color: theme.colors.muted, textDecoration: 'none' }}>Forgot Password?</Link>
                </div>
                <div style={{ textAlign: 'center', marginTop: '0.5rem', fontSize: '0.9rem' }}>
                    Don't have an account? <Link to="/signup" style={{ color: theme.colors.secondary, textDecoration: 'none' }}>Sign up</Link>
                </div>
            </form>
        </div>
    );
};

export default LoginPage;
