import { useEffect, useRef, useState } from "react";
import { type ListingType } from "../api";
import {
  loadGuideSeen,
  loadNudgeSeen,
  loadPresentSeen,
  saveGuideSeen,
  saveNudgeSeen,
  savePresentSeen,
} from "../guideStorage";
import type { Messages } from "../i18n";
import type { SentinelPose } from "../sentinelPose";
import type { SentinelaAction, SentinelaUiContext } from "../sentinela";
import { AssistantChat } from "./AssistantChat";
import { NamedCopy, SentinelBuddy, SentinelFace } from "./SentinelBuddy";

const NUDGE_AFTER_MS = 5 * 60 * 1000;
const CHECKIN_AFTER_MS = 14 * 1000;
const CHECKIN_AGAIN_MS = 90 * 1000;

type CheckIn = "off" | "found" | "help";

type AccountIntent = "job" | "housing";

type Props = {
  t: Messages;
  lang: string;
  zone: ListingType;
  page: "overview" | "search" | "account";
  searching: boolean;
  hasSession: boolean;
  onPickCategory: (type: ListingType | "both") => void;
  onOpenAlerts: (type?: ListingType) => void;
  onStartSearch: (location: string) => void;
  onOpenMap: () => void;
  onOpenAccount: (intent?: "job" | "housing") => void;
  onOpenPublish: () => void;
  uiContext: SentinelaUiContext;
  onExecuteActions: (actions: SentinelaAction[]) => Promise<{ n: number }>;
};

/**
 * Sentinela: greets once; tap outside the answers hides the bubble.
 * After 5 minutes she offers job/housing alerts. Searching hides the bubble.
 */
