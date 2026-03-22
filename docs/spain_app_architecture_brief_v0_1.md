# App Architecture Brief
## Spain Summer 2027 — City Discovery & Planning Tool

**Prepared:** March 2026 · **Status:** Draft · **Version:** 0.2

---

## 1. Purpose

This brief defines the architecture, technology stack, data layer, and build sequence for the Spain Summer 2027 local web application. It is the authoritative reference for all application development decisions and must be read alongside the other project documents.

This brief is downstream of the Project Brief (v1.2), Data Spec (v0.6), Scoring Brief (v1.1), and Research Pipeline Brief (v1.0). It does not redefine any data schema, scoring methodology, or research process — those are governed by their respective documents. Where this brief references field names, attribute IDs, or scoring weights, those definitions live in the Data Spec and Scoring Brief respectively.

---

## 2. Relationship to Other Documents

| Document | Version | Relationship |
|---|---|---|
| Project Brief | v1.2 | Parent — defines views, actions, hard requirements, traveler context |
| Data Spec | v0.6 | Schema authority — all field names, types, and enums used here conform to §3 and §10 of the Data Spec |
| Scoring Brief | v1.1 | Defines composite score formula and weights — the app calculates but does not define these |
| Research Pipeline Brief | v1.0 | Defines the JSON file format the app ingests — import logic must conform to the pipeline output structure |

---

## 3. Platform Constraints

These constraints are fixed and not subject to architectural trade-offs:

- Runs locally — no hosted deployment or cloud infrastructure
- Accessed via desktop web browser
- Two users: Cara and Abigail — no authentication required
- Data is produced by the research pipeline as structured JSON files — the app must ingest these
- Manual override of agent-populated data must be possible
- Started by running `next dev` in a terminal — this is acceptable for local use
- **Primary build and automation environment is Claude Cowork** — this is first and foremost a Cowork experiment. The research pipeline and the app run on the same machine. Cowork orchestrates file operations, pipeline runs, and automation tasks on the local desktop.
- The research pipeline writes JSON files to a shared local directory (`/research/cities/`) that the app reads from directly. No file upload step is required — the app watches or reads from this directory on demand.

---

## 4. Technology Stack

| Layer | Choice | Notes |
|---|---|---|
| Framework | **Next.js 14 (App Router)** | API routes replace a separate Express server. Server components handle data fetching. |
| Language | **TypeScript** | Strict mode. All Data Spec types modelled as TypeScript interfaces. |
| UI Components | **shadcn/ui** | Components installed as owned source files — not a black-box library. Built on Radix UI primitives. |
| Styling | **Tailwind CSS** | Included with shadcn. Utility-first. No separate CSS files. |
| Theming | **Dark / light mode via `next-themes`** | System preference as default. Toggle available in the app header. shadcn components support this natively via CSS variables. |
| Data Layer | **SQLite via `better-sqlite3`** | Synchronous API. No ORM. Raw SQL only. |
| Maps | **React Leaflet + OpenStreetMap tiles** | No API key required. Used for both country-level and city-level map views. |
| AI Summaries | **Anthropic Claude API** (`claude-sonnet-4-20250514`) | Called from a Next.js API route — API key never exposed to the browser. |

### Why SQLite over raw JSON reads

The research pipeline produces one JSON file per city. The app could read these directly, but the data model is genuinely relational — a city has five hard requirement records, up to 14 attribute records, multiple rental neighbourhood records, multiple language programme records, and contact tracking entries, all joined by city ID. Ranking, filtering, and composite score calculation across multiple cities is a SQL problem, not a JSON problem.

SQLite is the correct layer. JSON files remain the pipeline's output format and the app's import source. They are not the runtime data store.

---

## 5. Data Layer

### 5.1 File Structure

```
/data/
  spain2027.db          ← SQLite database (gitignored)

/research/              ← Pipeline output — read by import process
  index.json
  cities/
    {city-id}.json

/src/
  lib/
    db.ts               ← SQLite connection and migration runner
    schema.sql          ← Table definitions
    import.ts           ← JSON → SQLite import function
    score.ts            ← Composite score calculation
    types.ts            ← TypeScript interfaces matching Data Spec v0.6
```

### 5.2 Database Schema

Tables conform exactly to Data Spec v0.6. One table per data section.

