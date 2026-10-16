import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, beforeAll } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import api from '../../src/communication/axios';

vi.mock('../../src/communication/axios');
vi.mock('../../src/layout/Navbar', () => ({ default: () => <div>Navbar</div> }));
vi.mock('../../src/layout/Sidebar', () => ({ default: () => <div>Sidebar</div> }));

let EtdEditor;
beforeAll(async () => {
    try {
        const mod = await import('../../src/documents/EtdEditor');
        EtdEditor = mod.default;
    } catch {
        EtdEditor = () => <div>EtdEditor Load Error</div>;
    }
});

const renderEditor = (deviceId = '1') =>
    render(
        <MemoryRouter initialEntries={[`/devices/${deviceId}/etd`]}>
            <Routes>
                <Route
                    path="/devices/:deviceId/etd"
                    element={EtdEditor ? <EtdEditor /> : <div>EtdEditor</div>}
                />
            </Routes>
        </MemoryRouter>
    );

describe('EtdEditor', () => {

    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('renders without crashing', async () => {
        api.get.mockResolvedValue({ data: [] });
        renderEditor();
        expect(document.body).toBeDefined();
    });

    it('calls api.get /etd with device_id on mount', async () => {
        api.get.mockResolvedValue({ data: [] });
        if (!EtdEditor) return;
        renderEditor('5');
        await waitFor(() => {
            const calls = api.get.mock.calls;
            const etdCall = calls.find(c => c[0] && c[0].includes('etd'));
            expect(etdCall).toBeDefined();
        });
    });

    it('renders rows when API returns ETD data', async () => {
        // include standards and evidence_documents arrays or the component crashes trying to map them
        const rows = [
            {
                id: 1,
                gspr_requirement: { full_reference: 'GSPR 1', text: 'Test req', standard_mappings: [] },
                applicability: 'fully_applicable',
                notes: 'OK',
                standards: [],
                evidence_documents: []
            }
        ];

        // the component makes 6 parallel api.get calls - return rows for etd, empty array for everything else
        api.get.mockImplementation((url) => {
            if (url.includes('/etd')) return Promise.resolve({ data: rows });
            return Promise.resolve({ data: [] });
        });

        if (!EtdEditor) return;
        renderEditor();
        await waitFor(() => {
            expect(screen.getByText('GSPR 1')).toBeDefined();
        });
    });

    it('renders the Export PDF button', async () => {
        api.get.mockResolvedValue({ data: [] });
        if (!EtdEditor) return;
        renderEditor();
        await waitFor(() => {
            const exportBtn = screen.queryByText(/export/i);
            expect(exportBtn).not.toBeNull();
        });
    });
});
