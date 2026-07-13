import { useState } from "react";
import type { ListingType } from "../api";
import type { Messages } from "../i18n";

type Props = {
  t: Messages;
  onPickCategory: (type: ListingType) => void;
  onOpenAlerts: () => void;
};

export function GuideBot({ t, onPickCategory, onOpenAlerts }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button type="button" className="guide-fab" onClick={() => setOpen(true)}>
        {t.guide}
      </button>
      {open && (
        <div className="modal-backdrop" role="presentation" onClick={() => setOpen(false)}>
          <div className="modal" role="dialog" onClick={(event) => event.stopPropagation()}>
            <p>{t.guideHello}</p>
            <button
              type="button"
              className="option"
              onClick={() => {
                onPickCategory("housing");
                setOpen(false);
              }}
            >
              {t.guideHousing}
            </button>
            <button
              type="button"
              className="option"
              onClick={() => {
                onPickCategory("job");
                setOpen(false);
              }}
            >
              {t.guideJob}
            </button>
            <button
              type="button"
              className="option"
              onClick={() => {
                onOpenAlerts();
                setOpen(false);
              }}
            >
              {t.guideAlerts}
            </button>
            <button type="button" className="primary-btn" style={{ width: "100%" }} onClick={() => setOpen(false)}>
              {t.guideClose}
            </button>
          </div>
        </div>
      )}
    </>
  );
}