export function GuideBot({
  t,
  lang,
  zone,
  page,
  searching,
  hasSession,
  onPickCategory,
  onOpenAlerts,
  onStartSearch,
  onOpenMap,
  onOpenAccount,
  onOpenPublish,
  uiContext,
  onExecuteActions,
}: Props) {
  const [open, setOpen] = useState(false);
  const [needsIntro, setNeedsIntro] = useState(() => !loadGuideSeen());
  const [pickingAlertType, setPickingAlertType] = useState(false);
  const [chatMode, setChatMode] = useState(false);
  const [nudgeMode, setNudgeMode] = useState(false);
  const [nudgeDue, setNudgeDue] = useState(false);
  const [accountPitch, setAccountPitch] = useState<AccountIntent | null>(null);
  const [byeHint, setByeHint] = useState(false);
  const [gladHint, setGladHint] = useState(false);
  const [showPresent, setShowPresent] = useState(() => !loadPresentSeen());
  const [checkIn, setCheckIn] = useState<CheckIn>("off");
  const checkInSeen = useRef(false);
  const [chatBusy, setChatBusy] = useState(false);
  const [chatPose, setChatPose] = useState<SentinelPose | null>(null);
  const [restKey, setRestKey] = useState(0);
  const [mood, setMood] = useState<SentinelPose | null>(null);
  const prevUi = useRef({
    searching,
    count: 0,
    listing: null as number | null,
    tab: "",
    mode: "",
    query: "",
    zone: "",
    rooms: "",
    price: "",
    page: "",
  });

  const dismissPresent = () => {
    savePresentSeen();
    setShowPresent(false);
    setNeedsIntro(false);
    saveGuideSeen();
  };

  const dismissNudge = () => {
    saveNudgeSeen();
    setNudgeMode(false);
    setNudgeDue(false);
  };

  useEffect(() => {
    if (loadNudgeSeen() || hasSession || showPresent) {
      return;
    }
    const timer = window.setTimeout(() => {
      setNudgeDue(true);
    }, NUDGE_AFTER_MS);
    return () => window.clearTimeout(timer);
  }, [hasSession, showPresent]);

  useEffect(() => {
    if (showPresent || open || checkIn !== "off") {
      return;
    }
    const wait = checkInSeen.current ? CHECKIN_AGAIN_MS : CHECKIN_AFTER_MS;
    const timer = window.setTimeout(() => {
      checkInSeen.current = true;
      setCheckIn("found");
    }, wait);
    return () => window.clearTimeout(timer);
  }, [showPresent, open, checkIn]);

  useEffect(() => {
    setMood(null);
  }, [restKey]);

  useEffect(() => {
    const prev = prevUi.current;
    const listingId = uiContext.open_listing?.id ?? null;
    let next: SentinelPose | null = null;

    if (searching && !prev.searching) {
      next = "search";
    } else if (prev.searching && !searching) {
      next = uiContext.result_count > 0 ? "found" : page === "search" ? "think" : "sit";
    } else if (listingId != null && listingId !== prev.listing) {
      next = "found";
    } else if (uiContext.tab !== prev.tab && prev.tab) {
      if (uiContext.tab === "map") next = "search";
      else if (uiContext.tab === "alerts") next = "help";
      else if (uiContext.tab === "account" || uiContext.tab === "publish") next = "account";
      else if (uiContext.tab === "list" && uiContext.result_count > 0) next = "sit";
    } else if (
      prev.mode &&
      (uiContext.mode !== prev.mode ||
        uiContext.zone !== prev.zone ||
        uiContext.query !== prev.query ||
        uiContext.rooms !== prev.rooms ||
        uiContext.price_max !== prev.price)
    ) {
      next = searching ? "search" : "listen";
    }

    if (next) setMood(next);
    prevUi.current = {
      searching,
      count: uiContext.result_count,
      listing: listingId,
      tab: uiContext.tab,
      mode: uiContext.mode,
      query: uiContext.query,
      zone: uiContext.zone,
      rooms: uiContext.rooms,
      price: uiContext.price_max,
      page,
    };
  }, [searching, uiContext, page]);

  useEffect(() => {
    if (!mood || (mood === "search" && searching)) {
      return;
    }
    const timer = window.setTimeout(() => setMood(null), 60 * 1000);
    return () => window.clearTimeout(timer);
  }, [mood, searching]);

  useEffect(() => {
    const bubbleOpen =
      showPresent || nudgeDue || Boolean(accountPitch) || byeHint || checkIn !== "off";
    if (!bubbleOpen || open) return;

    const onPointerDown = (event: PointerEvent) => {
      const target = event.target as HTMLElement | null;
      if (!target) return;
      if (target.closest(".sentinel-hint-actions")) return;
      if (target.closest(".guide-sheet") || target.closest(".sheet-backdrop")) return;
      if (showPresent) {
        dismissPresent();
        return;
      }
      if (nudgeDue) {
        dismissNudge();
        return;
      }
      if (checkIn !== "off") {
        setCheckIn("off");
        return;
      }
      setAccountPitch(null);
      setByeHint(false);
    };

    document.addEventListener("pointerdown", onPointerDown);
    return () => document.removeEventListener("pointerdown", onPointerDown);
  }, [showPresent, nudgeDue, accountPitch, byeHint, open, checkIn]);

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
    (open && chatBusy
      ? "listen"
      : accountPitch
        ? "account"
        : gladHint
          ? "found"
          : checkIn === "help"
            ? "sit"
            : checkIn === "found"
              ? "ask"
              : showPresent
                ? "wave"
                : nudgeDue
                  ? "think"
                  : page === "account"
                    ? "account"
                    : mood
                      ? mood
                      : page === "search" && uiContext.result_count > 0 && uiContext.tab === "list"
                        ? "sit"
                        : "idle");

  const hint = gladHint
    ? t.guideFoundGlad
    : byeHint
      ? t.guideNudgeLater
    : accountPitch === "job"
      ? t.guidePitchJob
      : accountPitch === "housing"
        ? t.guidePitchHome
        : checkIn === "help"
          ? t.guideOfferHelp
          : checkIn === "found"
            ? t.guideAskFound
            : nudgeDue
              ? t.guideNudgeMessage
              : showPresent
                ? t.assistantPresent
                : undefined;

  const hintChoices = accountPitch
    ? [{ id: "ok", label: t.guidePitchOk, quiet: true }]
    : checkIn === "help"
      ? [
          { id: "help-talk", label: t.guideOfferTalk },
          { id: "help-alerts", label: t.guideOfferAlerts },
          { id: "help-later", label: t.guideNudgeNo, quiet: true },
        ]
      : checkIn === "found"
        ? [
            { id: "found-yes", label: t.guideAskFoundYes },
            { id: "found-no", label: t.guideAskFoundNo },
          ]
        : nudgeDue
          ? [
              { id: "job", label: t.guideNudgeJob },
              { id: "housing", label: t.guideNudgeHome },
              { id: "no", label: t.guideNudgeNo, quiet: true },
            ]
          : showPresent
            ? [
                { id: "look-housing", label: t.guideLookHome },
                { id: "look-job", label: t.guideLookJob },
                { id: "look-both", label: t.guideLookBoth },
              ]
            : undefined;

  const onHintChoice = (id: string) => {
    if (id === "found-yes") {
      setCheckIn("off");
      setGladHint(true);
      setMood("found");
      window.setTimeout(() => setGladHint(false), 3200);
      return;
    }
    if (id === "found-no" || id === "help-talk") {
      if (id === "found-no") {
        setCheckIn("help");
        return;
      }
      setCheckIn("off");
      setOpen(true);
      setChatMode(true);
      setChatPose("listen");
      setNeedsIntro(false);
      saveGuideSeen();
      return;
    }
    if (id === "help-alerts") {
      setCheckIn("off");
      setMood("help");
      onOpenAlerts();
      return;
    }
    if (id === "help-later") {
      setCheckIn("off");
      setByeHint(true);
      setRestKey((n) => n + 1);
      window.setTimeout(() => setByeHint(false), 2800);
      return;
    }
    if (id === "ok") {
      setAccountPitch(null);
      return;
    }
    if (id === "no") {
      saveNudgeSeen();
      setNudgeDue(false);
      setByeHint(true);
      setRestKey((n) => n + 1);
      window.setTimeout(() => setByeHint(false), 2800);
      return;
    }
    if (id === "look-housing" || id === "look-job" || id === "look-both") {
      dismissPresent();
      setMood(id === "look-both" ? "listen" : "search");
      if (id === "look-housing") onPickCategory("housing");
      else if (id === "look-job") onPickCategory("job");
      else onPickCategory("both");
      return;
    }
    if (id === "job" || id === "housing") {
      saveNudgeSeen();
      setNudgeDue(false);
      setAccountPitch(id);
      onOpenAccount(id);
    }
  };

  const chipPrimary = zone === "job" ? t.guideChipBestOpp : t.guideChipBestPrice;
  const chipSecondary = zone === "job" ? t.guideChipBestFit : t.guideChipBestMatch;

  return (
    <>
      <SentinelBuddy
        zone={zone}
        pose={pose}
        searching={searching}
        talking={chatBusy}
        sheetOpen={open}
        dock={page === "account" || accountPitch ? "left" : "right"}
        label={t.fireflyLabel}
        name={t.sentinelName}
        hint={hint}
        hintChoices={hintChoices}
        onHintChoice={onHintChoice}
        restKey={restKey}
        onOpen={() => {
          if (showPresent) {
            dismissPresent();
            setCheckIn("help");
            return;
          }
          if (checkIn === "found") {
            setCheckIn("help");
            return;
          }
          if (nudgeDue || accountPitch || byeHint || gladHint) {
            if (nudgeDue) dismissNudge();
            setAccountPitch(null);
            setByeHint(false);
            setGladHint(false);
            return;
          }
          if (checkIn === "help") {
            setCheckIn("off");
          }
          setOpen(true);
          setNeedsIntro(false);
          saveGuideSeen();
          setChatMode(true);
          setChatPose("listen");
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
                <SentinelFace size={52} zone={zone} />
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
                uiContext={uiContext}
                onExecuteActions={onExecuteActions}
                onBack={() => {
                  setChatMode(false);
                  setChatPose(null);
                }}
                onBusyChange={setChatBusy}
                onPoseChange={setChatPose}
                onPointAccount={() => {
                  setShowPresent(false);
                  setOpen(false);
                  setChatMode(false);
                  setChatPose("account");
                  onOpenAccount();
                }}
              />
            ) : (
              <>
                <p className="guide-message">
                  {pickingAlertType ? (
                    t.alertsAskType
                  ) : (
                    <NamedCopy text={t.guideHello} name={t.sentinelName} />
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
                        dismissPresent();
                        close();
                      }}
                    >
                      {t.guideLookHome}
                    </button>
                    <button
                      type="button"
                      className="option"
                      onClick={() => {
                        onPickCategory("job");
                        dismissPresent();
                        close();
                      }}
                    >
                      {t.guideLookJob}
                    </button>
                    <button
                      type="button"
                      className="option"
                      onClick={() => {
                        onPickCategory("both");
                        dismissPresent();
                        close();
                      }}
                    >
                      {t.guideLookBoth}
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
