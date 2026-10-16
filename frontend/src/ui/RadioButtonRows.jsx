
import "./RadioButtonRows.css";

export default function RadioButtonRows({ rows = [], value = {}, onChange }) {
    return (
        <div className="rbr">
            {rows.map((row) => {
                const groupName = `rbr-${row.key}`;
                const labelId = `${groupName}-label`;

                return (
                    <div
                        key={row.key}
                        className="rbr-row"
                        role="radiogroup"
                        aria-labelledby={labelId}
                    >
                        <div className="rbr-label" id={labelId}>
                            {row.label}
                        </div>

                        <div className="rbr-options">
                            {row.options.map((opt) => {
                                const id = `${groupName}-${String(opt.value)}`;
                                const isChecked = value?.[row.key] === opt.value;

                                return (
                                    <label key={id} className="rbr-radio" htmlFor={id}>
                                        <input
                                            id={id}
                                            type="radio"
                                            name={groupName}
                                            value={String(opt.value)}
                                            checked={isChecked}
                                            onChange={() => onChange?.(row.key, opt.value)}
                                        />
                                        <span className="rbr-radio__custom" aria-hidden="true" />
                                        <span className="rbr-radio__label">{opt.label}</span>
                                    </label>
                                );
                            })}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
