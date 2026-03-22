# Research Pipeline Brief
## Spain Summer 2027 — City Discovery & Planning Tool

**Prepared:** March 2026 · **Status:** Draft · **Version:** 1.0

---

## 1. Purpose

This brief defines the two-phase research pipeline that produces city data for the Spain Summer 2027 project. It governs how candidate cities are identified, screened, and researched, what data sources are used for each attribute, how data is stored, and what constitutes a complete research record.

This brief is downstream of the Data Spec (v0.6) and Scoring Brief (v1.1), which together define the schema and scoring methodology that all research output must conform to. Agents operating this pipeline should treat those documents as the authoritative reference for field definitions, scoring rubrics, and output format.

---

## 2. Pipeline Overview

The pipeline runs in two sequential phases separated by a human-in-the-loop (HITL) checkpoint.

```
Phase 1: Longlist Agent
  → Screens all Spanish cities against Screening Criteria Config v1.0
  → Outputs a candidate longlist spreadsheet

HITL Checkpoint
  → Human review and approval of the longlist
  → Cities may be added or removed before Phase 2 begins

Phase 2: Research Agent
  → Runs exhaustive research on each approved city
  → Populates complete city JSON files per Data Spec v0.6
  → Updates master index on completion of each city
```

The two phases are designed to be independent. Phase 1 is fast and broad. Phase 2 is deep and city-specific. Phase 2 does not begin until the HITL checkpoint is complete.

---

## 3. Data Storage

All research output is stored as structured JSON files on the local filesystem.

### File Structure

```
/research/
  index.json                  ← Master index (see §3.2)
  cities/
    {city-id}.json            ← One file per city (see §3.3)
```

### 3.1 Naming Conventions

City IDs are lowercase, hyphen-separated, using the English city name — e.g. `san-sebastian`, `malaga`, `cadiz`. IDs are stable once assigned and do not change if the city name is corrected.

### 3.2 Master Index (`index.json`)

Tracks all cities in the pipeline at a glance. Updated by the Research Agent after completing or partially completing each city record.

```json
{
  "lastUpdated": "2026-03-XX",
  "cities": [
    {
      "id": "san-sebastian",
      "name": "San Sebastián",
      "region": "País Vasco",
      "status": "active",
      "researchStatus": "complete",
      "hardRequirementsPass": true,
      "compositeScore": 8.2,
      "rank": 1
    }
  ]
}
```

### 3.3 City Files (`{city-id}.json`)

One file per city. Structure conforms exactly to Data Spec v0.6. Contains all sections: City Core, Hard Requirements, Discovery Attributes, Rental Neighbourhoods, Language Programmes, Contact Tracking, Research Notes, and Composite Score. See Data Spec v0.6 for the complete schema.

---

## 4. Phase 1 — Longlist Agent

### 4.1 Objective

Produce an exhaustive list of Spanish cities that plausibly meet all six screening criteria. The goal is completeness — it is better to include a borderline city than to exclude it. Cities can be removed at the HITL checkpoint; they cannot be added back without rerunning Phase 1.

### 4.2 Screening Criteria (v1.0)

A city must satisfy all six criteria to be admitted to the longlist:

1. Located in Spain
2. Not Madrid or Barcelona
3. Small-to-mid sized, walkable, character city
4. Has at least one competitive swimming pool or club (existence check only — not guest policy)
5. Has at least one Spanish language school operating in summer (existence check only — not enrolment availability)
6. Plausibly car-free livable — not a rural village or isolated resort

These are lightweight plausibility checks, not confirmed facts. The Research Agent confirms facts in Phase 2.

### 4.3 Research Approach

The Longlist Agent uses web search to systematically identify candidate cities. Suggested approach:

- Search for cities by region across all 17 autonomous communities of Spain
- Cross-reference against known walkable character cities of appropriate size
- Check for existence of competitive swimming clubs via RFEN club directory (rfen.es/clubs) filtered by city
- Check for existence of Spanish language schools via Instituto Cervantes accredited school directory
- Apply car-free plausibility judgment based on city size, density, and known character

The agent should cast a wide net. Borderline cases should be admitted with a note rather than excluded.

### 4.4 Output

A single spreadsheet (`longlist.csv`) with one row per candidate city:

| Column | Description |
|---|---|
| `city_name` | City name in Spanish |
| `region` | Autonomous community |
| `population_approx` | Approximate population (order of magnitude) |
| `screening_result` | admitted · rejected |
| `failed_criteria` | Comma-separated list of failed criteria (empty if admitted) |
| `notes` | Agent rationale — especially for borderline decisions |

Rejected cities are included in the spreadsheet with their failed criteria noted. This provides an auditable record of what was considered.

### 4.5 HITL Checkpoint

