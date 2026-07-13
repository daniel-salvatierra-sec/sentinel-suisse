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
  return (
    <article
      className="listing-card"
      style={selected ? { outline: "2px solid var(--jet)" } : undefined}
      onClick={onSelect}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") onSelect();
      }}
      role="button"
      tabIndex={0}
    >
      <h3>{listing.title}</h3>
      <div className="meta">
        {listing.location ?? "—"}
        {listing.price != null && listing.listing_type === "housing" && (
          <> · {listing.price} {t.priceMonthly}</>
        )}
      </div>
      <a href={listing.source_url} target="_blank" rel="noreferrer" onClick={(e) => e.stopPropagation()}>
        {t.openSource}
      </a>
      <a href={mapsDirectionsUrl(coords)} target="_blank" rel="noreferrer" onClick={(e) => e.stopPropagation()}>
        {t.route}
      </a>
    </article>
  );
}
