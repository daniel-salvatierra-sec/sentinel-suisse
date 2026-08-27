/** Persist launch / share promo codes from ?promo= links. */

const STORAGE_KEY = "linkswiss.promo";

export function readStoredPromo(): string | null {
  try {
    const value = localStorage.getItem(STORAGE_KEY);
    return value?.trim() || null;
  } catch {
    return null;
  }
}

export function storePromo(code: string): void {
  const trimmed = code.trim();
  if (!trimmed) return;
  try {
    localStorage.setItem(STORAGE_KEY, trimmed);
  } catch {
    /* ignore quota / private mode */
  }
}

/** Capture ?promo=CODE from the URL and remember it for checkout + share. */
export function capturePromoFromUrl(search: string = window.location.search): string | null {
  const params = new URLSearchParams(search);
  const code = params.get("promo")?.trim();
  if (!code) {
    return readStoredPromo();
  }
  storePromo(code);
  return code;
}

export function promoShareUrl(origin: string, code: string | null | undefined): string {
  const base = origin.replace(/\/$/, "") || "https://linkswiss.ch";
  if (!code?.trim()) {
    return base;
  }
  return `${base}/?promo=${encodeURIComponent(code.trim())}`;
}
