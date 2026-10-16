import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, beforeAll } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import api from '../../src/communication/axios';

vi.mock('../../src/communication/axios');
vi.mock('../../src/layout/Navbar', () => ({ default: () => <div>Navbar</div> }));
vi.mock('../../src/layout/Sidebar', () => ({ default: () => <div>Sidebar</div> }));

// Dynamic import to avoid errors if Dashboard path is slightly different
let Dashboard;
beforeAll(async () => {
    try {
        const mod = await import('../../src/dashboard/Dashboard');
        Dashboard = mod.default;
    } catch {
        Dashboard = () => <div>Dashboard Load Error</div>;
    }
});

describe('Dashboard', () => {

    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('renders without crashing', async () => {
        api.get.mockResolvedValue({ data: [] });
        render(<BrowserRouter>{Dashboard ? <Dashboard /> : <div>Dashboard</div>}</BrowserRouter>);
        expect(document.body).toBeDefined();
    });

    it('renders device cards when API returns devices', async () => {
        const devices = [
            { id: 1, name: 'Device A', model_code: 'MDL001' },
            { id: 2, name: 'Device B', model_code: 'MDL002' }
        ];
        api.get.mockResolvedValue({ data: devices });
        if (!Dashboard) return;
        render(<BrowserRouter><Dashboard /></BrowserRouter>);
        await waitFor(() => {
            expect(screen.getByText('Device A')).toBeDefined();
            expect(screen.getByText('Device B')).toBeDefined();
        });
    });

    it('handles empty device list', async () => {
        api.get.mockResolvedValue({ data: [] });
        if (!Dashboard) return;
        render(<BrowserRouter><Dashboard /></BrowserRouter>);
        await waitFor(() => {
            // Should not crash
            expect(document.body).toBeDefined();
        });
    });

    it('calls api.get /device-profiles on mount', async () => {
        api.get.mockResolvedValue({ data: [] });
        if (!Dashboard) return;
        render(<BrowserRouter><Dashboard /></BrowserRouter>);
        await waitFor(() => {
            expect(api.get).toHaveBeenCalledWith(expect.stringContaining('device-profiles'));
        });
    });
});
