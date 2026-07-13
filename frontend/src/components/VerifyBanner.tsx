import { useEffect, useState } from "react";
import { verifyEmailToken } from "../api";
import type { Messages } from "../i18n";

type Props = {
  t: Messages;
  onVerified: () => void;
};

type Status = "idle" | "loading" | "success" | "error";

export function VerifyBanner({ t, onVerified }: Props) {
  const [status, setStatus] = useState<Status>("idle");

  useEffect(() => {
    const token = new URLSearchParams(window.location.search).get("verify");
    if (!token) return;

    setStatus("loading");
    void verifyEmailToken(token)
      .then(() => {
        setStatus("success");
        onVerified();
      })
      .catch(() => setStatus("error"))
      .finally(() => {
        window.history.replaceState({}, "", window.location.pathname);
      });
  }, [onVerified]);

  if (status === "idle" || status === "loading") {
    return null;
  }

  return (
    <div className={`verify-banner ${status}`}>
      {status === "success" ? t.verifySuccess : t.verifyError}
    </div>
  );
}
