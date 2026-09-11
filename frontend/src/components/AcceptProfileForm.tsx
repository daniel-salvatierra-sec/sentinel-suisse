import { useEffect, useMemo, useState, type FormEvent } from "react";
import { updateAcceptProfile, type AcceptGoal, type AcceptPermit, type AcceptProfile } from "../api";
import { emptyAcceptProfile } from "../acceptProfile";
import type { Messages } from "../i18n";
import { SWISS_CITIES } from "../swissCities";
import { DE_CITIES, FR_CITIES, IT_CITIES } from "../zoneCities";

type Props = {
  t: Messages;
  initial: AcceptProfile | null;
  onSaved: (profile: AcceptProfile | null) => void;
  onGoalChange?: (goal: AcceptGoal) => void;
};

const PLACE_OPTIONS: string[] = [
  ...SWISS_CITIES,
  ...FR_CITIES,
  ...DE_CITIES,
  ...IT_CITIES,
];

const LANGUAGE_OPTIONS = [
  { value: "ES", label: "Español" },
  { value: "FR", label: "Français" },
  { value: "EN", label: "English" },
  { value: "DE", label: "Deutsch" },
  { value: "IT", label: "Italiano" },
  { value: "PT", label: "Português" },
  { value: "ES, FR", label: "ES + FR" },
  { value: "ES, FR, EN", label: "ES + FR + EN" },
  { value: "FR, EN", label: "FR + EN" },
  { value: "DE, EN", label: "DE + EN" },
  { value: "IT, EN", label: "IT + EN" },
  { value: "PT, FR", label: "PT + FR" },
] as const;

const BUDGET_OPTIONS = [1200, 1500, 1800, 2000, 2500, 3000, 3500, 4000, 5000];

function fromApi(raw: AcceptProfile | null | undefined): AcceptProfile {
  if (!raw) return emptyAcceptProfile();
  return { ...emptyAcceptProfile(), ...raw };
}

function moveInOptions(): string[] {
  const out: string[] = [];
  const now = new Date();
  for (let i = 0; i < 12; i += 1) {
    const d = new Date(now.getFullYear(), now.getMonth() + i, 1);
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    out.push(`${y}-${m}`);
  }
  return out;
}

function PlaceSelect({
  label,
  value,
  onChange,
  unsetLabel,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  unsetLabel: string;
}) {
  const options = useMemo(() => {
    const base = [...PLACE_OPTIONS];
    if (value && !base.includes(value)) {
      base.unshift(value);
    }
    return base;
  }, [value]);

  return (
    <label>
      {label}
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        <option value="">{unsetLabel}</option>
        {options.map((city) => (
          <option key={city} value={city}>
            {city}
          </option>
        ))}
      </select>
    </label>
  );
}

