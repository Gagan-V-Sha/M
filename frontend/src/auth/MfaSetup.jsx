import React from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { theme } from '../theme';
import { useMfaSetupPresenter } from './useMfaSetupPresenter';

const MfaSetup = () => {
    const {
        secret,
        qrUri,
        token,
        setToken,
        message,
        isSettingUp,
        isEnabled,
        showDisableForm,
        setShowDisableForm,
        handleSetup,
        handleEnable,
        handleDisable
    } = useMfaSetupPresenter();

    if (isEnabled) {
        return (
            <div style={{
                marginTop: '2rem',
                padding: '1.5rem',
                border: `1px solid #51cf66`,
                borderRadius: '8px',
                backgroundColor: 'rgba(0,255,0,0.05)'
            }}>
                <h3 style={{ margin: '0 0 10px 0', color: '#51cf66' }}>Multi-Factor Authentication</h3>

                {message.text && (
                    <div style={{
                        padding: '10px',
                        borderRadius: '4px',
                        backgroundColor: 'rgba(0,255,0,0.1)',
                        color: '#51cf66',
                        border: `1px solid #51cf66`,
                        fontSize: '0.9rem',
                        marginBottom: '1rem'
                    }}>
                        {message.text}
                    </div>
                )}

                <p style={{ margin: '0 0 1.5rem 0', fontSize: '0.9rem' }}>
                    Your account is currently protected with MFA.
                </p>

                {!showDisableForm ? (
                    <button
                        onClick={() => setShowDisableForm(true)}
                        style={{
                            padding: '8px 12px',
                            backgroundColor: 'transparent',
                            border: `1px solid #ff6b6b`,
                            color: '#ff6b6b',
                            cursor: 'pointer',
                            borderRadius: '4px',
                            fontSize: '0.8rem'
                        }}
                    >
                        Disable MFA
                    </button>
                ) : (
                    <form onSubmit={handleDisable} style={{ borderTop: `1px solid #51cf6644`, paddingTop: '1rem' }}>
                        <p style={{ fontSize: '0.85rem', marginBottom: '10px', color: '#ff6b6b' }}>
                            To disable MFA, please enter a code from your Authenticator app:
                        </p>
                        <div style={{ display: 'flex', gap: '10px' }}>
                            <input
                                type="text"
                                placeholder="000000"
                                maxLength="6"
                                required
                                value={token}
                                onChange={(e) => setToken(e.target.value.replace(/\D/g, ''))}
                                style={{
                                    padding: '8px',
                                    backgroundColor: theme.colors.background,
                                    color: theme.colors.text,
                                    border: `1px solid ${theme.colors.border}`,
                                    borderRadius: '4px',
                                    width: '100px',
                                    textAlign: 'center'
                                }}
                            />
                            <button type="submit" style={{
                                padding: '8px 12px',
                                backgroundColor: '#ff6b6b',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer'
                            }}>
                                Confirm Disable
                            </button>
                            <button
                                type="button"
                                onClick={() => setShowDisableForm(false)}
                                style={{
                                    padding: '8px 12px',
                                    backgroundColor: 'transparent',
                                    border: 'none',
                                    color: theme.colors.muted,
                                    cursor: 'pointer'
                                }}
                            >
                                Cancel
                            </button>
                        </div>
                    </form>
                )}
            </div>
        );
    }

    return (
        <div style={{
            marginTop: '2rem',
            padding: '1.5rem',
            border: `1px solid ${theme.colors.secondary}`,
            borderRadius: '8px',
            backgroundColor: theme.colors.surface
        }}>
            <h3 style={{ margin: '0 0 1rem 0' }}>Multi-Factor Authentication</h3>

            {message.text && (
                <div style={{
                    padding: '10px',
                    borderRadius: '4px',
                    backgroundColor: message.type === 'error' ? 'rgba(255,0,0,0.1)' : 'rgba(0,255,0,0.1)',
                    color: message.type === 'error' ? '#ff6b6b' : '#51cf66',
                    border: `1px solid ${message.type === 'error' ? '#ff6b6b' : '#51cf66'}`,
                    fontSize: '0.9rem',
                    marginBottom: '1rem'
                }}>
                    {message.text}
                </div>
            )}

            {!qrUri ? (
                <div>
                    <p style={{ fontSize: '0.9rem', color: theme.colors.muted, marginBottom: '1rem' }}>
                        Protect your account with an extra layer of security. We support Microsoft Authenticator, Google Authenticator, and other TOTP apps.
                    </p>
                    <button
                        onClick={handleSetup}
                        disabled={isSettingUp}
                        style={{
                            padding: '10px 15px',
                            backgroundColor: theme.colors.secondary,
                            color: theme.colors.background,
                            border: 'none',
                            borderRadius: '4px',
                            cursor: isSettingUp ? 'not-allowed' : 'pointer',
                            fontWeight: 'bold'
                        }}
                    >
                        {isSettingUp ? 'Generating...' : 'Setup MFA'}
                    </button>
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    <div>
                        <p style={{ fontSize: '0.9rem', marginBottom: '10px' }}>
                            <strong>Step 1:</strong> Scan this QR code with Microsoft Authenticator.
                        </p>
                        <div style={{ backgroundColor: 'white', padding: '15px', display: 'inline-block', borderRadius: '8px' }}>
                            <QRCodeSVG value={qrUri} size={150} />
                        </div>
                        <p style={{ fontSize: '0.8rem', color: theme.colors.muted, marginTop: '10px' }}>
                            Or enter this code manually: <strong style={{ letterSpacing: '2px', color: theme.colors.text }}>{secret}</strong>
                        </p>
                    </div>

                    <form onSubmit={handleEnable}>
                        <p style={{ fontSize: '0.9rem', marginBottom: '10px' }}>
                            <strong>Step 2:</strong> Enter the 6-digit code generated by your app.
                        </p>
                        <div style={{ display: 'flex', gap: '10px' }}>
                            <input
                                type="text"
                                placeholder="000000"
                                maxLength="6"
                                required
                                value={token}
                                onChange={(e) => setToken(e.target.value.replace(/\D/g, ''))} // only digits
                                style={{
                                    padding: '10px',
                                    backgroundColor: theme.colors.background,
                                    color: theme.colors.text,
                                    border: `1px solid ${theme.colors.border}`,
                                    borderRadius: '4px',
                                    width: '120px',
                                    fontSize: '1.2rem',
                                    letterSpacing: '4px',
                                    textAlign: 'center'
                                }}
                            />
                            <button type="submit" style={{
                                padding: '10px 15px',
                                backgroundColor: theme.colors.primary,
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                fontWeight: 'bold'
                            }}>
                                Verify & Enable
                            </button>
                        </div>
                    </form>
                </div>
            )}
        </div>
    );
};

export default MfaSetup;
