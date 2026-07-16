import { useEffect, useState } from "react";
import type { ListingType } from "../api";
import { loadGuideSeen, saveGuideSeen } from "../guideStorage";
import type { Messages } from "../i18n";
import { FireflyBuddy } from "./FireflyBuddy";

type Props = {
  t: Messages;
  zone: ListingType;
  searching: boolean;
  onPickCategory: (type: ListingType) => void;
  onOpenAlerts: () => void;
  onStartSearch: (location: string) => void;
  onOpenMap: () => void;
};

type Step = "welcome" | "category" | "search" | "map" | "alerts" | "done";

const STEPS: Step[] = ["welcome", "category", "search", "map", "alerts", "done"];

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
  const [step, setStep] = useState<Step>("welcome");

  useEffect(() => {
    if (!loadGuideSeen()) {
      setOpen(true);
    }
  }, []);

  const close = () => {
    saveGuideSeen();
    setOpen(false);
    setStep("welcome");
  };

  const stepIndex = STEPS.indexOf(step);

  const goNext = () => {
    const next = STEPS[stepIndex + 1];
    if (next) setStep(next);
  };

  const goBack = () => {
    const prev = STEPS[stepIndex - 1];
    if (prev) setStep(prev);
  };

  const stepMessage = (): string => {
    switch (step) {
      case "welcome":
        return t.guideHello;
      case "category":
        return t.guideStepCategory;
      case "search":
        return t.guideStepSearch;
      case "map":
        return t.guideStepMap;
      case "alerts":
        return t.guideStepAlerts;
      case "done":
        return t.guideStepDone;
      default:
        return t.guideHello;
    }
  };

  return (
    <>
      <FireflyBuddy
        zone={zone}
        searching={searching}
        label={t.fireflyLabel}
        onOpen={() => setOpen(true)}
      />
      {open && (
        <div className="modal-backdrop" role="presentation" onClick={close}>
          <div
            className="guide-modal"
            role="dialog"
            aria-labelledby="guide-title"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="guide-header">
              <span className="guide-avatar firefly-avatar" aria-hidden>
                ✦
              </span>
              <div>
                <h2 id="guide-title" className="guide-title">
                  {t.guide}
                </h2>
                <p className="guide-step-label">
                  {stepIndex + 1} / {STEPS.length}
                </p>
              </div>
            </div>
            <div className="guide-dots" aria-hidden>
              {STEPS.map((item, index) => (
                <span key={item} className={index <= stepIndex ? "active" : ""} />
              ))}
            </div>
            <p className="guide-message">{stepMessage()}</p>

            {step === "category" && (
              <div className="guide-actions">
                <button
                  type="button"
                  className="option"
                  onClick={() => {
                    onPickCategory("housing");
                    goNext();
                  }}
                >
                  {t.guideHousing}
                </button>
                <button
                  type="button"
                  className="option"
                  onClick={() => {
                    onPickCategory("job");
                    goNext();
                  }}
                >
                  {t.guideJob}
                </button>
              </div>
            )}

            {step === "search" && (
              <button
                type="button"
                className="primary-btn guide-cta"
                onClick={() => {
                  onStartSearch("Geneva");
                  goNext();
                }}
              >
                {t.guideSearchCta}
              </button>
            )}

            {step === "map" && (
              <button
                type="button"
                className="primary-btn guide-cta"
                onClick={() => {
                  onOpenMap();
                  goNext();
                }}
              >
                {t.guideMapCta}
              </button>
            )}

            {step === "alerts" && (
              <button
                type="button"
                className="primary-btn guide-cta"
                onClick={() => {
                  onOpenAlerts();
                  goNext();
                }}
              >
                {t.guideAlertsCta}
              </button>
            )}

            <div className="guide-nav">
              {stepIndex > 0 && step !== "done" && (
                <button type="button" className="secondary-btn" onClick={goBack}>
                  {t.guideBack}
                </button>
              )}
              {step === "welcome" && (
                <button type="button" className="primary-btn" onClick={goNext}>
                  {t.guideNext}
                </button>
              )}
              {step === "done" && (
                <button type="button" className="primary-btn" style={{ flex: 1 }} onClick={close}>
                  {t.guideClose}
                </button>
              )}
              {step !== "done" && (
                <button type="button" className="guide-skip" onClick={close}>
                  {t.guideSkip}
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
