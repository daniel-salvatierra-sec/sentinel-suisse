const GUIDE_SEEN_KEY = "linkswiss-guide-seen";
const NUDGE_SEEN_KEY = "linkswiss-bot-nudge-seen";

export function loadGuideSeen(): boolean {
  return localStorage.getItem(GUIDE_SEEN_KEY) === "1";
}

export function saveGuideSeen(): void {
  localStorage.setItem(GUIDE_SEEN_KEY, "1");
}

export function loadNudgeSeen(): boolean {
  return localStorage.getItem(NUDGE_SEEN_KEY) === "1";
}

export function saveNudgeSeen(): void {
  localStorage.setItem(NUDGE_SEEN_KEY, "1");
}
