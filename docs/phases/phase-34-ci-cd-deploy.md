# Phase 34 — CI/CD deploy (GitHub Actions → VPS)

**Branch:** `feature/phase-34-ci-cd-deploy`

## Goal
Deploy automatically on each push to `main` by SSH-ing into your VPS and running the production Docker Compose stack (Docker + Caddy).

## Assumptions
- Your VPS already has:
  - Docker + Docker Compose plugin (or `docker-compose`)
  - The repository checked out on disk (a real git folder exists in `DEPLOY_PATH`)
- Your VPS has a production `.env` file in `DEPLOY_PATH` (the workflow does not transfer secrets).

## GitHub Actions setup (secrets)
In your GitHub repo settings → **Secrets and variables** → **Actions** → **New repository secret**, add:

- `SSH_HOST` (e.g. `203.0.113.10`)
- `SSH_USER` (e.g. `root` or `ubuntu`)
- `SSH_PRIVATE_KEY` (your SSH private key, multiline allowed)
- `DEPLOY_PATH` (absolute path on VPS, e.g. `/opt/sentinel-suisse`)
- `SSH_PORT` (optional, default `22`)

## VPS setup (one-time)
1. Ensure `DEPLOY_PATH` contains:
   - `docker-compose.prod.yml`
   - `.env` with at least:
     - `APP_ENV=production`
     - `DOMAIN`
     - `PUBLIC_APP_URL`
     - `TRUSTED_HOSTS`
     - `POSTGRES_PASSWORD`
     - `SECRET_KEY`
     - `PII_ENCRYPTION_KEY`
     - `ADMIN_PASSWORD_HASH`
2. Ensure DNS points to the VPS and ports `80/443` are open (Caddy will request certificates automatically).

## Deploy behavior
- On push to `main`, the workflow connects to the VPS, does a `git pull --ff-only origin main`, then runs:
  - `docker compose -f docker-compose.prod.yml up -d --build`
  - (or `docker-compose` if the plugin isn’t available)

## Rollback
- If the deployment fails, revert the Git commit on the VPS manually and re-run:
  - `docker compose -f docker-compose.prod.yml up -d`

