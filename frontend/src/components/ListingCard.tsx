import type { Listing } from "../api";
import { coordsForLocation, mapsDirectionsUrl } from "../geo";
import type { Messages } from "../i18n";

type Props = {
  listing: Listing;
  t: Messages;
  selected: boolean;
  onSelect: () => void;
};

export function ListingCard({ listing, t, selected, onSelect }: Props) {
  const coords = coordsForLocation(listing.location);
  const isDemo = Boolean(listing.is_demo);
  return (
    <article
      className={`listing-card${isDemo ? " is-demo" : ""}`}
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
      {isDemo ? (
        <span className="listing-demo-note">{t.demoLinkUnavailable}</span>
      ) : (
        <a href={listing.source_url} target="_blank" rel="noreferrer" onClick={(e) => e.stopPropagation()}>
          {t.openSource}
        </a>
      )}
      <a href={mapsDirectionsUrl(coords)} target="_blank" rel="noreferrer" onClick={(e) => e.stopPropagation()}>
        {t.route}
      </a>
    </article>
  );
}
