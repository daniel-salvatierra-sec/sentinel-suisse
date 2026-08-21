import { useEffect, useState } from "react";
import type { Messages } from "../i18n";
import type { BeforeInstallPromptEvent } from "../pwa";

type Props = {
  t: Messages;
};

function isStandalone(): boolean {
  if (typeof window === "undefined") return false;
  const media = window.matchMedia("(display-mode: standalone)").matches;
  const ios =
    "standalone" in window.navigator &&
    Boolean((window.navigator as Navigator & { standalone?: boolean }).standalone);
  return media || ios;
}

function installHint(t: Messages): string {
  const ua = typeof navigator === "undefined" ? "" : navigator.userAgent;
  if (/iphone|ipad|ipod/i.test(ua)) return t.installIosHint;
  if (/android/i.test(ua)) return t.installAndroidHint;
  return t.installDesktopHint;
}

function currentPrompt(): BeforeInstallPromptEvent | null {
  return window.__pwaInstall ?? null;
}

/** Prompt to pin LinkSwiss on the home screen (PWA install / manual steps). */
export function InstallAppButton({ t }: Props) {
  const [open, setOpen] = useState(false);
  const [hidden, setHidden] = useState(() => isStandalone());
  const [deferred, setDeferred] = useState<BeforeInstallPromptEvent | null>(currentPrompt);

  useEffect(() => {
    if (isStandalone()) {
      setHidden(true);
      return;
    }
    const syncPrompt = () => setDeferred(currentPrompt());
    const onPrompt = (event: Event) => {
      event.preventDefault();
      window.__pwaInstall = event as BeforeInstallPromptEvent;
      setDeferred(event as BeforeInstallPromptEvent);
    };
    const onInstalled = () => {
      window.__pwaInstall = null;
      setHidden(true);
    };
    syncPrompt();
    window.addEventListener("beforeinstallprompt", onPrompt);
    window.addEventListener("pwa-install-ready", syncPrompt);
    window.addEventListener("appinstalled", onInstalled);
    return () => {
      window.removeEventListener("beforeinstallprompt", onPrompt);
      window.removeEventListener("pwa-install-ready", syncPrompt);
      window.removeEventListener("appinstalled", onInstalled);
    };
  }, []);

  if (hidden) return null;

  const onClick = async () => {
    const promptEvent = deferred ?? currentPrompt();
    if (promptEvent) {
      await promptEvent.prompt();
      const choice = await promptEvent.userChoice;
      window.__pwaInstall = null;
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
            <p className="guide-message">{installHint(t)}</p>
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
