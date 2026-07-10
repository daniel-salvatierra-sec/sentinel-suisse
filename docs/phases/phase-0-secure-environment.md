# Phase 0 — Secure Environment (COMPLETED)

**Project:** Sentinel Suisse  
**Author:** Daniel Salvatierra  
**Date completed:** 10 July 2026  
**Commit:** `832c0d2` — `chore: Fase 0 - entorno seguro inicial`  
**Branch:** `main`, `feature/fase-0` (same commit)

---

## Objective

Establish a secure development foundation before writing application logic: secret handling, Git workflow, automated security hooks, and local infrastructure skeleton.

---

## Tools installed

| Tool | Version | Purpose |
|------|---------|---------|
| Git | 2.55.0.windows.2 | Version control |
| Python | 3.14.6 | Runtime (project requires ≥ 3.11) |
| pre-commit | 4.6.0 | Git hooks orchestration |
| gitleaks | via hook | Secret detection |
| ruff | 0.15.21 | Linting / formatting |
| bandit | 1.9.4 | Python security static analysis |

---

## Commands executed (in order)

### 1. Navigate to project

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
```

### 2. Initialize Git repository

```powershell
git init -b main
```

**Result:** `Initialized empty Git repository in C:/Users/danin/Projects/sentinel-suisse/.git/`

### 3. Configure Git identity (first-time setup)

```powershell
git config --global user.name "Daniel Salvatierra"
git config --global user.email "daninohemyshoping2020@gmail.com"
```

### 4. Stage files and verify `.env` is ignored

```powershell
git add -A
git status
git check-ignore -v .env
```

**Evidence:** `.env` not listed in staged files.  
**check-ignore output:** `.gitignore:2:.env    .env`

### 5. First commit

```powershell
git commit -m "chore: Fase 0 - entorno seguro inicial"
```

**Result:** 13 files changed, 352 insertions.

### 6. Create feature branch

```powershell
git branch feature/fase-0
git branch
```

**Result:** `feature/fase-0` and `* main` both at `832c0d2`.

### 7. Python virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Verify:** prompt shows `(.venv)`.

### 8. Install development dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

### 9. Install pre-commit hooks

```powershell
pre-commit install
```

**Result:** `pre-commit installed at .git\hooks\pre-commit`

### 10. Security verification

```powershell
git ls-files .env
pre-commit run --all-files
git log --oneline
```

---

## Security checklist (all passed)

| # | Check | Evidence |
|---|-------|----------|
| 1 | `.gitignore` excludes `.env`, `*.pem`, credentials | File committed |
| 2 | `.env.example` has variable names only | File committed |
| 3 | `.env` not tracked by Git | `git ls-files .env` → empty |
| 4 | gitleaks clean | `Passed` |
| 5 | ruff clean | `Passed` |
| 6 | bandit clean | `Passed` |
| 7 | pre-commit hooks active | `.git/hooks/pre-commit` exists |
| 8 | CI workflow present | `.github/workflows/security.yml` |
| 9 | No secrets in commit history | gitleaks on all files |
| 10 | Feature branch workflow started | `feature/fase-0` created |

---

## pre-commit output (evidence)

```
Detect hardcoded secrets.................................................Passed
ruff.....................................................................Passed
ruff-format..............................................................Passed
bandit...................................................................Passed
```

---

## Repository scaffold created

- `.gitignore`, `.env.example`, `pyproject.toml`
- `.pre-commit-config.yaml` (gitleaks, ruff, bandit)
- `.github/workflows/security.yml`
- `docker-compose.yml` (Postgres 16 + Redis 7)
- `src/sentinel_suisse/__init__.py`
- `docs/agent-prompts/`

---

## Cross-cutting rules (every phase)

1. Agent builds the block with explicit security instructions.
2. No real credentials in prompts or code — use `os.getenv()`.
3. Work on `feature/*` branches, never commit directly to `main`.
4. Review full diff (auth, DB queries, external input).
5. Run phase security tools before merge.
6. Fix issues before advancing — never "fix later".

---

## Next phase

**Phase 1 — Data model:** SQLAlchemy models, Alembic migrations, privacy data map (nLPD). No business logic or public endpoints yet.

See [phase-1-data-model.md](phase-1-data-model.md).
