import React, { useState, useEffect } from 'react';
import api from '../communication/axios';
import styled from 'styled-components';
import DataTable from '../ui/DataTable';
import { useDatabaseViewerPresenter } from './useDatabaseViewerPresenter';

const ViewerContainer = styled.div`
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
`;

const Header = styled.div`
  margin-bottom: 20px;
`;

const Title = styled.h1`
  color: ${props => props.theme.colors.text};
  margin: 0 0 10px 0;
`;

const Subtitle = styled.p`
  color: ${props => props.theme.colors.textSecondary};
  margin: 0;
`;

const TabsContainer = styled.div`
  display: flex;
  margin-bottom: 20px;
  border-bottom: 1px solid ${props => props.theme.colors.border};
`;

const Tab = styled.div`
  padding: 10px 20px;
  cursor: pointer;
  color: ${props => props.active ? props.theme.colors.primary : props.theme.colors.textSecondary};
  border-bottom: 2px solid ${props => props.active ? props.theme.colors.primary : 'transparent'};
  font-weight: ${props => props.active ? 'bold' : 'normal'};
  transition: all 0.2s;

  &:hover {
    color: ${props => props.theme.colors.primary};
  }
`;

const ContentContainer = styled.div`
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

const SearchInput = styled.input`
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid ${props => props.theme.colors.border};
  background: ${props => props.theme.colors.surface};
  color: ${props => props.theme.colors.text};
  margin-bottom: 15px;
  width: 300px;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }
