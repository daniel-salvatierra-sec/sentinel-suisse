import { useEffect, useState } from "react";
import { fetchAssistantConfig, type ListingType } from "../api";
import {
  loadGuideSeen,
  loadNudgeSeen,
  saveGuideSeen,
  saveNudgeSeen,
} from "../guideStorage";
import type { Messages } from "../i18n";
import { AssistantChat } from "./AssistantChat";
import { SentinelBuddy, SentinelFace } from "./SentinelBuddy";

const NUDGE_AFTER_MS = 60_000;

type Props = {
  t: Messages;
  lang: string;
  zone: ListingType;
  searching: boolean;
  searchTab: boolean;
  hasSession: boolean;
  onPickCategory: (type: ListingType) => void;
  onOpenAlerts: (type?: ListingType) => void;
  onStartSearch: (location: string) => void;
  onOpenMap: () => void;
  onOpenAccount: () => void;
  onOpenPublish: () => void;
};

/**
 * Sentinel companion: dock FAB + bottom sheet with zone-specific radar chips.
 * After one minute on search, offers alerts + account once (not again).
 */
export function GuideBot({
  t,
  lang,
  zone,
  searching,
  searchTab,
  hasSession,
  onPickCategory,
  onOpenAlerts,
  onStartSearch,
  onOpenMap,
  onOpenAccount,
  onOpenPublish,
}: Props) {
  const [open, setOpen] = useState(() => !loadGuideSeen());
  const [needsIntro, setNeedsIntro] = useState(() => !loadGuideSeen());
  const [pickingAlertType, setPickingAlertType] = useState(false);
  const [chatMode, setChatMode] = useState(false);
  const [nudgeMode, setNudgeMode] = useState(false);
  const [nudgeDue, setNudgeDue] = useState(false);
  const [assistantEnabled, setAssistantEnabled] = useState(false);

  useEffect(() => {
    fetchAssistantConfig()
      .then((config) => setAssistantEnabled(config.enabled))
      .catch(() => setAssistantEnabled(false));
  }, []);

  useEffect(() => {
    if (loadNudgeSeen() || needsIntro) {
      return;
    }
    const timer = window.setTimeout(() => setNudgeDue(true), NUDGE_AFTER_MS);
    return () => window.clearTimeout(timer);
  }, [needsIntro]);

  useEffect(() => {
    if (!nudgeDue || loadNudgeSeen() || needsIntro || !searchTab || chatMode) {
      return;
    }
    setNudgeMode(true);
    setPickingAlertType(false);
    setOpen(true);
  }, [nudgeDue, needsIntro, searchTab, chatMode]);

  const dismissNudge = () => {
    saveNudgeSeen();
    setNudgeMode(false);
    setNudgeDue(false);
  };

  const close = () => {
    saveGuideSeen();
    if (nudgeMode) {
      dismissNudge();
    }
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
                    : nudgeMode
                      ? t.guideNudgeMessage
                      : pickingAlertType
                        ? t.alertsAskType
                        : radarMessage}
                </p>
                {nudgeMode && !hasSession ? (
                  <p className="guide-message guide-nudge-extra">{t.guideNudgeAccount}</p>
                ) : null}

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
                ) : nudgeMode ? (
                  <div className="guide-actions">
                    <button
                      type="button"
                      className="option"
                      onClick={() => {
                        onOpenAlerts(zone);
                        dismissNudge();
                        close();
                      }}
                    >
                      {t.guideNudgeAlerts}
                    </button>
                    {!hasSession ? (
                      <button
                        type="button"
                        className="option"
                        onClick={() => {
                          onOpenAccount();
                          dismissNudge();
                          close();
                        }}
                      >
                        {t.guideNudgeAccountCta}
                      </button>
                    ) : null}
                    <button type="button" className="option" onClick={close}>
                      {t.guideNudgeNo}
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
                    <button
                      type="button"
                      className="chip active"
                      onClick={() => {
                        onOpenPublish();
                        close();
                      }}
                    >
                      {t.guideChipPublish}
                    </button>
                    <button
                      type="button"
                      className="chip active"
                      onClick={() => {
                        onOpenAccount();
                        close();
                      }}
                    >
                      {t.guideChipAccount}
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
