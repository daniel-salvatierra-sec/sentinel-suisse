import type { Listing } from "../api";
import type { Lang, Messages } from "../i18n";
import {
  computeListingSignals,
  type ListingSignalContext,
} from "../listingSignals";
import { ListingCard } from "./ListingCard";

type Props = {
  listings: Listing[];
  t: Messages;
  lang: Lang;
  focusId: number | null;
  onSelect: (id: number) => void;
  hasMore: boolean;
  loadingMore: boolean;
  onLoadMore: () => void;
  signalContext: ListingSignalContext;
};

export function VirtualizedListingList({
  listings,
  t,
  lang,
  focusId,
  onSelect,
  hasMore,
  loadingMore,
  onLoadMore,
  signalContext,
}: Props) {
  return (
    <div className="listing-list">
      {listings.map((listing) => (
        <ListingCard
          key={listing.id}
          listing={listing}
          t={t}
          lang={lang}
          selected={listing.id === focusId}
          onSelect={() => onSelect(listing.id)}
          onShowOnMap={() => onSelect(listing.id)}
          signals={computeListingSignals(listing, listings, signalContext)}
        />
      ))}
      {hasMore ? (
        <button
          type="button"
          className="primary-btn load-more-btn"
          disabled={loadingMore}
          onClick={onLoadMore}
        >
          {loadingMore ? t.loading : t.loadMore}
        </button>
      ) : (
        <p className="end-of-results">{t.endOfResults}</p>
      )}
    </div>
  );
}