`;

const ExpandableText = ({ text }) => {
    const [expanded, setExpanded] = useState(false);
    const safeText = text || '';
    const isLongText = safeText.length > 100;

    return (
        <div>
            {expanded ? safeText : (isLongText ? safeText.substring(0, 100) + '...' : safeText)}
            {isLongText && (
                <span
                    onClick={() => setExpanded(!expanded)}
                    style={{
                        color: '#3498db',
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
    );
};

const DatabaseViewer = () => {
    const {
        activeTab,
        setActiveTab,
        loading,
        filterText,
        setFilterText,
        editingItem,
        setEditingItem,
        isAdmin,
        fileInputRef,
        scanningStandardIds,
        handleUploadClick,
        handleFileChange,
        handleEditClick,
        handleCreateClick,
        handleDeleteClick,
        handleSave,
        filteredData,
        alertMessage,
        alertType,
        clearAlert,
        mineruReady,
    } = useDatabaseViewerPresenter();

    const getColumns = () => {
        const columns = [];
        switch (activeTab) {
            case 'gspr':
                columns.push(
                    {
                        header: 'Ref',
                        accessor: 'full_reference',
                        width: '100px',
                        render: row => (
                            <div style={{
                                paddingLeft: row.parent_id ? '20px' : '0px',
                                fontWeight: row.parent_id ? 'normal' : 'bold',
                                opacity: row.parent_id ? 0.8 : 1
                            }}>
                                {row.full_reference}
                            </div>
                        )
                    },
                    { header: 'Chapter', accessor: 'chapter', width: '100px' },
                    { header: 'Description', accessor: 'text', render: row => <ExpandableText text={row.text} /> }
                    // Linked Standards column hidden for now — uncomment to restore
                    // {
                    //     header: 'Linked Standards',
                    //     accessor: 'standard_mappings',
                    //     render: row => {
                    //         const uniqueStandards = [];
                    //         const seenStandardIds = new Set();
                    //
                    //         if (row.standard_mappings) {
                    //             row.standard_mappings.forEach(m => {
                    //                 if (m.standard && !seenStandardIds.has(m.standard.id)) {
                    //                     seenStandardIds.add(m.standard.id);
                    //                     uniqueStandards.push(m);
                    //                 }
                    //             });
                    //         }
                    //
                    //         return (
                    //             <div>
                    //                 {uniqueStandards.length > 0 ? (
                    //                     uniqueStandards.map(m => (
                    //                         <span key={m.id} style={{ display: 'block', fontSize: '0.85em', marginBottom: '4px' }}>
                    //                             <strong>{m.standard?.code}</strong>
                    //                         </span>
                    //                     ))
                    //                 ) : (
                    //                     <span style={{ color: '#999', fontStyle: 'italic' }}>None</span>
                    //                 )}
                    //             </div>
                    //         );
                    //     }
                    // }
                );
                break;
            case 'standards':
                columns.push(
                    { header: 'Code', accessor: 'code', width: '150px' },
                    { header: 'Title', accessor: 'title' },
                    { header: 'Version', accessor: 'version', width: '100px' },
                    { header: 'Harmonised', accessor: 'harmonised', render: row => row.harmonised ? 'Yes' : 'No', width: '100px' },
                    {
                        header: 'Scan Status',
                        accessor: 'parse_status',
                        width: '130px',
                        render: row => {
                            const status = row.parse_status;
                            const isScanning =
                                scanningStandardIds.includes(row.id) ||
                                status === 'processing' ||
                                status === 'pending';
                            if (isScanning) {
                                return <span style={{ color: '#f39c12' }}>Processing…</span>;
                            }
                            if (status === 'failed') {
                                return (
                                    <span style={{ color: '#e74c3c' }} title={row.parse_error || 'Unknown error'}>
                                        Failed
                                    </span>
                                );
                            }
                            if (status === 'completed' || status === 'parsed') {
                                return <span style={{ color: '#2ecc71' }}>Scanned</span>;
                            }
                            // none / null / undefined — never scanned
                            return <span style={{ color: '#95a5a6' }}>Not scanned</span>;
                        }
                    }
                );
                break;
            case 'evidence':
                columns.push(
                    { header: 'TDD #', accessor: 'tdd_number', width: '120px' },
                    { header: 'Title', accessor: 'title' },
                    { header: 'Type', accessor: 'type', width: '150px' },
                    { header: 'Owner', accessor: 'owner', width: '120px' }
                );
                break;
        }

        if (isAdmin) {
            columns.push({
                header: 'Actions',
                accessor: 'actions',
                width: '180px', // Increased width
                render: (row) => (
                    <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
                        <ActionButton
                            color="#3498db"
                            onClick={() => handleEditClick(row)}
                            title="Edit"
                        >
                            Edit
                        </ActionButton>
                        <ActionButton
                            color="#e74c3c"
                            onClick={() => handleDeleteClick(row)}
                            title="Delete"
                        >
                            Delete
                        </ActionButton>
                        {activeTab === 'standards' && mineruReady && (
                            <ActionButton
                                color="#f39c12"
                                onClick={() => handleUploadClick(row.id)}
                                title="Upload PDF & Extract GSPR"
                            >
                                📄 Upload
                            </ActionButton>
                        )}
                        {activeTab === 'evidence' && (
                            <ActionButton
                                color="#f39c12"
                                onClick={() => handleUploadClick(row.id)}
                                title="Upload PDF"
                            >
                                📄 Upload
                            </ActionButton>
                        )}
                    </div>
                )
            });
        }
        return columns;
    };

    return (
        <ViewerContainer>
            <Header>
                <Title>Database Viewer</Title>
                <Subtitle>Inspect raw data for GSPR, Standards, and Evidence</Subtitle>
            </Header>

            <TabsContainer>
                <Tab active={activeTab === 'gspr'} onClick={() => setActiveTab('gspr')}>GSPR Requirements</Tab>
                <Tab active={activeTab === 'standards'} onClick={() => setActiveTab('standards')}>Standards</Tab>
                <Tab active={activeTab === 'evidence'} onClick={() => setActiveTab('evidence')}>Evidence</Tab>
            </TabsContainer>

            {alertMessage && (
                <div style={{
                    padding: '10px 15px',
                    marginBottom: '15px',
                    borderRadius: '4px',
                    backgroundColor: alertType === 'error' ? 'rgba(231, 76, 60, 0.1)' : alertType === 'success' ? 'rgba(46, 204, 113, 0.1)' : 'rgba(52, 152, 219, 0.1)',
                    border: `1px solid ${alertType === 'error' ? '#e74c3c' : alertType === 'success' ? '#2ecc71' : '#3498db'}`,
                    color: alertType === 'error' ? '#e74c3c' : alertType === 'success' ? '#2ecc71' : '#3498db',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}>
                    <span>{alertMessage}</span>
                    <button onClick={clearAlert} style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', fontSize: '1.2rem' }}>&times;</button>
                </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                <SearchInput
                    type="text"
                    placeholder="Search..."
                    value={filterText}
                    onChange={e => setFilterText(e.target.value)}
                    style={{ marginBottom: 0 }}
                />

                {isAdmin && (
                    <Button onClick={handleCreateClick} style={{ backgroundColor: '#2ecc71' }}>
                        + Add Item
                    </Button>
                )}
            </div>

            <input
                type="file"
                ref={fileInputRef}
                style={{ display: 'none' }}
                accept=".pdf"
                onChange={handleFileChange}
            />

            <ContentContainer>
                {loading ? (
                    <p>Loading...</p>
                ) : (
                    <DataTable
                        columns={getColumns()}
                        data={filteredData}
                    />
                )}
            </ContentContainer>

            {editingItem && (
                <EditModal
                    item={editingItem}
                    type={activeTab}
                    onClose={() => setEditingItem(null)}
                    onSave={handleSave}
                />
            )}
        </ViewerContainer>
    );
};

const ActionButton = styled.button`
    padding: 5px 10px;
    background-color: ${props => props.color};
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9em;
    &:hover {
        opacity: 0.9;
    }
