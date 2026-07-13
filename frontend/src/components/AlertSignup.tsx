import { useState } from "react";
import type { ListingType } from "../api";
import type { Messages } from "../i18n";

type Props = {
  t: Messages;
  listingType: ListingType;
  location: string;
  id?: string;
};

export function AlertSignup({ t, listingType, location, id = "alerts" }: Props) {
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [saved, setSaved] = useState(false);

  return (
    <section className="alert-panel" id={id}>
      <h2 style={{ marginTop: 0 }}>{t.alertsTitle}</h2>
      <p>{t.alertsDesc}</p>
      <div className="qr-placeholder" aria-hidden>
        QR
        <br />
        WhatsApp
      </div>
      <label>
        {t.phone}
        <input
          type="tel"
          value={phone}
          onChange={(event) => setPhone(event.target.value)}
          placeholder="+41 79 …"
        />
      </label>
      <label>
        {t.email}
        <input
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="you@example.com"
        />
      </label>
      <button
        type="button"
        className="primary-btn"
        style={{ width: "100%" }}
        onClick={() => {
          const payload = { listingType, location, phone, email };
          localStorage.setItem("suisse-alert-pending", JSON.stringify(payload));
          setSaved(true);
        }}
      >
        {t.saveSearch}
      </button>
      {saved && (
        <p style={{ fontSize: "0.85rem", opacity: 0.8 }}>
          {listingType} · {location || "—"} — enregistré localement (API Phase 16+)
        </p>
      )}
    </section>
  );
}
