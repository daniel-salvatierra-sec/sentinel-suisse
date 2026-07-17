const GUIDE_SEEN_KEY = "linkswiss-guide-seen";

export function loadGuideSeen(): boolean {
  return localStorage.getItem(GUIDE_SEEN_KEY) === "1";
}

export function saveGuideSeen(): void {
  localStorage.setItem(GUIDE_SEEN_KEY, "1");
}
