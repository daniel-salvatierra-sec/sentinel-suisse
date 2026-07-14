import L from "leaflet";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import { useEffect } from "react";
import type { Listing } from "../api";
import { coordsForLocation } from "../geo";
import "leaflet/dist/leaflet.css";

const defaultIcon = L.icon({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});
L.Marker.prototype.options.icon = defaultIcon;

type Props = {
  listings: Listing[];
  focusId: number | null;
  searchQuery?: string;
};

function mapCenter(
  listings: Listing[],
  focusId: number | null,
  searchQuery?: string,
): [number, number] {
  const focusListing = listings.find((item) => item.id === focusId);
  if (focusListing?.location) {
    return coordsForLocation(focusListing.location);
  }
  if (searchQuery?.trim()) {
    return coordsForLocation(searchQuery.trim());
  }
  return coordsForLocation(listings[0]?.location ?? null);
}

function MapFocus({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  return null;
}

export function MapView({ listings, focusId, searchQuery }: Props) {
  const focusListing = listings.find((item) => item.id === focusId);
  const center = mapCenter(listings, focusId, searchQuery);

  return (
    <div className="map-wrap">
      <MapContainer center={center} zoom={12} style={{ height: "100%", width: "100%" }} scrollWheelZoom={false}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MapFocus center={center} zoom={focusListing || searchQuery?.trim() ? 13 : 8} />
        {listings.map((listing) => {
          const coords = coordsForLocation(listing.location);
          return (
            <Marker key={listing.id} position={coords}>
              <Popup>
                <strong>{listing.title}</strong>
                <br />
                {listing.location}
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}