export function AcceptProfileForm({ t, initial, onSaved, onGoalChange }: Props) {
  const [form, setForm] = useState<AcceptProfile>(() => fromApi(initial));
  const [busy, setBusy] = useState(false);
  const [ok, setOk] = useState(false);
  const [error, setError] = useState(false);
  const months = useMemo(() => moveInOptions(), []);

  useEffect(() => {
    setForm(fromApi(initial));
  }, [initial]);

  const goal = form.goal;
  const showJob = goal === "job" || goal === "both";
  const showHousing = goal === "housing" || goal === "both";

  const setGoal = (next: AcceptGoal) => {
    setForm((prev) => ({ ...prev, goal: next }));
    onGoalChange?.(next);
  };

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!form.goal) return;
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

  const languageValue = LANGUAGE_OPTIONS.some((item) => item.value === (form.languages ?? ""))
    ? (form.languages ?? "")
    : form.languages
      ? form.languages
      : "";

  return (
    <section className="accept-profile">
      <h3>{t.acceptTitle}</h3>
      <p className="plan-hint">{t.acceptIntro}</p>
      <form onSubmit={(event) => void onSubmit(event)}>
        <p className="filter-group-label">{t.acceptGoal}</p>
        <div className="filter-chips" role="group" aria-label={t.acceptGoal}>
          {(
            [
              ["housing", t.acceptGoalHousing],
              ["job", t.acceptGoalJob],
              ["both", t.acceptGoalBoth],
            ] as const
          ).map(([value, label]) => (
            <button
              key={value}
              type="button"
              className={form.goal === value ? "chip active" : "chip"}
              aria-pressed={form.goal === value}
              onClick={() => setGoal(value)}
            >
              {label}
            </button>
          ))}
        </div>

        {!goal ? <p className="plan-hint">{t.acceptPickGoal}</p> : null}

        {showJob ? (
          <>
            {goal === "both" ? <p className="filter-group-label">{t.acceptGoalJob}</p> : null}
            <PlaceSelect
              label={t.acceptLiveIn}
              value={form.live_in ?? ""}
              unsetLabel={t.acceptPermitUnset}
              onChange={(live_in) => setForm((prev) => ({ ...prev, live_in }))}
            />
            <PlaceSelect
              label={t.acceptWorkIn}
              value={form.work_in ?? ""}
              unsetLabel={t.acceptPermitUnset}
              onChange={(work_in) => setForm((prev) => ({ ...prev, work_in }))}
            />
            <PlaceSelect
              label={t.acceptCities}
              value={form.cities ?? ""}
              unsetLabel={t.acceptPermitUnset}
              onChange={(cities) => setForm((prev) => ({ ...prev, cities }))}
            />
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
              <select
                value={languageValue}
                onChange={(e) => setForm((prev) => ({ ...prev, languages: e.target.value }))}
              >
                <option value="">{t.acceptPermitUnset}</option>
                {form.languages &&
                !LANGUAGE_OPTIONS.some((item) => item.value === form.languages) ? (
                  <option value={form.languages}>{form.languages}</option>
                ) : null}
                {LANGUAGE_OPTIONS.map((item) => (
                  <option key={item.value} value={item.value}>
                    {item.label}
                  </option>
                ))}
              </select>
            </label>
          </>
        ) : null}

        {showHousing ? (
          <>
            {goal === "both" ? <p className="filter-group-label">{t.acceptGoalHousing}</p> : null}
            {goal === "housing" ? (
              <>
                <PlaceSelect
                  label={t.acceptLiveIn}
                  value={form.live_in ?? ""}
                  unsetLabel={t.acceptPermitUnset}
                  onChange={(live_in) => setForm((prev) => ({ ...prev, live_in }))}
                />
                <PlaceSelect
                  label={t.acceptCities}
                  value={form.cities ?? ""}
                  unsetLabel={t.acceptPermitUnset}
                  onChange={(cities) => setForm((prev) => ({ ...prev, cities }))}
                />
              </>
            ) : null}
            <label>
              {t.acceptBudget}
              <select
                value={form.budget_chf ?? ""}
                onChange={(e) =>
                  setForm((prev) => ({
                    ...prev,
                    budget_chf: e.target.value === "" ? null : Number(e.target.value),
                  }))
                }
              >
                <option value="">{t.acceptPermitUnset}</option>
                {form.budget_chf != null && !BUDGET_OPTIONS.includes(form.budget_chf) ? (
                  <option value={form.budget_chf}>{form.budget_chf}</option>
                ) : null}
                {BUDGET_OPTIONS.map((amount) => (
                  <option key={amount} value={amount}>
                    {amount} CHF
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t.acceptHousehold}
              <select
                value={form.household ?? ""}
                onChange={(e) =>
                  setForm((prev) => ({
                    ...prev,
                    household: e.target.value === "" ? null : Number(e.target.value),
                  }))
                }
              >
                <option value="">{t.acceptPermitUnset}</option>
                {[1, 2, 3, 4, 5, 6, 7, 8].map((n) => (
                  <option key={n} value={n}>
                    {n}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t.acceptMoveIn}
              <select
                value={form.move_in ?? ""}
                onChange={(e) => setForm((prev) => ({ ...prev, move_in: e.target.value }))}
              >
                <option value="">{t.acceptPermitUnset}</option>
                {form.move_in && !months.includes(form.move_in) ? (
                  <option value={form.move_in}>{form.move_in}</option>
                ) : null}
                {months.map((month) => (
                  <option key={month} value={month}>
                    {month}
                  </option>
                ))}
              </select>
            </label>
          </>
        ) : null}

        {goal ? (
          <>
            <p className="housing-dossier-disclaimer">{t.acceptDisclaimer}</p>
            <button type="submit" className="apply-btn" disabled={busy} style={{ width: "100%" }}>
              {busy ? t.loading : t.acceptSave}
            </button>
          </>
        ) : null}
      </form>
      {ok ? <p className="alert-feedback success">{t.acceptSaved}</p> : null}
      {error ? <p className="alert-feedback error">{t.acceptError}</p> : null}
    </section>
  );
}
