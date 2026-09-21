import { useEffect, useState } from "react";
import { setPasswordWithToken } from "../api";
import type { Messages } from "../i18n";

type Props = {
  t: Messages;
  onLoggedIn: () => void;
};

type Status = "idle" | "form" | "loading" | "success" | "error";

export function SetPasswordBanner({ t, onLoggedIn }: Props) {
  const [token, setToken] = useState<string | null>(null);
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [status, setStatus] = useState<Status>("idle");

  useEffect(() => {
    const value = new URLSearchParams(window.location.search).get("setpw");
    if (!value) return;
    setToken(value);
    setStatus("form");
  }, []);

  const handleSubmit = async () => {
    if (!token || password.length < 8 || password !== confirm) return;
    setStatus("loading");
    try {
      await setPasswordWithToken(token, password);
      setStatus("success");
      onLoggedIn();
      window.history.replaceState({}, "", window.location.pathname);
    } catch {
      setStatus("error");
    }
  };

  if (status === "idle") return null;

  if (status === "success" || status === "error") {
    return (
      <div className={`verify-banner ${status === "success" ? "success" : "error"}`}>
        {status === "success" ? t.setPasswordSuccess : t.setPasswordError}
      </div>
    );
  }

  return (
    <div className="verify-banner pending setpw-banner">
      <p className="setpw-title">{t.setPasswordTitle}</p>
      <p className="plan-hint">{t.setPasswordDesc}</p>
      <label>
        {t.passwordLabel}
        <input
          type="password"
          autoComplete="new-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder={t.passwordPlaceholder}
          minLength={8}
        />
      </label>
      <label>
        {t.passwordConfirmLabel}
        <input
          type="password"
          autoComplete="new-password"
          value={confirm}
          onChange={(event) => setConfirm(event.target.value)}
          placeholder={t.passwordPlaceholder}
          minLength={8}
        />
      </label>
      {password.length > 0 && password.length < 8 && (
        <p className="alert-feedback error">{t.passwordTooShort}</p>
      )}
      {confirm.length > 0 && password !== confirm && (
        <p className="alert-feedback error">{t.passwordMismatch}</p>
      )}
      <button
        type="button"
        className="apply-btn"
        disabled={status === "loading" || password.length < 8 || password !== confirm}
        onClick={() => void handleSubmit()}
      >
        {status === "loading" ? t.loading : t.setPasswordCta}
      </button>
    </div>
  );
}
