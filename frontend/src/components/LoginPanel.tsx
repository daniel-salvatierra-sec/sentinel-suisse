import { useState } from "react";
import { getLastLoginEmail, requestForgotPassword, requestMagicLogin } from "../api";
import type { Lang, Messages } from "../i18n";

type Props = {
  t: Messages;
  locale: Lang;
  onBackToSignup?: () => void;
  onLoggedIn?: () => void;
};

type Status =
  | "idle"
  | "loading"
  | "ready"
  | "error"
  | "invalid"
  | "needs_password"
  | "forgot_sent";

export function LoginPanel({ t, locale, onBackToSignup, onLoggedIn }: Props) {
  const [email, setEmail] = useState(() => getLastLoginEmail() ?? "");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState<Status>("idle");

  const handleSubmit = async () => {
    if (!email.trim() || password.length < 8) return;
    setStatus("loading");
    try {
      const result = await requestMagicLogin(email.trim(), locale, password);
      if (result.kind === "session") {
        setStatus("ready");
        onLoggedIn?.();
        return;
      }
      if (result.kind === "needs_password") {
        setStatus("needs_password");
        return;
      }
      setStatus("invalid");
    } catch {
      setStatus("error");
    }
  };

  const handleForgot = async () => {
    if (!email.trim()) return;
    setStatus("loading");
    try {
      await requestForgotPassword(email.trim(), locale);
      setStatus("forgot_sent");
    } catch {
      setStatus("error");
    }
  };

  return (
    <div className="login-panel">
      <h3 className="alerts-subhead">{t.loginTitle}</h3>
      <p className="plan-hint">{t.loginDesc}</p>
      <label>
        {t.email}
        <input
          type="email"
          required
          autoComplete="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="you@example.com"
        />
      </label>
      <label>
        {t.passwordLabel}
        <input
          type="password"
          required
          autoComplete="current-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder={t.passwordPlaceholder}
          minLength={8}
        />
      </label>
      <button
        type="button"
        className="apply-btn"
        style={{ width: "100%" }}
        disabled={status === "loading" || !email.trim() || password.length < 8}
        onClick={() => void handleSubmit()}
      >
        {status === "loading" ? t.loading : t.loginCta}
      </button>
      <button
        type="button"
        className="linkish"
        disabled={status === "loading" || !email.trim()}
        onClick={() => void handleForgot()}
      >
        {t.loginForgotPassword}
      </button>
      {status === "needs_password" && (
        <p className="alert-feedback success">{t.loginNeedsPassword}</p>
      )}
      {status === "forgot_sent" && (
        <p className="alert-feedback success">{t.loginForgotSent}</p>
      )}
      {status === "ready" && <p className="alert-feedback success">{t.loginSuccess}</p>}
      {status === "invalid" && <p className="alert-feedback error">{t.loginInvalidCredentials}</p>}
      {status === "error" && <p className="alert-feedback error">{t.loginError}</p>}
      {onBackToSignup && (
        <button type="button" className="linkish" onClick={onBackToSignup}>
          {t.loginBackToSignup}
        </button>
      )}
    </div>
  );
}
