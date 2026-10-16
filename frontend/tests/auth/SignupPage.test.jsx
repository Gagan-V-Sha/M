import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import SignupPage from '../../src/auth/SignupPage';
import api from '../../src/communication/axios';

vi.mock('../../src/communication/axios');
vi.mock('../../src/ui/Logo', () => ({ default: () => <div data-testid="logo">Logo</div> }));

const renderSignup = () => render(<BrowserRouter><SignupPage /></BrowserRouter>);

const fillSignup = ({
    email = 'user@bec-robotics.com',
    password = 'ValidPass@99',
    confirm = 'ValidPass@99',
    acceptGdpr = true
} = {}) => {
    fireEvent.change(screen.getByPlaceholderText('Email'), { target: { value: email } });
    fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: password } });
    fireEvent.change(screen.getByPlaceholderText('Confirm Password'), { target: { value: confirm } });
    if (acceptGdpr) {
        fireEvent.click(screen.getByRole('checkbox'));
    }
};

describe('SignupPage', () => {

    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('renders email, password, and confirm password fields', () => {
        renderSignup();
        expect(screen.getByPlaceholderText('Email')).toBeDefined();
        expect(screen.getByPlaceholderText('Password')).toBeDefined();
        expect(screen.getByPlaceholderText('Confirm Password')).toBeDefined();
    });

    it('renders the Sign Up button', () => {
        renderSignup();
        expect(screen.getByText('Sign Up')).toBeDefined();
    });

    it('shows "Passwords do not match" when passwords differ', async () => {
        renderSignup();
        fillSignup({ confirm: 'Different@99' });
        fireEvent.click(screen.getByText('Sign Up'));
        await waitFor(() => {
            expect(screen.getByText(/passwords do not match/i)).toBeDefined();
        });
    });

    it('does not submit without GDPR consent', async () => {
        renderSignup();
        fillSignup({ acceptGdpr: false });
        fireEvent.click(screen.getByText('Sign Up'));
        await new Promise((resolve) => setTimeout(resolve, 50));
        expect(api.post).not.toHaveBeenCalled();
    });

    it('sends register request for a company email after GDPR consent', async () => {
        api.post.mockResolvedValue({ data: {} });
        renderSignup();
        fillSignup({ email: 'user@gmail.com' });
        fireEvent.click(screen.getByText('Sign Up'));
        await waitFor(() => {
            expect(api.post).toHaveBeenCalled();
            expect(api.post.mock.calls[0][0]).toBe('/auth/register');
        });
    });

    it('calls register then login on valid submission', async () => {
        api.post.mockResolvedValueOnce({ data: {} });
        api.post.mockResolvedValueOnce({ data: { access_token: 'fake-token' } });

        renderSignup();
        fillSignup();
        fireEvent.click(screen.getByText('Sign Up'));

        await waitFor(() => {
            expect(api.post).toHaveBeenCalledTimes(2);
            expect(api.post.mock.calls[0][0]).toBe('/auth/register');
            expect(api.post.mock.calls[1][0]).toBe('/auth/login');
        });
    });

    it('renders a link to the login page', () => {
        renderSignup();
        expect(screen.getByText('Log in')).toBeDefined();
    });

    it('displays server error message on API failure', async () => {
        api.post.mockRejectedValue({
            response: { data: { detail: 'Email already registered' } }
        });

        renderSignup();
        fillSignup({ email: 'dup@bec-robotics.com' });
        fireEvent.click(screen.getByText('Sign Up'));

        await waitFor(() => {
            expect(screen.getByText(/Email already registered/i)).toBeDefined();
        });
    });

    it('displays "Cannot connect to server" on network error', async () => {
        api.post.mockRejectedValue({ request: {}, message: 'Network Error' });

        renderSignup();
        fillSignup();
        fireEvent.click(screen.getByText('Sign Up'));

        await waitFor(() => {
            expect(screen.getByText(/cannot connect to server/i)).toBeDefined();
        });
    });
});
