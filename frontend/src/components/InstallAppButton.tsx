import { useEffect, useState } from "react";
import type { Messages } from "../i18n";

type Props = {
  t: Messages;
};

type BeforeInstallPromptEvent = Event & {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
};

function isStandalone(): boolean {
  if (typeof window === "undefined") return false;
  const media = window.matchMedia("(display-mode: standalone)").matches;
  const ios = "standalone" in window.navigator && Boolean((window.navigator as Navigator & { standalone?: boolean }).standalone);
  return media || ios;
}

function isIos(): boolean {
  if (typeof navigator === "undefined") return false;
  return /iphone|ipad|ipod/i.test(navigator.userAgent);
}

/** Prompt to pin LinkSwiss on the home screen (PWA install / iOS instructions). */
export function InstallAppButton({ t }: Props) {
  const [open, setOpen] = useState(false);
  const [hidden, setHidden] = useState(() => isStandalone());
  const [deferred, setDeferred] = useState<BeforeInstallPromptEvent | null>(null);

  useEffect(() => {
    if (isStandalone()) {
      setHidden(true);
      return;
    }
    const onPrompt = (event: Event) => {
      event.preventDefault();
      setDeferred(event as BeforeInstallPromptEvent);
    };
    const onInstalled = () => setHidden(true);
    window.addEventListener("beforeinstallprompt", onPrompt);
    window.addEventListener("appinstalled", onInstalled);
    return () => {
      window.removeEventListener("beforeinstallprompt", onPrompt);
      window.removeEventListener("appinstalled", onInstalled);
    };
  }, []);

  if (hidden) return null;

  const onClick = async () => {
    if (deferred) {
      await deferred.prompt();
      const choice = await deferred.userChoice;
      setDeferred(null);
      if (choice.outcome === "accepted") setHidden(true);
      return;
    }
    setOpen(true);
  };

  return (
    <>
      <button type="button" className="install-app-trigger" onClick={() => void onClick()}>
        {t.installApp}
      </button>
      {open && (
        <div className="modal-backdrop sheet-backdrop" role="presentation" onClick={() => setOpen(false)}>
          <div
            className="guide-sheet share-sheet"
            role="dialog"
            aria-labelledby="install-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="guide-sheet-handle" aria-hidden />
            <h2 id="install-title" className="guide-title">
              {t.installTitle}
            </h2>
            <p className="guide-message">{t.installDesc}</p>
            {isIos() ? <p className="guide-message">{t.installIosHint}</p> : null}
            <div className="guide-nav">
              <button type="button" className="guide-skip" onClick={() => setOpen(false)}>
                {t.guideClose}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
