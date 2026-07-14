import { useEffect, useState } from "react";
import { verifyChannelToken } from "../api";
import type { Messages } from "../i18n";

type Props = {
  t: Messages;
  onVerified: () => void;
};

type Status = "idle" | "loading" | "success" | "error";

export function VerifyBanner({ t, onVerified }: Props) {
  const [status, setStatus] = useState<Status>("idle");
  const [channelType, setChannelType] = useState<string>("email");

  useEffect(() => {
    const token = new URLSearchParams(window.location.search).get("verify");
    if (!token) return;

    setStatus("loading");
    void verifyChannelToken(token)
      .then((result) => {
        setChannelType(result.channel_type);
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

  const successMessage =
    channelType === "whatsapp" ? t.verifySuccessWhatsapp : t.verifySuccess;

  return (
    <div className={`verify-banner ${status}`}>
      {status === "success" ? successMessage : t.verifyError}
    </div>
  );
}
