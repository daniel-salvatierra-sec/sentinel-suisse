import { useLayoutEffect, useRef, useState } from "react";
import { useWindowVirtualizer } from "@tanstack/react-virtual";
import type { Listing } from "../api";
import type { Messages } from "../i18n";
import {
  computeListingSignals,
  type ListingSignalContext,
} from "../listingSignals";
import { InfiniteScrollSentinel } from "./InfiniteScrollSentinel";
import { ListingCard } from "./ListingCard";

type Props = {
  listings: Listing[];
  t: Messages;
  focusId: number | null;
  onSelect: (id: number) => void;
  hasMore: boolean;
  loadingMore: boolean;
  onLoadMore: () => void;
  signalContext: ListingSignalContext;
};

/** Window-scrolled virtual list — only mounts visible cards (+ overscan). */
export function VirtualizedListingList({
  listings,
  t,
  focusId,
  onSelect,
  hasMore,
  loadingMore,
  onLoadMore,
  signalContext,
}: Props) {
  const listRef = useRef<HTMLDivElement | null>(null);
  const [scrollMargin, setScrollMargin] = useState(0);

  useLayoutEffect(() => {
    setScrollMargin(listRef.current?.offsetTop ?? 0);
  }, []);

  const virtualizer = useWindowVirtualizer({
    count: listings.length,
    estimateSize: () => 140,
    overscan: 6,
    scrollMargin,
    useFlushSync: false,
  });

  return (
    <div ref={listRef} className="virtual-list">
      <div
        className="virtual-list-inner"
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: "100%",
          position: "relative",
        }}
      >
        {virtualizer.getVirtualItems().map((item) => {
          const listing = listings[item.index];
          if (!listing) return null;
          return (
            <div
              key={listing.id}
              data-index={item.index}
              ref={virtualizer.measureElement}
              className="virtual-list-item"
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "100%",
                transform: `translateY(${item.start - scrollMargin}px)`,
              }}
            >
              <ListingCard
                listing={listing}
                t={t}
                selected={listing.id === focusId}
                onSelect={() => onSelect(listing.id)}
                signals={computeListingSignals(listing, listings, signalContext)}
              />
            </div>
          );
        })}
      </div>

      {hasMore && (
        <>
          {loadingMore && <p className="empty scroll-loading">{t.loading}</p>}
          <InfiniteScrollSentinel
            enabled={hasMore && !loadingMore}
            loading={loadingMore}
            onVisible={onLoadMore}
          />
        </>
      )}
      {!hasMore && <p className="empty end-of-results">{t.endOfResults}</p>}
    </div>
  );
}
