import { useState } from "react";
import { requestMagicLogin } from "../api";
import type { Lang, Messages } from "../i18n";

type Props = {
  t: Messages;
  locale: Lang;
  onBackToSignup?: () => void;
};

type Status = "idle" | "loading" | "sent" | "error";

export function LoginPanel({ t, locale, onBackToSignup }: Props) {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<Status>("idle");

  const handleSubmit = async () => {
    if (!email.trim()) return;
    setStatus("loading");
    try {
      await requestMagicLogin(email.trim(), locale);
      setStatus("sent");
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
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="you@example.com"
        />
      </label>
      <button
        type="button"
        className="apply-btn"
        style={{ width: "100%" }}
        disabled={status === "loading" || !email.trim()}
        onClick={() => void handleSubmit()}
      >
        {status === "loading" ? t.loading : t.loginCta}
      </button>
      {status === "sent" && <p className="alert-feedback success">{t.loginEmailSent}</p>}
      {status === "error" && <p className="alert-feedback error">{t.loginError}</p>}
      {onBackToSignup && (
        <button type="button" className="linkish" onClick={onBackToSignup}>
          {t.loginBackToSignup}
        </button>
      )}
    </div>
  );
}
