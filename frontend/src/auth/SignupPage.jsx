import React from 'react';
import { Link } from 'react-router-dom';
import Logo from '../ui/Logo';
import { theme } from '../theme';
import { useSignupPagePresenter } from './useSignupPagePresenter';

const SignupPage = () => {
    const {
        name,
        setName,
        email,
        setEmail,
        password,
        setPassword,
        confirmPassword,
        setConfirmPassword,
        gdprConsent,
        setGdprConsent,
        error,
        loading,
        handleSubmit
    } = useSignupPagePresenter();

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
                <h2>Create Account</h2>
                {error && <div style={{ color: 'red', fontSize: '0.9rem' }}>{error}</div>}
                <input
                    type="text"
                    placeholder="Full Name (Optional)"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    style={{ padding: '10px', backgroundColor: theme.colors.surface, color: theme.colors.text, border: `1px solid ${theme.colors.border}`, borderRadius: '4px' }}
                />
                <input
                    type="email"
                    placeholder="Email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    style={{ padding: '10px', backgroundColor: theme.colors.surface, color: theme.colors.text, border: `1px solid ${theme.colors.border}`, borderRadius: '4px' }}
                />
                <input
                    type="password"
                    placeholder="Password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    style={{ padding: '10px', backgroundColor: theme.colors.surface, color: theme.colors.text, border: `1px solid ${theme.colors.border}`, borderRadius: '4px' }}
                />
                <input
                    type="password"
                    placeholder="Confirm Password"
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    style={{ padding: '10px', backgroundColor: theme.colors.surface, color: theme.colors.text, border: `1px solid ${theme.colors.border}`, borderRadius: '4px' }}
                />
                
                {/* Fix 8.2: GDPR Consent Checkbox */}
                <label style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '0.85rem', color: theme.colors.text }}>
                    <input 
                        type="checkbox" 
                        required
                        checked={gdprConsent}
                        onChange={(e) => setGdprConsent(e.target.checked)}
                        style={{ marginTop: '2px' }}
                    />
                    <span>
                        I agree to the processing of my personal data for the purpose of creating and managing my account in accordance with the Privacy Policy (GDPR Compliance).
                    </span>
                </label>

                <p style={{ fontSize: '0.8rem', color: theme.colors.muted }}>
                    Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character.
                </p>
                <button type="submit" disabled={loading} style={{
                    padding: '12px',
                    backgroundColor: theme.colors.secondary,
                    color: theme.colors.background,
                    border: 'none',
                    borderRadius: '4px',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    fontWeight: 'bold',
                    opacity: loading ? 0.7 : 1
                }}>
                    {loading ? 'Signing Up...' : 'Sign Up'}
                </button>
                <div style={{ textAlign: 'center', marginTop: '1rem', fontSize: '0.9rem' }}>
                    Already have an account? <Link to="/login" style={{ color: theme.colors.secondary, textDecoration: 'none' }}>Log in</Link>
                </div>
            </form>
        </div>
    );
};

export default SignupPage;
