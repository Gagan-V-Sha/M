import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import PasswordChangeForm from '../../src/settings/PasswordChangeForm';
import api from '../../src/communication/axios';

vi.mock('../../src/communication/axios');

const renderForm = () => render(<BrowserRouter><PasswordChangeForm /></BrowserRouter>);

describe('PasswordChangeForm', () => {

    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('renders Current Password label', () => {
        renderForm();
        expect(screen.getByText(/Current Password/i)).toBeDefined();
    });

    it('renders New Password label', () => {
        renderForm();
        // using exact string so it doesn't also match 'Confirm New Password'
        expect(screen.getByText('New Password')).toBeDefined();
    });

    it('renders Confirm New Password label', () => {
        renderForm();
        expect(screen.getByText(/Confirm New Password/i)).toBeDefined();
    });

    it('shows "do not match" error when new passwords differ', async () => {
        renderForm();
        // password inputs are type=password so we use querySelector, not getAllByRole
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        fireEvent.change(passwordInputs[0], { target: { value: 'OldPass@99' } });
        fireEvent.change(passwordInputs[1], { target: { value: 'NewPass@99' } });
        fireEvent.change(passwordInputs[2], { target: { value: 'DiffPass@99' } });
        fireEvent.click(screen.getByText('Update Password'));
        await waitFor(() => {
            expect(screen.getByText(/do not match/i)).toBeDefined();
        });
    });

    it('calls api.post /auth/password-change with correct payload on valid submit', async () => {
        api.post.mockResolvedValue({ data: {} });
        renderForm();
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        fireEvent.change(passwordInputs[0], { target: { value: 'OldPass@99' } });
        fireEvent.change(passwordInputs[1], { target: { value: 'NewPass@99' } });
        fireEvent.change(passwordInputs[2], { target: { value: 'NewPass@99' } });
        fireEvent.click(screen.getByText('Update Password'));
        await waitFor(() => {
            expect(api.post).toHaveBeenCalledWith('/auth/password-change', {
                old_password: 'OldPass@99',
                new_password: 'NewPass@99'
            });
        });
    });

    it('shows "Password changed successfully!" on success', async () => {
        api.post.mockResolvedValue({ data: {} });
        renderForm();
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        fireEvent.change(passwordInputs[0], { target: { value: 'OldPass@99' } });
        fireEvent.change(passwordInputs[1], { target: { value: 'NewPass@99' } });
        fireEvent.change(passwordInputs[2], { target: { value: 'NewPass@99' } });
        fireEvent.click(screen.getByText('Update Password'));
        await waitFor(() => {
            expect(screen.getByText(/Password changed successfully/i)).toBeDefined();
        });
    });

    it('clears all fields after successful change', async () => {
        api.post.mockResolvedValue({ data: {} });
        renderForm();
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        fireEvent.change(passwordInputs[0], { target: { value: 'OldPass@99' } });
        fireEvent.change(passwordInputs[1], { target: { value: 'NewPass@99' } });
        fireEvent.change(passwordInputs[2], { target: { value: 'NewPass@99' } });
        fireEvent.click(screen.getByText('Update Password'));
        await waitFor(() => {
            const freshInputs = document.querySelectorAll('input[type="password"]');
            freshInputs.forEach(input => expect(input.value).toBe(''));
        });
    });

    it('shows API error detail on failure', async () => {
        api.post.mockRejectedValue({
            response: { data: { detail: 'Current password is incorrect' } }
        });
        renderForm();
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        fireEvent.change(passwordInputs[0], { target: { value: 'WrongOld@99' } });
        fireEvent.change(passwordInputs[1], { target: { value: 'NewPass@99' } });
        fireEvent.change(passwordInputs[2], { target: { value: 'NewPass@99' } });
        fireEvent.click(screen.getByText('Update Password'));
        await waitFor(() => {
            expect(screen.getByText(/Current password is incorrect/i)).toBeDefined();
        });
    });

    it('shows loading button text during API call', async () => {
        let resolvePromise;
        api.post.mockReturnValue(new Promise(r => { resolvePromise = r; }));
        renderForm();
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        fireEvent.change(passwordInputs[0], { target: { value: 'OldPass@99' } });
        fireEvent.change(passwordInputs[1], { target: { value: 'NewPass@99' } });
        fireEvent.change(passwordInputs[2], { target: { value: 'NewPass@99' } });
        fireEvent.click(screen.getByText('Update Password'));
        await waitFor(() => {
            expect(screen.getByText(/Changing Password/i)).toBeDefined();
        });
        resolvePromise({ data: {} });
    });
});
