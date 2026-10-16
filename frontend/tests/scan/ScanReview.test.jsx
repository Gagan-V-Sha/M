import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import api from '../../src/communication/axios';
import ScanReview from '../../src/scan/ScanReview';

vi.mock('../../src/communication/axios');

describe('ScanReview', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('lists scan jobs and shows extracted mappings', async () => {
        api.get.mockImplementation((url) => {
            if (url === '/imports/scan-review') {
                return Promise.resolve({
                    data: [
                        {
                            standard_id: 7,
                            code: 'ISO 13485',
                            title: 'QMS',
                            parse_status: 'completed',
                            mapping_count: 1,
                        },
                    ],
                });
            }
            if (url === '/imports/scan-review/7') {
                return Promise.resolve({
                    data: {
                        standard_id: 7,
                        code: 'ISO 13485',
                        title: 'QMS',
                        parse_status: 'completed',
                        saved_mappings: [{ id: 1, iso_clause: '4.1', gspr_reference: '10.1', coverage_note: 'ok' }],
                        middle_json_loaded: true,
                        engine_note: { recommended: 'MinerU', version: '3.4.5', reason: 'Keep MinerU' },
                        inspection: {
                            page_count: 2,
                            clause_count: 1,
                            mapping_count: 1,
                            table_row_count: 1,
                            html_tables_detected: 1,
                            warnings: [],
                            annex_z_mappings: [
                                { iso_clause: '4.1', gspr_reference: '10.1', coverage_note: 'Chapter I' },
                            ],
                            clauses: [{ clause_ref: '4.1', title: 'Quality', body_preview: 'body' }],
                            table_row_samples: ['4.1 | 10.1'],
                        },
                    },
                });
            }
            return Promise.resolve({ data: [] });
        });

        render(
            <MemoryRouter>
                <ScanReview />
            </MemoryRouter>
        );

        await waitFor(() => {
            expect(screen.getByText('ISO 13485')).toBeDefined();
        });

        screen.getByText('ISO 13485').click();

        await waitFor(() => {
            expect(screen.getByRole('heading', { name: /Annex Z → GSPR \(required result\)/i })).toBeDefined();
            expect(screen.getByText('10.1')).toBeDefined();
            expect(screen.getByText(/Engine: MinerU/i)).toBeDefined();
        });
    });
});
