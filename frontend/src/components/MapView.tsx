import L from "leaflet";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import { useEffect, useMemo } from "react";
import type { Listing } from "../api";
import {
  coordsForLocation,
  formatMapPrice,
  jitterCoords,
} from "../geo";
import type { Messages } from "../i18n";
import "leaflet/dist/leaflet.css";

type Props = {
  listings: Listing[];
  focusId: number | null;
  searchQuery?: string;
  t: Messages;
  onSelect?: (id: number) => void;
};

function pinLabel(listing: Listing, t: Messages): string {
  if (listing.listing_type === "housing" && listing.price != null) {
    return formatMapPrice(listing.price);
  }
  if (listing.listing_type === "job") {
    return t.job;
  }
  return "·";
}

function priceIcon(label: string, focused: boolean): L.DivIcon {
  return L.divIcon({
    className: "map-pin-wrap",
    html: `<span class="map-price-pin${focused ? " is-focus" : ""}">${label}</span>`,
    iconSize: [1, 1],
    iconAnchor: [0, 12],
  });
}

function FitListings({
  points,
  focusId,
}: {
  points: { id: number; coords: [number, number] }[];
  focusId: number | null;
}) {
  const map = useMap();
  useEffect(() => {
    if (points.length === 0) return;
    if (focusId != null) {
      const focus = points.find((p) => p.id === focusId);
      if (focus) {
        map.setView(focus.coords, Math.max(map.getZoom(), 13), { animate: true });
        return;
      }
    }
    if (points.length === 1) {
      map.setView(points[0].coords, 13);
      return;
    }
    const bounds = L.latLngBounds(points.map((p) => p.coords));
    map.fitBounds(bounds, { padding: [36, 36], maxZoom: 14 });
  }, [points, focusId, map]);
  return null;
}

export function MapView({ listings, focusId, searchQuery, t, onSelect }: Props) {
  const points = useMemo(() => {
    const byKey = new Map<string, number>();
    return listings.map((listing) => {
      const base = coordsForLocation(listing.location ?? searchQuery ?? null);
      const key = `${base[0].toFixed(4)},${base[1].toFixed(4)}`;
      const stackIndex = byKey.get(key) ?? 0;
      byKey.set(key, stackIndex + 1);
      const sameCount = listings.filter((other) => {
        const c = coordsForLocation(other.location);
        return c[0].toFixed(4) === base[0].toFixed(4) && c[1].toFixed(4) === base[1].toFixed(4);
      }).length;
      return {
        listing,
        coords: jitterCoords(base, stackIndex, sameCount),
      };
    });
  }, [listings, searchQuery]);

  const center = points[0]?.coords ?? coordsForLocation(searchQuery ?? null);

  return (
    <div className="map-wrap map-wrap-listings">
      <MapContainer
        center={center}
        zoom={12}
        style={{ height: "100%", width: "100%" }}
        scrollWheelZoom
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <FitListings
          points={points.map((p) => ({ id: p.listing.id, coords: p.coords }))}
          focusId={focusId}
        />
        {points.map(({ listing, coords }) => {
          const focused = listing.id === focusId;
          const label = pinLabel(listing, t);
          return (
            <Marker
              key={listing.id}
              position={coords}
              icon={priceIcon(label, focused)}
              eventHandlers={{
                click: () => onSelect?.(listing.id),
              }}
            >
              <Popup>
                <strong>{listing.title}</strong>
                <br />
                {listing.location}
                {listing.price != null && listing.listing_type === "housing" ? (
                  <>
                    <br />
                    {formatMapPrice(listing.price)}
                  </>
                ) : null}
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}
