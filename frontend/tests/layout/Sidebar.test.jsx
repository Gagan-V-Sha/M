import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import Sidebar from '../../src/layout/Sidebar';
import api from '../../src/communication/axios';

vi.mock('../../src/communication/axios');

describe('Sidebar', () => {

    let sessionStorageMock;

    beforeEach(() => {
        vi.clearAllMocks();
        sessionStorageMock = {};
        vi.stubGlobal('sessionStorage', {
            getItem: (key) => sessionStorageMock[key] ?? null,
            setItem: vi.fn((key, val) => { sessionStorageMock[key] = val; }),
            removeItem: vi.fn((key) => { delete sessionStorageMock[key]; }),
            clear: vi.fn(),
        });
        api.get.mockImplementation((url) => {
            if (url === '/config') {
                return Promise.resolve({
                    data: {
                        role: 'scanner',
                        mineru_ready: true,
                        mineru_enabled: true,
                        mineru_available: true,
                    },
                });
            }
            return Promise.resolve({ data: [] });
        });
    });

    afterEach(() => {
        vi.unstubAllGlobals();
    });

    const renderSidebar = (path = '/dashboard') =>
        render(
            <MemoryRouter initialEntries={[path]}>
                <Routes>
                    <Route path="/*" element={<Sidebar />} />
                </Routes>
            </MemoryRouter>
        );

    it('renders without crashing', () => {
        renderSidebar();
        expect(document.body).toBeDefined();
    });

    it('shows Dashboard link', () => {
        renderSidebar('/dashboard');
        expect(screen.getByText(/Dashboard/i)).toBeDefined();
    });

    it('shows Database Viewer link', () => {
        renderSidebar('/dashboard');
        expect(screen.getByText(/Database Viewer/i)).toBeDefined();
    });

    it('shows Scan review link when MinerU is ready', async () => {
        api.get.mockImplementation((url) => {
            if (url === '/config') {
                return Promise.resolve({
                    data: { role: 'scanner', mineru_ready: true, mineru_enabled: true, mineru_available: true },
                });
            }
            return Promise.resolve({ data: [] });
        });
        renderSidebar('/dashboard');
        expect(await screen.findByText(/Scan review/i)).toBeDefined();
    });

    it('hides Scan review when MinerU is not ready (Pi/runtime)', async () => {
        api.get.mockImplementation((url) => {
            if (url === '/config') {
                return Promise.resolve({
                    data: { role: 'runtime', mineru_ready: false, mineru_enabled: false, mineru_available: false },
                });
            }
            return Promise.resolve({ data: [] });
        });
        renderSidebar('/dashboard');
        await screen.findByText(/Dashboard/i);
        expect(screen.queryByText(/Scan review/i)).toBeNull();
    });

    it('highlights Scan review on /scan-review', async () => {
        api.get.mockImplementation((url) => {
            if (url === '/config') {
                return Promise.resolve({
                    data: { role: 'scanner', mineru_ready: true, mineru_enabled: true, mineru_available: true },
                });
            }
            return Promise.resolve({ data: [] });
        });
        renderSidebar('/scan-review');
        const item = await screen.findByText(/^Scan review$/i);
        expect(item.style.borderLeft).toMatch(/accent|4px/i);
    });

    it('highlights Database Viewer on /database-viewer', () => {
        renderSidebar('/database-viewer');
        const item = screen.getByText(/^Database Viewer$/i);
        expect(item.style.borderLeft).toMatch(/accent|4px/i);
        const dash = screen.getByText(/^Dashboard$/i);
        expect(dash.style.backgroundColor === 'var(--card)').toBe(false);
    });

    it('does NOT show chapter list on /dashboard', () => {
        api.get.mockResolvedValue({ data: [] });
        renderSidebar('/dashboard');
        // No chapter items should appear for non-device-route
        expect(screen.queryByText(/Chapter I/i)).toBeNull();
    });

    it('stores device ID in sessionStorage when on a device route', async () => {
        api.get.mockResolvedValue({ data: ['Chapter I', 'Chapter II'] });
        renderSidebar('/devices/42/etd');
        await waitFor(() => {
            expect(sessionStorage.setItem).toHaveBeenCalledWith(
                expect.stringContaining('Device'), '42'
            );
        });
    });

    it('renders known chapter title mapping', () => {
        // Chapter title mapping: "Chapter I" → "General requirements"
        api.get.mockResolvedValue({ data: ['Chapter I'] });
        renderSidebar('/devices/1/etd');
        waitFor(() => {
            expect(screen.getByText(/General requirements/i)).toBeDefined();
        });
    });
});
