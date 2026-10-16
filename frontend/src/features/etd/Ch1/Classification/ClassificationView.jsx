import React from "react";
import "./Classification.css"
import RuleTable from "./RuleTable"
import { rows } from "./ClassificationRadioData";
import TitleWithHelp from "../../../ui/TitleWithHelp";
import PrintButton from "../../../ui/PrintButton";
import RadioButtonRows from "../../../ui/RadioButtonRows";

/**
 * 
 * @param {any} ready: param 
 * @returns
 */
export default function ClassificationView({ready, value, onChange, className = "Classification", radioSetting, ruleRows, rowState, onRowChange }) {
    if (!ready) return <div style={{ color: "#e9e9e9" }}>Preparing Designation and Classification...</div>;
    return (

        <section className={`cls-container ${className}`} aria-label="Designation and Classification selection">
                <RadioButtonRows
                    rows={rows}
                    value={value}
                    onChange={onChange}
                />

            {/* This is the MDCG help Button This should be a reuse component*/ }
            <TitleWithHelp title="Classification Rules" helpUrl="https://health.ec.europa.eu/system/files/2021-10/mdcg_2021-24_en_0.pdf" />
            <div>
                <RuleTable
                    featureState={radioSetting}
                    rows={ruleRows}
                    rowState={rowState}
                    onRowChange={onRowChange }
                />
            <PrintButton/>
            </div>
        </section>
    );

}