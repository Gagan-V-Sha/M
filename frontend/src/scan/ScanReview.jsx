import React from 'react';
import { useScanReviewPresenter } from './useScanReviewPresenter';

const statusColor = (status) => {
    const value = (status || 'none').toLowerCase();
    if (value === 'completed') return 'var(--green, #10b981)';
    if (value === 'processing' || value === 'pending') return 'var(--yellow, #f59e0b)';
    if (value === 'failed') return 'var(--red, #ef4444)';
    return 'var(--muted)';
};

const ScanReview = () => {
    const {
        jobs,
        selectedId,
        setSelectedId,
        detail,
        loadingList,
        loadingDetail,
        error,
    } = useScanReviewPresenter();

    const inspection = detail?.inspection;
    const engine = detail?.engine_note;

    return (
        <div className="page" style={{ padding: '20px 0' }}>
            <div className="section-head">
                <div>
                    <h1 style={{ fontSize: '30px', margin: 0 }}>Scan review (temporary)</h1>
                    <p style={{ color: 'var(--muted)', margin: '8px 0 0' }}>
                        MinerU status, extracted ISO clauses, and Annex Z → GSPR mappings.
                    </p>
                </div>
            </div>

            {error && (
                <div className="card" style={{ marginTop: '16px', color: 'var(--red)' }}>
                    {error}
                </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(260px, 340px) 1fr', gap: '20px', marginTop: '20px', alignItems: 'start' }}>
                <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                    <div style={{ padding: '16px 18px', borderBottom: '1px solid var(--border)', fontWeight: 600 }}>
                        Standards {loadingList ? '(loading…)' : `(${jobs.length})`}
                    </div>
                    <ul style={{ listStyle: 'none', margin: 0, padding: 0, maxHeight: '70vh', overflowY: 'auto' }}>
                        {jobs.map((job) => (
                            <li key={job.standard_id}>
                                <button
                                    type="button"
                                    onClick={() => setSelectedId(job.standard_id)}
                                    style={{
                                        width: '100%',
                                        textAlign: 'left',
                                        padding: '12px 18px',
                                        border: 'none',
                                        borderBottom: '1px solid var(--border)',
                                        background: selectedId === job.standard_id ? 'var(--card)' : 'transparent',
                                        color: 'var(--text)',
                                        cursor: 'pointer',
                                    }}
                                >
                                    <div style={{ fontWeight: 600 }}>{job.code}</div>
                                    <div style={{ fontSize: '12px', color: 'var(--muted)', marginTop: 4 }}>
                                        <span style={{ color: statusColor(job.parse_status) }}>{job.parse_status}</span>
                                        {' · '}
                                        {job.mapping_count} saved mappings
                                    </div>
                                </button>
                            </li>
                        ))}
                        {!loadingList && jobs.length === 0 && (
                            <li style={{ padding: '16px 18px', color: 'var(--muted)' }}>No standards in the catalog yet.</li>
                        )}
                    </ul>
                </div>

                <div>
                    {!selectedId && (
                        <div className="card">Select a standard to inspect the scan output.</div>
                    )}
                    {selectedId && loadingDetail && !detail && (
                        <div className="card">Loading scan result…</div>
                    )}
                    {detail && (
                        <>
                            <div className="card">
                                <div className="section-head" style={{ marginBottom: '12px' }}>
                                    <h3 style={{ margin: 0 }}>{detail.code}</h3>
                                    <span style={{ color: statusColor(detail.parse_status), fontWeight: 600 }}>
                                        {detail.parse_status}
                                    </span>
                                </div>
                                <p style={{ color: 'var(--muted)', marginTop: 0 }}>{detail.title}</p>
                                {detail.filename && (
                                    <div style={{ fontSize: '13px', color: 'var(--muted)' }}>
                                        File: {detail.filename}
                                        {detail.uploaded_at ? ` · ${detail.uploaded_at}` : ''}
                                    </div>
                                )}
                                {detail.parse_error && (
                                    <p style={{ color: 'var(--red)' }}>{detail.parse_error}</p>
                                )}
                                {inspection && (
                                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginTop: '16px' }}>
                                        {[
                                            ['Pages', inspection.page_count],
                                            ['Clauses', inspection.clause_count],
                                            ['Annex Z mappings', inspection.mapping_count],
                                            ['Table rows', inspection.table_row_count],
                                            ['HTML tables', inspection.html_tables_detected],
                                            ['Saved in DB', detail.saved_mappings?.length || 0],
                                        ].map(([label, value]) => (
                                            <div key={label} style={{ minWidth: '110px', padding: '10px 12px', border: '1px solid var(--border)', borderRadius: '8px' }}>
                                                <div style={{ fontSize: '11px', color: 'var(--muted)', textTransform: 'uppercase' }}>{label}</div>
                                                <div style={{ fontSize: '20px', fontWeight: 700 }}>{value}</div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                                {inspection?.warnings?.length > 0 && (
                                    <ul style={{ marginTop: '16px', color: 'var(--yellow, #f59e0b)' }}>
                                        {inspection.warnings.map((warning) => (
                                            <li key={warning}>{warning}</li>
                                        ))}
                                    </ul>
                                )}
                                {!detail.middle_json_loaded && detail.parse_status === 'completed' && (
                                    <p style={{ color: 'var(--yellow, #f59e0b)' }}>Scan marked completed, but middle JSON was not found on disk.</p>
                                )}
                            </div>

                            {engine && (
                                <div className="card" style={{ marginTop: '16px' }}>
                                    <h3 style={{ marginTop: 0 }}>
                                        Engine: {engine.recommended}
                                        {engine.version ? ` ${engine.version}` : ''}
                                    </h3>
                                    <p style={{ color: 'var(--muted)', marginBottom: 0 }}>{engine.reason}</p>
                                </div>
                            )}

                            <div className="card" style={{ marginTop: '16px' }}>
                                <h3 style={{ marginTop: 0 }}>Annex Z → GSPR (required result)</h3>
                                {(!inspection?.annex_z_mappings || inspection.annex_z_mappings.length === 0) && (
                                    <p style={{ color: 'var(--muted)' }}>No mappings extracted from this scan yet.</p>
                                )}
                                {inspection?.annex_z_mappings?.length > 0 && (
                                    <div style={{ overflowX: 'auto' }}>
                                        <table className="etd-table" style={{ width: '100%' }}>
                                            <thead>
                                                <tr>
                                                    <th>ISO clause</th>
                                                    <th>GSPR reference</th>
                                                    <th>Coverage note</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {inspection.annex_z_mappings.map((row, index) => (
                                                    <tr key={`${row.iso_clause}-${index}`}>
                                                        <td>{row.iso_clause}</td>
                                                        <td>{row.gspr_reference}</td>
                                                        <td>{row.coverage_note}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                            </div>

                            <div className="card" style={{ marginTop: '16px' }}>
                                <h3 style={{ marginTop: 0 }}>ISO clauses found</h3>
                                {(!inspection?.clauses || inspection.clauses.length === 0) && (
                                    <p style={{ color: 'var(--muted)' }}>No clause headings matched yet.</p>
                                )}
                                {inspection?.clauses?.map((clause) => (
                                    <div key={`${clause.clause_ref}-${clause.title}`} style={{ padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
                                        <strong>{clause.clause_ref}</strong> {clause.title}
                                        {clause.body_preview && (
                                            <div style={{ fontSize: '13px', color: 'var(--muted)', marginTop: 4 }}>{clause.body_preview}</div>
                                        )}
                                    </div>
                                ))}
                            </div>

                            <div className="card" style={{ marginTop: '16px' }}>
                                <h3 style={{ marginTop: 0 }}>Table row samples</h3>
                                {(!inspection?.table_row_samples || inspection.table_row_samples.length === 0) && (
                                    <p style={{ color: 'var(--muted)' }}>No table rows flattened from MinerU output.</p>
                                )}
                                {inspection?.table_row_samples?.map((row, index) => (
                                    <div key={index} style={{ fontFamily: 'monospace', fontSize: '12px', padding: '6px 0', borderBottom: '1px solid var(--border)' }}>
                                        {row}
                                    </div>
                                ))}
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ScanReview;
