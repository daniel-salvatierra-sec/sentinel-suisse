import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { listenForInstallPrompt } from "./pwa";
import "./styles.css";

listenForInstallPrompt();

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);

if (import.meta.env.PROD && "serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    void navigator.serviceWorker.register("/sw.js");
  });
}
