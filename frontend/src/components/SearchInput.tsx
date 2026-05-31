interface Props {
  value: string;
  onChange: (value: string) => void;
  onRefresh: () => void;
}

export function SearchInput({ value, onChange, onRefresh }: Props) {
  const canRefresh = value.length >= 3;

  return (
    <div className="search-wrap">
      <div className="search-row">
        <input
          className="search-input"
          type="text"
          placeholder="Search station"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          autoFocus
        />
        <div className="tooltip-wrap">
          <button
            className="refresh-btn"
            onClick={onRefresh}
            disabled={!canRefresh}
            aria-label="Refresh departures"
          >
            ↻
          </button>
          <span className="tooltip">
            Refresh departures for the current search
          </span>
        </div>
      </div>
      {value.length > 0 && value.length < 3 && (
        <p className="search-hint">Keep typing — need at least 3 characters</p>
      )}
    </div>
  );
}
