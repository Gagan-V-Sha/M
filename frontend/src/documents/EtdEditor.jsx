import React from 'react';
import DataTable from '../ui/DataTable';
import MultiSelect from '../ui/MultiSelect';
import { theme } from '../theme';
import { useEtdEditorPresenter } from './useEtdEditorPresenter';

const EtdEditor = () => {
    const {
        id,
        navigate,
        selectedChapter,
        loading,
        device,
        isSaving,
        lastSaved,
        saveError,
        allChapters,
        filterText,
        setFilterText,
        hideNotApplicable,
        setHideNotApplicable,
        filteredRows,
        standardsOptions,
        evidenceOptions,
        updateRow,
        updateRowStandards,
        updateRowEvidence,
        updateDeviceMeta,
        handleExportPdf,
        isExporting // Fix 2.6
    } = useEtdEditorPresenter();

    const columns = [
        {
            header: '#',
            width: '88px',
            accessor: 'gspr_requirement.full_reference',
            render: row => (
                <div style={{
                    fontWeight: row.gspr_requirement?.parent_id ? 'normal' : 'bold',
                    paddingLeft: row.gspr_requirement?.parent_id ? '15px' : '0px',
                    opacity: row.gspr_requirement?.parent_id ? 0.8 : 1
                }}>
                    {row.gspr_requirement?.full_reference}
                </div>
            )
        },
        {
            header: 'Requirement',
            width: '30%',
            render: row => {
                const mappings = row.gspr_requirement?.standard_mappings || [];

                // Group by standard code
                const grouped = mappings.reduce((acc, m) => {
                    const code = m.standard?.code || 'Mapping';
                    if (!acc[code]) acc[code] = [];
                    acc[code].push(m.iso_clause);
                    return acc;
                }, {});

                const suggestionCount = Object.keys(grouped).length;
                const tooltipText = Object.entries(grouped)
                    .map(([code, clauses]) => `${code}: Clauses ${clauses.join(', ')}`)
                    .join('\\n');

                return <ExpandableText text={row.gspr_requirement?.text} mappingCount={suggestionCount} tooltipText={tooltipText} />;
            }
        },
        {
            header: 'Applicability',
            width: '150px',
            render: row => (
                <div style={{ width: '100%', minWidth: 0 }}>
                    <select
                        value={row.applicability}
                        onChange={e => updateRow(row.id, 'applicability', e.target.value)}
                        style={{ padding: '6px', borderRadius: '4px', borderColor: theme.colors.border, width: '100%', maxWidth: '100%', boxSizing: 'border-box' }}
                    >
                        <option value="fully_applicable">Fully Applicable</option>
                        <option value="partially_applicable">Partially Applicable</option>
                        <option value="not_applicable">Not Applicable</option>
                    </select>
                </div>
            )
        },
        {
            header: 'Standards',
            width: '18%',
            render: row => (
                <div style={{ width: '100%', minWidth: 0, maxWidth: '100%', boxSizing: 'border-box' }}>
                    <MultiSelect
                        options={standardsOptions}
                        value={row.standards.map(s => ({
                            value: s.id,
                            label: standardsOptions.find(o => o.value === s.id)?.label || s.code
                        }))}
                        onChange={val => updateRowStandards(row.id, val)}
                        placeholder="Standards..."
                    />
                </div>
            )
        },
        {
            header: 'Evidence',
            width: '18%',
            render: row => (
                <div style={{ width: '100%', minWidth: 0, maxWidth: '100%', boxSizing: 'border-box' }}>
                    <MultiSelect
                        options={evidenceOptions}
                        value={row.evidence_documents.map(e => ({
                            value: e.id,
                            label: evidenceOptions.find(o => o.value === e.id)?.label || e.tdd_number
                        }))}
                        onChange={val => updateRowEvidence(row.id, val)}
                        placeholder="Evidence..."
                    />
                </div>
            )
        },
        {
            header: 'Notes',
            width: '110px',
            render: row => (
                <textarea
                    value={row.notes || ''}
                    maxLength={5000} // Fix 2.4
                    onChange={e => updateRow(row.id, 'notes', e.target.value)}
                    style={{ width: '100%', minHeight: '42px', maxHeight: '72px', borderRadius: '4px', borderColor: theme.colors.border }}
                />
            )
        }
    ];

    return (
        <div className="etd-editor" style={{ padding: '1rem', maxWidth: '100%', minWidth: 0 }}>
            <div className="etd-editor-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px', gap: '16px', flexWrap: 'wrap' }}>
                <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '15px', flexWrap: 'wrap' }}>
                        <h1 style={{ margin: 0, minWidth: 0 }}>eTD Editor - {device?.name || `Device ${id}`}</h1>
                        {/* Auto-save Indicator */}
                        <div style={{
                            fontSize: '0.85rem',
                            padding: '4px 10px',
                            borderRadius: '12px',
                            backgroundColor: saveError ? 'rgba(255,0,0,0.1)' : (isSaving ? 'rgba(255,255,255,0.1)' : 'rgba(0,255,0,0.1)'),
                            color: saveError ? '#ff6b6b' : (isSaving ? '#aaa' : '#51cf66'),
                            border: `1px solid ${saveError ? '#ff6b6b44' : (isSaving ? '#aaa44' : '#51cf6644')}`,
                            display: 'flex',
                            alignItems: 'center',
                            gap: '5px'
                        }}>
                            {isSaving && <span className="spinner" style={{ width: '10px', height: '10px', border: '2px solid #aaa', borderTopColor: 'transparent', borderRadius: '50%', display: 'inline-block', animation: 'spin 1s linear infinite' }}></span>}
                            <span>
                                {saveError ? `Error: ${saveError}` : (isSaving ? 'Saving...' : (lastSaved ? `Saved at ${lastSaved.toLocaleTimeString()}` : 'No unsaved changes'))}
                            </span>
                        </div>
                    </div>
                    <div style={{ display: 'flex', gap: '20px', marginTop: '10px' }}>
                        <div>
                            <label style={{ fontSize: '0.8rem', color: '#aaa', display: 'block' }}>Part/Model Code</label>
                            <input
                                value={device?.model_code || ''}
                                onChange={e => updateDeviceMeta('model_code', e.target.value)}
                                placeholder="e.g. PRD000031"
                                style={{ padding: '4px 8px', borderRadius: '4px', border: `1px solid ${theme.colors.border}`, background: theme.colors.background, color: 'white' }}
                            />
                        </div>
                        <div>
                            <label style={{ fontSize: '0.8rem', color: '#aaa', display: 'block' }}>Document Number</label>
                            <input
                                value={device?.document_number || ''}
                                onChange={e => updateDeviceMeta('document_number', e.target.value)}
                                placeholder="e.g. TDD001572"
                                style={{ padding: '4px 8px', borderRadius: '4px', border: `1px solid ${theme.colors.border}`, background: theme.colors.background, color: 'white' }}
                            />
                        </div>
                    </div>
                    <div style={{ marginTop: '15px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        <div>
                            <label style={{ fontSize: '0.8rem', color: '#aaa', display: 'block' }}>Purpose of the document</label>
                            <textarea
                                value={device?.purpose || ''}
                                onChange={e => updateDeviceMeta('purpose', e.target.value)}
                                placeholder="Describe the purpose of this document..."
                                style={{ width: '100%', minHeight: '60px', padding: '8px', borderRadius: '4px', border: `1px solid ${theme.colors.border}`, background: theme.colors.background, color: 'white', resize: 'vertical' }}
                            />
                        </div>
                        <div>
                            <label style={{ fontSize: '0.8rem', color: '#aaa', display: 'block' }}>Identification of the product</label>
                            <textarea
                                value={device?.product_description || ''}
                                onChange={e => updateDeviceMeta('product_description', e.target.value)}
                                placeholder="Insert description of the product..."
                                style={{ width: '100%', minHeight: '60px', padding: '8px', borderRadius: '4px', border: `1px solid ${theme.colors.border}`, background: theme.colors.background, color: 'white', resize: 'vertical' }}
                            />
                        </div>
                    </div>
                </div>
                {/* button to download the pdf report */}
                <button
                    onClick={handleExportPdf}
                    disabled={isExporting} // Fix 2.6
                    style={{
                        padding: '10px 20px',
                        backgroundColor: isExporting ? theme.colors.border : theme.colors.primary,
                        color: isExporting ? '#aaa' : 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: isExporting ? 'not-allowed' : 'pointer'
                    }}
                >
                    {isExporting ? 'Exporting...' : 'Export PDF'}
                </button>
            </div>

            <div style={{ marginBottom: '20px', display: 'flex', gap: '10px', overflowX: 'auto', paddingBottom: '10px', borderBottom: `1px solid ${theme.colors.border}` }}>
                {allChapters.map((ch, idx) => {
                    const chapterTitles = {
                        "Chapter I": "General requirements",
                        "Chapter II": "Requirements regarding design and manufacture",
                        "Chapter III": "Information supplied with the device"
                    };
                    const title = chapterTitles[ch] || "";

                    return (
                        <button
                            key={idx}
                            onClick={() => navigate(`/devices/${id}/etd?chapter=${ch}`)}
                            title={title}
                            style={{
                                padding: '10px 20px',
                                backgroundColor: selectedChapter === ch ? theme.colors.primary : 'rgba(255,255,255,0.05)',
                                color: selectedChapter === ch ? 'white' : '#aaa',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                fontSize: '0.9rem',
                                fontWeight: selectedChapter === ch ? 'bold' : 'normal',
                                transition: 'all 0.2s',
                                whiteSpace: 'nowrap',
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'flex-start',
                                minWidth: '150px'
                            }}
                        >
                            <span style={{ fontSize: '0.8rem', opacity: selectedChapter === ch ? 1 : 0.7 }}>{ch}</span>
                            {title && <span style={{ fontSize: '0.7rem', opacity: selectedChapter === ch ? 1 : 0.6, marginTop: '2px' }}>{title}</span>}
                        </button>
                    );
                })}
            </div>

            <div className="etd-editor-toolbar" style={{ marginBottom: '20px', padding: '15px', background: theme.colors.surface, borderRadius: '8px', display: 'flex', gap: '20px', alignItems: 'center', flexWrap: 'wrap' }}>
                <input
                    type="text"
                    placeholder="Search requirements..."
                    value={filterText}
                    onChange={e => setFilterText(e.target.value)}
                    style={{ padding: '8px', width: 'min(300px, 100%)', maxWidth: '100%', borderRadius: '4px', border: `1px solid ${theme.colors.border}`, backgroundColor: theme.colors.background, color: theme.colors.text }}
                />
                <label style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <input
                        type="checkbox"
                        checked={hideNotApplicable}
                        onChange={e => setHideNotApplicable(e.target.checked)}
                    />
                    Hide Not Applicable
                </label>
            </div>

            {loading ? <p>Loading...</p> : <DataTable className="etd-table" columns={columns} data={filteredRows} />}
        </div>
    );
};

