import { useEffect, useState } from "react";
import { fetchMe, getApiKey, type Listing } from "../api";
import {
  buildHousingCoverLetter,
  letterTeaser,
  listingIsFrontalier,
} from "../housingDossier";
import type { Messages } from "../i18n";

type Props = {
  listing: Listing;
  t: Messages;
  onNeedPremium: () => void;
};

export function HousingDossierPanel({ listing, t, onNeedPremium }: Props) {
  const [premium, setPremium] = useState(false);
  const [name, setName] = useState("");
  const [copied, setCopied] = useState(false);

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

  const letter = buildHousingCoverLetter(listing, name);
  const frontalier = listingIsFrontalier(listing);

  const copyLetter = async () => {
    try {
      await navigator.clipboard.writeText(letter.text);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  };

  return (
    <div className="housing-dossier">
      <h3>{t.dossierTitle}</h3>
      <p className="plan-hint">{t.dossierIntro}</p>
      <ol className="housing-dossier-list">
        <li>{t.dossierItem1}</li>
        <li>{t.dossierItem2}</li>
        <li>{t.dossierItem3}</li>
        <li>{t.dossierItem4}</li>
        <li>{t.dossierItem5}</li>
      </ol>
      <p className="plan-hint">{t.dossierItemOptional}</p>
      {frontalier ? <p className="plan-hint">{t.dossierFrontalier}</p> : null}
      <p className="housing-dossier-disclaimer">{t.dossierDisclaimer}</p>

      <h4>{t.dossierLetterTitle}</h4>
      <p className="plan-hint">{t.dossierLetterLang.replace("{lang}", letter.lang.toUpperCase())}</p>

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
            rows={14}
            value={letter.text}
          />
          <button type="button" className="apply-btn" onClick={() => void copyLetter()}>
            {copied ? t.dossierCopied : t.dossierCopy}
          </button>
        </>
      ) : (
        <>
          <pre className="housing-dossier-teaser" tabIndex={0}>
            {letterTeaser(letter.text)}
          </pre>
          <p className="plan-hint">{t.dossierTeaserHint}</p>
          <button type="button" className="apply-btn" onClick={onNeedPremium}>
            {t.dossierPremiumCta}
          </button>
        </>
      )}
    </div>
  );
}
