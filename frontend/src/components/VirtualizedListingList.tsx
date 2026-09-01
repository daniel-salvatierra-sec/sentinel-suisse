import type { AcceptProfile, Listing } from "../api";
import { acceptReasons } from "../acceptProfile";
import type { Messages } from "../i18n";
import {
  computeListingSignals,
  type ListingSignalContext,
} from "../listingSignals";
import { ListingCard } from "./ListingCard";

type Props = {
  listings: Listing[];
  t: Messages;
  focusId: number | null;
  onSelect: (id: number) => void;
  onNeedPremium?: () => void;
  hasMore: boolean;
  loadingMore: boolean;
  onLoadMore: () => void;
  signalContext: ListingSignalContext;
  acceptProfile?: AcceptProfile | null;
};

export function VirtualizedListingList({
  listings,
  t,
  focusId,
  onSelect,
  onNeedPremium,
  hasMore,
  loadingMore,
  onLoadMore,
  signalContext,
  acceptProfile,
}: Props) {
  return (
    <div className="listing-list">
      {listings.map((listing) => (
        <ListingCard
          key={listing.id}
          listing={listing}
          t={t}
          selected={listing.id === focusId}
          onSelect={() => onSelect(listing.id)}
          onShowOnMap={() => onSelect(listing.id)}
          onNeedPremium={onNeedPremium}
          signals={computeListingSignals(listing, listings, signalContext)}
          reasons={acceptReasons(listing, acceptProfile, t)}
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
