import { useCallback, useEffect, useState, type FormEvent } from "react";
import {
  createAdminSponsor,
  deleteAdminSponsor,
  fetchAdminSponsors,
  updateAdminSponsor,
  type AdminSponsor,
  type AdminSponsorInput,
} from "../adminApi";

function formatWhen(iso: string | null): string {
  if (!iso) {
    return "—";
  }
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    return iso;
  }
  return date.toLocaleString("es-CH", { dateStyle: "short", timeStyle: "short" });
}

function formatMoney(amount: number | string): string {
  const value = Number(amount);
  const safe = Number.isFinite(value) ? value : 0;
  return `CHF ${safe.toFixed(2)}`;
}

function fromLocalInput(value: string): string | null {
  const trimmed = value.trim();
  if (!trimmed) {
    return null;
  }
  const date = new Date(trimmed);
  if (Number.isNaN(date.getTime())) {
    return null;
  }
  return date.toISOString();
}

const EMPTY_FORM: AdminSponsorInput = {
  sponsor_name: "",
  context: "all",
  headline: "",
  image_url: "",
  target_url: "",
  monthly_chf: 0,
  starts_at: null,
  ends_at: null,
  is_active: true,
  sort_order: 0,
};

type Props = {
  busy: boolean;
  onBusyChange: (value: boolean) => void;
};

export function AdminSponsorsPanel({ busy, onBusyChange }: Props) {
  const [rows, setRows] = useState<AdminSponsor[]>([]);
  const [error, setError] = useState(false);
  const [form, setForm] = useState<AdminSponsorInput>(EMPTY_FORM);
  const [startsLocal, setStartsLocal] = useState("");
  const [endsLocal, setEndsLocal] = useState("");

  const load = useCallback(async () => {
    onBusyChange(true);
    setError(false);
    try {
      setRows(await fetchAdminSponsors());
    } catch {
      setError(true);
    } finally {
      onBusyChange(false);
    }
  }, [onBusyChange]);

  useEffect(() => {
    void load();
  }, [load]);

  async function onCreate(event: FormEvent) {
    event.preventDefault();
    onBusyChange(true);
    setError(false);
    try {
      const payload: AdminSponsorInput = {
        ...form,
        headline: form.headline?.trim() || null,
        image_url: form.image_url?.trim() || null,
        starts_at: fromLocalInput(startsLocal),
        ends_at: fromLocalInput(endsLocal),
      };
      await createAdminSponsor(payload);
      setForm(EMPTY_FORM);
      setStartsLocal("");
      setEndsLocal("");
      await load();
    } catch {
      setError(true);
    } finally {
      onBusyChange(false);
    }
  }

  async function toggleActive(row: AdminSponsor) {
    onBusyChange(true);
    try {
      await updateAdminSponsor(row.id, { is_active: !row.is_active });
      await load();
    } catch {
      setError(true);
    } finally {
      onBusyChange(false);
    }
  }

  async function onDelete(id: number) {
    if (!window.confirm("¿Eliminar este patrocinio?")) {
      return;
    }
    onBusyChange(true);
    try {
      await deleteAdminSponsor(id);
      await load();
    } catch {
      setError(true);
    } finally {
      onBusyChange(false);
    }
  }

  return (
    <>
      {error ? <p className="admin-banner is-error">No se pudieron cargar o guardar patrocinios.</p> : null}

      <section className="card admin-panel">
        <h2>Nuevo patrocinio</h2>
        <form className="admin-form-grid" onSubmit={(event) => void onCreate(event)}>
          <label>
            Patrocinador
            <input
              value={form.sponsor_name}
              onChange={(event) => setForm({ ...form, sponsor_name: event.target.value })}
              required
            />
          </label>
          <label>
            Contexto
            <select
              value={form.context}
              onChange={(event) =>
                setForm({ ...form, context: event.target.value as AdminSponsorInput["context"] })
              }
            >
              <option value="all">Todo LinkSwiss</option>
              <option value="housing">Solo vivienda</option>
              <option value="job">Solo empleo</option>
            </select>
          </label>
          <label>
            Titular
            <input
              value={form.headline ?? ""}
              onChange={(event) => setForm({ ...form, headline: event.target.value })}
              placeholder="Ej. Escuela de idiomas en Lausanne"
            />
          </label>
          <label>
            URL imagen (opcional)
            <input
              value={form.image_url ?? ""}
              onChange={(event) => setForm({ ...form, image_url: event.target.value })}
              placeholder="https://..."
            />
          </label>
          <label>
            Enlace destino
            <input
              value={form.target_url}
              onChange={(event) => setForm({ ...form, target_url: event.target.value })}
              required
              placeholder="https://..."
            />
          </label>
          <label>
            CHF / mes
            <input
              type="number"
              min={0}
              step="0.01"
              value={form.monthly_chf ?? 0}
              onChange={(event) =>
                setForm({ ...form, monthly_chf: Number(event.target.value) || 0 })
              }
            />
          </label>
          <label>
            Desde
            <input
              type="datetime-local"
              value={startsLocal}
              onChange={(event) => setStartsLocal(event.target.value)}
            />
          </label>
          <label>
            Hasta
            <input
              type="datetime-local"
              value={endsLocal}
              onChange={(event) => setEndsLocal(event.target.value)}
            />
          </label>
          <label>
            Orden
            <input
              type="number"
              min={0}
              value={form.sort_order ?? 0}
              onChange={(event) =>
                setForm({ ...form, sort_order: Number(event.target.value) || 0 })
              }
            />
          </label>
          <label className="admin-check">
            <input
              type="checkbox"
              checked={form.is_active ?? true}
              onChange={(event) => setForm({ ...form, is_active: event.target.checked })}
            />
            Activo
          </label>
          <div className="admin-form-actions">
            <button type="submit" disabled={busy}>
              Crear patrocinio
            </button>
          </div>
        </form>
        <p className="admin-muted">
          Necesitas titular o imagen. Los activos en fechas válidas aparecen en la web como
          “Patrocinado”.
        </p>
      </section>

      <section className="card admin-panel">
        <h2>Patrocinios guardados</h2>
        {rows.length === 0 ? (
          <p className="admin-muted">Aún no hay patrocinios. Crea el primero arriba.</p>
        ) : (
          <table className="admin-table">
            <thead>
              <tr>
                <th>Patrocinador</th>
                <th>Contexto</th>
                <th>CHF/mes</th>
                <th>Impresiones</th>
                <th>Clics</th>
                <th>Estado</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id}>
                  <td>
                    <strong>{row.sponsor_name}</strong>
                    <p className="admin-muted">{row.headline ?? row.target_url}</p>
                    <p className="admin-muted">
                      {formatWhen(row.starts_at)} → {formatWhen(row.ends_at)}
                    </p>
                  </td>
                  <td>{row.context}</td>
                  <td>{formatMoney(row.monthly_chf)}</td>
                  <td>{row.impression_count}</td>
                  <td>{row.click_count}</td>
                  <td>{row.is_active ? "Activo" : "Pausado"}</td>
                  <td className="admin-actions">
                    <button type="button" onClick={() => void toggleActive(row)} disabled={busy}>
                      {row.is_active ? "Pausar" : "Activar"}
                    </button>
                    <button
                      type="button"
                      className="is-danger"
                      onClick={() => void onDelete(row.id)}
                      disabled={busy}
                    >
                      Eliminar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </>
  );
}
