import { useEffect, useState } from "react";
import QRCode from "qrcode";
import type { Messages } from "../i18n";

type Props = {
  t: Messages;
};

function appUrl(): string {
  if (typeof window !== "undefined" && window.location?.origin) {
    return window.location.origin;
  }
  return "https://linkswiss.ch";
}

/** Mobile-friendly share sheet: QR + WhatsApp / email / SMS / native share. */
export function ShareAppButton({ t }: Props) {
  const [open, setOpen] = useState(false);
  const [dataUrl, setDataUrl] = useState("");
  const [copied, setCopied] = useState(false);
  const url = appUrl();
  const shareText = `${t.shareText} ${url}`;

  useEffect(() => {
    if (!open) return;
    let cancelled = false;
    void QRCode.toDataURL(url, {
      width: 220,
      margin: 2,
      color: { dark: "#1a6f8a", light: "#FFFFFF" },
    }).then((value) => {
      if (!cancelled) setDataUrl(value);
    });
    return () => {
      cancelled = true;
    };
  }, [open, url]);

  const close = () => setOpen(false);

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  };

  const nativeShare = async () => {
    if (!navigator.share) return;
    try {
      await navigator.share({ title: t.appName, text: t.shareText, url });
    } catch {
      /* user cancelled */
    }
  };

  return (
    <>
      <button type="button" className="share-app-trigger" onClick={() => setOpen(true)}>
        {t.shareApp}
      </button>
      {open && (
        <div className="modal-backdrop sheet-backdrop" role="presentation" onClick={close}>
          <div
            className="guide-sheet share-sheet"
            role="dialog"
            aria-labelledby="share-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="guide-sheet-handle" aria-hidden />
            <h2 id="share-title" className="guide-title">
              {t.shareTitle}
            </h2>
            <p className="guide-message">{t.shareDesc}</p>
            {dataUrl ? (
              <img className="share-qr-img" src={dataUrl} alt={t.shareTitle} width={220} height={220} />
            ) : (
              <div className="subscribe-qr-placeholder" aria-hidden />
            )}
            <div className="share-actions">
              {"share" in navigator && (
                <button type="button" className="primary-btn" onClick={() => void nativeShare()}>
                  {t.shareNative}
                </button>
              )}
              <a
                className="secondary-btn share-link-btn"
                href={`https://wa.me/?text=${encodeURIComponent(shareText)}`}
                target="_blank"
                rel="noreferrer"
              >
                {t.shareWhatsApp}
              </a>
              <a
                className="secondary-btn share-link-btn"
                href={`mailto:?subject=${encodeURIComponent(t.appName)}&body=${encodeURIComponent(shareText)}`}
              >
                {t.shareEmail}
              </a>
              <a
                className="secondary-btn share-link-btn"
                href={`sms:?&body=${encodeURIComponent(shareText)}`}
              >
                {t.shareSms}
              </a>
              <button type="button" className="secondary-btn" onClick={() => void copyLink()}>
                {copied ? t.qrCopied : t.qrCopy}
              </button>
            </div>
            <div className="guide-nav">
              <button type="button" className="guide-skip" onClick={close}>
                {t.guideClose}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
