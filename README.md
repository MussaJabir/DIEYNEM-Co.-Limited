# DIEYNEM Co. Limited — Website & Admin Dashboard

[![CI](https://github.com/MussaJabir/DIEYNEM-Co.-Limited/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/MussaJabir/DIEYNEM-Co.-Limited/actions/workflows/ci.yml)
[![Deploy](https://github.com/MussaJabir/DIEYNEM-Co.-Limited/actions/workflows/deploy.yml/badge.svg?branch=main)](https://github.com/MussaJabir/DIEYNEM-Co.-Limited/actions/workflows/deploy.yml)

**Live:** [dieynem.bjptechnologies.co.tz](https://dieynem.bjptechnologies.co.tz)

A portfolio-driven **credibility platform** for DIEYNEM Co. Limited — a Tanzanian Class One electrical, ICT, fire-detection, HVAC, solar and rural-electrification contractor — backed by a **custom-branded admin dashboard** for in-house content management.

> Public repository. The code is the proprietary property of DIEYNEM Co. Limited (see `LICENSE`) — viewable, but not licensed for reuse.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Django 5.x · Python 3.12 |
| Database | PostgreSQL (prod) · SQLite (dev) |
| Frontend | Django templates · Tailwind CSS · Alpine.js · HTMX |
| Admin | Custom dashboard app (not Django admin) |
| Hosting | Ubuntu · Apache (reverse-proxy) → Gunicorn → PostgreSQL · TLS via certbot |

## Documentation

| File | Purpose |
|---|---|
| `dieynem_website_analysis_report.md` | Strategy, content & brand direction (the "what / why") |
| `dieynem_website_build_scope.md` | Technical implementation plan, data model, design system, custom dashboard (the "how") |
| `implementation_plan.md` | Lean phase-by-phase execution checklist |
| `CLAUDE.md` | Conventions for Claude Code / contributors |

## Project structure (see build scope §4)

```
config/        # settings (base/dev/prod), urls, wsgi
apps/
  core/        # site settings, stats, clients, team, SEO
  services/    # services
  projects/    # projects, images, milestones, updates
  credentials/ # certificates & compliance
  media_center/# gallery & downloads
  leads/       # quotation / contact inquiries
  dashboard/   # custom branded admin
templates/     # public/ + dashboard/
static/        # tailwind input/output, js, icons
```

## Local development

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
python manage.py migrate           # also seeds verified content
npm install && npm run tailwind:build   # compile Tailwind CSS
python manage.py runserver
```

## Branching & workflow

- `main` — production (protected)
- `develop` — integration (protected); all PRs target this branch
- `feat/*`, `fix/*`, `chore/*`, `phaseN/*` — work branches off `develop`
- `reports` — auto-generated PR report PDFs (machine-managed, do not edit)

Flow: branch off `develop` → build (with tests) → PR into `develop` → review & merge → release via `develop → main` PR.

## Automated PR reports

When a PR is **merged**, a GitHub Action generates a branded PDF report (PR summary, commits, files changed, diff stats, test status) and commits it to the **`reports`** branch — directly viewable on GitHub, plus uploaded as a workflow artifact. See [`reports` branch](https://github.com/MussaJabir/DIEYNEM-Co.-Limited/tree/reports).

## Deployment

Hosted on an Ubuntu server: Apache reverse-proxies to Gunicorn (systemd) over a
unix socket, backed by PostgreSQL, with TLS via certbot.

**Auto-deploy:** merging `develop → main` runs the full test suite, then deploys
over SSH — it pulls `main`, rebuilds Tailwind, applies migrations (which seed
content), collects static files, and restarts Gunicorn.

One-time server setup, the systemd/Apache config and the deploy script live in
[`deploy/`](deploy/) — see [`deploy/README.md`](deploy/README.md) for the full runbook.

## License

Proprietary — © 2026 DIEYNEM Co. Limited. All rights reserved. See [`LICENSE`](LICENSE).