The Longlist Agent pauses after producing `longlist.csv`. A human reviews the list and may:

- Remove cities they know are unsuitable
- Add cities the agent missed
- Annotate cities for the Research Agent

The approved longlist is the authoritative input to Phase 2. No city enters Phase 2 without appearing on the approved longlist.

---

## 5. Phase 2 — Research Agent

### 5.1 Objective

For each city on the approved longlist, produce a complete city JSON file conforming to Data Spec v0.6. Research is exhaustive — every field that can be populated from web sources should be populated. Fields that require manual outreach (guest policy, enrolment availability, broadband confirmation) are noted as `unknown` with findings recorded in `notes`.

### 5.2 Research Sequence Per City

For each city, the Research Agent works in this order:

1. **Create city record** — populate City Core fields, set `researchStatus` to `in_progress`
2. **Hard requirements** — research all five hard requirements before scoring any attributes
3. **Check for eliminations** — if any hard requirement is a confirmed `fail`, set city status to `eliminated`, record `eliminationReason`, and stop. Do not research attributes for eliminated cities.
4. **Discovery attributes** — research all 12 scored attributes plus the 2 unscored display fields
5. **Rental neighbourhoods** — identify 1–3 candidate neighbourhoods and populate records
6. **Language programmes** — populate one record per accredited programme found
7. **Calculate composite score** — apply weights from Scoring Config (Data Spec §10)
8. **Update master index** — update `index.json` with current status and score
9. **Set `researchStatus` to `complete`**

### 5.3 Hard Requirements Research

Hard requirements are researched before attributes. The Research Agent populates findings in the `notes` field and sets status to `pass`, `fail`, or `unknown` per the definitions below.

| requirementId | Research approach | Status guidance |
|---|---|---|
| `swim_club` | Search RFEN club directory (rfen.es/clubs) for clubs in the city. Identify the most competitive club. Confirm pool type and coaching programme from the club website. Record club name, address, and coordinates in facility location fields. | `pass` if a competitive club with coaching exists. `unknown` if existence confirmed but guest policy unconfirmed — **guest policy requires manual outreach and cannot be confirmed remotely.** `fail` if no competitive club found. |
| `spanish_program` | Search Instituto Cervantes accredited school directory. Confirm summer operation from school website. Record institution name, address, and coordinates. Populate Language Programmes records (§5.5 below). | `pass` if at least one accredited programme with confirmed summer operation found. `unknown` if programme exists but summer availability unconfirmed. `fail` if no programme found. |
| `rental_housing` | Research Idealista for available rentals in candidate neighbourhoods. Assess proximity to both the swim club and language program via Google Maps. | `pass` if suitable rentals appear available within walking or transit distance of both facilities. `unknown` if uncertain. `fail` if no suitable options found. |
| `broadband` | Cannot be confirmed remotely for a specific rental. Always set to `unknown`. Note city-level broadband quality in the `notes` field as context. | Always `unknown` at research phase. Confirmed by manual outreach only. |
| `car_free_living` | Research transit options and walkability of candidate neighbourhoods. Test representative journeys (groceries, pharmacy, errands) via Google Maps. | `pass` if daily essentials are accessible on foot or transit without a car. `fail` if a car is required. |

### 5.4 Discovery Attribute Research

For each scored attribute, the agent must populate three fields: `rawValue`, `score`, and `notes`. Scores are integers from 1–10 per the rubrics in Scoring Brief v1.1. `rawValue` is the underlying data point. `notes` explains the score and cites the source.

Quality attributes (`swim_club_quality`, `language_program_quality`, `rental_quality_proximity`, `car_free_quality`) must not be populated until the corresponding hard requirement has a `pass` status.

**Data sources by attribute:**

