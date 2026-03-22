# Scoring Brief
## Spain Summer 2027 — City Discovery & Planning Tool

**Prepared:** March 2026 · **Status:** Draft · **Version:** 1.1

---

## 1. Purpose

This brief defines the scoring and weighting methodology used to rank candidate cities that have passed all five hard requirements. It governs how discovery attribute scores are assigned, how the weighted composite score is calculated, and how the research agent should interpret each scoring rubric.

This brief is downstream of the Data Spec (v0.6) and upstream of the Research Pipeline. All attribute IDs used here correspond directly to those defined in §3 and §10 of the Data Spec.

---

## 2. Relationship to Hard Requirements

Hard requirements function as a binary gate. A city that fails any single hard requirement is eliminated and does not receive a composite score.

However, hard requirements vary significantly in quality among cities that pass. To capture this variability, four of the five hard requirements have a corresponding **quality attribute** in the scored attribute list below. The hard requirement record retains its `pass / fail / unknown` status — the quality attribute scores the *degree of quality* among passing cities only.

| Hard Requirement | Quality Attribute | Notes |
|---|---|---|
| Swim Club | `swim_club_quality` | Scored only if `swim_club` status = pass |
| Spanish Program | `language_program_quality` | Scored only if `spanish_program` status = pass |
| Rental Housing | `rental_quality_proximity` | Scored only if `rental_housing` status = pass |
| Car-Free Living | `car_free_quality` | Scored only if `car_free_living` status = pass |
| Broadband | *(not scored)* | Pass/fail only — no meaningful quality gradient |

---

## 3. Composite Score Formula

```
Composite Score = Σ (attribute_score × weight)
```

- **Attribute scores** are integers from 1–10, assigned by the research agent per the rubrics in §5.
- **Weights** are defined in §4 and sum to 1.00.
- **Score range:** minimum 1.0, maximum 10.0.
- The composite score is recalculated whenever any attribute score or weight changes.
- Eliminated cities are excluded from ranking.

---

## 4. Scoring Weights

12 scored attributes. Weights sum to 1.00.

| # | Attribute ID | Category | Weight | Description |
|---|---|---|---|---|
| 1 | `swim_club_quality` | Hard Req Quality | **0.15** | Coaching level, training environment, pool quality |
| 2 | `language_program_quality` | Hard Req Quality | **0.13** | Number of accredited programmes, summer availability |
| 3 | `walkability_transit` | Practical | 0.10 | Transit quality and car-free daily friction |
| 4 | `avg_june_july_temp` | Climate | **0.12** | Average June/July high temperature |
| 5 | `scuba_diving_access` | Outdoor | **0.10** | Distance and quality of diving / snorkeling sites |
| 6 | `mountain_hiking_access` | Outdoor | 0.07 | Distance and quality of serious hiking terrain |
| 7 | `food_market_culture` | Cultural | 0.06 | Distinctive local food and market culture |
| 8 | `european_rail_access` | Practical | 0.06 | Access to major European hubs within a day |
| 9 | `car_free_quality` | Hard Req Quality | 0.06 | Ease and completeness of car-free daily life |
| 10 | `rental_cost` | Practical | 0.05 | Monthly rental cost for a 1–2 month stay |
| 11 | `rental_quality_proximity` | Hard Req Quality | 0.05 | Rental quality and walking/transit proximity to both facilities |
| 12 | `tourist_density` | Livability | 0.05 | Summer tourist density and overtourism risk |
| — | `moorish_architecture` | Cultural | *unscored* | Boolean display field only — see §6 |
| — | `day_trip_quality` | Cultural | *unscored* | Text display field only — see §6 |
| | **Total** | | **1.00** | |

---

## 5. Scoring Rubrics

Each rubric defines what a score of 9–10, 7–8, 5–6, 3–4, and 1–2 looks like. The agent assigns a single integer from 1–10. Half-point scores are not used.

---

### 5.1 `swim_club_quality` — Weight 0.15

**Context:** The daughter is an incoming D1/D2 collegiate swimmer. A passing city has a club willing to accept a guest swimmer for 6–8 weeks. This attribute scores the quality of that training environment.

