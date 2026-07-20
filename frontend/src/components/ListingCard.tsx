import { useState, type MouseEvent } from "react";
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
  const [detailOpen, setDetailOpen] = useState(false);
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

  const openListing = (event: MouseEvent) => {
    event.stopPropagation();
    if (isDemo) {
      setDetailOpen(true);
      return;
    }
    window.open(listing.source_url, "_blank", "noopener,noreferrer");
  };

  return (
    <>
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
        <button type="button" className="listing-open-btn" onClick={openListing}>
          {t.openSource}
        </button>
        <a href={mapsDirectionsUrl(coords)} target="_blank" rel="noreferrer" onClick={(e) => e.stopPropagation()}>
          {t.route}
        </a>
      </article>

      {detailOpen && (
        <div
          className="modal-backdrop sheet-backdrop"
          role="presentation"
          onClick={() => setDetailOpen(false)}
        >
          <div
            className="guide-sheet listing-detail-sheet"
            role="dialog"
            aria-labelledby={`listing-detail-${listing.id}`}
            onClick={(event) => event.stopPropagation()}
          >
            <div className="guide-sheet-handle" aria-hidden />
            <div className="listing-card-title-row">
              <h2 id={`listing-detail-${listing.id}`} className="guide-title">
                {listing.title}
              </h2>
              {isDemo ? <span className="listing-demo-badge">{t.demoBadge}</span> : null}
            </div>
            <p className="meta listing-detail-meta">
              {listing.location ?? "—"}
              {listing.price != null && listing.listing_type === "housing" && (
                <> · {listing.price} {t.priceMonthly}</>
              )}
              {listing.workload_min != null && listing.listing_type === "job" && (
                <>
                  {" "}
                  · {listing.workload_min}
                  {listing.workload_max != null ? `–${listing.workload_max}` : "+"}%
                </>
              )}
            </p>
            <p className="listing-detail-body">
              {listing.description?.trim() || t.listingNoDescription}
            </p>
            {isDemo ? <p className="listing-detail-demo-note">{t.listingDemoNote}</p> : null}
            <div className="listing-detail-actions">
              <a
                className="secondary-btn share-link-btn"
                href={mapsDirectionsUrl(coords)}
                target="_blank"
                rel="noreferrer"
              >
                {t.route}
              </a>
              <button type="button" className="apply-btn" onClick={() => setDetailOpen(false)}>
                {t.guideClose}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
