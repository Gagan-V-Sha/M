import React from "react";

function ruleRow(row, featureState, rowState) {
    const visible = row.isVisible ? !!row.isVisible(featureState, rowState) : true;
    const enabled = row.isEnabled ? !!row.isEnabled(featureState, rowState) : true;
    const applicableComputed = row.applicable ? row.applicable(featureState, rowState): true;
    const reasoningComputed = row.reasoning ? row.reasoning(featureState, rowState) : "";
    const riskClass = row.riskClass ? row.riskClass(featureState, rowState) : "";
    return { visible, enabled, applicableComputed, reasoningComputed, riskClass };
}

export default function RuleTable({ featureState, rows, rowState, onRowChange }) {
    return (
        <div className="cls-table">
            <div className="cls-thead">
                <div className="cls-th cls-col-nr">Nr. Rule</div>
                <div className="cls-th cls-col-text">Rule Text</div>
                <div className="cls-th cls-col-app">Applicable</div>
                <div className="cls-th cls-col-reason">Reasoning</div>
                <div className="cls-th cls-col-risk">Resulting Risk Class</div>
            </div>

            <div className="cls-tbody">
                {rows.map((row) => {
                    const { visible, enabled, applicableComputed, reasoningComputed, riskClass } =
                        ruleRow(row, featureState, rowState);
                    if (!visible) return null;
                    const rowLocal = rowState[row.id] || {};
                    const applicableValue = rowLocal.applicable ?? (applicableComputed === true ? true : false);
                    const disabledApplicable = applicableComputed === "n/a" || !enabled;
                    return (
                        <div key={row.id} className={`cls-tr ${!enabled ? "is-disabled" : ""}`}>
                            <div className="cls-td cls-col-nr">{row.nr}. {row.rule}</div>
                            <div className="cls-td cls-col-text">{row.text}</div>
                            <div className="cls-td cls-col-app">
                                {applicableComputed === "n/a" ? (<span className="cls-badge">n/a</span>
                                ) : (
                                        <div className="cls-radio-group" role="radiogroup" aria-label={`Applicable for ${row.rule}`}>

                                        <label className={`cls-radio-sm ${disabledApplicable ? "is-disabled" : ""}`}>
                                            <input
                                                type="radio"
                                                name={`app-${row.id}`}
                                                checked={applicableValue === true}
                                                disabled={disabledApplicable}
                                                onChange={() => onRowChange?.(row.id, { applicable: true })}
                                            />
                                            <span>Yes</span>
                                            </label>

                                        <label className={`cls-radio-sm ${disabledApplicable ? "is-disabled" : ""}`}>
                                            <input
                                                type="radio"
                                                name={`app-${row.id}`}
                                                checked={applicableValue === false}
                                                disabled={disabledApplicable}
                                                onChange={() => onRowChange?.(row.id, { applicable: false })}
                                            />
                                            <span>No</span>
                                        </label>
                                    </div>
                                )}
                            </div>

                            <div className="cls-td cls-col-reason">
                                <input
                                    className="cls-input"
                                    type="text"
                                    placeholder={reasoningComputed || "Enter Reasoning here"}
                                    value={rowLocal.reasoning ?? ""}
                                    onChange={(e) => onRowChange?.(row.id, { reasoning: e.target.value })}
                                    disabled={!enabled}
                                />
                            </div>

                            <div className="cls-td cls-col-risk">{riskClass ?? "�"}</div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
