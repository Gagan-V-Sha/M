import React from 'react';
import { theme } from '../theme';

const DataTable = ({ columns, data, className = '' }) => {
    return (
        <div className="table-wrap" style={{ overflowX: 'auto', width: '100%', maxWidth: '100%' }}>
            <table
                className={`data-table ${className}`.trim()}
                style={{
                    width: '100%',
                    borderCollapse: 'separate',
                    borderSpacing: 0,
                    marginTop: '1rem',
                    tableLayout: 'fixed'
                }}
            >
                <colgroup>
                    {columns.map((col, idx) => (
                        <col key={idx} style={{ width: col.width }} />
                    ))}
                </colgroup>
                <thead>
                    <tr style={{ backgroundColor: theme.colors.tableHeader, color: theme.colors.tableHeaderText }}>
                        {columns.map((col, idx) => (
                            <th key={idx} style={{ padding: '10px', textAlign: 'left', borderBottom: `2px solid ${theme.colors.border}` }}>
                                {col.header}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {data.map((row, rIdx) => (
                        <tr key={rIdx} style={{ borderBottom: `1px solid ${theme.colors.border}` }}>
                            {columns.map((col, cIdx) => (
                                <td
                                    key={cIdx}
                                    style={{
                                        padding: '8px',
                                        verticalAlign: 'top',
                                        overflow: 'hidden',
                                        maxWidth: 0,
                                        width: col.width
                                    }}
                                >
                                    {col.render ? col.render(row) : row[col.accessor]}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default DataTable;