**Research approach:** RFEN competition tier is the primary proxy for training quality and should be the first data point checked. Source the club from the RFEN club directory (rfen.es/clubs), then look up the club's tier in RFEN competition results. Use the club's own website to confirm pool type and programme detail. Guest policy confirmation requires manual outreach and is tracked in the `swim_club` hard requirement notes field — it does not affect this quality score.

**RFEN tier guidance:**

| Score | RFEN tier |
|---|---|
| 9–10 | División de Honor or top national competition |
| 7–8 | Regional Primera División |
| 5–6 | Regional lower division with structured programme |
| 3–4 | Basic federated club |
| 1–2 | Federated but no competitive programme evident |

**Full scoring rubric:**

| Score | Description |
|---|---|
| 9–10 | 50m pool · competitive training group · structured coached programming · stroke/event specialism available · División de Honor or national level |
| 7–8 | 50m pool · competitive group · coached programming · no specialism · Regional Primera División |
| 5–6 | Coached programming + competitive group · 25m pool only · regional lower division |
| 3–4 | Coached sessions but recreational or mixed group — no competitive environment · basic federated club |
| 1–2 | Lane access only — no coaching, no competitive group (technically passes the hard requirement) |

---

### 5.2 `language_program_quality` — Weight 0.13

**Context:** A passing city has a beginner Spanish immersion program running 6–8 weeks. This attribute scores the number of accredited programmes available and confirmed summer operation. Abigail's profile: approximately A2 level (junior high + 2 years high school Spanish, functional but not conversational). Per-programme fit assessments are stored separately in the Language Programmes sub-table in the Data Spec (§5).

**Research approach:** Use the Instituto Cervantes accredited school directory as the primary source. Confirm summer (June/July) operation from individual school websites. Populate one Language Programmes record per programme found, including an agent-written summary of fit for Abigail's profile.

**Scoring criteria:**
- Number of accredited programmes in the city with confirmed summer operation
- Confirmed June/July availability

| Score | Description |
|---|---|
| 9–10 | 3+ accredited programmes · all confirmed summer operation |
| 7–8 | 2 accredited programmes · confirmed summer operation |
| 5–6 | 1 accredited programme · confirmed summer operation |
| 3–4 | 1 accredited programme · summer operation unconfirmed |
| 1–2 | Programmes found but none accredited · summer operation unclear |

---

### 5.3 `walkability_transit` — Weight 0.10

**Context:** All longlist cities pass a walkability floor by definition (screening criteria require small-to-mid sized, walkable character city). This attribute scores transit quality and car-free daily friction — not baseline walkability. Research using the city transit authority website and Google Maps transit routing for representative journeys (residential neighbourhood → swim club, → language school, → supermarket).

| Score | Description |
|---|---|
| 9–10 | Excellent transit network · essentially zero friction for daily life |
| 7–8 | Good transit with minor gaps · most needs easily met |
| 5–6 | Transit adequate but requires planning for some journeys |
| 3–4 | Patchy transit · car-free requires ongoing effort |
| 1–2 | Technically car-free possible but requires significant daily workarounds |

---

### 5.4 `avg_june_july_temp` — Weight 0.12

**Context:** Cooler is better. The swim training environment and general comfort over 6–8 weeks strongly favour mild summer temperatures. Scores decrease as temperatures rise above ~25°C.

| Score | Description |
|---|---|
| 9–10 | Average high 20–25°C — ideal summer comfort |
| 7–8 | Average high 25–27°C — warm but comfortable |
| 5–6 | Average high 27–30°C — warm, noticeable heat |
| 3–4 | Average high 30–33°C — hot, affects comfort |
| 1–2 | Average high 33°C+ — oppressive summer heat |

*Agent: use historical average June/July high temperature (°C) from meteoblue or Weather Atlas. Note the data source and year range.*

---

### 5.5 `scuba_diving_access` — Weight 0.10

