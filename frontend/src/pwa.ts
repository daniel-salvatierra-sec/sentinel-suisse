export type BeforeInstallPromptEvent = Event & {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
};

export type InstallKind =
  | "ios"
  | "android-firefox"
  | "android"
  | "desktop-firefox"
  | "desktop-safari"
  | "desktop-chromium";

export type InstallSurface = {
  kind: InstallKind;
  browser: string;
  device: "pc" | "phone" | "ios";
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

export function detectInstallSurface(): InstallSurface {
  const ua = typeof navigator === "undefined" ? "" : navigator.userAgent;
  const iPadOs = navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1;
  const isIos = /iPhone|iPad|iPod/i.test(ua) || iPadOs;
  const isAndroid = /Android/i.test(ua);
  const isFirefox = /Firefox|FxiOS/i.test(ua);
  const isSafari =
    /Safari/i.test(ua) && !/Chrome|Chromium|Android|CriOS|FxiOS|Edg|OPR|SamsungBrowser/i.test(ua);

  let browser = "Chrome";
  if (isFirefox) browser = "Firefox";
  else if (/Edg/i.test(ua)) browser = "Edge";
  else if (/OPR|Opera/i.test(ua)) browser = "Opera";
  else if (/SamsungBrowser/i.test(ua)) browser = "Samsung Internet";
  else if (isSafari) browser = "Safari";

  if (isIos) return { kind: "ios", browser, device: "ios" };
  if (isAndroid && isFirefox) return { kind: "android-firefox", browser, device: "phone" };
  if (isAndroid) return { kind: "android", browser, device: "phone" };
  if (isFirefox) return { kind: "desktop-firefox", browser, device: "pc" };
  if (isSafari) return { kind: "desktop-safari", browser, device: "pc" };
  return { kind: "desktop-chromium", browser, device: "pc" };
}
