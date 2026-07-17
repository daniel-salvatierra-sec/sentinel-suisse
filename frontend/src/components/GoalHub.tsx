import type { ListingType } from "../api";
import type { Messages } from "../i18n";

type Props = {
  t: Messages;
  active: ListingType;
  onSelect: (type: ListingType) => void;
};

/** Vertical Home / Work hub — first viewport composition for LinkSwiss. */
export function GoalHub({ t, active, onSelect }: Props) {
  return (
    <section className="goal-hub" aria-label={t.goalHubLabel}>
      <button
        type="button"
        className={`goal-zone home${active === "housing" ? " active" : ""}`}
        onClick={() => onSelect("housing")}
        aria-pressed={active === "housing"}
      >
        <span className="goal-zone-kicker">{t.goalHomeKicker}</span>
        <strong className="goal-zone-title">{t.goalHome}</strong>
        <span className="goal-zone-desc">{t.housingDesc}</span>
      </button>
      <button
        type="button"
        className={`goal-zone work${active === "job" ? " active" : ""}`}
        onClick={() => onSelect("job")}
        aria-pressed={active === "job"}
      >
        <span className="goal-zone-kicker">{t.goalWorkKicker}</span>
        <strong className="goal-zone-title">{t.goalWork}</strong>
        <span className="goal-zone-desc">{t.jobDesc}</span>
        <span className="goal-zone-hint">{t.goalWorkHint}</span>
      </button>
    </section>
  );
}
