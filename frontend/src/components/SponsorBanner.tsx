import { useEffect, useRef } from "react";
import type { SponsorAd } from "../api";
import { recordSponsorEvent } from "../api";
import type { Messages } from "../i18n";

type Props = {
  sponsors: SponsorAd[];
  t: Messages;
};

export function SponsorBanner({ sponsors, t }: Props) {
  const logged = useRef<Set<number>>(new Set());

  useEffect(() => {
    for (const item of sponsors) {
      if (logged.current.has(item.id)) {
        continue;
      }
      logged.current.add(item.id);
      void recordSponsorEvent(item.id, "impression");
    }
  }, [sponsors]);

  if (sponsors.length === 0) {
    return null;
  }

  return (
    <div className="sponsor-strip" role="complementary" aria-label={t.sponsorSectionLabel}>
      {sponsors.map((item) => (
        <a
          key={item.id}
          className="sponsor-card"
          href={item.target_url}
          target="_blank"
          rel="noopener noreferrer sponsored"
          onClick={() => {
            void recordSponsorEvent(item.id, "click");
          }}
        >
          <span className="sponsor-badge">{t.sponsorLabel}</span>
          {item.image_url ? (
            <img className="sponsor-image" src={item.image_url} alt={item.headline ?? t.sponsorLabel} />
          ) : null}
          {item.headline ? <span className="sponsor-headline">{item.headline}</span> : null}
        </a>
      ))}
    </div>
  );
}
