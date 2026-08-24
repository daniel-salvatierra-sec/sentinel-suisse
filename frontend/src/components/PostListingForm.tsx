import { useEffect, useState, type FormEvent } from "react";
import {
  createMyListing,
  deleteMyListing,
  fetchMyListings,
  type Listing,
  type ListingType,
} from "../api";
import type { Messages } from "../i18n";
import { JOB_FIELDS, type JobField } from "../jobTaxonomy";

type Props = {
  t: Messages;
  listingType: ListingType;
};

function fieldLabel(t: Messages, field: JobField): string {
  const map: Record<JobField, string> = {
    it: t.jobCatIt,
    healthcare: t.jobCatHealthcare,
    construction: t.jobCatConstruction,
    hospitality: t.jobCatHospitality,
    admin: t.jobCatAdmin,
    finance: t.jobCatFinance,
    sales: t.jobCatSales,
    education: t.jobCatEducation,
    logistics: t.jobCatLogistics,
    watchmaking: t.jobCatWatchmaking,
    other: t.jobCatOther,
  };
  return map[field];
}

export function PostListingForm({ t, listingType }: Props) {
  const isJob = listingType === "job";
  const [mine, setMine] = useState<Listing[]>([]);
  const [title, setTitle] = useState("");
  const [location, setLocation] = useState("");
  const [price, setPrice] = useState("");
  const [rooms, setRooms] = useState("");
  const [parking, setParking] = useState(false);
  const [jobField, setJobField] = useState<JobField>("other");
  const [contactUrl, setContactUrl] = useState("");
  const [description, setDescription] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const reload = () => {
    void fetchMyListings()
      .then((items) => setMine(items.filter((item) => item.listing_type === listingType)))
      .catch(() => setMine([]));
  };

  useEffect(() => {
    reload();
  }, [listingType]);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    setSaved(false);
    try {
      const priceNum = price.trim() === "" ? undefined : Number(price);
      const roomsNum = rooms.trim() === "" ? undefined : Number(rooms);
      await createMyListing({
        listing_type: listingType,
        title: title.trim(),
        location: location.trim(),
        price: isJob ? priceNum : priceNum,
        rooms: isJob ? undefined : roomsNum,
        has_parking: isJob ? undefined : parking,
        job_category: isJob ? jobField : undefined,
        contact_url: contactUrl.trim(),
        description: description.trim() || undefined,
      });
      setTitle("");
      setLocation("");
      setPrice("");
      setRooms("");
      setParking(false);
      setJobField("other");
      setContactUrl("");
      setDescription("");
      setSaved(true);
      reload();
    } catch (err) {
      const message = err instanceof Error ? err.message : "";
      setError(message.includes("Maximum") ? t.postListingLimit : t.postListingError);
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="post-listing">
      <h3>{isJob ? t.postJobTitle : t.postListingTitle}</h3>
      <p className="plan-hint">{isJob ? t.postJobHint : t.postListingHint}</p>
      <form onSubmit={(event) => void onSubmit(event)}>
        <label>
          {isJob ? t.postJobTitleField : t.postListingTitleField}
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            minLength={8}
            placeholder={isJob ? t.postJobTitleHint : t.postListingTitleHint}
          />
        </label>
        <label>
          {isJob ? t.postJobLocation : t.postListingLocation}
          <input
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            required
            placeholder={isJob ? t.postJobLocationHint : t.postListingLocationHint}
          />
        </label>
        {isJob ? (
          <>
            <label>
              {t.postJobCategory}
              <select value={jobField} onChange={(e) => setJobField(e.target.value as JobField)}>
                {JOB_FIELDS.map((field) => (
                  <option key={field} value={field}>
                    {fieldLabel(t, field)}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t.postJobSalary}
              <input
                type="number"
                min={1}
                step="1"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
              />
            </label>
          </>
        ) : (
          <>
            <label>
              {t.postListingPrice}
              <input
                type="number"
                min={1}
                step="1"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                required
                placeholder={t.postListingPriceHint}
              />
            </label>
            <label>
              {t.postListingRooms}
              <input
                type="number"
                min={0}
                max={20}
                step="0.5"
                value={rooms}
                onChange={(e) => setRooms(e.target.value)}
              />
            </label>
            <label className="checkbox-row">
              <input
                type="checkbox"
                checked={parking}
                onChange={(e) => setParking(e.target.checked)}
              />
              {t.parkingLabel}
            </label>
          </>
        )}
        <label>
          {t.postListingContact}
          <input
            type="tel"
            inputMode="tel"
            autoComplete="tel"
            placeholder={t.postListingContactPlaceholder}
            value={contactUrl}
            onChange={(e) => setContactUrl(e.target.value)}
            required
          />
        </label>
        <p className="plan-hint">{t.postListingContactHint}</p>
        <label>
          {t.postListingDescription}
          <textarea
            rows={4}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder={isJob ? t.postJobDescriptionHint : t.postListingDescriptionHint}
          />
        </label>
        <button type="submit" className="apply-btn" disabled={busy} style={{ width: "100%" }}>
          {t.postListingCta}
        </button>
      </form>
      {saved ? <p className="alert-feedback">{isJob ? t.postJobSaved : t.postListingSaved}</p> : null}
      {error ? <p className="alert-feedback error">{error}</p> : null}
      <h4>{t.postListingMine}</h4>
      {mine.length === 0 ? (
        <p className="empty">{isJob ? t.postJobEmpty : t.postListingEmpty}</p>
      ) : (
        mine.map((item) => (
          <article key={item.id} className="listing-card account-search">
            <h4>{item.title}</h4>
            <div className="meta">
              {item.location}
              {item.price != null ? ` · ${item.price}` : ""}
            </div>
            <button
              type="button"
              className="danger-btn"
              onClick={() => {
                void deleteMyListing(item.id).then(reload);
              }}
            >
              {t.postListingDelete}
            </button>
          </article>
        ))
      )}
    </section>
  );
}
