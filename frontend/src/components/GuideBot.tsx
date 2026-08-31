import { useEffect, useState } from "react";
import { fetchAssistantConfig, type ListingType } from "../api";
import {
  loadGuideSeen,
  loadNudgeSeen,
  saveGuideSeen,
  saveNudgeSeen,
} from "../guideStorage";
import type { Messages } from "../i18n";
import type { SentinelPose } from "../sentinelPose";
import { AssistantChat } from "./AssistantChat";
import { NamedCopy, SentinelBuddy, SentinelFace } from "./SentinelBuddy";

const NUDGE_AFTER_MS = 5 * 60 * 1000;

type Props = {
  t: Messages;
  lang: string;
  zone: ListingType;
  page: "overview" | "search" | "account";
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
 * Sentinela: presents on open; after 5 minutes asks about alerts (yes/no).
 * Yes → points to Account. No → she steps back.
 */
export function GuideBot({
  t,
  lang,
  zone,
  page,
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
  const [open, setOpen] = useState(false);
  const [needsIntro, setNeedsIntro] = useState(() => !loadGuideSeen());
  const [pickingAlertType, setPickingAlertType] = useState(false);
  const [chatMode, setChatMode] = useState(false);
  const [nudgeMode, setNudgeMode] = useState(false);
  const [nudgeDue, setNudgeDue] = useState(false);
  const [nudgeStep, setNudgeStep] = useState<"whatsapp" | "account">("whatsapp");
  const [showPresent, setShowPresent] = useState(true);
  const [assistantEnabled, setAssistantEnabled] = useState(false);
  const [chatBusy, setChatBusy] = useState(false);
  const [chatPose, setChatPose] = useState<SentinelPose | null>(null);

  useEffect(() => {
    fetchAssistantConfig()
      .then((config) => setAssistantEnabled(config.enabled))
      .catch(() => setAssistantEnabled(false));
  }, []);

  useEffect(() => {
    if (loadNudgeSeen() || hasSession) {
      return;
    }
    const timer = window.setTimeout(() => {
      setNudgeDue(true);
      setNudgeStep("whatsapp");
    }, NUDGE_AFTER_MS);
    return () => window.clearTimeout(timer);
  }, [hasSession]);

  const dismissNudge = () => {
    saveNudgeSeen();
    setNudgeMode(false);
    setNudgeDue(false);
    setNudgeStep("whatsapp");
  };

  const close = () => {
    saveGuideSeen();
    if (nudgeMode) {
      dismissNudge();
    }
    setNeedsIntro(false);
    setPickingAlertType(false);
    setChatMode(false);
    setChatPose(null);
    setOpen(false);
  };

  const pose: SentinelPose =
    chatPose ??
    (nudgeDue && nudgeStep === "account"
      ? "account"
      : nudgeDue
        ? "think"
        : page === "account"
          ? "account"
          : page === "search"
            ? "search"
            : "idle");

  const hint = nudgeDue
    ? nudgeStep === "account"
      ? t.guidePointAccount
      : t.guideNudgeWhatsapp
    : showPresent
      ? t.assistantPresent
      : undefined;

  const radarMessage = zone === "job" ? t.guideRadarMessageJob : t.guideRadarMessageHousing;
  const chipPrimary = zone === "job" ? t.guideChipBestOpp : t.guideChipBestPrice;
  const chipSecondary = zone === "job" ? t.guideChipBestFit : t.guideChipBestMatch;

  return (
    <>
      <SentinelBuddy
        zone={zone}
        pose={pose}
        searching={searching}
        talking={chatBusy}
        label={t.fireflyLabel}
        name={t.sentinelName}
        hint={hint}
        hintYes={nudgeDue && nudgeStep === "whatsapp" ? t.guideYes : undefined}
        hintNo={nudgeDue && nudgeStep === "whatsapp" ? t.guideNo : undefined}
        onHintYes={() => {
          setShowPresent(false);
          setNudgeStep("account");
        }}
        onHintNo={() => {
          setShowPresent(false);
          dismissNudge();
        }}
        onOpen={() => {
          setShowPresent(false);
          if (nudgeDue && nudgeStep === "whatsapp") return;
          if (nudgeDue && nudgeStep === "account") {
            onOpenAccount();
            dismissNudge();
            return;
          }
          setOpen(true);
          if (assistantEnabled && !needsIntro) {
            setChatMode(true);
          }
        }}
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
              <span className={`guide-avatar sentinel-avatar${chatBusy ? " is-talking" : ""}`} aria-hidden>
                <SentinelFace size={52} />
              </span>
              <div>
                <h2 id="guide-title" className="guide-title">
                  {t.sentinelName}
                </h2>
                <p className="guide-step-label">{t.guideRadarHint}</p>
              </div>
            </div>

            {chatMode ? (
              <AssistantChat
                t={t}
                lang={lang}
                onBack={() => {
                  setChatMode(false);
                  setChatPose(null);
                }}
                onBusyChange={setChatBusy}
                onPoseChange={setChatPose}
              />
            ) : (
              <>
                <p className="guide-message">
                  {needsIntro ? (
                    <NamedCopy text={t.guideHello} name={t.sentinelName} />
                  ) : nudgeMode ? (
                    nudgeStep === "account" ? t.guidePointAccount : t.guideNudgeWhatsapp
                  ) : pickingAlertType ? (
                    t.alertsAskType
                  ) : (
                    radarMessage
                  )}
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
