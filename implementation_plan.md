# DIEYNEM Website — Implementation Plan (Execution Tracker)

> **Lean step-by-step checklist.** Detail lives in `dieynem_website_build_scope.md` (referenced as *BS §x*) and `dieynem_website_analysis_report.md` (*AR §x*). This file is the "what do I do next" tracker — keep it updated as work lands.

## Working agreement (read first)

- **Branches:** `main` = production · `develop` = integration. **Never commit directly to `main` or `develop`.**
- **Flow:** branch off `develop` → build → open **PR into `develop`** → wait for Mussa to allow → he merges (or tells Claude to proceed). `develop → main` only for production releases (its own PR).
- **Branch naming:** `phase0/setup`, `feat/projects-model`, `feat/dashboard-projects`, `fix/<thing>`, `chore/<thing>`.
- **Every PR includes tests** for its change and must pass CI (`test` check) before merge (BS §15).
- **On each merged PR**, a branded PDF report (summary + test status) is auto-generated to the `reports` branch.
- Design tokens (navy `#1E4E86` / amber `#F59E0B`) per **BS §5** — use them everywhere, public + dashboard.
- Don't publish unverified PDF facts — see **AR Appendix / BS §17** before putting figures live.

---

## Phase 0 — Foundations  ·  branch `phase0/setup` → PR into `develop`

- [ ] Django 5.x project (`config/` settings split: base/dev/prod via `django-environ`)
- [ ] App skeletons: `core`, `services`, `projects`, `credentials`, `media_center`, `leads`, `dashboard` (BS §4)
- [ ] PostgreSQL (prod) / SQLite (dev); `requirements.txt` + `requirements-dev.txt` (pinned)
- [ ] Tooling: `ruff`, `black`, `pytest`/Django test runner, `pip-audit`
- [ ] Tailwind pipeline + **design tokens from BS §5.5** in `tailwind.config.js`; self-hosted Inter/Manrope
- [ ] Base public layout (`templates/public/base.html`) + dashboard shell (`templates/dashboard/base.html`, navy sidebar / amber active)
- [ ] Auth: custom branded login, `Administrator` & `Editor` groups (BS §6.7)
- [ ] **Tests:** smoke test (home 200), login required on `/dashboard/`, role permission test
- [ ] CI green; update README setup section

## Phase 1 — Credibility MVP (shippable)  ·  one PR per feature into `develop`

**Models & dashboard CRUD** (BS §6, §8)
- [ ] `SiteSetting` (singleton) + dashboard settings form + **tests**
- [ ] `Service` + dashboard CRUD + **tests**
- [ ] `Project` (+ `ProjectImage` inline, drag-reorder) + dashboard CRUD + **tests**
- [ ] `Certificate` (validity chips, expiry logic) + dashboard CRUD + **tests**
- [ ] `Inquiry` + dashboard list/detail + status flow + **tests**

**Public pages** (BS §7, AR §9/§11/§12)
- [ ] Home (hero, trust strip, services grid, featured projects, ongoing strip, certs preview, CTA) + **test**
- [ ] Services list + detail + **test**
- [ ] Projects list (basic) + case-study detail (AR §12 template) + **test**
- [ ] Certifications page (cards + on-demand download, no raw scans) + **test**
- [ ] Contact + Request-Quotation form → saves lead **and** emails `info@dieynem.co.tz`; honeypot + reCAPTCHA + **test**
- [ ] Seed real content from AR (verified facts only)
- [ ] **Deploy to staging; this is the first live, credible cut.**

## Phase 2 — Living portfolio & depth  ·  PRs into `develop`

- [ ] Ongoing projects: `ProjectMilestone`, `ProjectUpdate`, progress %; public ongoing page + dashboard module + **tests**
- [ ] Gallery (`GalleryImage` + `ProjectImage.show_in_gallery`) + lightbox + dashboard manager + **tests**
- [ ] Downloads (`Download`) + page + dashboard + **tests**
- [ ] `Client`/`Partner` band + `TeamMember` (About) + `Statistic` band + dashboard CRUD + **tests**
- [ ] About page (history, motto, leadership) + **test**
- [ ] SEO: `sitemap.xml`, `robots.txt`, meta + Open Graph + JSON-LD (Organization/Service) + **tests**
- [ ] Image optimisation (WebP/srcset via easy-thumbnails)
- [ ] Certificate expiry warnings on dashboard Overview (< 60 days)

## Phase 3 — Polish & extras  ·  PRs into `develop`

- [ ] Project filtering (HTMX) by service/sector/region/status + **test**
- [ ] Animations / scroll counters / hover states
- [ ] Leads pipeline polish + CSV export
- [ ] Dashboard dark mode (navy surfaces)
- [ ] Audit trail (`django-simple-history`)
- [ ] Performance pass (caching, query tuning) → Lighthouse targets (BS §2)
- [ ] Accessibility pass (focus states, alt text, contrast)
- [ ] *(optional)* Swahili locale · *(optional)* 2FA on dashboard

## Release → production

- [ ] `develop → main` PR, CI green → merge → deploy production
- [ ] Confirm no expired certificate shows as "current"; verify lead email + sitemap live

---

### Pre-launch content gate (from AR Appendix / BS §17)
Confirm with DIEYNEM before going live: VAT number (40-009322-R vs 40-009333-R), Magomeni Market values, Watumishi Housing value, TBS contract ref, plot number (104 vs 106), PAPU contract value & main contractor, and whether the OPPLE table (PDF p.38) lists DIEYNEM's own projects.
