import { useEffect, useMemo, useState } from "react";
import { fetchMe, getApiKey, type Listing } from "../api";
import { letterTeaser } from "../housingDossier";
import type { Messages } from "../i18n";
import { buildJobCoverLetter, detectCvGaps, swissCvFrame, type CvGapId } from "../jobCv";

type Props = {
  listing: Listing;
  t: Messages;
  onNeedPremium: () => void;
};

const GAP_KEY: Record<CvGapId, keyof Messages> = {
  permit: "cvGapPermit",
  cefr: "cvGapCefr",
  dates: "cvGapDates",
  length: "cvGapLength",
  nationality: "cvGapNationality",
};

export function JobCvPanel({ listing, t, onNeedPremium }: Props) {
  const [premium, setPremium] = useState(false);
  const [name, setName] = useState("");
  const [cvText, setCvText] = useState("");
  const [copiedLetter, setCopiedLetter] = useState(false);
  const [copiedCv, setCopiedCv] = useState(false);

  useEffect(() => {
    if (!getApiKey()) {
      setPremium(false);
      return;
    }
    let cancelled = false;
    void fetchMe()
      .then((me) => {
        if (!cancelled) setPremium(Boolean(me.is_premium));
      })
      .catch(() => {
        if (!cancelled) setPremium(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const letter = buildJobCoverLetter(listing, name);
  const gaps = useMemo(() => detectCvGaps(cvText), [cvText]);
  const framed = swissCvFrame(letter.lang, name, cvText);

  const copyText = async (value: string, which: "letter" | "cv") => {
    try {
      await navigator.clipboard.writeText(value);
      if (which === "letter") {
        setCopiedLetter(true);
        window.setTimeout(() => setCopiedLetter(false), 2000);
      } else {
        setCopiedCv(true);
        window.setTimeout(() => setCopiedCv(false), 2000);
      }
    } catch {
      /* ignore */
    }
  };

  return (
    <div className="housing-dossier">
      <h3>{t.cvTitle}</h3>
      <p className="plan-hint">{t.cvIntro}</p>
      <ol className="housing-dossier-list">
        <li>{t.cvItem1}</li>
        <li>{t.cvItem2}</li>
        <li>{t.cvItem3}</li>
        <li>{t.cvItem4}</li>
        <li>{t.cvItem5}</li>
      </ol>
      <p className="housing-dossier-disclaimer">{t.cvDisclaimer}</p>

      <label>
        {t.cvPasteLabel}
        <textarea
          className="housing-dossier-letter"
          rows={7}
          value={cvText}
          onChange={(event) => setCvText(event.target.value)}
          placeholder={t.cvPastePlaceholder}
        />
      </label>
      <p className="plan-hint">{t.cvPasteHint}</p>

      {cvText.trim() ? (
        gaps.length > 0 ? (
          <>
            <h4>{t.cvGapsTitle}</h4>
            <ol className="housing-dossier-list">
              {gaps.map((id) => (
                <li key={id}>{t[GAP_KEY[id]]}</li>
              ))}
            </ol>
          </>
        ) : (
          <p className="plan-hint">{t.cvGapsNone}</p>
        )
      ) : (
        <p className="plan-hint">{t.cvPasteToSeeGaps}</p>
      )}

      <h4>{t.cvLetterTitle}</h4>
      <p className="plan-hint">{t.cvLetterLang.replace("{lang}", letter.lang.toUpperCase())}</p>

      {premium ? (
        <>
          <label>
            {t.dossierNameLabel}
            <input
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder={t.dossierNamePlaceholder}
              autoComplete="name"
            />
          </label>
          <p className="plan-hint">{t.dossierNameHint}</p>
          <textarea
            className="housing-dossier-letter"
            readOnly
            rows={12}
            value={letter.text}
          />
          <button
            type="button"
            className="apply-btn"
            onClick={() => void copyText(letter.text, "letter")}
          >
            {copiedLetter ? t.dossierCopied : t.cvCopyLetter}
          </button>
          <h4>{t.cvFrameTitle}</h4>
          <p className="plan-hint">{t.cvFrameHint}</p>
          <textarea className="housing-dossier-letter" readOnly rows={10} value={framed} />
          <button
            type="button"
            className="apply-btn"
            onClick={() => void copyText(framed, "cv")}
          >
            {copiedCv ? t.dossierCopied : t.cvCopyFrame}
          </button>
        </>
      ) : (
        <>
          <pre className="housing-dossier-teaser" tabIndex={0}>
            {letterTeaser(letter.text)}
          </pre>
          <p className="plan-hint">{t.cvTeaserHint}</p>
          <button type="button" className="apply-btn" onClick={onNeedPremium}>
            {t.cvPremiumCta}
          </button>
        </>
      )}
    </div>
  );
}
