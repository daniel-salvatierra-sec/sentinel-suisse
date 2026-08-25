import { useCallback, useEffect, useState, type FormEvent } from "react";
import {
  clearAdminSession,
  createAdminListing,
  eraseAdminUser,
  fetchAdminListings,
  fetchAdminUsers,
  fetchOverview,
  hasAdminSession,
  saveAdminSession,
  setListingHidden,
  setUserFreeAlerts,
  setUserPremium,
  updateAdminListing,
  type AdminListing,
  type AdminUser,
  type DashboardOverview,
} from "./adminApi";

type Tab = "overview" | "listings" | "users" | "ingest";

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

export function AdminDashboard() {
  const [authed, setAuthed] = useState(hasAdminSession);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState(false);
  const [tab, setTab] = useState<Tab>("overview");
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
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
    if (tab === "overview" || tab === "ingest") {
      void loadOverview();
    } else if (tab === "listings") {
      void loadListings();
    } else {
      void loadUsers();
    }
  }, [authed, tab, loadOverview, loadListings, loadUsers]);

  async function onLogin(event: FormEvent) {
    event.preventDefault();
    saveAdminSession(username.trim(), password);
    setPassword("");
    try {
      await fetchOverview();
      setLoginError(false);
      setAuthed(true);
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
          <p className="eyebrow">LinkSwiss</p>
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
        <p className="eyebrow">LinkSwiss</p>
        <h1>Operador</h1>
        <button
          type="button"
          className="admin-logout"
          onClick={() => {
            clearAdminSession();
            setAuthed(false);
            setOverview(null);
          }}
        >
          Salir
        </button>
      </header>

      <nav className="admin-tabs" aria-label="Secciones">
        {(
          [
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
