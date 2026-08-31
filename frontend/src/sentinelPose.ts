export type SentinelPose = "idle" | "account" | "search" | "think";

const GESTURE_RE = /\[\[gesture:(idle|account|search|think)\]\]/gi;

const POSE_SRC: Record<SentinelPose, string> = {
  idle: "/hub/sentinel-figure.png?v=3",
  account: "/hub/sentinel-figure-account.png?v=1",
  search: "/hub/sentinel-figure-search.png?v=1",
  think: "/hub/sentinel-figure-think.png?v=1",
};

export function poseSrc(pose: SentinelPose): string {
  return POSE_SRC[pose];
}

export function extractGesture(raw: string): { text: string; pose: SentinelPose | null } {
  const tagged = /\[\[gesture:(idle|account|search|think)\]\]/i.exec(raw);
  const text = raw.replace(GESTURE_RE, "").trim();
  if (tagged) {
    return { text, pose: tagged[1].toLowerCase() as SentinelPose };
  }
  return { text, pose: inferPoseFromText(text) };
}

export function inferPoseFromText(text: string): SentinelPose | null {
  const n = text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
  if (
    /(cuenta|compte|konto|account|premium|suscri|abonn|inscri|login|sesion)/.test(n)
  ) {
    return "account";
  }
  if (
    /(alerta|alert|aviso|whatsapp|buscar|recherche|search|casa|trabajo|logement|emploi|job|vivienda|pisos)/.test(
      n,
    )
  ) {
    return "search";
  }
  return null;
}