const ExpandableText = ({ text, mappingCount, tooltipText }) => {
    const [expanded, setExpanded] = React.useState(false);
    const safeText = text || '';
    const isLongText = safeText.length > 280;

    return (
        <div style={{
            width: '100%',
            maxWidth: '100%',
            overflow: 'hidden',
            wordBreak: 'break-word',
            overflowWrap: 'anywhere'
        }}>
            <div
                className="etd-requirement-text"
                style={{
                    fontSize: '0.9em',
                    color: '#eee',
                    marginBottom: '4px',
                    lineHeight: '1.45',
                    whiteSpace: 'normal',
                    overflow: 'hidden',
                    wordBreak: 'break-word',
                    overflowWrap: 'anywhere'
                }}
            >
                {expanded ? safeText : (isLongText ? safeText.substring(0, 280) + '...' : safeText)}
                {isLongText && (
                    <span
                        onClick={() => setExpanded(!expanded)}
                        style={{
                            color: theme.colors.primary,
                            cursor: 'pointer',
                            marginLeft: '5px',
                            fontWeight: 'bold',
                            fontSize: '0.8em'
                        }}
                    >
                        {expanded ? ' (Show Less)' : ' (Show More)'}
                    </span>
                )}
            </div>
            {mappingCount > 0 && (
                <div
                    title={tooltipText}
                    style={{
                        display: 'inline-block',
                        fontSize: '0.65rem',
                        color: theme.colors.primary,
                        cursor: 'help',
                        padding: '2px 8px',
                        background: 'rgba(52, 152, 219, 0.12)',
                        borderRadius: '12px',
                        border: `1px solid ${theme.colors.primary}44`,
                        fontWeight: 'bold',
                        marginTop: '4px'
                    }}
                >
                    💡 Standards Mapping Available ({mappingCount})
                </div>
            )}
        </div>
    );
};

// Add global styles for the spinner if not already present
if (typeof document !== 'undefined' && !document.getElementById('etd-spinner-style')) {
    const style = document.createElement('style');
    style.id = 'etd-spinner-style'; // Fix 9.2: Guard against duplicate injection
    style.textContent = `
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .etd-table td { overflow: hidden !important; max-width: 0 !important; }
        .etd-requirement-text { word-break: break-word !important; overflow-wrap: anywhere !important; white-space: normal !important; }
    `;
    document.head.appendChild(style);
}

export default EtdEditor;
