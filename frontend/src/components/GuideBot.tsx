import { useEffect, useState } from "react";
import type { ListingType } from "../api";
import { loadGuideSeen, saveGuideSeen } from "../guideStorage";
import type { Messages } from "../i18n";
import { SentinelBuddy, SentinelFace } from "./SentinelBuddy";

type Props = {
  t: Messages;
  zone: ListingType;
  searching: boolean;
  onPickCategory: (type: ListingType) => void;
  onOpenAlerts: () => void;
  onStartSearch: (location: string) => void;
  onOpenMap: () => void;
};

/**
 * Sentinel companion: dock FAB + bottom sheet with 3 primary actions.
 * First visit still offers Home / Work once, then radar chips.
 */
export function GuideBot({
  t,
  zone,
  searching,
  onPickCategory,
  onOpenAlerts,
  onStartSearch,
  onOpenMap,
}: Props) {
  const [open, setOpen] = useState(false);
  const [needsIntro, setNeedsIntro] = useState(false);

  useEffect(() => {
    if (!loadGuideSeen()) {
      setNeedsIntro(true);
      setOpen(true);
    }
  }, []);

  const close = () => {
    saveGuideSeen();
    setNeedsIntro(false);
    setOpen(false);
  };

  return (
    <>
      <SentinelBuddy
        zone={zone}
        searching={searching}
        label={t.fireflyLabel}
        onOpen={() => setOpen(true)}
      />
      {open && (
        <div className="modal-backdrop sheet-backdrop" role="presentation" onClick={close}>
          <div
            className="guide-sheet"
            role="dialog"
            aria-labelledby="guide-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="guide-sheet-handle" aria-hidden />
            <div className="guide-header">
              <span className="guide-avatar sentinel-avatar" aria-hidden>
                <SentinelFace size={36} />
              </span>
              <div>
                <h2 id="guide-title" className="guide-title">
                  {t.guide}
                </h2>
                <p className="guide-step-label">{t.guideRadarHint}</p>
              </div>
            </div>

            <p className="guide-message">
              {needsIntro ? t.guideHello : t.guideRadarMessage}
            </p>

            {needsIntro ? (
              <div className="guide-actions">
                <button
                  type="button"
                  className="option"
                  onClick={() => {
                    onPickCategory("housing");
                    setNeedsIntro(false);
                    saveGuideSeen();
                  }}
                >
                  {t.guideHousing}
                </button>
                <button
                  type="button"
                  className="option"
                  onClick={() => {
                    onPickCategory("job");
                    setNeedsIntro(false);
                    saveGuideSeen();
                  }}
                >
                  {t.guideJob}
                </button>
              </div>
            ) : (
              <div className="guide-chip-actions">
                <button
                  type="button"
                  className="chip active"
                  onClick={() => {
                    onStartSearch("Geneva");
                    close();
                  }}
                >
                  {t.guideChipBestPrice}
                </button>
                <button
                  type="button"
                  className="chip active"
                  onClick={() => {
                    onOpenMap();
                    close();
                  }}
                >
                  {t.guideChipBestMatch}
                </button>
                <button
                  type="button"
                  className="chip active"
                  onClick={() => {
                    onOpenAlerts();
                    close();
                  }}
                >
                  {t.guideChipAlert}
                </button>
              </div>
            )}

            <div className="guide-nav">
              <button type="button" className="guide-skip" onClick={close}>
                {t.guideClose}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
