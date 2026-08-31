const GUIDE_SEEN_KEY = "linkswiss-guide-seen";
const NUDGE_SEEN_KEY = "linkswiss-bot-nudge-v2";

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

const ASSISTANT_CHAT_KEY = "linkswiss-assistant-chat";

export function loadAssistantMessages(): { role: "user" | "assistant"; content: string }[] {
  try {
    const raw = sessionStorage.getItem(ASSISTANT_CHAT_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(
      (item): item is { role: "user" | "assistant"; content: string } =>
        Boolean(item) &&
        (item.role === "user" || item.role === "assistant") &&
        typeof item.content === "string",
    );
  } catch {
    return [];
  }
}

export function saveAssistantMessages(
  messages: { role: "user" | "assistant"; content: string }[],
): void {
  sessionStorage.setItem(ASSISTANT_CHAT_KEY, JSON.stringify(messages.slice(-24)));
}