| Table | Data Spec Section | Notes |
|---|---|---|
| `cities` | §1 City Core | One row per city |
| `hard_requirements` | §2 Hard Requirements | Five rows per city. Includes facility location fields for `swim_club` and `spanish_program`. |
| `discovery_attributes` | §3 Discovery Attributes | Up to 14 rows per city (12 scored + 2 unscored display fields) |
| `rental_neighbourhoods` | §4 Rental Neighbourhoods | One or more rows per city |
| `language_programmes` | §5 Language Programmes | One row per programme per city |
| `contact_tracking` | §6 Contact Tracking | Three rows per city (swim_club, language_program, rental) |
| `research_notes` | §7 Research Notes & AI Summary | One row per city |
| `scoring_config` | §10 Scoring Config | Single shared config — 12 rows, one per scored attribute |

`moorish_architecture` and `day_trip_quality` are stored as rows in `discovery_attributes` with `score = null` — consistent with Data Spec §3 which classifies them as unscored display fields excluded from the composite score calculation.

### 5.3 Scoring Config Seed Values

The `scoring_config` table is seeded on first run with the weights defined in Scoring Brief v1.1. These values are the authoritative source — do not hardcode weights in application logic.

| attributeId | weight |
|---|---|
| swim_club_quality | 0.15 |
| language_program_quality | 0.13 |
| avg_june_july_temp | 0.12 |
| walkability_transit | 0.10 |
| scuba_diving_access | 0.10 |
| mountain_hiking_access | 0.07 |
| food_market_culture | 0.06 |
| european_rail_access | 0.06 |
| car_free_quality | 0.06 |
| rental_cost | 0.05 |
| rental_quality_proximity | 0.05 |
| tourist_density | 0.05 |

### 5.4 Composite Score Calculation

Implemented in `src/lib/score.ts`. Conforms to Scoring Brief v1.1 §3:

```
Composite Score = Σ (attribute_score × weight)
```

- Reads weights from `scoring_config` table — never hardcoded
- Only scored attributes contribute (excludes `moorish_architecture` and `day_trip_quality`)
- Only attributes with a non-null `score` value are included in the sum
- Eliminated cities are excluded from ranking
- Score is recalculated on demand — not stored as a static value until explicitly written back to the `cities` table

### 5.5 JSON Import

`src/lib/import.ts` handles ingestion of research pipeline output.

- Accepts a single city JSON file path or the full `/research/cities/` directory
- Upserts all sections into the correct tables — idempotent, safe to re-run
- Respects `sourceType` field: pipeline-produced records are marked `agent`, manually edited records retain `manual`
- Manual overrides are preserved on re-import — agent data does not overwrite `sourceType = manual` records
- Triggers composite score recalculation after each city import
- Updates `cities.updatedAt` and `cities.researchStatus` from the imported file

---

## 6. API Routes

All data mutations and external calls go through Next.js API routes. The browser never accesses SQLite or the Claude API directly.

| Route | Method | Purpose |
|---|---|---|
| `/api/import` | POST | Import a single city JSON file by path from the shared local directory |
| `/api/import/all` | POST | Import all JSON files from `/research/cities/` on the local filesystem |
| `/api/cities` | GET | Return all cities with status and composite score |
| `/api/cities/[id]` | GET | Return full city record |
| `/api/cities/[id]` | PATCH | Update any field — manual override support |
| `/api/cities/[id]/score` | POST | Recalculate and persist composite score |
| `/api/cities/[id]/summary` | POST | Generate AI executive summary via Claude API |
| `/api/scoring-config` | GET | Return current scoring weights |
| `/api/scoring-config` | PATCH | Update weights — triggers score recalculation for all active cities |

---

## 7. Views

Conforms to Project Brief v1.2 §4.1. Each view maps to a Next.js App Router page.

| View | Route | Description |
|---|---|---|
| City List | `/` | Table of all candidate cities — hard requirement status badges, composite score, research status, rank. Filterable by status. Default landing page. |
| Dashboard | `/dashboard` | Aggregate view — research completion progress, score distribution, top-ranked cities, cities needing attention. |
| City Detail | `/cities/[id]` | Full city record — all attributes with raw values and scores, hard requirement status, rental neighbourhoods, language programmes, contact tracking notes, AI summary. |
| Comparison | `/compare` | Side-by-side comparison of 2–4 cities. All scored attributes shown with score and raw value. Composite score and rank displayed per city. |
| Country Map | `/map` | React Leaflet map of Spain. One pin per city, coloured by status (active / eliminated / pending). Click pin to navigate to City Detail. |
| City Map | `/cities/[id]/map` | City-level React Leaflet map. Pins for swim club, language program, and candidate rental neighbourhoods. Walking/transit time labels from hard requirement and rental neighbourhood records. |

---

## 8. Actions and Interactions

Conforms to Project Brief v1.2 §4.2.

