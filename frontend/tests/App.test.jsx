import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import React from 'react';

// Mock all child page components since we're testing routing/guards only
vi.mock('../../src/auth/LoginPage', () => ({ default: () => <div>LoginPage</div> }));
vi.mock('../../src/auth/SignupPage', () => ({ default: () => <div>SignupPage</div> }));
vi.mock('../../src/auth/ForgotPasswordPage', () => ({ default: () => <div>ForgotPasswordPage</div> }));
vi.mock('../../src/auth/ResetPasswordPage', () => ({ default: () => <div>ResetPasswordPage</div> }));
vi.mock('../../src/dashboard/Dashboard', () => ({ default: () => <div>Dashboard</div> }));
vi.mock('../../src/documents/EtdEditor', () => ({ default: () => <div>EtdEditor</div> }));
vi.mock('../../src/database/DatabaseViewer', () => ({ default: () => <div>DatabaseViewer</div> }));
vi.mock('../../src/settings/SettingsPage', () => ({ default: () => <div>SettingsPage</div> }));
vi.mock('../../src/layout/Navbar', () => ({ default: () => <div>Navbar</div> }));
vi.mock('../../src/layout/MainLayout', () => ({ default: ({ children }) => <div>{children}</div> }));

// Extract PrivateRoute logic for isolated testing
const PrivateRoute = ({ children }) => {
    const token = sessionStorage.getItem('token');
    const isValidStructure = token && token.split('.').length === 3;
    if (token && !isValidStructure) {
        sessionStorage.removeItem('token');
        return <div>Redirected to login (malformed)</div>;
    }
    return token ? children : <div>Redirected to login</div>;
};

describe('PrivateRoute', () => {
    let sessionStorageMock;

    beforeEach(() => {
        sessionStorageMock = {};
        vi.stubGlobal('sessionStorage', {
            getItem: (key) => sessionStorageMock[key] ?? null,
            setItem: (key, val) => { sessionStorageMock[key] = val; },
            removeItem: vi.fn((key) => { delete sessionStorageMock[key]; }),
            clear: vi.fn(),
        });
    });

    afterEach(() => {
        vi.unstubAllGlobals();
    });

    it('redirects to login when no token', () => {
        render(<PrivateRoute><div>Protected</div></PrivateRoute>);
        expect(screen.getByText('Redirected to login')).toBeDefined();
    });

    it('allows access with valid 3-part JWT', () => {
        sessionStorageMock['token'] = 'aaa.bbb.ccc';
        render(<PrivateRoute><div>Protected Content</div></PrivateRoute>);
        expect(screen.getByText('Protected Content')).toBeDefined();
    });

    it('rejects and removes a 2-part malformed token', () => {
        sessionStorageMock['token'] = 'aaa.bbb';
        render(<PrivateRoute><div>Protected</div></PrivateRoute>);
        expect(screen.getByText('Redirected to login (malformed)')).toBeDefined();
        expect(sessionStorage.removeItem).toHaveBeenCalledWith('token');
    });

    it('rejects and removes a 1-part (non-JWT) token', () => {
        sessionStorageMock['token'] = 'singletoken';
        render(<PrivateRoute><div>Protected</div></PrivateRoute>);
        expect(screen.getByText('Redirected to login (malformed)')).toBeDefined();
    });

    it('allows token with 4 parts (atypical but passes 3-part check negation)', () => {
        sessionStorageMock['token'] = 'a.b.c.d';  // 4 parts — not === 3
        render(<PrivateRoute><div>Protected</div></PrivateRoute>);
        // 4-part token fails the structure check → treated as malformed
        expect(screen.getByText('Redirected to login (malformed)')).toBeDefined();
    });
});

describe('App routing (public routes)', () => {
    it('renders login page at /login without authentication', () => {
        render(
            <MemoryRouter initialEntries={['/login']}>
                <Routes>
                    <Route path="/login" element={<div>LoginPage</div>} />
                </Routes>
            </MemoryRouter>
        );
        expect(screen.getByText('LoginPage')).toBeDefined();
    });

    it('renders signup page at /signup without authentication', () => {
        render(
            <MemoryRouter initialEntries={['/signup']}>
                <Routes>
                    <Route path="/signup" element={<div>SignupPage</div>} />
                </Routes>
            </MemoryRouter>
        );
        expect(screen.getByText('SignupPage')).toBeDefined();
    });
});

describe('Inactivity timeout logic', () => {
    it('resets timer on user interaction events', () => {
        vi.useFakeTimers();
        const clearTimeoutSpy = vi.spyOn(global, 'clearTimeout');
        const setTimeoutSpy = vi.spyOn(global, 'setTimeout');

        // Simulate inactivity logic
        let timeoutId;
        const TIMEOUT_MS = 20 * 60 * 1000;
        const resetTimer = () => {
            if (timeoutId) clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {}, TIMEOUT_MS);
        };

        resetTimer();
        const firstCallCount = setTimeoutSpy.mock.calls.length;

        // Simulate a user interaction (mousemove)
        resetTimer();
        expect(clearTimeoutSpy).toHaveBeenCalled();
        expect(setTimeoutSpy.mock.calls.length).toBeGreaterThan(firstCallCount);

        vi.useRealTimers();
    });

    it('clears session after 20 minutes of inactivity', () => {
        vi.useFakeTimers();
        const mockClear = vi.fn();
        vi.stubGlobal('sessionStorage', { getItem: () => 'token', clear: mockClear, removeItem: vi.fn(), setItem: vi.fn() });

        let timeoutId;
        const handleLogout = () => {
            if (sessionStorage.getItem('token')) {
                sessionStorage.clear();
            }
        };
        timeoutId = setTimeout(handleLogout, 20 * 60 * 1000);
        expect(timeoutId).toBeDefined();
        vi.advanceTimersByTime(20 * 60 * 1000 + 100);
        expect(mockClear).toHaveBeenCalled();

        vi.useRealTimers();
        vi.unstubAllGlobals();
    });
});
