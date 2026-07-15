# Phase 25 — WhatsApp keyword-gated verify

**Branch:** `feature/phase-25-wa-keyword`  
**Goal:** Only auto-verify WhatsApp when the inbound text matches `WHATSAPP_VERIFY_KEYWORD` (default `OK`, case-insensitive).

---

## Your steps (run in order)

### Step 1 — Branch

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
git pull origin main
git checkout -b feature/phase-25-wa-keyword
pip install -e .
```

### Step 2 — Tests

```powershell
$env:TEST_ADMIN_PASSWORD = Read-Host "Contraseña admin"
pytest -q
```

Expect **~76 passed**.

### Step 3 — Commit + merge

```powershell
pre-commit run --all-files
git add -A
git commit -m "feat: require OK keyword for WhatsApp inbound verify (Phase 25)"
git checkout main
git merge feature/phase-25-wa-keyword
git push origin main
```

---

## Behaviour

| Inbound text | Keyword `OK` | Result |
|--------------|--------------|--------|
| `OK` / `ok` | default | Verify |
| `hello` | default | Ignore |
| anything | keyword empty | Verify (legacy) |

Verification WhatsApp copy (5 langs) now tells users they can reply **OK**.

## Config

```
WHATSAPP_VERIFY_KEYWORD=OK
```

## Out of scope (Phase 26+)

- Hosting / TLS
- Conversational bot beyond keyword
- UI polish / guide bot improvements
