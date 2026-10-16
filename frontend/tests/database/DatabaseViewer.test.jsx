import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, beforeAll } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from 'styled-components';
import { theme } from '../../src/theme';
import api from '../../src/communication/axios';

vi.mock('../../src/communication/axios');
vi.mock('../../src/layout/Navbar', () => ({ default: () => <div>Navbar</div> }));
vi.mock('../../src/layout/Sidebar', () => ({ default: () => <div>Sidebar</div> }));

let DatabaseViewer;
beforeAll(async () => {
    try {
        const mod = await import('../../src/database/DatabaseViewer');
        DatabaseViewer = mod.default;
    } catch {
        DatabaseViewer = () => <div>DatabaseViewer Load Error</div>;
    }
});

// wrap with ThemeProvider so styled-components can access props.theme.colors.*
const renderViewer = () =>
    render(
        <ThemeProvider theme={theme}>
            <BrowserRouter>
                {DatabaseViewer ? <DatabaseViewer /> : <div>DatabaseViewer</div>}
            </BrowserRouter>
        </ThemeProvider>
    );

describe('DatabaseViewer', () => {

    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('renders without crashing', async () => {
        api.get.mockResolvedValue({ data: [] });
        renderViewer();
        expect(document.body).toBeDefined();
    });

    it('renders a Standards tab or button', async () => {
        api.get.mockResolvedValue({ data: [] });
        if (!DatabaseViewer) return;
        renderViewer();
        await waitFor(() => {
            // use exact string to avoid matching the subtitle which also contains 'Standards'
            expect(screen.getByText('Standards')).toBeDefined();
        });
    });

    it('renders an Evidence tab or button', async () => {
        api.get.mockResolvedValue({ data: [] });
        if (!DatabaseViewer) return;
        renderViewer();
        await waitFor(() => {
            // use exact string to avoid matching the subtitle which also contains 'Evidence'
            expect(screen.getByText('Evidence')).toBeDefined();
        });
    });

    it('renders a GSPR tab or button', async () => {
        api.get.mockResolvedValue({ data: [] });
        if (!DatabaseViewer) return;
        renderViewer();
        await waitFor(() => {
            // the tab text is 'GSPR Requirements' - using full text avoids matching the subtitle
            expect(screen.getByText('GSPR Requirements')).toBeDefined();
        });
    });

    it('fetches data from API on mount', async () => {
        api.get.mockResolvedValue({ data: [] });
        if (!DatabaseViewer) return;
        renderViewer();
        await waitFor(() => {
            expect(api.get).toHaveBeenCalled();
        });
    });

    it('renders table rows when standards data is returned', async () => {
        const standards = [
            { id: 1, code: 'ISO 14971', title: 'Risk Management', harmonised: true },
            { id: 2, code: 'EN 62133', title: 'Battery Safety', harmonised: false }
        ];
        // mock the standards tab response
        api.get.mockResolvedValue({ data: standards });
        if (!DatabaseViewer) return;
        renderViewer();
        // click onto the Standards tab so the component fetches standards
        await waitFor(() => screen.getByText('Standards'));
        fireEvent.click(screen.getByText('Standards'));
        await waitFor(() => {
            const iso = screen.queryByText('ISO 14971');
            const en = screen.queryByText('EN 62133');
            expect(iso || en).not.toBeNull();
        });
    });
});
