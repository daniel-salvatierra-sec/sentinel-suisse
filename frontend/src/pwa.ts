export type BeforeInstallPromptEvent = Event & {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
};

declare global {
  interface Window {
    __pwaInstall?: BeforeInstallPromptEvent | null;
  }
}

/** Capture the native install event as early as possible (it can fire before React mounts). */
export function listenForInstallPrompt(): void {
  window.__pwaInstall = window.__pwaInstall ?? null;
  window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault();
    window.__pwaInstall = event as BeforeInstallPromptEvent;
    window.dispatchEvent(new Event("pwa-install-ready"));
  });
}
