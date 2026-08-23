import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { AdminDashboard } from "./AdminDashboard";
import { listenForInstallPrompt } from "./pwa";
import "./styles.css";

listenForInstallPrompt();

const path = window.location.pathname.replace(/\/+$/, "") || "/";
const isAdmin = path === "/admin" || path.startsWith("/admin/");

createRoot(document.getElementById("root")!).render(
  <StrictMode>{isAdmin ? <AdminDashboard /> : <App />}</StrictMode>,
);

if (!isAdmin && import.meta.env.PROD && "serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    void navigator.serviceWorker.register("/sw.js");
  });
}
