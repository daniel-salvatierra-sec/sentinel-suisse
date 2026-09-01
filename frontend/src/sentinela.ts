import type { Messages } from "./i18n";

export type SentinelaActionType =
  | "set_mode"
  | "apply_filters"
  | "run_search"
  | "switch_tab"
  | "open_listing"
  | "highlight_listings"
  | "focus_map"
  | "compose_alert"
  | "point_to"
  | "suggest_chips"
  | "open_guide";

export type SentinelaAction = {
  type: SentinelaActionType;
  payload: Record<string, unknown>;
};

export type SentinelaSayId =
  | "filtered"
  | "empty"
  | "need_city"
  | "unknown_city"
  | "alert"
  | "open_first"
  | "open_listing"
  | "map"
  | "out_of_scope"
  | "guide";

export type SentinelaTurn = {
  actions: SentinelaAction[];
  say_id: SentinelaSayId;
  slots: Record<string, string>;
  chips: string[];
};

export type SentinelaUiContext = {
  tab: string;
  mode: "housing" | "job";
  zone: "CH" | "FR" | "DE" | "IT";
  query: string;
  rooms: string;
  price_max: string;
  has_session: boolean;
  result_count: number;
  open_listing: { id: number; location: string | null; price: number | null } | null;
};

export function formatSentinelaSay(
  t: Messages,
  sayId: SentinelaSayId,
  slots: Record<string, string>,
  n = 0,
): string {
  const fill = (template: string) =>
    template
      .replaceAll("{ville}", slots.ville ?? "")
      .replaceAll("{pieces}", slots.pieces ?? "")
      .replaceAll("{prix}", slots.prix ?? "")
      .replaceAll("{lieu}", slots.lieu ?? slots.ville ?? "")
      .replaceAll("{n}", String(n));

  if (sayId === "filtered" && n === 0) {
    return t.sentinelaSayEmpty;
  }
  const map: Record<SentinelaSayId, string> = {
    filtered: t.sentinelaSayResults,
    empty: t.sentinelaSayEmpty,
    need_city: t.sentinelaSayNeedCity,
    unknown_city: t.sentinelaSayUnknownCity,
    alert: t.sentinelaSayAlert,
    open_first: t.sentinelaSayOpen,
    open_listing: t.sentinelaSayOpen,
    map: t.sentinelaSayMap,
    out_of_scope: t.sentinelaSayOutOfScope,
    guide: t.sentinelaSayGuide,
  };
  return fill(map[sayId] ?? t.sentinelaSayOutOfScope);
}

export function sentinelaChipLabel(t: Messages, id: string): string {
  const labels: Record<string, string> = {
    see_first: t.sentinelaChipSeeFirst,
    create_alert: t.sentinelaChipAlert,
    on_map: t.sentinelaChipMap,
    how_apply: t.sentinelaChipHowApply,
    keep_looking: t.sentinelaChipKeepLooking,
    look_home: t.guideLookHome,
    look_job: t.guideLookJob,
  };
  return labels[id] ?? id;
}

export const SENTINELA_CHIP_ACTIONS: Record<string, SentinelaAction[]> = {
  see_first: [{ type: "open_listing", payload: { which: "first" } }],
  create_alert: [{ type: "compose_alert", payload: {} }],
  on_map: [
    { type: "switch_tab", payload: { tab: "map" } },
    { type: "focus_map", payload: {} },
  ],
  keep_looking: [{ type: "switch_tab", payload: { tab: "list" } }],
  look_home: [{ type: "set_mode", payload: { mode: "housing" } }],
  look_job: [{ type: "set_mode", payload: { mode: "job" } }],
  how_apply: [{ type: "open_guide", payload: {} }],
};