| Action | Location | Behaviour |
|---|---|---|
| Import city data | Dashboard or City List | Trigger import of a single city by ID or bulk import of all files from `/research/cities/` on the local filesystem. No file upload required — pipeline and app share the same directory. Runs upsert — safe to re-run. |
| Override attribute score or notes | City Detail | Inline edit on any agent-populated field. Saves with `sourceType: manual`. Manual records are visually distinguished from agent records. |
| Update hard requirement status | City Detail | Toggle pass / fail / unknown per requirement. If any requirement is set to `fail`, city status is automatically updated to `eliminated`. |
| Recalculate composite score | City Detail / City List | Triggered manually or automatically after any attribute or weight change. |
| Edit research notes | City Detail | Free-text field, autosaved. |
| Edit contact tracking notes | City Detail | Free-text field per contact type (swim_club, language_program, rental), autosaved. |
| Flag city status | City List / City Detail | Set city status to active / pending / eliminated / flagged. |
| Generate AI summary | City Detail | On-demand button. Sends full city record to Claude API. Displays result inline. Stores result with `aiSummaryGeneratedAt` timestamp. Staleness indicator shown if underlying data has changed since last generation. |
| Compare cities | City List | Multi-select cities, navigate to Comparison view. |

---

## 9. AI Executive Summary

The AI summary feature calls the Claude API from a server-side Next.js API route (`/api/cities/[id]/summary`).

- Model: `claude-sonnet-4-20250514`
- API key stored in `.env.local` — never exposed to the browser
- Input: full city record serialised as structured context — all hard requirement statuses, all attribute scores and raw values, research notes
- Prompt instructs the model to surface: key strengths, notable weaknesses, open items requiring manual outreach, and a plain-language recommendation on whether the city warrants shortlisting
- Response stored in `research_notes.aiSummary` with `aiSummaryGeneratedAt` timestamp
- Staleness detection: `aiSummaryDataVersion` stores a hash of the city data at time of generation. App flags the summary as potentially stale if the underlying data has changed since generation — consistent with Data Spec §7.

---

## 10. TypeScript Types

All Data Spec v0.6 entities are modelled as TypeScript interfaces in `src/lib/types.ts`. Interface names and field names match Data Spec field names exactly — no renaming or aliasing. This ensures that import logic, API routes, and UI components all use a consistent vocabulary that traces directly back to the Data Spec.

---

## 11. Build Sequence

| Phase | Deliverable | Depends On |
|---|---|---|
| 1 | Project scaffold — Next.js, shadcn, SQLite wired up, schema created, scoring config seeded | Nothing |
| 2 | JSON import pipeline — import function, `/api/import` route, idempotent upsert | Phase 1 |
| 3 | City List view — table with status badges, composite score, research status | Phase 2 |
| 4 | City Detail page — all attributes, hard requirements, contact notes, manual override | Phase 2 |
| 5 | Composite score calculation and ranking | Phase 2 |
| 6 | Comparison view | Phase 4 |
| 7 | Dashboard | Phases 3–5 |
| 8 | Country Map | Phase 3 |
| 9 | City Map | Phase 4 |
| 10 | AI Executive Summary | Phase 4 |

Build sequence is ordered to validate the full data model end-to-end as early as possible (Phases 1–3), before investing in secondary views and features.

---

## 12. Out of Scope

The following are explicitly outside the scope of this brief and the application build:

- Scoring methodology and weight values — defined in Scoring Brief v1.1
- Research pipeline and data sources — defined in Research Pipeline Brief v1.0
- Data schema — defined in Data Spec v0.6
- Manual outreach to swim clubs, language programs, and rental contacts — tracked in the app but conducted outside it
- Property-level rental research — neighbourhood-level only, per Research Pipeline Brief §6
- Hosted deployment, cloud infrastructure, or authentication
- Mobile browser support

---

## 13. Open Questions

No open questions — all resolved as of v0.2.

| Question | Resolution |
|---|---|
| Will the research pipeline run on the same machine as the app? | Yes. Pipeline and app share the same local filesystem. App reads from `/research/cities/` directly — no upload step needed. |
| Light or dark mode default? | Both supported via `next-themes`. System preference as default, with a toggle in the app header. |

---

## 14. Version History

| Version | Date | Changes |
|---|---|---|
| 0.1 | March 2026 | Initial draft |
| 0.2 | March 2026 | Added Cowork as primary build and automation environment. Resolved both open questions: shared local directory for pipeline→app handoff; dark/light mode via `next-themes`. Updated import routes and actions to remove file upload step. Added `next-themes` to tech stack. |

---

*Spain Summer 2027 Project · App Architecture Brief v0.2 · March 2026 · Confidential*
