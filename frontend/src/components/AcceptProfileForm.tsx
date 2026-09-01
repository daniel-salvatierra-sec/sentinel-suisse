import { useEffect, useState, type FormEvent } from "react";
import { updateAcceptProfile, type AcceptGoal, type AcceptPermit, type AcceptProfile } from "../api";
import { emptyAcceptProfile } from "../acceptProfile";
import type { Messages } from "../i18n";

type Props = {
  t: Messages;
  initial: AcceptProfile | null;
  onSaved: (profile: AcceptProfile | null) => void;
};

function fromApi(raw: AcceptProfile | null | undefined): AcceptProfile {
  if (!raw) return emptyAcceptProfile();
  return { ...emptyAcceptProfile(), ...raw };
}

export function AcceptProfileForm({ t, initial, onSaved }: Props) {
  const [form, setForm] = useState<AcceptProfile>(() => fromApi(initial));
  const [busy, setBusy] = useState(false);
  const [ok, setOk] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    setForm(fromApi(initial));
  }, [initial]);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError(false);
    setOk(false);
    try {
      const me = await updateAcceptProfile(form);
      onSaved(me.accept_profile ?? null);
      setOk(true);
    } catch {
      setError(true);
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="accept-profile">
      <h3>{t.acceptTitle}</h3>
      <p className="plan-hint">{t.acceptIntro}</p>
      <form onSubmit={(event) => void onSubmit(event)}>
        <p className="filter-group-label">{t.acceptGoal}</p>
        <div className="filter-chips" role="group" aria-label={t.acceptGoal}>
          {(
            [
              ["", t.acceptGoalUnset],
              ["housing", t.acceptGoalHousing],
              ["job", t.acceptGoalJob],
              ["both", t.acceptGoalBoth],
            ] as const
          ).map(([value, label]) => (
            <button
              key={value || "unset"}
              type="button"
              className={(!form.goal && value === "") || form.goal === value ? "chip active" : "chip"}
              aria-pressed={(!form.goal && value === "") || form.goal === value}
              onClick={() =>
                setForm((prev) => ({ ...prev, goal: (value || null) as AcceptGoal | null }))
              }
            >
              {label}
            </button>
          ))}
        </div>
        <label>
          {t.acceptLiveIn}
          <input
            value={form.live_in ?? ""}
            onChange={(e) => setForm((prev) => ({ ...prev, live_in: e.target.value }))}
            placeholder={t.acceptLiveInHint}
          />
        </label>
        <label>
          {t.acceptWorkIn}
          <input
            value={form.work_in ?? ""}
            onChange={(e) => setForm((prev) => ({ ...prev, work_in: e.target.value }))}
            placeholder={t.acceptWorkInHint}
          />
        </label>
        <label>
          {t.acceptCities}
          <input
            value={form.cities ?? ""}
            onChange={(e) => setForm((prev) => ({ ...prev, cities: e.target.value }))}
            placeholder={t.acceptCitiesHint}
          />
        </label>
        <label>
          {t.acceptPermit}
          <select
            value={form.permit ?? ""}
            onChange={(e) =>
              setForm((prev) => ({
                ...prev,
                permit: (e.target.value || null) as AcceptPermit | null,
              }))
            }
          >
            <option value="">{t.acceptPermitUnset}</option>
            <option value="G">G</option>
            <option value="B">B</option>
            <option value="C">C</option>
            <option value="L">L</option>
            <option value="none">{t.acceptPermitNone}</option>
            <option value="other">{t.acceptPermitOther}</option>
          </select>
        </label>
        <label>
          {t.acceptLanguages}
          <input
            value={form.languages ?? ""}
            onChange={(e) => setForm((prev) => ({ ...prev, languages: e.target.value }))}
            placeholder={t.acceptLanguagesHint}
          />
        </label>
        <label>
          {t.acceptBudget}
          <input
            type="number"
            min={1}
            step={50}
            value={form.budget_chf ?? ""}
            onChange={(e) =>
              setForm((prev) => ({
                ...prev,
                budget_chf: e.target.value === "" ? null : Number(e.target.value),
              }))
            }
            placeholder="1800"
          />
        </label>
        <label>
          {t.acceptHousehold}
          <input
            type="number"
            min={1}
            max={12}
            value={form.household ?? ""}
            onChange={(e) =>
              setForm((prev) => ({
                ...prev,
                household: e.target.value === "" ? null : Number(e.target.value),
              }))
            }
          />
        </label>
        <label>
          {t.acceptMoveIn}
          <input
            type="month"
            value={form.move_in ?? ""}
            onChange={(e) => setForm((prev) => ({ ...prev, move_in: e.target.value }))}
          />
        </label>
        <p className="housing-dossier-disclaimer">{t.acceptDisclaimer}</p>
        <button type="submit" className="apply-btn" disabled={busy} style={{ width: "100%" }}>
          {busy ? t.loading : t.acceptSave}
        </button>
      </form>
      {ok ? <p className="alert-feedback success">{t.acceptSaved}</p> : null}
      {error ? <p className="alert-feedback error">{t.acceptError}</p> : null}
    </section>
  );
}
