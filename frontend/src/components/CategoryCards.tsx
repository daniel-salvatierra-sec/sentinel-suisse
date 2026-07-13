import type { ListingType } from "../api";
import type { Messages } from "../i18n";

type Props = {
  t: Messages;
  active: ListingType;
  onSelect: (type: ListingType) => void;
};

export function CategoryCards({ t, active, onSelect }: Props) {
  return (
    <div className="category-grid">
      <button
        type="button"
        className={`category-card housing${active === "housing" ? " selected" : ""}`}
        onClick={() => onSelect("housing")}
        aria-pressed={active === "housing"}
      >
        <strong>{t.housing}</strong>
        <span>{t.housingDesc}</span>
      </button>
      <button
        type="button"
        className={`category-card job${active === "job" ? " selected" : ""}`}
        onClick={() => onSelect("job")}
        aria-pressed={active === "job"}
      >
        <strong>{t.job}</strong>
        <span>{t.jobDesc}</span>
      </button>
    </div>
  );
}
