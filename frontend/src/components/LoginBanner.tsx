import { useEffect, useState } from "react";
import { confirmMagicLogin } from "../api";
import type { Messages } from "../i18n";

type Props = {
  t: Messages;
  onLoggedIn: () => void;
};

type Status = "idle" | "loading" | "success" | "error";

export function LoginBanner({ t, onLoggedIn }: Props) {
  const [status, setStatus] = useState<Status>("idle");

  useEffect(() => {
    const token = new URLSearchParams(window.location.search).get("login");
    if (!token) return;

    setStatus("loading");
    void confirmMagicLogin(token)
      .then(() => {
        setStatus("success");
        onLoggedIn();
      })
      .catch(() => setStatus("error"))
      .finally(() => {
        window.history.replaceState({}, "", window.location.pathname);
      });
  }, [onLoggedIn]);

  if (status === "idle" || status === "loading") {
    return null;
  }

  return (
    <div className={`verify-banner ${status}`}>
      {status === "success" ? t.loginSuccess : t.loginError}
    </div>
  );
}
