import React from 'react';
import Select from 'react-select';
import { theme } from '../theme';

const MultiSelect = (props) => {
    const customStyles = {
        container: (provided) => ({
            ...provided,
            width: '100%',
            minWidth: 0,
            maxWidth: '100%',
        }),
        control: (provided) => ({
            ...provided,
            backgroundColor: theme.colors.surface,
            borderColor: theme.colors.border,
            color: theme.colors.text,
            minHeight: '34px',
            minWidth: 0,
            width: '100%',
            fontSize: '12px',
            boxSizing: 'border-box',
        }),
        menu: (provided) => ({
            ...provided,
            backgroundColor: theme.colors.surface,
            fontSize: '12px',
        }),
        option: (provided, state) => ({
            ...provided,
            backgroundColor: state.isFocused ? theme.colors.hover : theme.colors.surface,
            color: theme.colors.text,
            fontSize: '12px',
            padding: '6px 10px',
        }),
        singleValue: (provided) => ({
            ...provided,
            color: theme.colors.text,
        }),
        menuPortal: (provided) => ({
            ...provided,
            zIndex: 9999,
        }),
        multiValue: (provided) => ({
            ...provided,
            backgroundColor: theme.colors.primary,
            maxWidth: '100%',
        }),
        multiValueLabel: (provided) => ({
            ...provided,
            color: 'white',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            maxWidth: '140px',
            fontSize: '11px',
            padding: '2px 4px',
        }),
        valueContainer: (provided) => ({
            ...provided,
            maxHeight: '52px',
            overflowY: 'auto',
            padding: '2px 6px',
        }),
        indicatorsContainer: (provided) => ({
            ...provided,
            height: '32px',
        }),
    };

    return (
        <Select
            {...props}
            isMulti
            styles={customStyles}
            menuPortalTarget={typeof document !== 'undefined' ? document.body : null}
            menuPosition="fixed"
        />
    );
};

export default MultiSelect;
