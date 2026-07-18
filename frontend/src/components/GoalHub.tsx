import type { ListingType } from "../api";
import type { Messages } from "../i18n";

type Props = {
  t: Messages;
  active: ListingType;
  onSelect: (type: ListingType) => void;
};

/**
 * Full-bleed Home / Work hub — spring (home) above, winter climb (work) below.
 * Visual: /hub/hero.png
 */
export function GoalHub({ t, active, onSelect }: Props) {
  const workActive = active === "job";

  return (
    <section
      className={`goal-hub${active === "housing" ? " focus-home" : " focus-work"}`}
      aria-label={t.goalHubLabel}
      style={{ backgroundImage: "url(/hub/hero.png?v=2)" }}
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

      <div className={`goal-hub-divider${workActive ? " point-down" : " point-up"}`} aria-hidden="true">
        <span className="goal-hub-divider-line" />
        <span className="goal-hub-climb-arrow" />
        <span className="goal-hub-divider-line" />
      </div>

      <button
        type="button"
        className={`goal-zone work${workActive ? " active" : ""}`}
        onClick={() => onSelect("job")}
        aria-pressed={workActive}
      >
        <span className="goal-zone-kicker">{t.goalWorkKicker}</span>
        <strong className="goal-zone-title">{t.goalWork}</strong>
        <span className="goal-zone-desc">{t.jobDesc}</span>
        {t.goalWorkHint ? <span className="goal-zone-hint">{t.goalWorkHint}</span> : null}
      </button>
    </section>
  );
}