**Context:** Advanced diver seeking quality, varied dive sites. Snorkeling-only access does not score highly. Proximity matters — sites should be reachable for a weekend outing without a car, or with a reasonable car rental day trip. Source from PADI dive site directory (padi.com/dive-sites/spain) and dive.site.

| Score | Description |
|---|---|
| 9–10 | Multiple quality dive sites within 30 min · varied marine environments · suitable for advanced divers |
| 7–8 | Good dive sites within 1 hour · decent variety |
| 5–6 | Accessible diving within 1–2 hours · limited variety or depth interest |
| 3–4 | Basic snorkeling only · or quality diving requires 2+ hours travel |
| 1–2 | No meaningful diving or snorkeling access |

---

### 5.6 `mountain_hiking_access` — Weight 0.07

**Context:** Serious hiking — multi-hour routes with significant elevation gain and challenging terrain. Scenic flat walks do not score highly. Source from AllTrails and Wikiloc, filtering for difficult/challenging trails within range.

| Score | Description |
|---|---|
| 9–10 | Challenging multi-hour trails within 30 min · significant elevation · varied routes |
| 7–8 | Serious trails within 1 hour · good elevation gain |
| 5–6 | Moderate trails nearby · limited challenging options |
| 3–4 | Mostly casual or flat walks · no serious terrain within reasonable distance |
| 1–2 | No meaningful hiking access |

---

### 5.7 `food_market_culture` — Weight 0.06

**Context:** Source from spain.info gastronomic markets section, Google Maps (market existence and reviews), Michelin Spain regional guide, and city tourism website. Score reflects both market presence and distinctiveness of regional food identity.

| Score | Description |
|---|---|
| 9–10 | Distinctive, celebrated local cuisine · active daily or weekly market · strong local food identity distinct from generic Spanish tourist food |
| 7–8 | Notable food culture · regular market |
| 5–6 | Some local food character · occasional or modest market |
| 3–4 | Generic dining scene · no distinct market culture |
| 1–2 | Tourist-dominated food scene — little authentic local character |

---

### 5.8 `european_rail_access` — Weight 0.06

**Context:** Access to major European destinations for weekend or multi-day trips. Direct or 1-connection service is the ideal. Same-day arrival at a major hub (Paris, Amsterdam, Lisbon, Rome, etc.) defines the high end. Source from Renfe (renfe.com) and Trainline timetables.

| Score | Description |
|---|---|
| 9–10 | Direct or single-connection service to a major European hub in under 6 hours |
| 7–8 | Major European hub reachable same day with connections — reasonable routing |
| 5–6 | European travel possible but requires overnight journey or complex multi-leg routing |
| 3–4 | Very limited European rail options — flying is the only practical route |
| 1–2 | No practical European rail access |

---

### 5.9 `car_free_quality` — Weight 0.06

**Context:** Scores the quality of car-free daily life beyond the binary pass/fail gate. Specifically tests whether groceries, pharmacies, and everyday errands are accessible without a car — not just the swim club and language school. Research using Google Maps routing for daily errand journeys from candidate rental neighbourhoods.

| Score | Description |
|---|---|
| 9–10 | All daily needs walkable · excellent transit · zero car dependency or friction |
| 7–8 | Most needs walkable · minor transit gaps easily managed |
| 5–6 | Core needs covered on foot or transit · some friction for specific tasks |
| 3–4 | Technically car-free possible but requires significant planning or workarounds |
| 1–2 | Barely passes the hard requirement — car-free living is effortful and limiting |

---

### 5.10 `rental_cost` — Weight 0.05

**Context:** Cost of a quality 1–2 month rental in a suitable neighbourhood. Lower cost scores higher — budget is not the primary driver but fair value matters. Prices are estimated monthly EUR at time of research. Source from Idealista.

| Score | Description |
|---|---|
| 9–10 | Under €1,200/month |
| 7–8 | €1,200–1,600/month |
| 5–6 | €1,600–2,000/month |
| 3–4 | €2,000–2,500/month |
| 1–2 | Over €2,500/month |

*Agent: note the neighbourhood(s) surveyed and the date of the estimate.*

---

