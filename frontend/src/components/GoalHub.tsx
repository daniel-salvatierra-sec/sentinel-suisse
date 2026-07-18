import type { ListingType } from "../api";
import type { Messages } from "../i18n";

type Props = {
  t: Messages;
  active: ListingType;
  onSelect: (type: ListingType) => void;
};

/**
 * Full-bleed Home / Work hub — climb (work) → arrival (home).
 * Visual: /hub/hero.png (warm modern illustration).
 */
export function GoalHub({ t, active, onSelect }: Props) {
  return (
    <section
      className={`goal-hub${active === "housing" ? " focus-home" : " focus-work"}`}
      aria-label={t.goalHubLabel}
      style={{ backgroundImage: "url(/hub/hero.png)" }}
    >
      <div className="goal-hub-veil" aria-hidden="true" />
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
      <div className="goal-hub-climb" aria-hidden="true">
        <span className="goal-hub-climb-arrow" />
      </div>
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