`;

const EditModal = ({ item, type, onClose, onSave }) => {
    // If item is empty object, it's a create action
    const isCreate = !item.id;
    const [formData, setFormData] = useState({ ...item });
    const [allStandards, setAllStandards] = useState([]);
    const [loadingStandards, setLoadingStandards] = useState(false);
    const [saveError, setSaveError] = useState('');
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        if (type === 'gspr') {
            fetchStandards();
            // Initialize standard_ids from existing mappings if any
            if (item.standard_mappings) {
                setFormData(prev => ({
                    ...prev,
                    standard_ids: item.standard_mappings.map(m => m.standard_id)
                }));
            }
        }
    }, [type, item]);

    const fetchStandards = async () => {
        setLoadingStandards(true);
        try {
            const response = await api.get('/standards');
            setAllStandards(response.data);
        } catch (error) {
            console.error("Error fetching standards:", error);
        } finally {
            setLoadingStandards(false);
        }
    };

    const handleChange = (e) => {
        const { name, value, type: inputType, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: inputType === 'checkbox' ? checked : value
        }));
    };

    const handleStandardToggle = (standardId) => {
        const currentIds = formData.standard_ids || [];
        let newIds;
        if (currentIds.includes(standardId)) {
            newIds = currentIds.filter(id => id !== standardId);
        } else {
            newIds = [...currentIds, standardId];
        }
        setFormData(prev => ({ ...prev, standard_ids: newIds }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaveError('');
        setSaving(true);
        try {
            const result = await onSave(formData);
            if (result && result !== true) {
                setSaveError(result);
            }
        } finally {
            setSaving(false);
        }
    };

    const renderFields = () => {
        switch (type) {
            case 'gspr':
                return (
                    <>
                        <Label>Chapter</Label>
                        <Input name="chapter" value={formData.chapter || ''} onChange={handleChange} />
                        <Label>Section</Label>
                        <Input name="section" value={formData.section || ''} onChange={handleChange} />
                        <Label>Full Reference</Label>
                        <Input name="full_reference" value={formData.full_reference || ''} onChange={handleChange} />
                        <Label>Text</Label>
                        <TextArea name="text" value={formData.text || ''} onChange={handleChange} rows={5} />

                        <Label>Linked Standards</Label>
                        <div style={{
                            maxHeight: '150px',
                            overflowY: 'auto',
                            border: '1px solid #444',
                            padding: '10px',
                            borderRadius: '4px',
                            background: '#1a1a1a'
                        }}>
                            {loadingStandards ? (
                                <span>Loading standards...</span>
                            ) : allStandards.length === 0 ? (
                                <span style={{ color: '#666' }}>No standards available</span>
                            ) : (
                                allStandards.map(std => (
                                    <div key={std.id} style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
                                        <input
                                            type="checkbox"
                                            id={`std-${std.id}`}
                                            checked={(formData.standard_ids || []).includes(std.id)}
                                            onChange={() => handleStandardToggle(std.id)}
                                            style={{ marginRight: '10px' }}
                                        />
                                        <label htmlFor={`std-${std.id}`} style={{ cursor: 'pointer', fontSize: '0.9em' }}>
                                            <strong>{std.code}</strong>: {std.title}
                                        </label>
                                    </div>
                                ))
                            )}
                        </div>
                    </>
                );
            case 'standards':
                return (
                    <>
                        <Label>Code</Label>
                        <Input name="code" value={formData.code || ''} onChange={handleChange} />
                        <Label>Title</Label>
                        <Input name="title" value={formData.title || ''} onChange={handleChange} />
                        <Label>Version</Label>
                        <Input name="version" value={formData.version || ''} onChange={handleChange} />
                        <Label>
                            <input
                                type="checkbox"
                                name="harmonised"
                                checked={formData.harmonised || false}
                                onChange={handleChange}
                            /> Harmonised
                        </Label>
                        <Label>Status</Label>
                        <Input name="status" value={formData.status || ''} onChange={handleChange} />
                    </>
                );
            case 'evidence':
                return (
                    <>
                        <Label>TDD Number</Label>
                        <Input name="tdd_number" value={formData.tdd_number || ''} onChange={handleChange} />
                        <Label>Title</Label>
                        <Input name="title" value={formData.title || ''} onChange={handleChange} />
                        <Label>Version</Label>
                        <Input name="version" value={formData.version || ''} onChange={handleChange} />
                        <Label>Type</Label>
                        <Input name="type" value={formData.type || ''} onChange={handleChange} />
                        <Label>Owner</Label>
                        <Input name="owner" value={formData.owner || ''} onChange={handleChange} />
                    </>
                );
            default: return null;
        }
    };

    return (
        <Overlay>
            <Modal>
                <ModalHeader>
                    <h3>{isCreate ? 'Add New Item' : 'Edit Item'}</h3>
                    <CloseButton onClick={onClose}>&times;</CloseButton>
                </ModalHeader>
                <ModalBody>
                    <form onSubmit={handleSubmit}>
                        {saveError && (
                            <div style={{
                                padding: '10px 12px',
                                marginBottom: '12px',
                                borderRadius: '4px',
                                backgroundColor: 'rgba(231, 76, 60, 0.15)',
                                border: '1px solid #e74c3c',
                                color: '#e74c3c',
                                fontSize: '14px',
                                lineHeight: 1.4
                            }}>
                                {saveError}
                            </div>
                        )}
                        {renderFields()}
                        <div style={{ marginTop: '20px', textAlign: 'right' }}>
                            <Button type="button" onClick={onClose} style={{ marginRight: '10px', background: '#ccc' }}>Cancel</Button>
                            <Button type="submit" disabled={saving}>{saving ? 'Saving...' : (isCreate ? 'Create' : 'Save')}</Button>
                        </div>
                    </form>
                </ModalBody>
            </Modal>
        </Overlay>
    );
};

// Styled Components for Modal
const Overlay = styled.div`
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.7);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
`;

const Modal = styled.div`
    background: ${props => props.theme.colors.surface};
    color: ${props => props.theme.colors.text};
    padding: 20px;
    border-radius: 8px;
    width: 600px;
    max-width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    border: 1px solid ${props => props.theme.colors.border};
`;

const ModalHeader = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    border-bottom: 1px solid ${props => props.theme.colors.border};
    padding-bottom: 10px;
`;

const ModalBody = styled.div``;

const CloseButton = styled.button`
    background: none;
    border: none;
    color: ${props => props.theme.colors.text};
    font-size: 1.5rem;
    cursor: pointer;
`;

const Label = styled.label`
    display: block;
    margin-bottom: 5px;
    margin-top: 15px;
    font-weight: bold;
    color: ${props => props.theme.colors.textSecondary};
`;

const Input = styled.input`
    width: 100%;
    padding: 8px;
    border-radius: 4px;
    border: 1px solid ${props => props.theme.colors.border};
    background: ${props => props.theme.colors.background};
    color: ${props => props.theme.colors.text};
`;

const TextArea = styled.textarea`
    width: 100%;
    padding: 8px;
    border-radius: 4px;
    border: 1px solid ${props => props.theme.colors.border};
    background: ${props => props.theme.colors.background};
    color: ${props => props.theme.colors.text};
    resize: vertical;
`;

const Button = styled.button`
    padding: 10px 20px;
    background: ${props => props.theme.colors.primary};
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
`;

export default DatabaseViewer;
