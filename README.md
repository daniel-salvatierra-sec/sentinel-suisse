# Sentinel Suisse

Agregador suizo de anuncios de vivienda y empleo con alertas multicanal (WhatsApp, email).

Proyecto personal con metodología secure-by-design: cada fase cierra con checklist de seguridad y evidencia antes de avanzar.

## Fase 0 — Entorno seguro

### Requisitos

- Python 3.11+
- Git
- Docker Desktop (opcional, para Postgres y Redis locales)
- [gitleaks](https://github.com/gitleaks/gitleaks) (vía pre-commit)

### Configuración inicial (una sola vez)

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup-fase0.ps1
```

El script hace: `git init`, primer commit, rama `feature/fase-0`, venv, `pip install`, `pre-commit install`, y verifica que `.env` está ignorado.

**Repo privado en GitHub** (cuando tengas `gh` autenticado):

```powershell
gh repo create sentinel-suisse --private --source=. --remote=origin
git push -u origin main
```

**Servicios locales** (Postgres + Redis):

```powershell
docker compose up -d
```

### Checklist Fase 0

- [x] `.gitignore` con `.env`, `*.pem`, credenciales
- [x] `.env.example` con nombres de variables (sin valores reales)
- [x] `pre-commit` configurado (gitleaks, ruff, bandit)
- [x] CI seguridad en `.github/workflows/security.yml`
- [x] `docker-compose.yml` (Postgres 16 + Redis 7)
- [ ] Ejecutar `.\scripts\setup-fase0.ps1` en tu máquina
- [ ] `gitleaks` limpio sobre el historial git
- [ ] `.env` real NO está en el repo (`git status` no lo lista)
- [ ] `pre-commit run --all-files` pasa sin errores
- [ ] Repo privado creado en GitHub

### Estructura

```
sentinel-suisse/
├── src/sentinel_suisse/    # Código fuente
├── docs/agent-prompts/     # Prompts de seguridad por fase
├── .github/workflows/      # CI seguridad
└── docker-compose.yml      # Postgres + Redis
```

## Licencia

Privado — uso personal.
