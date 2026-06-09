# DIEYNEM Co. Limited — Website & Custom Admin Dashboard Build Scope

**Companion to:** `dieynem_website_analysis_report.md` (strategy & content)
**This document:** the technical implementation plan — stack, architecture, data model, **full brand/colour system**, the **custom admin dashboard**, build phases, and definition of done.
**Audience:** developer (build), client (what they're getting).
**Date:** June 2026

---

## 1. Purpose & Scope

Build DIEYNEM a **portfolio-driven credibility platform** (public website) backed by a **custom-branded admin dashboard** so the client can manage all living content in-house — projects, ongoing-project updates, services, certificates, gallery, downloads and incoming leads — without a developer and without ever touching code or the stock Django admin chrome.

Two deliverables, one Django project:

1. **Public website** — server-rendered, SEO-strong, premium engineering-contractor site (maps to the sitemap in report §8).
2. **Custom admin dashboard** — a bespoke, brand-themed management UI (explicit client/boss requirement: *not* the default Django admin). Covered in detail in §8.

---

## 2. Goals & Success Criteria

- A procurement officer understands "this is a Class One contractor with proven, certified projects" within ~5 seconds of the homepage.
- Every content area in report §13 is editable by non-technical staff from the custom dashboard.
- The site never displays an **expired** certificate as "current" (Tax Clearance & Business License expire annually).
- Lighthouse: Performance ≥ 90, SEO ≥ 95, Accessibility ≥ 90 on the homepage and a project detail page.
- Leads from "Request Quotation / Invite to Tender" are captured in the dashboard **and** emailed to `info@dieynem.co.tz`.
- The admin dashboard visually matches the public brand palette (§5) — it must look like *DIEYNEM's* dashboard, not a generic Django screen.

---

## 3. Stack Decision

**Recommended (committed):**

| Layer | Choice | Why |
|---|---|---|
| Backend | **Django 5.x, Python 3.12** | Matches your stack; batteries-included; ORM + auth + sessions ideal for content + dashboard. |
| Database | **PostgreSQL** (prod) / SQLite (dev) | Robust, free, standard. Pin versions in `requirements.txt`. |
| Public templating | **Django templates** (server-rendered) | Best-in-class SEO, fastest to ship, simplest to host. |
| Styling | **Tailwind CSS** (via `django-tailwind` or a small Node build) | Token-driven design system → enforces the §5 palette consistently across site + dashboard. |
| Interactivity | **Alpine.js** + **HTMX** | Alpine for menus/lightbox/counters; HTMX for project filtering, inline dashboard actions, and partial reloads — no SPA overhead. |
| Rich text | **django-ckeditor-5** (or TinyMCE) | For scope/description fields; configured, not free-form HTML. |
| Images | **Pillow** + **easy-thumbnails** (or `django-imagekit`) | Auto-generate responsive/WebP derivatives — critical for premium look + performance. |
| Forms / spam | Django forms + **honeypot** + optional **django-recaptcha v3** | Protect the quotation/contact forms. |
| Email | Django `EmailBackend` over SMTP | Lead notifications to `info@dieynem.co.tz`. |
| Auth (dashboard) | Django sessions + **custom branded login** + Groups/permissions | Roles: Admin vs Editor (report §13). |
| SEO | `django.contrib.sitemaps`, robots.txt, meta + Open Graph + JSON-LD | Org/Service structured data. |
| Static serving | **WhiteNoise** (or Nginx) | Compressed, hashed static assets. |

**Rejected alternative — Decoupled DRF API + Next.js frontend.** More moving parts, two deploys, harder SEO setup, slower to ship for a content/marketing site, and unnecessary for this traffic profile. Documented here so the decision is explicit and reversible if the client later wants a headless setup.

**On the custom admin:** the boss requires a custom dashboard, so the **primary plan builds a bespoke dashboard app** (§8) using the same Django + Tailwind + Alpine/HTMX stack. *Fallback only if timeline collapses:* theme the Django admin with `django-unfold` to the §5 palette — visually close, far less effort — but this is a contingency, not the plan.

---

## 4. High-Level Architecture

```
Django project: dieynem
│
├── apps/
│   ├── core/          # SiteSetting (singleton), Statistic, Client/Partner, TeamMember, SEO mixin, base templates
│   ├── services/      # Service
│   ├── projects/      # Project, ProjectImage, ProjectMilestone, ProjectUpdate
│   ├── credentials/   # Certificate (registration / tax / license / accreditation / safety / completion)
│   ├── media_center/  # GalleryImage, Download
│   ├── leads/         # Inquiry / QuotationRequest
│   └── dashboard/     # CUSTOM admin: views, forms, templates, permissions (the bespoke UI)
│
├── templates/
│   ├── public/        # home, about, services, projects, ongoing, certifications, gallery, downloads, contact, quote
│   └── dashboard/     # branded login, dashboard shell (sidebar/topbar), CRUD screens, components
│
├── static/  (Tailwind input + compiled CSS, Alpine, icons, JS)
├── media/   (uploaded images, certificate PDFs, downloads)  — or S3-compatible bucket
└── config/  (settings split: base / dev / prod, env via django-environ)
```

One project, two faces (public + dashboard) sharing the same models. Auth separates them: public is open; `/dashboard/*` requires login + role.

---

## 5. Brand & Design System (Colour Scheme, Typography, Components)

This palette applies to **both** the public site and the custom admin dashboard, so they feel like one product. It formalises report §10 (engineering navy + safety-amber accent, drawn from the "Safety First" warning-sticker motif on PDF p.50).

### 5.1 Core palette — hex tokens

**Primary — Engineering Navy** (authority, electrical/utility)

| Token | Hex | Use |
|---|---|---|
| `navy-950` | `#08111E` | Footer bg, deepest surfaces |
| `navy-900` | `#0C1B30` | **Dashboard sidebar**, dark sections |
| `navy-800` | `#12294A` | Hero overlays, dark cards |
| `navy-700` | `#173A66` | Headings on light, button hover |
| `navy-600` | `#1E4E86` | **Primary brand / primary buttons / links** |
| `navy-500` | `#2766AE` | Hover states, secondary accents |
| `navy-400` | `#5089C6` | Icons, borders on dark |
| `navy-300` | `#8FB3DC` | Muted text on dark |
| `navy-100` | `#DCE8F5` | Tints, hover backgrounds |
| `navy-50` | `#EEF4FB` | Section backgrounds |

**Accent — Safety Amber** (energy, CTAs, "high-voltage" highlight — use sparingly)

| Token | Hex | Use |
|---|---|---|
| `amber-600` | `#D97706` | Accent hover, warnings |
| `amber-500` | `#F59E0B` | **Primary accent / key CTAs / active sidebar indicator** |
| `amber-400` | `#FBBF24` | Highlights, focus rings |
| `amber-100` | `#FEF3C7` | Warning chip backgrounds |
| *(optional)* `volt-400` | `#FFD400` | Electric-yellow spark — only for tiny highlights; avoid large fills |

**Neutrals — Slate** (structure, text, surfaces)

| Token | Hex | Use |
|---|---|---|
| `slate-900` | `#0F172A` | Primary body text |
| `slate-700` | `#334155` | Secondary text |
| `slate-500` | `#64748B` | Muted text, captions |
| `slate-300` | `#CBD5E1` | Borders, dividers |
| `slate-200` | `#E2E8F0` | Card borders, table lines |
| `slate-100` | `#F1F5F9` | Chips, hover rows |
| `slate-50` | `#F8FAFC` | **Dashboard content background** |
| `white` | `#FFFFFF` | Cards, nav bar, page bg |

### 5.2 Semantic colours (status chips — used heavily in the dashboard)

| Meaning | Text/Border | Background | Applied to |
|---|---|---|---|
| **Success / Completed / Current** | `#16A34A` | `#DCFCE7` | Completed projects, valid certificates |
| **Warning / Ongoing / Expiring** | `#D97706` | `#FEF3C7` | Ongoing projects, certs near expiry |
| **Danger / Expired / Lost** | `#DC2626` | `#FEE2E2` | Expired certs, lost leads |
| **Info / New** | `#2563EB` | `#DBEAFE` | New inquiries, featured flags |
| **Neutral / Draft** | `#475569` | `#F1F5F9` | Drafts, archived |

### 5.3 Typography

- **Headings:** `Manrope` (or `Inter`) — 600–800 weight; tight tracking on large sizes. Technical, confident.
- **Body:** `Inter` — 400/500; line-height 1.6 for data-heavy project pages.
- **Numbers / IDs / stats:** tabular-nums; optional `JetBrains Mono`/`IBM Plex Mono` for contract values & registration numbers to reinforce the engineered feel.
- Self-host the fonts (performance + offline reliability for the TZ audience).

### 5.4 Component styling rules

- **Buttons:** primary = `navy-600` bg / white text, hover `navy-700`; accent/CTA = `amber-500` bg / `navy-950` text; secondary = white bg / `navy-600` border+text. Radius `rounded-lg`, generous padding, clear focus ring (`amber-400`).
- **Cards:** white, `slate-200` 1px border, `rounded-xl`, subtle shadow (`shadow-sm`→`shadow-md` on hover). Service/project/certificate grids all share this card.
- **Trust badges & status chips:** pill shape, semantic colours (§5.2), uppercase 12px label.
- **Icons:** single-weight line icons (Lucide / Heroicons outline), `navy-600` default, `amber-500` on emphasis.
- **Imagery:** real project photos (PAPU power room, airports, transformers) colour-corrected; navy gradient overlay (`navy-900` 70% → transparent) for text legibility over hero images.
- **Motion:** stat counters animate on scroll; cards lift on hover; restrained fade-ins. No parallax.
- **Avoid:** raw scanned stamps on display surfaces, clip-art, multiple bright accents, rainbow gradients.

### 5.5 Tailwind theme tokens (drop-in config)

```js
// tailwind.config.js — theme.extend.colors
colors: {
  navy:  { 50:'#EEF4FB',100:'#DCE8F5',300:'#8FB3DC',400:'#5089C6',
           500:'#2766AE',600:'#1E4E86',700:'#173A66',800:'#12294A',
           900:'#0C1B30',950:'#08111E' },
  amber: { 100:'#FEF3C7',400:'#FBBF24',500:'#F59E0B',600:'#D97706' },
  volt:  { 400:'#FFD400' },
  slate: { 50:'#F8FAFC',100:'#F1F5F9',200:'#E2E8F0',300:'#CBD5E1',
           500:'#64748B',700:'#334155',900:'#0F172A' },
  ok:'#16A34A', warn:'#D97706', danger:'#DC2626', info:'#2563EB',
}
// fontFamily: { sans:['Inter',...], heading:['Manrope',...], mono:['IBM Plex Mono',...] }
```

> Optional **dark mode for the dashboard**: surfaces shift to `navy-950`/`navy-900`, cards `navy-800`, text `slate-100`, keeping `amber-500` as the accent. Scope as Phase 3 nice-to-have.

---

## 6. Data Model / Schema

All content models inherit a shared **`SEOMixin`** (`meta_title`, `meta_description`, `og_image`) and a **`TimeStampedModel`** (`created_at`, `updated_at`). Ordering via an `order` integer where lists are hand-sorted.

### 6.1 `core` app

**SiteSetting** *(singleton — one editable record)*
| Field | Type | Notes |
|---|---|---|
| company_name | Char | "DIEYNEM Co. Limited" |
| motto | Char | "Quality is our Motto" |
| logo / logo_light | Image | for light/dark surfaces |
| po_box, physical_address | Char/Text | report §2 |
| phones | JSON/Text | multiple numbers |
| emails | JSON/Text | multiple addresses |
| map_embed | Text | Google Maps iframe/coords |
| socials | JSON | optional links |
| default_og_image | Image | SEO fallback |
| footer_text | Text | |

**Statistic** — `label`, `value` (int), `prefix`/`suffix` (e.g. "km", "+"), `order`, `is_active`. Powers the homepage animated band (years, projects, km of line, transformers, solar sets, countries). **Editable so counts stay honest** as the portfolio grows.

**Client** (clients/partners/main contractors) — `name`, `logo`, `type` (client/partner/main_contractor), `website?`, `order`, `is_featured`.

**TeamMember** — `name`, `role`, `qualification` (e.g. "Eng."), `group` (leadership/engineer/support), `photo?`, `order`, `is_active`.

### 6.2 `services` app

**Service** — `name`, `slug`, `short_description`, `full_description` (rich), `icon` (key or SVG), `hero_image?`, `capabilities` (list/JSON), `order`, `is_featured` (homepage), `+SEO`.

### 6.3 `projects` app

**Project**
| Field | Type | Notes |
|---|---|---|
| title | Char | |
| slug | Slug | |
| status | Choice | `completed` / `ongoing` |
| client_name | Char | employer |
| main_contractor | Char? | e.g. BCEG, China Wuyi |
| consultant | Char? | e.g. Atkins |
| location | Char | city/region |
| country | Char | default Tanzania |
| sector | Choice/Tag | Aviation, Government, Education, Housing, Institutional… |
| role | Choice | Prime / Sub / JV Member / Nominated Sub |
| year_start, year_end | Int? | |
| completion_date | Date? | |
| overview | Text | |
| scope_of_work | Rich/List | |
| technical_highlights | Rich/List | kVA/kV specs |
| systems | M2M/Multi | Electrical, ICT, Fire, HVAC, Solar, Power Lines |
| contract_value | Char? | as documented (string to keep currency/notes) |
| contract_value_visible | Bool | hide where unstated (e.g. PAPU) |
| outcome | Text? | |
| related_services | M2M→Service | |
| hero_image | Image | |
| is_featured | Bool | homepage feature |
| order | Int | |
| progress_percent | Int? | ongoing only |
| last_updated_label | Date? | "Last updated" for ongoing |
| +SEO | | |

**ProjectImage** — `project` FK, `image`, `caption`, `date_taken?`, `show_in_gallery` (bool — surfaces in global Gallery), `order`.

**ProjectMilestone** — `project` FK, `title`, `is_complete`, `date?`, `order`. (Ongoing-project milestone bar.)

**ProjectUpdate** — `project` FK, `date`, `note`, `image?`. (Latest-update feed for ongoing projects.)

> One `Project` model covers both completed and ongoing (via `status`); ongoing-specific fields (progress, milestones, updates) simply stay empty for completed projects. Avoids a duplicate model.

### 6.4 `credentials` app

**Certificate**
| Field | Type | Notes |
|---|---|---|
| name | Char | e.g. "CRB Specialist Contractor – Class One" |
| category | Choice | registration / tax / license / accreditation / safety / completion |
| issuer | Char | e.g. Contractors Registration Board |
| number | Char? | reg/cert number |
| issue_date | Date? | |
| valid_to | Date? | null = no expiry |
| is_current | Bool/computed | auto-false past `valid_to`; shown as status chip |
| display_image | Image? | clean thumbnail/icon (NOT raw scan on card face) |
| file | File | the real scan/PDF, download-on-demand |
| downloadable | Bool | |
| related_project | FK→Project? | for completion certificates |
| order | Int | |

> `is_current` should be derived from `valid_to` at render time (and surfaced as Success/Expiring/Expired chips per §5.2), with a manual override flag. Dashboard must warn on certs expiring < 60 days.

### 6.5 `media_center` app

**GalleryImage** — `title?`, `image`, `caption`, `category` (optional), `related_project?`, `order`, `is_active`. (Global gallery = these + `ProjectImage` where `show_in_gallery=True`.)

**Download** — `title`, `description?`, `file`, `category` (company_profile / capability_statement / brochure), `order`, `is_public`.

### 6.6 `leads` app

**Inquiry / QuotationRequest**
| Field | Type | Notes |
|---|---|---|
| name | Char | |
| company | Char? | |
| email, phone | Char | |
| service_interest | FK→Service? | |
| project_type | Char? | |
| message | Text | |
| status | Choice | new / contacted / quoted / won / lost |
| source | Char | quote-form / contact-form |
| created_at | DateTime | |
| internal_notes | Text? | staff notes |

On submit: persist + email `info@dieynem.co.tz` + show success state. Spam-protected (honeypot + reCAPTCHA v3).

### 6.7 Auth & roles

Django `User` + `Group`s:
- **Administrator** — full access incl. SiteSetting, Certificates, Users, SEO.
- **Editor** — Projects, ProjectUpdates/Images, Gallery, Downloads, Inquiries; **no** access to certificates, settings, users.

Permissions enforced in dashboard views (decorators/mixins), not just hidden in UI.

---

## 7. Public Website — Pages & Routes

| Route | Page | Key content |
|---|---|---|
| `/` | Home | Hero, trust-badge strip, services grid, stats band, featured projects, ongoing-airports strip, certifications preview, why-DIEYNEM, clients band, CTA, contact (report §9). |
| `/about/` | About | History (2011), motto, leadership/team, credentials link. |
| `/services/` + `/services/<slug>/` | Services | Grid + detail (capabilities, linked projects). |
| `/projects/` | Portfolio | Filterable (service/sector/region/status) via HTMX; cards. |
| `/projects/<slug>/` | Case study | Report §12 template. |
| `/ongoing-projects/` | Ongoing | Live status, progress bars, milestones, latest updates (airports). |
| `/certifications/` | Credentials | Credential cards by category, status chips, download-on-demand. |
| `/gallery/` | Gallery | Filterable image grid + lightbox. |
| `/downloads/` | Downloads | Company profile PDF, capability statements. |
| `/contact/` | Contact | Address, map, phones, emails, enquiry form. |
| `/request-quotation/` | Quote/Tender | Primary conversion form. |
| `/sitemap.xml`, `/robots.txt` | SEO | Auto-generated. |

---

## 8. Custom Admin Dashboard (bespoke — boss requirement)

A purpose-built, brand-themed management UI at `/dashboard/`, replacing stock Django admin. Server-rendered Django templates + Tailwind (§5 palette) + Alpine/HTMX for snappy inline actions. It must feel like a polished SaaS dashboard, **DIEYNEM-branded**.

### 8.1 Look & layout

- **Branded login** (`/dashboard/login/`) — navy-900 background, DIEYNEM logo, amber-500 sign-in button, subtle engineering motif. No Django admin styling.
- **Shell:** fixed left **sidebar** (`navy-900` bg, white/`slate-300` nav text, `amber-500` active indicator + left border), top bar (white, `slate-200` border) with page title, search, user menu, logout. Content area on `slate-50`.
- **Cards & tables** per §5.4; **status chips** per §5.2 used everywhere (project status, cert validity, lead stage).
- Responsive (usable on tablet); accessible focus states.

### 8.2 Screens / modules

| Module | Screens | Notes |
|---|---|---|
| **Overview / Home** | KPI cards (total projects, ongoing count, new leads this week, certs expiring < 60 days), recent leads table, recent project updates feed, quick-add buttons. | The dashboard landing — surfaces what needs attention. |
| **Projects** | List (filter/search, status chips, featured toggle), Create/Edit (all §6.3 fields; **inline** image uploader with drag-reorder; rich-text scope/highlights; systems multiselect), Delete (confirm). | Core CRUD. Image inline is essential. |
| **Ongoing updates** | Per-project: edit `progress_percent`, manage **milestones** (add/toggle/reorder), post **ProjectUpdate** entries (date + note + photo), set "last updated". | Keeps airport projects looking live. |
| **Services** | List + Create/Edit (capabilities list, icon picker, feature toggle, linked projects). | |
| **Certificates** | List grouped by category with **validity chips**; Create/Edit (file upload, dates, downloadable toggle); **expiry warnings** banner. | Must flag Tax Clearance / Business License renewals. |
| **Gallery** | Grid manager, bulk upload, captions, reorder, show/hide, link to project. | |
| **Downloads** | Upload/replace company profile & brochures, categorise, public toggle. | |
| **Leads / Inquiries** | Table (status chips, filter by stage), detail drawer, change status (new→contacted→quoted→won/lost), internal notes, export CSV. | The sales pipeline view. |
| **Clients / Partners** | Logo manager, type, order, feature. | Homepage clients band. |
| **Team** | Members CRUD, group, order, photo. | About page. |
| **Statistics** | Edit the homepage counters (label/value/suffix/active). | Honest, editable numbers. |
| **Site Settings** | Singleton form: contacts, address, map, socials, logos, default OG image, footer. | Admin role only. |
| **SEO** | Per-page meta defaults + per-record meta (title/description/OG) editable inline on each content form. | |
| **Users & Roles** | Manage staff accounts, assign Administrator/Editor. | Admin role only. |

### 8.3 Cross-cutting dashboard features

- **Image handling in-UI:** drag-drop upload, auto-thumbnail preview, reorder, alt/caption — all without leaving the form (HTMX + Alpine).
- **Validation & autosave-draft** on long project forms; slug auto-from-title.
- **Confirmations** on destructive actions; soft-delete/archive option for projects.
- **Expiry intelligence:** background check (or on-load query) flags certificates within 60 days of `valid_to` on the Overview and Certificates screens.
- **Audit trail (Phase 3):** who changed what, when (Django simple-history) — useful for a multi-staff client.
- **Empty states & helper text** so non-technical staff are never lost.

### 8.4 Build approach

- Reusable Django **`ModelForm`s** + class-based views (`ListView`/`CreateView`/`UpdateView`/`DeleteView`) wrapped in a shared `dashboard/base.html` shell.
- Generic, themeable **table** and **form** partial templates to avoid rebuilding UI per model.
- HTMX endpoints for inline reorder, status changes, image upload, and filtered tables.
- Permission mixins gate Administrator-only modules.
- *Contingency (only if timeline collapses):* `django-unfold` theming of Django admin to the §5 palette — visually adjacent, ~70% less effort — but the committed deliverable is the custom dashboard above.

---

## 9. SEO & Structured Data

- Per-page `<title>`/meta/Open Graph from `SEOMixin` with `SiteSetting` fallbacks.
- **JSON-LD:** `Organization` (name, logo, address, contacts), `Service` per service, and `CreativeWork`/`Project`-style markup per case study.
- `sitemap.xml` (services, projects, static pages), `robots.txt`.
- Semantic headings, descriptive alt text (enforced in dashboard image forms), clean slugs.
- Target keywords baked into copy: "electrical contractor Tanzania", "HVAC contractor Dar es Salaam", "ICT structured cabling Tanzania", "rural electrification contractor", "solar street lights Tanzania".
- Swahili locale (`django.utils.translation`) — **Phase 3 / optional**.

---

## 10. Media & Image Handling

- `easy-thumbnails`/`imagekit` to generate responsive sizes + **WebP**; serve via `<picture>`/`srcset`.
- Lazy-load below-the-fold images; navy gradient overlays on heroes.
- Certificate **scans/PDFs** stored as downloadable files; **never** rendered as the card face (report §7) — clean re-typeset card + on-demand download.
- Media storage: local `media/` behind Nginx for v1; **S3-compatible bucket** recommended if image volume grows (the source PDF alone is 30 MB of photos). Decide in Phase 0.

---

## 11. Security & Forms

- HTTPS everywhere; `SECURE_*` settings, HSTS, secure cookies in prod.
- CSRF on all forms; honeypot + reCAPTCHA v3 on public forms.
- Rate-limit the quotation/contact endpoints.
- Secrets via env (`django-environ`); never commit `.env`.
- Dashboard behind login + role checks; strong password policy; optional 2FA (Phase 3).
- `pip-audit` in CI (your standing rule).

---

## 12. Performance

- WhiteNoise compressed/hashed static; Tailwind purged build.
- DB query optimisation (`select_related`/`prefetch_related`) on project/cert lists.
- Page/fragment caching for public pages (low write frequency); cache-bust on dashboard save.
- Self-hosted fonts, deferred non-critical JS, image optimisation (§10).

---

## 13. Deployment & DevOps

- **Hosting:** Ubuntu VPS (Gunicorn + Nginx + PostgreSQL) — practical and cost-effective for the TZ audience; or a managed PaaS if preferred.
- **CI/CD:** GitHub Actions — lint (`ruff`/`black`), `python manage.py test`, `pip-audit`, build Tailwind, deploy on merge to `main`.
- **Settings split:** `base/dev/prod`; env-driven.
- **Backups:** nightly DB dump + media backup (especially certificates/leads).
- **Domain/email:** align with existing `dieynem.co.tz`; configure SMTP for lead notifications.

---

## 14. Build Phases & Sequencing

Estimates assume **one experienced full-stack dev**; ranges, not promises.

### Phase 0 — Foundations (≈ 2–3 days)
Repo, Django project + apps skeleton, settings split, PostgreSQL, Tailwind + **§5 design tokens**, base public layout + dashboard shell, auth + roles, deployment skeleton, CI.

### Phase 1 — Credibility MVP *(shippable)* (≈ 7–10 days)
Models: `Service`, `Project` (+images), `Certificate`, `SiteSetting`, `Inquiry`. Custom dashboard CRUD for these. Public pages: Home, Services (+detail), Projects (+case study), Certifications, Contact + Request-Quotation (with email). Seed real content from the report. **This is the minimum that out-credentials competitors.**

### Phase 2 — Living portfolio & depth (≈ 6–8 days)
Ongoing projects (milestones/updates/progress), Gallery, Downloads, Clients/Partners, Team, Statistics band, About page, dashboard modules for all of the above, SEO (sitemaps + JSON-LD), image optimisation, cert expiry warnings.

### Phase 3 — Polish & extras (≈ 4–6 days)
Project filtering (HTMX), animations/counters, leads pipeline polish + CSV export, dashboard dark mode, audit trail, performance pass, accessibility pass, optional Swahili, optional 2FA.

**Ship Phase 1, then iterate.** Don't gold-plate the dashboard before the public site is live and generating leads.

---

## 15. Definition of Done (acceptance criteria)

- [ ] All report §13 content types are CRUD-manageable from the **custom** dashboard by an Editor (no code, no Django admin).
- [ ] Public site matches the §5 palette and renders the report §9 homepage sections.
- [ ] Project case studies follow the report §12 template; images optimised/WebP.
- [ ] Certificates show correct validity chips; an expired cert is never labelled "current"; expiry warnings appear < 60 days.
- [ ] Quotation/contact submissions persist to the dashboard **and** email `info@dieynem.co.tz`; spam-protected.
- [ ] Roles enforced (Editor cannot reach Certificates/Settings/Users).
- [ ] Lighthouse targets met (§2); responsive on mobile/tablet.
- [ ] `sitemap.xml`, `robots.txt`, JSON-LD present; meta editable per page.
- [ ] Backups + CI (tests, `pip-audit`) green.

---

## 16. Out of Scope (v1) / Future

E-commerce/payments; client login portal; multi-language beyond Swahili; blog/news (optional add-on); CRM integrations; mobile app. Note in proposal as future phases.

---

## 17. Dependencies & Open Questions (need from client before/while building)

**Content/assets needed:** high-res logo (light/dark), brand confirmation of navy+amber palette, real high-res project photos (beyond the PDF), confirmed contacts/office address, Google Maps location, client-logo usage permission, final company-profile PDF for Downloads.

**Data-integrity items to confirm** (carried from report appendix — do not publish until resolved): correct VAT number (40-009322-R vs 40-009333-R); Magomeni Market values; Watumishi Housing value; TBS contract reference; physical plot number (104 vs 106); PAPU contract value & main contractor; whether the OPPLE p.38 table lists DIEYNEM's own projects.

**Decisions:** media storage (local vs S3); hosting (VPS vs PaaS); reCAPTCHA vs honeypot-only; dashboard dark mode in v1 or later; Swahili in v1 or later.

---

## 18. Traceability — report section → build feature

| Report § | Build artefact |
|---|---|
| §2 Identity | `SiteSetting`, `TeamMember`, About page |
| §3 Services | `Service` model + Services pages |
| §4 Selling points | Trust-badge strip, stats band (`Statistic`) |
| §5 Portfolio | `Project` + case studies + filtering |
| §6 Ongoing | `Project(status=ongoing)`, milestones, updates |
| §7 Certificates | `Certificate` + Certifications page + dashboard expiry logic |
| §8 Sitemap | §7 routes |
| §9 Homepage | Home template sections |
| §10 Design | §5 design system + Tailwind tokens |
| §11 Tone/messaging | Seed copy |
| §12 Case study template | `Project` fields + case-study template |
| §13 Admin panel | **§8 Custom Admin Dashboard** |
| §14 Benchmark | Portfolio/cert emphasis (the differentiators competitors lack) |
| §15 Final rec | Phase 1 priority = credibility MVP |
```
