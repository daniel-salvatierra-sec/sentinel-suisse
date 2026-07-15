import type { Messages } from "../i18n";

type Props = {
  t: Messages;
  visible: boolean;
  priceMin: string;
  priceMax: string;
  onPriceMinChange: (value: string) => void;
  onPriceMaxChange: (value: string) => void;
  onApply: () => void;
};

export function FilterBar({
  t,
  visible,
  priceMin,
  priceMax,
  onPriceMinChange,
  onPriceMaxChange,
  onApply,
}: Props) {
  if (!visible) return null;

  return (
    <form
      className="filter-bar"
      onSubmit={(event) => {
        event.preventDefault();
        onApply();
      }}
    >
      <p className="filter-bar-label">{t.filters}</p>
      <div className="filter-row">
        <label>
          {t.priceMin}
          <input
            type="number"
            min={0}
            inputMode="numeric"
            value={priceMin}
            onChange={(event) => onPriceMinChange(event.target.value)}
            placeholder="0"
          />
        </label>
        <label>
          {t.priceMax}
          <input
            type="number"
            min={0}
            inputMode="numeric"
            value={priceMax}
            onChange={(event) => onPriceMaxChange(event.target.value)}
            placeholder="5000"
          />
        </label>
        <button type="submit" className="secondary-btn">
          {t.applyFilters}
        </button>
      </div>
    </form>
  );
}
