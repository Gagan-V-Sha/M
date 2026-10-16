import React from "react";
import "./TitleWithHelp.css";

export default function TitleWithHelp({ title, helpUrl, className = "" }) {
    const isLink = !!helpUrl;

    const HelpButton = isLink ? "a" : "button";
    const commonProps = isLink
        ? {
            href: helpUrl,
            target: "_blank",
            rel: "noopener noreferrer",
        }
        : {
            type: "button",
        };

    return (
        <div className={`twh-header ${className}`}>
            <h3 className="twh-title">{title}</h3>
            <HelpButton
                className="twh-help"
                aria-label={`${title} � more info ${isLink ? "(opens in a new tab)" : ""}`}
                title="More info"
                href={helpUrl}
                {...commonProps}
            >
                {/* Info icon (SVG) */}
                <svg
                    className="twh-help__icon"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                    focusable="false"
                >
                    <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" strokeWidth="2" />
                    <line x1="12" y1="10" x2="12" y2="17" stroke="currentColor" strokeWidth="2" />
                    <circle cx="12" cy="7" r="1.5" fill="currentColor" />
                </svg>
            </HelpButton>
        </div>
    );
}
