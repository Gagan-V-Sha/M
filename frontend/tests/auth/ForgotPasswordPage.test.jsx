import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import ForgotPasswordPage from '../../src/auth/ForgotPasswordPage';
import api from '../../src/communication/axios';

vi.mock('../../src/communication/axios');
vi.mock('../../src/ui/Logo', () => ({ default: () => <div data-testid="logo">Logo</div> }));

const renderPage = () => render(<BrowserRouter><ForgotPasswordPage /></BrowserRouter>);

describe('ForgotPasswordPage', () => {

    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('renders email input with "Email Address" placeholder', () => {
        renderPage();
        expect(screen.getByPlaceholderText('Email Address')).toBeDefined();
    });

    it('renders the "Request Reset Token" button', () => {
        renderPage();
        expect(screen.getByText('Request Reset Token')).toBeDefined();
    });

    it('"I have a token" button is hidden before form submission', () => {
        renderPage();
        expect(screen.queryByText(/I have a token/i)).toBeNull();
    });

    it('calls api.post /auth/password-reset-request with the entered email', async () => {
        api.post.mockResolvedValue({ data: {} });
        renderPage();
        fireEvent.change(screen.getByPlaceholderText('Email Address'), {
            target: { value: 'user@bec-robotics.com' }
        });
        fireEvent.click(screen.getByText('Request Reset Token'));
        await waitFor(() => {
            expect(api.post).toHaveBeenCalledWith('/auth/password-reset-request', {
                email: 'user@bec-robotics.com'
            });
        });
    });

    it('shows success message regardless of whether email exists (anti-enumeration)', async () => {
        api.post.mockRejectedValue({ response: { status: 500 } });
        renderPage();
        fireEvent.change(screen.getByPlaceholderText('Email Address'), {
            target: { value: 'unknown@bec-robotics.com' }
        });
        fireEvent.click(screen.getByText('Request Reset Token'));
        await waitFor(() => {
            // Always success message
            expect(screen.getByText(/password reset token/i)).toBeDefined();
        });
    });

    it('shows "I have a token" button after successful submission', async () => {
        api.post.mockResolvedValue({ data: {} });
        renderPage();
        fireEvent.change(screen.getByPlaceholderText('Email Address'), {
            target: { value: 'user@bec-robotics.com' }
        });
        fireEvent.click(screen.getByText('Request Reset Token'));
        await waitFor(() => {
            expect(screen.getByText(/I have a token/i)).toBeDefined();
        });
    });

    it('renders a link back to the login page', () => {
        renderPage();
        expect(screen.getByText('Log in')).toBeDefined();
    });
});
