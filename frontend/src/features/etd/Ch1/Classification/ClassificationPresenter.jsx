import ClassificationView from "./ClassificationView";
import {ruleRows } from "./RuleRows"
import React, { useEffect, useState, useCallback} from "react";

/**
 * ClassificationPresenter
 * This class handles the UI inputs of ClassidicationView
 * @param {any} featureContext
 * @returns ClassificationView
 */
export default function ClassificationPresenter({ featureContext }) {

    const [isReady, setReadiness] = useState({ ready: false, details: null });

    // rowState and Setter for the rows themself, full implementation tbd
    const [rowState, setRowState] = useState({});

    // State and Setter for the upper radioButtons
    const [radioSetting, setRadioSetting] = useState(() => ({
        deviceType: "medical",
        active: true,
        invasive: true,
        sterile: true,
        reprocessed: true
    }));


    /**
     * Handles radio button change
     */
    const handleChange = useCallback((key, value) => {
        setRadioSetting((prev) => {
            const next = { ...prev, [key]: value };
            setRadioSetting?.(next);
            return next;
        });
    }, [setRadioSetting]
    )

    /**
     * Loader of the view
     */
    useEffect(() => {
        let cancelled = false;
        const token = featureContext?.getGuard?.() ?? 0;
        (async () => {
            await new Promise((r) => setTimeout(r, 600));
            if (cancelled || featureContext?.isStale?.(token))
                return;
            setReadiness({ ready: true, details: { Ch1: "classification", ts: Date.now() } });
        })();

        return () => { cancelled = true; };
    }, [featureContext]);

    /**
    * Handle row changes ==> currently not effective
    */
    const handleRowChange = useCallback((rowId, patch) => {
        setRowState((prev) => ({
            ...prev,
            [rowId]: { ...(prev[rowId] || {}), ...patch },
        }));
    }, []);


    return (
        <>
            <ClassificationView
                ready={isReady.ready}
                details={isReady.details}
                value={radioSetting}
                onChange={handleChange}
                radioSetting={radioSetting}
                ruleRows={ruleRows}
                rowState={rowState}
                onRowChange={handleRowChange}
            />;
        </>
    );
}
