# CLAUDE.md — DIEYNEM Co. Limited Website

Project-specific guidance for Claude Code. Global rules in `~/.claude/CLAUDE.md` still apply; this file adds and, where stated, overrides for this repo.

## What this project is

A **portfolio-driven credibility website** for DIEYNEM Co. Limited (a Tanzanian Class One electrical / ICT / fire / HVAC / rural-electrification contractor) **plus a custom-branded admin dashboard** the client manages content from.

- Strategy & content source of truth: `dieynem_website_analysis_report.md` (*AR*)
- Technical plan: `dieynem_website_build_scope.md` (*BS*)
- Execution checklist: `implementation_plan.md`

## Stack (committed — see BS §3)

- **Backend:** Django 5.x · Python 3.12 · PostgreSQL (prod) / SQLite (dev)
- **Frontend:** Django templates (server-rendered) · **Tailwind CSS** · Alpine.js · HTMX. **No React/Next/Vue.**
- **Admin:** a **custom dashboard app** (`dashboard/`) — **NOT** the stock Django admin. The client/boss requires a bespoke, brand-themed UI.
- Email leads via SMTP to `info@dieynem.co.tz`.

## Branch & PR flow (strict)

- `main` = production · `develop` = integration.
- **Never push directly to `main` or `develop`** — both are protected.
- Work on a feature branch off `develop` (`feat/…`, `fix/…`, `chore/…`, `phaseN/…`), then **open a PR into `develop`**.
- **Stop after opening the PR.** Mussa reviews, allows, and merges (or tells Claude to proceed). Do not self-merge.
- Production releases are a separate `develop → main` PR.
- The `reports` branch holds auto-generated PR PDFs — **do not edit it manually.**
- > Note: PRs are authored and accepted by the same GitHub account, so GitHub disables self-"Approve". The report automation therefore triggers on **merge**, which is the effective "approval".

## Testing (required every step — BS §15)

- Every feature/fix PR **must add or update tests** for its change.
- `python manage.py test` (or `pytest`) must pass; CI `test` check must be green before merge.
- Cover: model behaviour, views/permissions (Editor vs Administrator), forms (lead capture + spam guard), and the certificate-expiry logic.

## Code conventions

- Follow Django idioms (MTV, fat models / thin views, DRF only if an API is later needed).
- Run `ruff check .` and `black .` before every commit; type hints in function signatures.
- Pin dependency versions in `requirements*.txt`; run `pip-audit` periodically.
- English for all code, comments, docs.
- Secrets via env (`django-environ`); never commit `.env` or the source company-profile PDF.

## Design system (use everywhere — BS §5)

- **Primary navy** `#1E4E86` (scale `navy-50…950`), **accent amber** `#F59E0B`, slate neutrals, semantic status chips (completed=green, ongoing/expiring=amber, expired/lost=red, new=blue).
- Headings Manrope, body Inter, mono for contract values / reg numbers.
- Tailwind tokens are the single source of truth (BS §5.5) — apply identically to public site and dashboard.
- Never render raw certificate scans on display surfaces — clean card + download-on-demand (AR §7).

## Content integrity

Do **not** publish unverified facts from the source PDF. The figures flagged in *AR Appendix* / *BS §17* (VAT number, Magomeni/Watumishi values, TBS ref, plot number, PAPU value, OPPLE table) must be confirmed by DIEYNEM before going live.

## Handy commands (once Phase 0 lands)

```bash
python manage.py runserver        # dev server
python manage.py test             # tests (must pass before PR)
ruff check . && black --check .   # lint/format
npm run tailwind:build            # compile CSS (or django-tailwind equivalent)
```
