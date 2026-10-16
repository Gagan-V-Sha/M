import React from 'react';
import PasswordChangeForm from './PasswordChangeForm';
import MfaSetup from '../auth/MfaSetup';
import { theme } from '../theme';

const SettingsPage = () => {
    return (
        <div style={{ padding: '2rem' }}>
            <h1 style={{ marginBottom: '2rem' }}>User Settings</h1>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                <section>
                    <h3 style={{ color: theme.colors.primary, borderBottom: `1px solid ${theme.colors.border}`, paddingBottom: '0.5rem', marginBottom: '1.5rem' }}>
                        Security
                    </h3>
                    <PasswordChangeForm />
                    <MfaSetup />
                </section>

                {/* Future settings sections (e.g. Profile, Notifications) can go here */}
            </div>
        </div>
    );
};

export default SettingsPage;
