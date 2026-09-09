import { useEffect, useState } from "react";
import { poseSrc, ALL_POSES, type SentinelPose } from "../sentinelPose";

const POINT_HOLD_MS = 5000;
const IDLE_BEATS: SentinelPose[] = ["sit", "wave", "listen", "think", "found", "help", "sit"];
const IDLE_BEAT_MS = 2400;

if (typeof window !== "undefined") {
  for (const pose of ALL_POSES) {
    const preload = new Image();
    preload.src = poseSrc(pose);
  }
}

export type HintChoice = {
  id: string;
  label: string;
  quiet?: boolean;
};

type Props = {
  zone: "housing" | "job";
  pose?: SentinelPose;
  searching: boolean;
  talking?: boolean;
  sheetOpen?: boolean;
  dock?: "left" | "right";
  label: string;
  hint?: string;
  name?: string;
  hintChoices?: HintChoice[];
  onHintChoice?: (id: string) => void;
  onOpen: () => void;
};

const FACE_SRC = "/hub/sentinel-buddy.png?v=3";

function NamedCopy({ text, name }: { text: string; name: string }) {
  const parts = text.split("{name}");
  if (parts.length === 1) return <>{text}</>;
  return (
    <>
      {parts[0]}
      <strong className="sentinel-name">{name}</strong>
      {parts.slice(1).join(name)}
    </>
  );
}

export { NamedCopy };

/** Photoreal companion face — reused in sheet + alerts. */
export function SentinelFace({
  size = 40,
  zone,
}: {
  size?: number;
  zone?: "housing" | "job";
}) {
  return (
    <img
      className={`sentinel-face${zone ? ` zone-${zone}` : ""}`}
      src={FACE_SRC}
      alt=""
      width={size}
      height={size}
      draggable={false}
    />
  );
}

/** Full-body cutout: a gesture lasts 5s, then she stands at ease. */
export function SentinelBuddy({
  zone,
  pose = "idle",
  searching,
  talking = false,
  sheetOpen = false,
  dock = "right",
  label,
  hint,
  name = "Sentinela",
  hintChoices,
  onHintChoice,
  onOpen,
}: Props) {
  const live = talking;
  const choices = hintChoices?.length && onHintChoice ? hintChoices : null;
  const [shownPose, setShownPose] = useState<SentinelPose>(pose);
  const [hover, setHover] = useState(false);
  const [idleBeat, setIdleBeat] = useState<SentinelPose>("sit");

  useEffect(() => {
    setShownPose(pose);
    if (pose === "idle" || hint) return;
    const timer = window.setTimeout(() => setShownPose("idle"), POINT_HOLD_MS);
    return () => window.clearTimeout(timer);
  }, [pose, hint]);

  useEffect(() => {
    const canFidget = pose === "idle" && shownPose === "idle" && !hover && !sheetOpen;
    if (!canFidget) {
      return;
    }
    let i = 0;
    const tick = () => {
      i = (i + 1) % IDLE_BEATS.length;
      setIdleBeat(IDLE_BEATS[i]);
    };
    const first = window.setTimeout(tick, 900);
    const timer = window.setInterval(tick, IDLE_BEAT_MS);
    return () => {
      window.clearTimeout(first);
      window.clearInterval(timer);
    };
  }, [pose, shownPose, hover, sheetOpen]);

  const hoverPose: SentinelPose = dock === "left" ? "account" : "help";
  const displayPose = hover ? hoverPose : shownPose !== "idle" ? shownPose : idleBeat;

  return (
    <button
      type="button"
      className={`sentinel-buddy zone-${zone} pose-${displayPose} dock-${dock}${searching ? " searching" : ""}${talking || hint ? " talking" : ""}${sheetOpen ? " is-hidden" : ""}${hover ? " is-hover" : ""}`}
      aria-hidden={sheetOpen}
      onPointerEnter={(event) => {
        if (event.pointerType === "mouse") setHover(true);
      }}
      onPointerLeave={() => setHover(false)}
      onClick={(event) => {
        if ((event.target as HTMLElement).closest(".sentinel-hint-actions")) return;
        onOpen();
      }}
      aria-label={label}
    >
      {hint ? (
        <span className={`sentinel-hint${choices ? " has-choices" : ""}`}>
          <NamedCopy text={hint} name={name} />
          {choices ? (
            <span className="sentinel-hint-actions">
              {choices.map((choice) => (
                <span
                  key={choice.id}
                  className={`sentinel-hint-choice${choice.quiet ? " is-quiet" : ""}`}
                  role="button"
                  tabIndex={0}
                  onClick={(event) => {
                    event.stopPropagation();
                    onHintChoice?.(choice.id);
                  }}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      event.stopPropagation();
                      onHintChoice?.(choice.id);
                    }
                  }}
                >
                  {choice.label}
                </span>
              ))}
            </span>
          ) : null}
        </span>
      ) : null}
      <img
        className={`sentinel-figure${live ? " is-live" : ""}`}
        src={poseSrc(displayPose)}
        alt=""
        draggable={false}
      />
    </button>
  );
}
