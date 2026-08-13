import { useEffect, useState } from "react";
import { fetchAssistantConfig, type ListingType } from "../api";
import { loadGuideSeen, saveGuideSeen } from "../guideStorage";
import type { Messages } from "../i18n";
import { AssistantChat } from "./AssistantChat";
import { SentinelBuddy, SentinelFace } from "./SentinelBuddy";

type Props = {
  t: Messages;
  lang: string;
  zone: ListingType;
  searching: boolean;
  onPickCategory: (type: ListingType) => void;
  onOpenAlerts: (type?: ListingType) => void;
  onStartSearch: (location: string) => void;
  onOpenMap: () => void;
};

/**
 * Sentinel companion: dock FAB + bottom sheet with zone-specific radar chips.
 */
export function GuideBot({
  t,
  lang,
  zone,
  searching,
  onPickCategory,
  onOpenAlerts,
  onStartSearch,
  onOpenMap,
}: Props) {
  const [open, setOpen] = useState(false);
  const [needsIntro, setNeedsIntro] = useState(false);
  const [pickingAlertType, setPickingAlertType] = useState(false);
  const [chatMode, setChatMode] = useState(false);
  const [assistantEnabled, setAssistantEnabled] = useState(false);

  useEffect(() => {
    if (!loadGuideSeen()) {
      setNeedsIntro(true);
      setOpen(true);
    }
  }, []);

  useEffect(() => {
    fetchAssistantConfig()
      .then((config) => setAssistantEnabled(config.enabled))
      .catch(() => setAssistantEnabled(false));
  }, []);

  const close = () => {
    saveGuideSeen();
    setNeedsIntro(false);
    setPickingAlertType(false);
    setChatMode(false);
    setOpen(false);
  };

  const radarMessage = zone === "job" ? t.guideRadarMessageJob : t.guideRadarMessageHousing;
  const chipPrimary = zone === "job" ? t.guideChipBestOpp : t.guideChipBestPrice;
  const chipSecondary = zone === "job" ? t.guideChipBestFit : t.guideChipBestMatch;

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

            {chatMode ? (
              <AssistantChat t={t} lang={lang} onBack={() => setChatMode(false)} />
            ) : (
              <>
                <p className="guide-message">
                  {needsIntro
                    ? t.guideHello
                    : pickingAlertType
                      ? t.alertsAskType
                      : radarMessage}
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
                ) : pickingAlertType ? (
                  <div className="guide-actions">
                    <button
                      type="button"
                      className="option"
                      onClick={() => {
                        onOpenAlerts("housing");
                        close();
                      }}
                    >
                      {t.housing}
                    </button>
                    <button
                      type="button"
                      className="option"
                      onClick={() => {
                        onOpenAlerts("job");
                        close();
                      }}
                    >
                      {t.job}
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
                      {chipPrimary}
                    </button>
                    <button
                      type="button"
                      className="chip active"
                      onClick={() => {
                        onOpenMap();
                        close();
                      }}
                    >
                      {chipSecondary}
                    </button>
                    <button
                      type="button"
                      className="chip active"
                      onClick={() => setPickingAlertType(true)}
                    >
                      {t.guideChipAlert}
                    </button>
                    {assistantEnabled && (
                      <button
                        type="button"
                        className="chip active assistant-chip"
                        onClick={() => setChatMode(true)}
                      >
                        {t.assistantChatCta}
                      </button>
                    )}
                  </div>
                )}

                <div className="guide-nav">
                  <button type="button" className="guide-skip" onClick={close}>
                    {t.guideClose}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}