### 5.11 `rental_quality_proximity` — Weight 0.05

**Context:** Scores the quality of available rental options and their proximity to both the swim club and the language program. Research at this stage is neighbourhood-level, not property-level. Source from Idealista for neighbourhood quality; Google Maps for proximity routing to both facilities.

| Score | Description |
|---|---|
| 9–10 | Under 10 min walk to both swim club and language program · well-reviewed neighbourhood and property quality |
| 7–8 | Under 10 min walk to one facility, short transit (under 10 min) to the other · good quality |
| 5–6 | Transit required to both, but under 20 min each · adequate quality |
| 3–4 | Longer commutes to one or both facilities · or property quality concerns |
| 1–2 | Technically passes the hard requirement but proximity or quality are poor |

---

### 5.12 `tourist_density` — Weight 0.05

**Context:** Overtourism should be penalised; moderate tourism is acceptable. Source from INE (Instituto Nacional de Estadística) Frontur regional tourism data and Turespaña/Dataestur. Supplement with qualitative web research on known overtourism complaints per city.

| Score | Description |
|---|---|
| 9–10 | Light tourism · locals-first atmosphere even in peak summer |
| 7–8 | Moderate tourism · manageable summer crowds · local life intact |
| 5–6 | Noticeable summer tourism · some crowding in peak areas but not overwhelming |
| 3–4 | Heavy summer crowds · tourist-dominated in peak months · affects daily experience |
| 1–2 | Overtourism — significantly degrades quality of daily life in June/July |

---

## 6. Unscored Display Fields

The following fields are displayed on the City Detail page and Comparison View but are not scored and do not contribute to the composite score.

### `moorish_architecture` — Boolean Display Field

| Field | Value |
|---|---|
| `rawValue` | `true` / `false` |
| `score` | null (not populated) |
| Presence definition | Meaningful Moorish or Andalusian architecture present **in the city or within a day trip (1–2 hours)** |

This field may serve as a human tie-breaker but has no algorithmic weight.

### `day_trip_quality` — Text Display Field

| Field | Value |
|---|---|
| `rawValue` | Agent-written qualitative summary of day trip options within 1–2 hours |
| `score` | null (not populated) |

No reliable aggregatable data sources exist to justify a numerical score with consistent confidence across cities. The agent writes a descriptive summary covering variety of options (coast, mountains, cities, cultural sites) reachable within 1–2 hours by car or transit. Car rental is available for weekend excursions so car-accessible destinations count.

---

## 7. Agent Scoring Instructions

- Assign all scores as integers from **1–10**. No half-points.
- Always populate `rawValue` with the underlying data point (e.g. `22°C`, `3 dive sites within 40 min`, `€1,350/month estimated`).
- Always populate `notes` with a brief rationale and source reference.
- If data is insufficient to score confidently, assign the score your best estimate supports and flag uncertainty in `notes`.
- Do not leave `score` null for a city that has passed hard requirements — an unknown is not the same as unscored.
- Scores for quality attributes (`swim_club_quality`, `language_program_quality`, `rental_quality_proximity`, `car_free_quality`) should only be populated once the corresponding hard requirement has a `pass` status.
- For `language_program_quality`, populate one Language Programmes record (Data Spec §5) per programme found, in addition to assigning the city-level score.

---

## 8. Version History

| Version | Date | Changes |
|---|---|---|
| 1.0 | March 2026 | Initial release — 13 scored attributes, 1 boolean display field, full rubrics, data spec change requests |
| 1.1 | March 2026 | 12 scored attributes. `day_trip_quality` reclassified as unscored text display field. `avg_june_july_temp` weight increased 0.09 → 0.12. `scuba_diving_access` weight increased 0.08 → 0.10. `language_program_quality` rubric rewritten around programme count and summer availability; Abigail's A2 profile added to context. `swim_club_quality` rubric annotated with RFEN tier guidance. Data source guidance added to all rubrics. References updated to Data Spec v0.6. |

---

*Spain Summer 2027 Project · Scoring Brief v1.1 · March 2026 · Confidential*
