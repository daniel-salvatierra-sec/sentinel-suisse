export type ListingType = "housing" | "job";

export type Listing = {
  id: number;
  title: string;
  location: string | null;
  price: number | null;
  listing_type: ListingType;
  source_url: string;
  description?: string | null;
};

export async function searchListings(params: {
  listing_type: ListingType;
  location?: string;
}): Promise<Listing[]> {
  const query = new URLSearchParams();
  query.set("listing_type", params.listing_type);
  if (params.location?.trim()) {
    query.set("location", params.location.trim());
  }
  const response = await fetch(`/api/v1/public/search?${query}`);
  if (!response.ok) {
    throw new Error("search failed");
  }
  return response.json();
}

export async function fetchPrivacy(lang: string): Promise<string> {
  const response = await fetch(`/api/v1/legal/privacy?lang=${lang}`);
  if (!response.ok) return "";
  const data = await response.json();
  return data.content as string;
}
