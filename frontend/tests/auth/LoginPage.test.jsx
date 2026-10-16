import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import LoginPage from '../../src/auth/LoginPage';
import api from '../../src/communication/axios';

vi.mock('../../src/communication/axios');
vi.mock('../../src/ui/Logo', () => ({ default: () => <div data-testid="logo">Logo</div> }));

const renderLogin = () => render(<BrowserRouter><LoginPage /></BrowserRouter>);

describe('LoginPage', () => {

    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('renders the email placeholder field', () => {
        renderLogin();
        expect(screen.getByPlaceholderText('Email')).toBeDefined();
    });

    it('renders the password placeholder field', () => {
        renderLogin();
        expect(screen.getByPlaceholderText('Password')).toBeDefined();
    });

    it('renders a Sign In button', () => {
        renderLogin();
        expect(screen.getByText('Sign In')).toBeDefined();
    });

    it('calls api.post with email and password on submit', async () => {
        api.post.mockResolvedValue({ data: { access_token: 'fake-token', token_type: 'bearer', expires_in: 1800 } });

        renderLogin();
        fireEvent.change(screen.getByPlaceholderText('Email'), { target: { value: 'test@bec-robotics.com' } });
        fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'ValidPass@99' } });
        fireEvent.click(screen.getByText('Sign In'));

        await waitFor(() => {
            expect(api.post).toHaveBeenCalledWith('/auth/login', {
                email: 'test@bec-robotics.com',
                password: 'ValidPass@99'
            });
        });
    });

    it('shows error message on failed login', async () => {
        api.post.mockRejectedValue({
            response: { data: { detail: 'Incorrect email or password' } }
        });

        renderLogin();
        fireEvent.change(screen.getByPlaceholderText('Email'), { target: { value: 'x@bec-robotics.com' } });
        fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'wrong' } });
        fireEvent.click(screen.getByText('Sign In'));

        await waitFor(() => {
            const errorEl = screen.queryByText(/incorrect email|invalid|error/i);
            expect(errorEl).not.toBeNull();
        });
    });

    it('shows MFA field when api returns mfa_required error', async () => {
        api.post.mockRejectedValue({
            response: { status: 401, data: { detail: 'mfa_required' } }
        });

        renderLogin();
        fireEvent.change(screen.getByPlaceholderText('Email'), { target: { value: 'mfa@bec-robotics.com' } });
        fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'ValidPass@99' } });
        fireEvent.click(screen.getByText('Sign In'));

        await waitFor(() => {
            // the mfa input has placeholder "000000" in the LoginPage component
            const mfaInput = screen.queryByPlaceholderText('000000');
            expect(mfaInput).not.toBeNull();
        });
    });

    it('renders the Logo component', () => {
        renderLogin();
        expect(screen.getByTestId('logo')).toBeDefined();
    });
});
