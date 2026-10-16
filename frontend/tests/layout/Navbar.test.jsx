import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import Navbar from '../../src/layout/Navbar';
import api from '../../src/communication/axios';

vi.mock('../../src/communication/axios');
vi.mock('../../src/ui/Logo', () => ({ default: () => <div data-testid="logo">Logo</div> }));

const renderNavbar = () => render(<BrowserRouter><Navbar /></BrowserRouter>);

describe('Navbar', () => {

    let localStorageMock;

    beforeEach(() => {
        vi.clearAllMocks();
        localStorageMock = {};
        vi.stubGlobal('localStorage', {
            getItem: (key) => localStorageMock[key] ?? null,
            setItem: vi.fn((key, val) => { localStorageMock[key] = val; }),
            removeItem: vi.fn((key) => { delete localStorageMock[key]; }),
            clear: vi.fn(),
        });
    });

    afterEach(() => {
        vi.unstubAllGlobals();
    });

    it('renders without crashing', () => {
        api.get.mockResolvedValue({ data: { name: 'Test User', email: 'test@bec-robotics.com' } });
        renderNavbar();
        expect(screen.getByRole('navigation')).toBeDefined();
    });

    it('shows loading "..." before user data loads', () => {
        api.get.mockReturnValue(new Promise(() => {})); // Never resolves
        renderNavbar();
        expect(screen.getByText('...')).toBeDefined();
    });

    it('shows user name when API returns name field', async () => {
        localStorageMock['is_authenticated'] = 'true';
        api.get.mockResolvedValue({ data: { name: 'Alice Smith', email: 'alice@bec-robotics.com' } });
        renderNavbar();
        await waitFor(() => {
            expect(screen.getByText('Alice Smith')).toBeDefined();
        });
    });

    it('shows email when user has no name', async () => {
        localStorageMock['is_authenticated'] = 'true';
        api.get.mockResolvedValue({ data: { name: null, email: 'noname@bec-robotics.com' } });
        renderNavbar();
        await waitFor(() => {
            expect(screen.getByText('noname@bec-robotics.com')).toBeDefined();
        });
    });

    it('renders Settings button', () => {
        api.get.mockResolvedValue({ data: { name: 'User', email: 'u@bec-robotics.com' } });
        renderNavbar();
        expect(screen.getByText('Settings')).toBeDefined();
    });

    it('renders Logout button', () => {
        api.get.mockResolvedValue({ data: { name: 'User', email: 'u@bec-robotics.com' } });
        renderNavbar();
        expect(screen.getByText('Logout')).toBeDefined();
    });

    it('calls api.post /auth/logout on logout click', async () => {
        localStorageMock['is_authenticated'] = 'true';
        api.get.mockResolvedValue({ data: { name: 'User', email: 'u@bec-robotics.com' } });
        api.post.mockResolvedValue({ data: {} });
        renderNavbar();
        await waitFor(() => screen.getByText('Logout'));
        fireEvent.click(screen.getByText('Logout'));
        await waitFor(() => {
            expect(api.post).toHaveBeenCalledWith('/auth/logout');
        });
    });

    it('clears auth flag from localStorage on logout', async () => {
        localStorageMock['is_authenticated'] = 'true';
        api.get.mockResolvedValue({ data: { name: 'User', email: 'u@bec-robotics.com' } });
        api.post.mockResolvedValue({ data: {} });
        renderNavbar();
        await waitFor(() => screen.getByText('Logout'));
        fireEvent.click(screen.getByText('Logout'));
        await waitFor(() => {
            expect(localStorage.removeItem).toHaveBeenCalledWith('is_authenticated');
        });
    });

    it('does NOT call api.get /auth/me when not authenticated', async () => {
        api.get.mockResolvedValue({ data: {} });
        renderNavbar();
        await new Promise(r => setTimeout(r, 50));
        expect(api.get).not.toHaveBeenCalled();
    });
});
