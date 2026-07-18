import type { ListingType } from "../api";
import type { Messages } from "../i18n";

type Props = {
  t: Messages;
  active: ListingType;
  onSelect: (type: ListingType) => void;
};

/** Vertical Home / Work hub — warm alpine composition for LinkSwiss. */
export function GoalHub({ t, active, onSelect }: Props) {
  return (
    <section className="goal-hub" aria-label={t.goalHubLabel}>
      <span className="goal-hub-dream" aria-hidden="true" />
      <button
        type="button"
        className={`goal-zone home${active === "housing" ? " active" : ""}`}
        onClick={() => onSelect("housing")}
        aria-pressed={active === "housing"}
      >
        <span className="goal-zone-art home-art" aria-hidden="true" />
        <span className="goal-zone-copy">
          <span className="goal-zone-kicker">{t.goalHomeKicker}</span>
          <strong className="goal-zone-title">{t.goalHome}</strong>
          <span className="goal-zone-desc">{t.housingDesc}</span>
        </span>
      </button>
      <button
        type="button"
        className={`goal-zone work${active === "job" ? " active" : ""}`}
        onClick={() => onSelect("job")}
        aria-pressed={active === "job"}
      >
        <span className="goal-zone-art work-art" aria-hidden="true" />
        <span className="goal-zone-copy">
          <span className="goal-zone-kicker">{t.goalWorkKicker}</span>
          <strong className="goal-zone-title">{t.goalWork}</strong>
          <span className="goal-zone-desc">{t.jobDesc}</span>
          <span className="goal-zone-hint">{t.goalWorkHint}</span>
        </span>
      </button>
    </section>
  );
}
