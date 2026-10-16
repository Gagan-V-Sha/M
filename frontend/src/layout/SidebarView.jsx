
import React from "react";
import "./SidebarView.css";


export default function SidebarView({
    sections,
    currentSelection,
    openId,
    onToggleSection,
    onChange,
    onPrefetch,
    radioName = "sidebar-global-radio"
}) {

    return (
        <aside className="sb-container" aria-label="Sidebar filters">
            <div className="sb-header">Chapters</div>

            <nav className="sb-nav" aria-label="Filter categories">
                {sections.map((section) => {
                    const isOpen = openId === section.id;

                    return (
                        <div className="sb-section" key={section.id}>
                            <button
                                className={`sb-toggle ${isOpen ? "is-open" : ""}`}
                                onClick={() => onToggleSection(section.id)}
                                aria-expanded={isOpen}
                                aria-controls={`panel-${section.id}`}
                                id={`button-${section.id}`}
                                type="button"
                            >
                                <span className="sb-toggle__title">{section.title}</span>
                                <span className="sb-toggle__chevron" aria-hidden="true">
                                    {isOpen ? "▾" : "▸"}
                                </span>
                            </button>

                            <div
                                id={`panel-${section.id}`}
                                role="region"
                                aria-labelledby={`button-${section.id}`}
                                className={`sb-panel ${isOpen ? "open" : "closed"}`}
                            >
                                <fieldset className="sb-fieldset">
                                    <legend className="sr-only">{section.title}</legend>
                                    {section.options.map((opt) => { 
                                        const inputId = `${section.id}-${opt.id}`;
                                        const compoundKey = `${section.id}:${opt.id}`;
                                        const checked = currentSelection === compoundKey;
                                        return (
                                            <label className="sb-radio" htmlFor={inputId} key={opt.id} onMouseEnter={() => onPrefetch?.(compoundKey)}>
                                                <input
                                                    type="radio"
                                                    id={inputId}
                                                    name={radioName}
                                                    value={compoundKey}
                                                    checked={checked}
                                                    onChange={() => {
                                                        onChange?.(compoundKey)
                                                    }}
                                                />
                                                <span className="sb-radio__custom" aria-hidden="true" />
                                                <span className="sb-radio__label">{opt.label}</span>
                                            </label>
                                        );
                                    })}
                                </fieldset>
                            </div>
                        </div>
                    );
                })}
            </nav>
        </aside>
    );
}
``
