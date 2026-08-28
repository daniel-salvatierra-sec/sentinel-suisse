import { useCallback, useEffect, useState, type FormEvent } from "react";
import {
  clearAdminSession,
  createAdminListing,
  eraseAdminUser,
  fetchAdminInsights,
  fetchAdminListings,
  fetchAdminUsers,
  fetchOverview,
  hasAdminSession,
  saveAdminSession,
  setListingHidden,
  setUserFreeAlerts,
  setUserPremium,
  updateAdminListing,
  type AdminInsights,
  type AdminListing,
  type AdminUser,
  type DashboardOverview,
} from "./adminApi";

type Tab = "apps" | "revenue" | "metrics" | "overview" | "listings" | "users" | "ingest";

function formatWhen(iso: string | null): string {
  if (!iso) {
    return "nunca";
  }
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    return iso;
  }
  return date.toLocaleString("es-CH", { dateStyle: "short", timeStyle: "short" });
}

function formatDay(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    return iso;
  }
  return date.toLocaleDateString("es-CH", { weekday: "short", day: "numeric", month: "short" });
}

function formatMoney(amount: number, currency = "CHF"): string {
  return `${currency.toUpperCase()} ${amount.toFixed(2)}`;
}

export function AdminDashboard() {
  const [authed, setAuthed] = useState(hasAdminSession);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState(false);
  const [tab, setTab] = useState<Tab>("apps");
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [insights, setInsights] = useState<AdminInsights | null>(null);
  const [listings, setListings] = useState<AdminListing[]>([]);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [q, setQ] = useState("");
  const [listingType, setListingType] = useState<"" | "housing" | "job">("");
  const [hiddenOnly, setHiddenOnly] = useState(false);
  const [ownerOnly, setOwnerOnly] = useState(false);
  const [busy, setBusy] = useState(false);
  const [loadError, setLoadError] = useState(false);
  const [showCreateListing, setShowCreateListing] = useState(false);
  const [createType, setCreateType] = useState<"housing" | "job">("housing");
  const [createTitle, setCreateTitle] = useState("");
  const [createLocation, setCreateLocation] = useState("");
  const [createPrice, setCreatePrice] = useState("");
  const [createContact, setCreateContact] = useState("");
  const [createDescription, setCreateDescription] = useState("");
  const [createHidden, setCreateHidden] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editLocation, setEditLocation] = useState("");
  const [editPrice, setEditPrice] = useState("");
  const [editContact, setEditContact] = useState("");
  const [editDescription, setEditDescription] = useState("");

  useEffect(() => {
    document.title = "LinkSwiss — Operador";
    let robots = document.querySelector('meta[name="robots"]');
    if (!robots) {
      robots = document.createElement("meta");
      robots.setAttribute("name", "robots");
      document.head.appendChild(robots);
    }
    robots.setAttribute("content", "noindex, nofollow");
  }, []);

  const loadInsights = useCallback(async () => {
    setBusy(true);
    setLoadError(false);
    try {
      setInsights(await fetchAdminInsights());
    } catch {
      setLoadError(true);
      setAuthed(hasAdminSession());
    } finally {
      setBusy(false);
    }
  }, []);

  const loadOverview = useCallback(async () => {
    setBusy(true);
    setLoadError(false);
    try {
      setOverview(await fetchOverview());
    } catch {
      setLoadError(true);
      setAuthed(hasAdminSession());
    } finally {
      setBusy(false);
    }
  }, []);

  const loadListings = useCallback(async () => {
    setBusy(true);
    setLoadError(false);
    try {
      setListings(
        await fetchAdminListings({
          q,
          listing_type: listingType,
          hidden: hiddenOnly ? true : undefined,
          owner_only: ownerOnly,
        }),
      );
    } catch {
      setLoadError(true);
      setAuthed(hasAdminSession());
    } finally {
      setBusy(false);
    }
  }, [q, listingType, hiddenOnly, ownerOnly]);

  const loadUsers = useCallback(async () => {
    setBusy(true);
    setLoadError(false);
    try {
      setUsers(await fetchAdminUsers());
    } catch {
      setLoadError(true);
      setAuthed(hasAdminSession());
    } finally {
      setBusy(false);
    }
  }, []);

  useEffect(() => {
    if (!authed) {
      return;
    }
    if (tab === "apps" || tab === "revenue" || tab === "metrics") {
      void loadInsights();
    } else if (tab === "overview" || tab === "ingest") {
      void loadOverview();
    } else if (tab === "listings") {
      void loadListings();
    } else {
      void loadUsers();
    }
  }, [authed, tab, loadInsights, loadOverview, loadListings, loadUsers]);

  async function onLogin(event: FormEvent) {
    event.preventDefault();
    saveAdminSession(username.trim(), password);
    setPassword("");
    try {
      await fetchAdminInsights();
      setLoginError(false);
      setAuthed(true);
      setTab("apps");
    } catch {
      clearAdminSession();
      setLoginError(true);
      setAuthed(false);
    }
  }

  if (!authed) {
    return (
      <div className="admin-dash">
        <header className="admin-head">
        <p className="eyebrow">Centro de operaciones</p>
        <h1>Operador</h1>
          <p className="lede">Acceso privado. No forma parte de la app pública.</p>
        </header>
        <form className="card admin-login" onSubmit={(event) => void onLogin(event)}>
          <label>
            Usuario
            <input
              autoComplete="username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              required
            />
          </label>
          <label>
            Contraseña
            <input
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>
          {loginError ? <p className="admin-error">Credenciales no válidas.</p> : null}
          <button type="submit">Entrar</button>
        </form>
      </div>
    );
  }

  return (
    <div className="admin-dash">
      <header className="admin-head">
        <p className="eyebrow">Centro de operaciones</p>
        <h1>Operador</h1>
        <p className="lede">Apps, ingresos y métricas en un solo lugar.</p>
        <button
          type="button"
          className="admin-logout"
          onClick={() => {
            clearAdminSession();
            setAuthed(false);
            setOverview(null);
            setInsights(null);
          }}
        >
          Salir
        </button>
      </header>

      <nav className="admin-tabs" aria-label="Secciones">
        {(
          [
            ["apps", "Apps"],
            ["revenue", "Ingresos"],
            ["metrics", "Métricas"],
            ["overview", "Resumen"],
            ["listings", "Anuncios"],
            ["users", "Usuarios"],
            ["ingest", "Fuentes"],
          ] as const
        ).map(([id, label]) => (
          <button
            key={id}
            type="button"
            className={tab === id ? "is-active" : ""}
            onClick={() => setTab(id)}
          >
            {label}
          </button>
        ))}
      </nav>

      {loadError ? <p className="admin-error">No se pudo cargar. Revisa la sesión.</p> : null}
      {busy ? <p className="admin-muted">Cargando…</p> : null}

      {tab === "apps" && insights ? (
        <section className="admin-apps-grid">
          {insights.apps.map((app) => (
            <article key={app.id} className={`card admin-app-card${app.is_current ? " is-current" : ""}`}>
              <h2>{app.name}</h2>
              <p className="admin-muted">{app.status}</p>
              <p className="admin-app-url">{app.public_url}</p>
              <div className="admin-actions">
                <a className="admin-link-btn" href={app.public_url} target="_blank" rel="noreferrer">
                  Abrir app
                </a>
                {app.is_current ? (
                  <button type="button" className="is-active" disabled>
                    Admin aquí
                  </button>
                ) : (
                  <a className="admin-link-btn" href={app.admin_url} target="_blank" rel="noreferrer">
                    Admin
                  </a>
                )}
              </div>
            </article>
          ))}
          <article className="card admin-app-card admin-app-placeholder">
            <h2>Próxima app</h2>
            <p className="admin-muted">
              Añade más proyectos en <code>OPS_APPS_JSON</code> del servidor.
            </p>
          </article>
        </section>
      ) : null}

      {tab === "revenue" && insights ? (
        <>
          <section className="admin-stats">
            <article className="card">
              <h2>Ingresos 30 días</h2>
              <p className="admin-metric">
                {insights.stripe.configured
                  ? formatMoney(insights.stripe.last_30_days_total_chf, insights.stripe.currency)
                  : "Stripe off"}
              </p>
              <p>
                {insights.stripe.premium_payments_30d} Premium ·{" "}
                {insights.stripe.boost_payments_30d} boosts
              </p>
            </article>
            <article className="card">
              <h2>Boosts activos</h2>
              <p className="admin-metric">{insights.active_boosts.length}</p>
              <p>Anuncios destacados ahora mismo</p>
            </article>
          </section>
          <section className="card admin-panel">
            <h2>Boosts activos</h2>
            {insights.active_boosts.length === 0 ? (
              <p className="admin-muted">Ningún boost activo.</p>
            ) : (
              <ul className="admin-list">
                {insights.active_boosts.map((item) => (
                  <li key={item.id}>
                    <div>
                      <strong>{item.title}</strong>
                      <p>
                        #{item.id} · {item.listing_type === "job" ? "empleo" : "vivienda"} ·{" "}
                        {item.location ?? "—"}
                        {item.owner_user_id ? ` · usuario ${item.owner_user_id}` : ""}
                      </p>
                      <p className="admin-muted">
                        Hasta {formatWhen(item.featured_until)}
                      </p>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
          <section className="card admin-panel">
            <h2>Pagos recientes (Stripe)</h2>
            {!insights.stripe.configured ? (
              <p className="admin-muted">Configura STRIPE_SECRET_KEY en el servidor.</p>
            ) : insights.stripe.recent_payments.length === 0 ? (
              <p className="admin-muted">Sin pagos completados aún.</p>
            ) : (
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Fecha</th>
                    <th>Tipo</th>
                    <th>Importe</th>
                  </tr>
                </thead>
                <tbody>
                  {insights.stripe.recent_payments.map((row) => (
                    <tr key={row.checkout_id}>
                      <td>{formatWhen(row.paid_at)}</td>
                      <td>
                        {row.label}
                        {row.listing_id ? ` #${row.listing_id}` : ""}
                      </td>
                      <td>{formatMoney(row.amount_chf, insights.stripe.currency)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>
        </>
      ) : null}

      {tab === "metrics" && insights ? (
        <>
          <section className="card admin-panel">
            <h2>Registros por día (14 días)</h2>
            <div className="admin-bar-chart">
              {insights.signups_by_day.map((row) => {
                const max = Math.max(...insights.signups_by_day.map((item) => item.count), 1);
                const height = Math.round((row.count / max) * 100);
                return (
                  <div key={row.day} className="admin-bar-col" title={`${row.count} registros`}>
                    <div className="admin-bar" style={{ height: `${height}%` }} />
                    <span className="admin-bar-value">{row.count}</span>
                    <span className="admin-bar-label">{formatDay(row.day)}</span>
                  </div>
                );
              })}
            </div>
          </section>
          <section className="card admin-panel">
            <h2>Pagos por semana</h2>
            {!insights.stripe.configured ? (
              <p className="admin-muted">Stripe no configurado.</p>
            ) : insights.stripe.payments_by_week.length === 0 ? (
              <p className="admin-muted">Sin pagos en las últimas semanas.</p>
            ) : (
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Semana</th>
                    <th>Premium</th>
                    <th>Boosts</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {insights.stripe.payments_by_week.map((row) => (
                    <tr key={row.week_start}>
                      <td>{formatDay(row.week_start)}</td>
                      <td>{row.premium_count}</td>
                      <td>{row.boost_count}</td>
                      <td>{formatMoney(row.amount_chf, insights.stripe.currency)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>
        </>
      ) : null}

      {tab === "overview" && overview ? (
        <section className="admin-stats">
          <article className="card">
            <h2>Usuarios</h2>
            <p className="admin-metric">{overview.users_total}</p>
            <p>{overview.users_active} activos · {overview.users_premium} Premium</p>
          </article>
          <article className="card">
            <h2>Anuncios</h2>
            <p className="admin-metric">
              {overview.listings_housing + overview.listings_job}
            </p>
            <p>
              {overview.listings_housing} vivienda · {overview.listings_job} empleo ·{" "}
              {overview.listings_direct} directos · {overview.listings_hidden} ocultos
            </p>
          </article>
          <article className="card">
            <h2>Salud</h2>
            <p className="admin-metric">{overview.database_ok ? "OK" : "BD error"}</p>
            <p>
              Ventana de frescura {overview.listing_fresh_hours} h ·{" "}
              {overview.providers.filter((item) => item.stale).length} fuentes atrasadas
            </p>
          </article>
        </section>
      ) : null}

      {tab === "listings" ? (
        <section className="card admin-panel">
          <div className="admin-actions">
            <button type="button" onClick={() => setShowCreateListing((value) => !value)}>
              {showCreateListing ? "Cerrar formulario" : "Nuevo anuncio"}
            </button>
          </div>
          {showCreateListing ? (
            <form
              className="admin-filters admin-create"
              onSubmit={(event) => {
                event.preventDefault();
                const priceNum = createPrice.trim() === "" ? undefined : Number(createPrice);
                void createAdminListing({
                  listing_type: createType,
                  title: createTitle.trim(),
                  location: createLocation.trim(),
                  contact_url: createContact.trim(),
                  price: createType === "housing" ? priceNum : priceNum,
                  description: createDescription.trim() || undefined,
                  is_hidden: createHidden,
                })
                  .then(() => {
                    setCreateTitle("");
                    setCreateLocation("");
                    setCreatePrice("");
                    setCreateContact("");
                    setCreateDescription("");
                    setCreateHidden(false);
                    setShowCreateListing(false);
                    return loadListings();
                  })
                  .catch(() => setLoadError(true));
              }}
            >
              <select
                value={createType}
                onChange={(event) => setCreateType(event.target.value as "housing" | "job")}
              >
                <option value="housing">Vivienda</option>
                <option value="job">Empleo</option>
              </select>
              <input
                placeholder="Título"
                value={createTitle}
                onChange={(event) => setCreateTitle(event.target.value)}
                required
                minLength={8}
              />
              <input
                placeholder="Lugar"
                value={createLocation}
                onChange={(event) => setCreateLocation(event.target.value)}
                required
              />
              <input
                placeholder={createType === "housing" ? "Precio CHF" : "Salario (opc.)"}
                value={createPrice}
                onChange={(event) => setCreatePrice(event.target.value)}
                type="number"
                required={createType === "housing"}
              />
              <input
                placeholder="URL contacto"
                value={createContact}
                onChange={(event) => setCreateContact(event.target.value)}
                required
              />
              <textarea
                placeholder="Descripción (opc.)"
                value={createDescription}
                onChange={(event) => setCreateDescription(event.target.value)}
                rows={2}
              />
              <label className="admin-check">
                <input
                  type="checkbox"
                  checked={createHidden}
                  onChange={(event) => setCreateHidden(event.target.checked)}
                />
                Oculto al publicar
              </label>
              <button type="submit">Publicar</button>
            </form>
          ) : null}
          <form
            className="admin-filters"
            onSubmit={(event) => {
              event.preventDefault();
              void loadListings();
            }}
          >
            <input
              placeholder="Título, lugar o id"
              value={q}
              onChange={(event) => setQ(event.target.value)}
            />
            <select
              value={listingType}
              onChange={(event) => setListingType(event.target.value as "" | "housing" | "job")}
            >
              <option value="">Todos</option>
              <option value="housing">Vivienda</option>
              <option value="job">Empleo</option>
            </select>
            <label className="admin-check">
              <input
                type="checkbox"
                checked={hiddenOnly}
                onChange={(event) => setHiddenOnly(event.target.checked)}
              />
              Solo ocultos
            </label>
            <label className="admin-check">
              <input
                type="checkbox"
                checked={ownerOnly}
                onChange={(event) => setOwnerOnly(event.target.checked)}
              />
              Solo directos
            </label>
            <button type="submit">Buscar</button>
          </form>
          <ul className="admin-list">
            {listings.map((item) => (
              <li key={item.id}>
                {editingId === item.id ? (
                  <form
                    className="admin-edit"
                    onSubmit={(event) => {
                      event.preventDefault();
                      const priceNum = editPrice.trim() === "" ? undefined : Number(editPrice);
                      void updateAdminListing(item.id, {
                        title: editTitle.trim(),
                        location: editLocation.trim(),
                        contact_url: editContact.trim(),
                        price: priceNum,
                        description: editDescription.trim() || undefined,
                      })
                        .then(() => {
                          setEditingId(null);
                          return loadListings();
                        })
                        .catch(() => setLoadError(true));
                    }}
                  >
                    <input
                      value={editTitle}
                      onChange={(event) => setEditTitle(event.target.value)}
                      required
                      minLength={8}
                    />
                    <input
                      value={editLocation}
                      onChange={(event) => setEditLocation(event.target.value)}
                      required
                    />
                    <input
                      value={editPrice}
                      onChange={(event) => setEditPrice(event.target.value)}
                      type="number"
                    />
                    <input
                      value={editContact}
                      onChange={(event) => setEditContact(event.target.value)}
                      required
                    />
                    <textarea
                      value={editDescription}
                      onChange={(event) => setEditDescription(event.target.value)}
                      rows={2}
                    />
                    <div className="admin-actions">
                      <button type="submit">Guardar</button>
                      <button type="button" onClick={() => setEditingId(null)}>
                        Cancelar
                      </button>
                    </div>
                  </form>
                ) : (
                  <>
                    <div>
                      <strong>{item.title}</strong>
                      <p>
                        #{item.id} · {item.listing_type === "job" ? "empleo" : "vivienda"} ·{" "}
                        {item.provider_slug}
                        {item.owner_user_id ? ` · usuario ${item.owner_user_id}` : ""} ·{" "}
                        {item.location ?? "—"}
                        {item.price != null ? ` · CHF ${item.price}` : ""}
                      </p>
                    </div>
                    <div className="admin-actions">
                      <button
                        type="button"
                        onClick={() => {
                          setEditingId(item.id);
                          setEditTitle(item.title);
                          setEditLocation(item.location ?? "");
                          setEditPrice(item.price != null ? String(item.price) : "");
                          setEditContact(item.source_url);
                          setEditDescription(item.description ?? "");
                        }}
                      >
                        Editar
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          void setListingHidden(item.id, !item.is_hidden).then(() => loadListings());
                        }}
                      >
                        {item.is_hidden ? "Mostrar" : "Ocultar"}
                      </button>
                    </div>
                  </>
                )}
              </li>
            ))}
          </ul>
          {listings.length === 0 && !busy ? <p className="admin-muted">Sin anuncios.</p> : null}
        </section>
      ) : null}

      {tab === "users" ? (
        <section className="card admin-panel">
          <ul className="admin-list">
            {users.map((user) => (
              <li key={user.id}>
                <div>
                  <strong>{user.email}</strong>
                  <p>
                    #{user.id} · {user.locale} · {formatWhen(user.created_at)} ·{" "}
                    {user.saved_search_count} búsquedas
                    {user.is_active ? "" : " · inactivo"}
                    {user.can_receive_alerts
                      ? " · alertas activas"
                      : " · sin alertas automáticas"}
                  </p>
                </div>
                <div className="admin-actions">
                  <button
                    type="button"
                    onClick={() => {
                      void setUserPremium(user.id, !user.is_premium).then(() => loadUsers());
                    }}
                  >
                    {user.is_premium ? "Quitar Premium" : "Dar Premium"}
                  </button>
                  {!user.is_premium ? (
                    <button
                      type="button"
                      onClick={() => {
                        void setUserFreeAlerts(
                          user.id,
                          !user.free_alerts_grandfathered,
                        ).then(() => loadUsers());
                      }}
                    >
                      {user.free_alerts_grandfathered
                        ? "Quitar alertas gratis"
                        : "Dar alertas gratis"}
                    </button>
                  ) : null}
                  <button
                    type="button"
                    className="admin-danger"
                    onClick={() => {
                      if (
                        window.confirm(
                          `Borrar ${user.email} y sus datos (nLPD)? Esta acción no se deshace.`,
                        )
                      ) {
                        void eraseAdminUser(user.id).then(() => loadUsers());
                      }
                    }}
                  >
                    Borrar
                  </button>
                </div>
              </li>
            ))}
          </ul>
          {users.length === 0 && !busy ? <p className="admin-muted">Sin usuarios.</p> : null}
        </section>
      ) : null}

      {tab === "ingest" && overview ? (
        <section className="card admin-panel">
          <p className="admin-muted">
            Captura automática. Directos no dependen de ingest. No se lanza ingest desde aquí.
          </p>
          <table className="admin-table">
            <thead>
              <tr>
                <th>Fuente</th>
                <th>Anuncios</th>
                <th>Última captura</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {overview.providers.map((item) => (
                <tr key={item.slug}>
                  <td>
                    {item.slug}
                    {item.is_active ? "" : " (off)"}
                  </td>
                  <td>{item.listing_count}</td>
                  <td>
                    {formatWhen(item.last_fetched_at)}
                    {item.hours_since_fetch != null ? ` (${item.hours_since_fetch} h)` : ""}
                  </td>
                  <td>{item.stale ? "Atrasada" : "Al día"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ) : null}
    </div>
  );
}
