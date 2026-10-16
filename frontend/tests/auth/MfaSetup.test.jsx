import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import MfaSetup from '../../src/auth/MfaSetup';
import api from '../../src/communication/axios';

vi.mock('../../src/communication/axios');
// Minimal mock for qrcode.react since it requires canvas
vi.mock('qrcode.react', () => ({
    QRCodeSVG: ({ value }) => <div data-testid="qr-code">{value}</div>
}));

const renderMfa = () => render(<BrowserRouter><MfaSetup /></BrowserRouter>);

describe('MfaSetup', () => {

    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('shows "Setup MFA" button when MFA is disabled', async () => {
        api.get.mockResolvedValue({ data: { mfa_enabled: false } });
        renderMfa();
        await waitFor(() => {
            expect(screen.getByText('Setup MFA')).toBeDefined();
        });
    });

    it('shows "Disable MFA" button when MFA is enabled', async () => {
        api.get.mockResolvedValue({ data: { mfa_enabled: true } });
        renderMfa();
        await waitFor(() => {
            expect(screen.getByText('Disable MFA')).toBeDefined();
        });
    });

    it('shows QR code and secret after clicking Setup MFA', async () => {
        api.get.mockResolvedValue({ data: { mfa_enabled: false } });
        api.post.mockResolvedValue({ data: { secret: 'TESTBASESECRET', qr_uri: 'otpauth://totp/test' } });
        renderMfa();
        await waitFor(() => screen.getByText('Setup MFA'));
        fireEvent.click(screen.getByText('Setup MFA'));
        await waitFor(() => {
            expect(screen.getByTestId('qr-code')).toBeDefined();
            expect(screen.getByText('TESTBASESECRET')).toBeDefined();
        });
    });

    it('token input only accepts digits (via onChange filter)', async () => {
        api.get.mockResolvedValue({ data: { mfa_enabled: false } });
        api.post.mockResolvedValue({ data: { secret: 'SECRET', qr_uri: 'otpauth://test' } });
        renderMfa();
        await waitFor(() => screen.getByText('Setup MFA'));
        fireEvent.click(screen.getByText('Setup MFA'));
        await waitFor(() => screen.getByPlaceholderText('000000'));
        fireEvent.change(screen.getByPlaceholderText('000000'), { target: { value: 'abc123' } });
        // The onChange replaces(/\D/g, '') so only '123' should remain
        expect(screen.getByPlaceholderText('000000').value).toBe('123');
    });

    it('calls api.post /auth/mfa/enable on form submission', async () => {
        api.get.mockResolvedValue({ data: { mfa_enabled: false } });
        api.post
            .mockResolvedValueOnce({ data: { secret: 'SECRET', qr_uri: 'otpauth://test' } })
            .mockResolvedValueOnce({ data: {} });
        renderMfa();
        await waitFor(() => screen.getByText('Setup MFA'));
        fireEvent.click(screen.getByText('Setup MFA'));
        await waitFor(() => screen.getByPlaceholderText('000000'));
        fireEvent.change(screen.getByPlaceholderText('000000'), { target: { value: '123456' } });
        fireEvent.click(screen.getByText(/Verify/i));
        await waitFor(() => {
            expect(api.post).toHaveBeenCalledWith('/auth/mfa/enable', { token: '123456' });
        });
    });

    it('shows confirmation form on "Disable MFA" click', async () => {
        api.get.mockResolvedValue({ data: { mfa_enabled: true } });
        renderMfa();
        await waitFor(() => screen.getByText('Disable MFA'));
        fireEvent.click(screen.getByText('Disable MFA'));
        await waitFor(() => {
            expect(screen.getByText('Confirm Disable')).toBeDefined();
        });
    });

    it('hides confirmation form on Cancel click', async () => {
        api.get.mockResolvedValue({ data: { mfa_enabled: true } });
        renderMfa();
        await waitFor(() => screen.getByText('Disable MFA'));
        fireEvent.click(screen.getByText('Disable MFA'));
        await waitFor(() => screen.getByText('Cancel'));
        fireEvent.click(screen.getByText('Cancel'));
        await waitFor(() => {
            expect(screen.queryByText('Confirm Disable')).toBeNull();
        });
    });

    it('shows error message when API call fails', async () => {
        api.get.mockResolvedValue({ data: { mfa_enabled: false } });
        api.post
            .mockResolvedValueOnce({ data: { secret: 'SECRET', qr_uri: 'otpauth://test' } })
            .mockRejectedValueOnce({ response: { data: { detail: 'Invalid TOTP code' } } });
        renderMfa();
        await waitFor(() => screen.getByText('Setup MFA'));
        fireEvent.click(screen.getByText('Setup MFA'));
        await waitFor(() => screen.getByPlaceholderText('000000'));
        fireEvent.change(screen.getByPlaceholderText('000000'), { target: { value: '000000' } });
        fireEvent.click(screen.getByText(/Verify/i));
        await waitFor(() => {
            expect(screen.getByText(/Invalid TOTP code/i)).toBeDefined();
        });
    });
});
