import type { ListingType } from "../api";
import type { Messages } from "../i18n";

type Props = {
  t: Messages;
  active: ListingType;
  focused?: boolean;
  onSelect: (type: ListingType) => void;
};

/**
 * Full-bleed Home / Work hub — spring (home) above, winter climb (work) below.
 * Visual: /hub/hero.png
 */
export function GoalHub({ t, active, focused = true, onSelect }: Props) {
  const homeActive = focused && active === "housing";
  const workActive = focused && active === "job";
  const focusClass = !focused
    ? " is-overview"
    : active === "housing"
      ? " focus-home"
      : " focus-work";

  return (
    <section
      className={`goal-hub${focusClass}`}
      aria-label={t.goalHubLabel}
      style={{ backgroundImage: "url(/hub/hero.png?v=3)" }}
    >
      <div className="goal-hub-veil" aria-hidden="true" />
      <button
        type="button"
        className={`goal-zone home${homeActive ? " active" : ""}`}
        onClick={() => onSelect("housing")}
        aria-pressed={homeActive}
      >
        <span className="goal-zone-kicker">{t.goalHomeKicker}</span>
        <strong className="goal-zone-title">{t.goalHome}</strong>
        <span className="goal-zone-desc">{t.housingDesc}</span>
      </button>

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
