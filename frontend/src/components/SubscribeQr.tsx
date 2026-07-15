import { useEffect, useState } from "react";
import QRCode from "qrcode";
import type { ListingType } from "../api";
import type { Lang, Messages } from "../i18n";
import { buildSubscribeUrl } from "../subscribeLink";

type Props = {
  t: Messages;
  lang: Lang;
  listingType: ListingType;
  location: string;
};

export function SubscribeQr({ t, lang, listingType, location }: Props) {
  const [dataUrl, setDataUrl] = useState<string>("");
  const [copied, setCopied] = useState(false);
  const url = buildSubscribeUrl({ lang, listingType, location });

  useEffect(() => {
    let cancelled = false;
    void QRCode.toDataURL(url, {
      width: 200,
      margin: 2,
      color: { dark: "#1E6B8C", light: "#FFFFFF" },
    }).then((value) => {
      if (!cancelled) setDataUrl(value);
    });
    return () => {
      cancelled = true;
    };
  }, [url]);

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  };

  return (
    <div className="subscribe-qr">
      <h3 className="subscribe-qr-title">{t.qrTitle}</h3>
      <p className="subscribe-qr-desc">{t.qrDesc}</p>
      {dataUrl ? (
        <img className="subscribe-qr-img" src={dataUrl} alt={t.qrTitle} width={200} height={200} />
      ) : (
        <div className="subscribe-qr-placeholder" aria-hidden />
      )}
      <p className="subscribe-qr-url" title={url}>
        {url}
      </p>
      <button type="button" className="secondary-btn" onClick={() => void copyLink()}>
        {copied ? t.qrCopied : t.qrCopy}
      </button>
    </div>
  );
}