| attributeId | Primary Source | Secondary Source | rawValue format |
|---|---|---|---|
| `swim_club_quality` | RFEN club directory (rfen.es/clubs) + RFEN competition results for tier | Club website for pool type and programme detail | e.g. `Regional Primera División · 50m pool` |
| `language_program_quality` | Instituto Cervantes accredited school directory | Individual school websites for summer confirmation | e.g. `2 accredited programmes · both confirmed June/July` |
| `rental_quality_proximity` | Idealista (neighbourhood quality) | Google Maps (proximity routing to both facilities) | e.g. `8 min walk to swim club · 12 min transit to language school` |
| `car_free_quality` | City transit authority website | Google Maps (daily errand routing from candidate neighbourhoods) | e.g. `Bus network covers all daily needs · supermarket 6 min walk` |
| `avg_june_july_temp` | meteoblue.com or Weather Atlas | — | e.g. `24°C average high (June/July, 30-year historical)` |
| `scuba_diving_access` | PADI dive site directory (padi.com/dive-sites/spain) | dive.site | e.g. `4 PADI-listed sites within 35 min · advanced-rated` |
| `mountain_hiking_access` | AllTrails (alltrails.com) | Wikiloc (wikiloc.com) | e.g. `3 difficult trails within 25 min · 800m+ elevation gain` |
| `food_market_culture` | spain.info gastronomic markets section | Google Maps (market existence) · Michelin Spain regional guide · city tourism website | e.g. `Active mercado municipal · strong Basque culinary identity` |
| `european_rail_access` | Renfe timetables (renfe.com) | Trainline | e.g. `Paris reachable in 5h45 via Barcelona (1 connection)` |
| `rental_cost` | Idealista | — | e.g. `€1,350–1,600/month estimated (Casco Viejo neighbourhood, March 2026)` |
| `walkability_transit` | City transit authority website | Google Maps transit routing | e.g. `EMT bus network · swim club 9 min transit · language school 7 min walk` |
| `tourist_density` | INE Frontur regional tourism data (ine.es) | Turespaña/Dataestur · qualitative web research | e.g. `1.2M international visitors in summer 2024 · overtourism protests reported` |
| `moorish_architecture` | Web search · Wikipedia regional architecture | City tourism website | `true` or `false` |
| `day_trip_quality` | Web search synthesis | Google Maps proximity checks | Agent-written summary, 2–4 sentences |

### 5.5 Language Programmes

For every accredited Spanish language programme found in the city, the agent populates one Language Programmes record (Data Spec §5). This is done in addition to assigning the city-level `language_program_quality` score.

Each record must include an `agentSummary` — a 2–4 sentence assessment of fit for Abigail's profile: approximately A2 level (junior high plus 2 years high school Spanish, functional but not conversational, needs structured beginner-to-intermediate progression). The summary should cover level alignment, programme structure, confirmed summer availability, and cohort or schedule notes where findable.

### 5.6 Rental Neighbourhoods

For each city that passes hard requirements, the agent identifies 1–3 candidate neighbourhoods and populates Rental Neighbourhood records (Data Spec §4). Research is neighbourhood-level only — specific properties are identified in a later phase after shortlisting.

Candidate neighbourhoods should be assessed for: estimated monthly rental cost (from Idealista), walking or transit time to both the swim club and the language program (from Google Maps), and a brief character description.

### 5.7 Scoring and Confidence

- Assign all scores as integers from 1–10. No half-points.
- Always populate `rawValue` with the specific underlying data point — not a general description.
- Always cite the source in `notes`.
- If data is insufficient to score confidently, assign the score your best estimate supports and flag uncertainty explicitly in `notes` with a note such as "low confidence — limited data available."
- Do not leave `score` null for a city that has passed hard requirements. An unknown is not the same as unscored.
- Do not inflate scores to compensate for missing data. Score what is known.

---

## 6. Out of Scope

The following are explicitly outside the scope of this pipeline:

- **Manual outreach** — contacting swim clubs to confirm guest policy, contacting language schools to confirm enrolment availability, or confirming broadband at specific rentals. These are tracked in the Contact Tracking section (Data Spec §6) and completed as a separate manual phase.
- **Property-level rental research** — specific rental listings are identified only after shortlisting. The pipeline researches at neighbourhood level only.
- **Application build** — the pipeline produces JSON data files. The application that reads and displays this data is a separate workstream.

---

## 7. Definition of Complete

A city research record is considered **complete** when:

- All five hard requirement records are populated with status and notes
- If status = `eliminated`: `eliminationReason` is set and no further fields are required
- If status = `active`: all 12 scored attributes have a `score` and `rawValue` populated
- Both unscored display fields (`moorish_architecture`, `day_trip_quality`) have `rawValue` populated
- At least one Rental Neighbourhood record exists
- At least one Language Programmes record exists (if `spanish_program` status = `pass`)
- `researchStatus` is set to `complete`
- Master index is updated

A city record with `researchStatus = complete` may still have `unknown` hard requirement statuses (e.g. broadband, guest policy) — these are resolved through manual outreach, not the research pipeline.

---

## 8. Reference Documents

| Document | Version | Role |
|---|---|---|
| Project Brief | v1.2 | Scope, hard requirements, traveler context |
| Data Spec | v0.6 | Schema — all field definitions and output format |
| Scoring Brief | v1.1 | Scoring rubrics, weights, and agent scoring instructions |

---

## 9. Version History

| Version | Date | Changes |
|---|---|---|
| 1.0 | March 2026 | Initial release — two-phase pipeline, data storage spec, per-attribute data sources, agent instructions, definition of complete |

---

*Spain Summer 2027 Project · Research Pipeline Brief v1.0 · March 2026 · Confidential*
