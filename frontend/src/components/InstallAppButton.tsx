import { useEffect, useState } from "react";
import type { Messages } from "../i18n";
import {
  detectInstallSurface,
  type BeforeInstallPromptEvent,
  type InstallKind,
} from "../pwa";

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

function stepsFor(kind: InstallKind, t: Messages): string {
  switch (kind) {
    case "ios":
      return t.installIosHint;
    case "android-firefox":
      return t.installAndroidFirefoxHint;
    case "android":
      return t.installAndroidHint;
    case "desktop-firefox":
      return t.installDesktopFirefoxHint;
    case "desktop-safari":
      return t.installDesktopSafariHint;
    default:
      return t.installDesktopHint;
  }
}

function currentPrompt(): BeforeInstallPromptEvent | null {
  return window.__pwaInstall ?? null;
}

/** Prompt to pin LinkSwiss on the home screen (PWA install / manual steps). */
export function InstallAppButton({ t }: Props) {
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const [hidden, setHidden] = useState(() => isStandalone());
  const [deferred, setDeferred] = useState<BeforeInstallPromptEvent | null>(currentPrompt);
  const surface = detectInstallSurface();
  const deviceLabel =
    surface.device === "ios" ? t.installDeviceIos : surface.device === "phone" ? t.installDevicePhone : t.installDevicePc;

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

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.origin);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  };

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
            <p className="install-detected">
              {surface.browser} · {deviceLabel}
            </p>
            <p className="guide-message">{t.installDesc}</p>
            <p className="install-steps">{stepsFor(surface.kind, t)}</p>
            <button type="button" className="secondary-btn share-link-btn" onClick={() => void copyLink()}>
              {copied ? t.qrCopied : t.qrCopy}
            </button>
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
