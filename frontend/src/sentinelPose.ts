export type SentinelPose =
  | "idle"
  | "sit"
  | "wave"
  | "think"
  | "search"
  | "account"
  | "ask"
  | "help"
  | "listen"
  | "found";

const POSE_NAMES =
  "idle|sit|wave|think|search|account|ask|help|listen|found";
const GESTURE_RE = new RegExp(`\\[\\[gesture:(${POSE_NAMES})\\]\\]`, "gi");

const POSE_SRC: Record<SentinelPose, string> = {
  idle: "/hub/sentinel-figure.png?v=4",
  sit: "/hub/sentinel-figure-sit.png?v=3",
  wave: "/hub/sentinel-figure-wave.png?v=1",
  think: "/hub/sentinel-figure-think.png?v=2",
  search: "/hub/sentinel-figure-search.png?v=2",
  account: "/hub/sentinel-figure-account.png?v=3",
  ask: "/hub/sentinel-figure-ask.png?v=1",
  help: "/hub/sentinel-figure-help.png?v=1",
  listen: "/hub/sentinel-figure-listen.png?v=1",
  found: "/hub/sentinel-figure-found.png?v=1",
};

export const ALL_POSES = Object.keys(POSE_SRC) as SentinelPose[];

export function poseSrc(pose: SentinelPose): string {
  return POSE_SRC[pose];
}

export function extractGesture(raw: string): { text: string; pose: SentinelPose | null } {
  const tagged = new RegExp(`\\[\\[gesture:(${POSE_NAMES})\\]\\]`, "i").exec(raw);
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
  if (/(hola|hello|bonjour|hallo|oi\b|buenas)/.test(n)) {
    return "wave";
  }
  if (/(encontre|encontraste|trouve|gefunden|found|me gusta|este anuncio|abrir|voir|open)/.test(n)) {
    return "found";
  }
  if (/(ayud|aider|helfen|help|ajuda|alerta|alert|aviso|whatsapp)/.test(n)) {
    return "help";
  }
  if (
    /(cuenta|compte|konto|account|premium|suscri|abonn|inscri|login|sesion)/.test(n)
  ) {
    return "account";
  }
  if (/(nada|empty|ningun|aucun|keine|sem resultado|no hay|0 anunc)/.test(n)) {
    return "think";
  }
  if (/(mapa|carte|karte|map\b)/.test(n)) {
    return "search";
  }
  if (
    /(buscar|recherche|search|casa|trabajo|logement|emploi|job|vivienda|pisos|ciudad|ville|city|ginebra|geneve|zurich|lausanne)/.test(
      n,
    )
  ) {
    return "search";
  }
  if (/(pregunt|question|dime|tell me|erzahl|espera|wait)/.test(n)) {
    return "listen";
  }
  return null;
}
