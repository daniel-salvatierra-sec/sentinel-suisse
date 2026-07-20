import type { Listing } from "../api";
import { coordsForLocation, mapsDirectionsUrl } from "../geo";
import type { Messages } from "../i18n";
import type { ListingSignals } from "../listingSignals";

type Props = {
  listing: Listing;
  t: Messages;
  selected: boolean;
  onSelect: () => void;
  signals?: ListingSignals;
};

export function ListingCard({ listing, t, selected, onSelect, signals }: Props) {
  const coords = coordsForLocation(listing.location);
  const isDemo = Boolean(listing.is_demo);
  const goodPrice = Boolean(signals?.goodPrice);
  const goodMatch = Boolean(signals?.goodMatch);
  const accentClass = [
    "listing-card",
    isDemo ? "is-demo" : "",
    goodPrice ? "signal-price" : "",
    goodMatch ? "signal-match" : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <article
      className={accentClass}
      style={selected ? { outline: "2px solid var(--jet)" } : undefined}
      onClick={onSelect}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") onSelect();
      }}
      role="button"
      tabIndex={0}
    >
      <div className="listing-card-title-row">
        <h3>{listing.title}</h3>
        {isDemo ? <span className="listing-demo-badge">{t.demoBadge}</span> : null}
      </div>
      <div className="meta">
        {listing.location ?? "—"}
        {listing.price != null && listing.listing_type === "housing" && (
          <> · {listing.price} {t.priceMonthly}</>
        )}
      </div>
      {(goodPrice || goodMatch) && (
        <div className="listing-signals" aria-label={t.signalLabel}>
          {goodPrice ? <span className="signal signal-price-tag">{t.signalGoodPrice}</span> : null}
          {goodMatch ? <span className="signal signal-match-tag">{t.signalGoodMatch}</span> : null}
        </div>
      )}
      {!isDemo ? (
        <a href={listing.source_url} target="_blank" rel="noreferrer" onClick={(e) => e.stopPropagation()}>
          {t.openSource}
        </a>
      ) : null}
      <a href={mapsDirectionsUrl(coords)} target="_blank" rel="noreferrer" onClick={(e) => e.stopPropagation()}>
        {t.route}
      </a>
    </article>
  );
}
