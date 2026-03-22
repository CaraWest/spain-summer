# Spain Summer 2027
## Data Specification

**Version:** 0.6 · **Status:** Draft · **Prepared:** March 2026

---

### Purpose

This document defines the complete data schema for the Spain Summer 2027 city research application. It governs how every city record is structured, what data points are tracked, and how derived values such as composite scores are calculated. All application views, research agents, and scoring tools must conform to this spec.

### Relationship to Other Documents

| Document | Relationship |
|---|---|
| Project Brief | Parent — defines scope, hard requirements, and discovery attributes |
| Research Pipeline Brief | Downstream — populates city records using this schema |
| Scoring Brief | Downstream — defines scoring weights that feed the Scoring Config |

---

## 1. City Core

The identity and status record for each candidate city. One record per city. A city enters this table when it passes longlist screening — see §9 Screening Log for the upstream process.

| Field | Type | Notes |
|---|---|---|
| id | string (uuid) | Stable, system-generated identifier |
| name | string | e.g. San Sebastián |
| region | string | e.g. País Vasco, Andalucía |
| latitude | number | Decimal degrees — for map pins |
| longitude | number | Decimal degrees — for map pins |
| status | enum | active · pending · eliminated · flagged |
| researchStatus | enum | not_started · in_progress · complete |
| eliminationReason | string? | Populated only when status = eliminated |
| longlistCriteriaVersion | string | Version of screening config that admitted this city |
| longlistSource | enum | agent · manual — how the city was added |
| createdAt | timestamp | |
| updatedAt | timestamp | Auto-updated on any change to the record |

---

## 2. Hard Requirements

One record per requirement per city. Five requirements per city. A single fail status eliminates the city — status is automatically propagated to City Core.

| Field | Type | Notes |
|---|---|---|
| requirementId | enum | swim_club · spanish_program · rental_housing · broadband · car_free_living |
| status | enum | pass · fail · unknown |
| notes | string | Agent-populated findings. Human-overridable. |
| sourceType | enum | agent · manual |
| lastUpdated | timestamp | |

### Requirement IDs

| requirementId | Description |
|---|---|
| swim_club | Competitive club willing to accept a guest swimmer for 6–8 weeks with structured coaching. Agent identifies candidate club via RFEN directory; guest policy confirmed by manual outreach. |
| spanish_program | Beginner immersive Spanish program running 6–8 weeks. Agent identifies candidate programmes via Instituto Cervantes directory; enrolment availability confirmed by manual outreach. See §5 Language Programmes for per-programme detail. |
| rental_housing | 1–2 month rental reachable on foot or transit to both facilities. See §4 for detail. |
| broadband | Reliable fast internet confirmed for the specific rental, not assumed city-wide |
| car_free_living | All daily essentials accessible on foot or transit. No car required. |

### Facility Location Fields

The swim club and language program hard requirement records carry additional location fields to support the city-level map view.

| Field | Type | Applies To |
|---|---|---|
| facilityName | string | swim_club, spanish_program |
| facilityAddress | string | swim_club, spanish_program |
| facilityLat | number | swim_club, spanish_program |
| facilityLng | number | swim_club, spanish_program |

---

## 3. Discovery Attributes

Attributes used to rank cities that pass all hard requirements. One record per attribute per city. Scored attributes are agent-populated and feed the weighted composite score in §8. Boolean and text display fields are not scored and do not contribute to the composite score.

| Field | Type | Notes |
|---|---|---|
| attributeId | enum | See attribute list below |
| rawValue | string \| number \| boolean | Actual data point. Always agent-populated. e.g. 28°C, 45 min drive, true/false, text summary |
| score | number (1–10)? | Normalised score. Agent-populated. Null for boolean and text display fields. |
| notes | string | Agent context and caveats. Human-overridable. |
| sourceType | enum | agent · manual |
| lastUpdated | timestamp | |

### Attribute IDs

| attributeId | Category | Description |
|---|---|---|
| swim_club_quality | Hard Req Quality | Coaching level, pool quality, and training environment of the confirmed swim club. Scored using RFEN competition tier as primary signal. Scored only when `swim_club` hard requirement status = pass. |
| language_program_quality | Hard Req Quality | Scored on number of accredited programmes with confirmed summer (June/July) operation. Soft criteria (cohort fit, curriculum, schedule) are captured in Language Programmes sub-table (§5). Scored only when `spanish_program` hard requirement status = pass. |
| rental_quality_proximity | Hard Req Quality | Quality of available rental options and walking/transit proximity to both the swim club and language program. Scored only when `rental_housing` hard requirement status = pass. |
| car_free_quality | Hard Req Quality | Ease and completeness of car-free daily living — groceries, pharmacy, and everyday errands — beyond the binary hard requirement gate. Scored only when `car_free_living` hard requirement status = pass. |
| scuba_diving_access | Outdoor | Distance and access to quality scuba diving / snorkelling sites |
| mountain_hiking_access | Outdoor | Distance and access to mountain hiking trails |
| avg_june_july_temp | Climate | Average June/July high temperature in °C |
| moorish_architecture | Cultural | **Boolean display field only. Not scored. `score` is always null. Excluded from composite score calculation.** `rawValue` = true/false. Presence defined as: Moorish or Andalusian architecture present in the city or within a day trip (1–2 hours). |
| food_market_culture | Cultural | Distinctive local food and market culture |
| day_trip_quality | Cultural | **Text display field only. Not scored. `score` is always null. Excluded from composite score calculation.** `rawValue` = agent-written qualitative summary of day trip options within 1–2 hours (coast, mountains, cities, cultural sites). Car-accessible destinations count. |
| rental_cost | Practical | Cost of a 1–2 month rental in the city |
| walkability_transit | Practical | Transit quality and car-free daily friction. All longlist cities pass a walkability floor by definition — this attribute scores the transit network and ease of car-free living, not baseline walkability. |
| european_rail_access | Practical | Access to major European destinations by rail — whether a major European hub is reachable within a day (direct or with connections) |
| tourist_density | Livability | Summer tourist density and overtourism risk |

---

## 4. Rental Neighbourhoods

Research at this stage is conducted at neighbourhood level, not individual property level. Specific rentals are identified only once a city is shortlisted. One or more neighbourhood records may exist per city.

| Field | Type | Notes |
|---|---|---|
| neighbourhoodId | string (uuid) | |
| name | string | Neighbourhood name |
| character | string | Brief agent-written description of neighbourhood character |
| lat | number | Approximate centre point — for city-level map |
| lng | number | |
| walkTimeSwimClub | string? | e.g. 12 min walk, 8 min transit |
| walkTimeSpanishProg | string? | e.g. 20 min walk, 5 min transit |
| estMonthlyCostEUR | string | Estimated monthly rental cost range e.g. €1,400–1,800 |
| notes | string | Agent findings. Human-overridable. |
| sourceType | enum | agent · manual |
| lastUpdated | timestamp | |

---

## 5. Language Programmes

One record per programme per city. Agent-populated during research phase. Captures per-programme detail and fit assessment for Abigail's profile (approximately A2 level — junior high plus 2 years high school Spanish, functional but not conversational). Multiple records may exist per city. These records feed the `language_program_quality` score and are displayed on the City Detail page.

| Field | Type | Notes |
|---|---|---|
| programmeId | string (uuid) | |
| cityId | string | Foreign key to City Core |
| institutionName | string | e.g. Instituto Cervantes Málaga |
| accredited | boolean | Instituto Cervantes accredited or equivalent |
| summerOperation | boolean | Confirmed June/July programme running |
| levelOffered | string | e.g. A1–B1, beginner-intermediate |
| levelFit | enum | good · possible · poor · unknown |
| programmeUrl | string | |
| agentSummary | string | Agent-written assessment of fit for Abigail's profile — level alignment, programme structure, summer availability, cohort notes where findable |
| sourceType | enum | agent · manual |
| lastUpdated | timestamp | |

---

## 6. Contact Tracking

One notes record per contact type per city. No workflow state — free-text notes capture outreach history, responses, and status.

| Field | Type | Notes |
|---|---|---|
| type | enum | swim_club · language_program · rental |
| notes | string | Free-text — outreach history, responses, current status |
| lastUpdated | timestamp | |

---

## 7. Research Notes & AI Summary

One record per city. Captures free-text research findings and the on-demand AI-generated executive summary.

| Field | Type | Notes |
|---|---|---|
| researchNotes | string | Free-text. Agent or human. |
| notesUpdatedAt | timestamp | |
| aiSummary | string? | On-demand generated summary |
| aiSummaryGeneratedAt | timestamp? | |
| aiSummaryDataVersion | string? | Snapshot hash — allows app to flag when summary is stale relative to underlying data |

---

## 8. Composite Score

Derived/calculated — not stored as raw input. Computed from attribute scores multiplied by weights from the Scoring Config (§10). Recalculated whenever attribute scores or config weights change.

| Field | Type | Notes |
|---|---|---|
| weightedCompositeScore | number | Sum of (attribute score × weight) across all scored attributes |
| rank | number | Rank among active cities only. Eliminated cities excluded. |
| scoreLastCalculated | timestamp | |
| scoringConfigVersion | string | Records which config version produced this score — enables staleness detection |

---

## 9. Screening Log

Records the outcome of longlist screening for every city evaluated — both admitted and rejected. Admitted cities have a corresponding City Core record. Rejected cities exist only here, providing an auditable record of what was considered and why it was excluded.

| Field | Type | Notes |
|---|---|---|
| screeningLogId | string (uuid) | |
| cityName | string | |
| region | string | |
| screeningResult | enum | admitted · rejected |
| failedCriteria | string[] | Which of the six screening criteria failed. Empty if admitted. |
| notes | string | Agent rationale for the decision |
| screenedAt | timestamp | |
| criteriaVersion | string | Which version of the Screening Criteria config was applied |
| cityId | string? | Foreign key to City Core record. Populated only if screeningResult = admitted. |

---

## 10. Scoring Config

A single shared config — not per city. Defines the weight applied to each scored discovery attribute when calculating composite scores. Structure is locked. Weight values are defined in Scoring Brief v1.1.

> `moorish_architecture` and `day_trip_quality` are excluded from this config — they are boolean and text display fields respectively and do not contribute to the composite score. See §3 for detail.

### Config Schema

| Field | Type | Notes |
|---|---|---|
| attributeId | enum | Matches scored attribute IDs in §3. Does not include moorish_architecture or day_trip_quality. |
| weight | number? | Defined in Scoring Brief v1.1. All weights across all scored attributes sum to 1.0. |
| scoringNotes | string? | Optional rationale for the weight assignment |
| configVersion | string | Incremented when any weight changes |
| lastUpdated | timestamp | |

### Scored Attributes

| # | attributeId | Category | Weight |
|---|---|---|---|
| 1 | swim_club_quality | Hard Req Quality | 0.15 |
| 2 | language_program_quality | Hard Req Quality | 0.13 |
| 3 | walkability_transit | Practical | 0.10 |
| 4 | avg_june_july_temp | Climate | 0.12 |
| 5 | scuba_diving_access | Outdoor | 0.10 |
| 6 | mountain_hiking_access | Outdoor | 0.07 |
| 7 | food_market_culture | Cultural | 0.06 |
| 8 | european_rail_access | Practical | 0.06 |
| 9 | car_free_quality | Hard Req Quality | 0.06 |
| 10 | rental_cost | Practical | 0.05 |
| 11 | rental_quality_proximity | Hard Req Quality | 0.05 |
| 12 | tourist_density | Livability | 0.05 |
| — | moorish_architecture | Cultural | *Unscored — boolean display field only. Excluded from composite score.* |
| — | day_trip_quality | Cultural | *Unscored — text display field only. Excluded from composite score.* |

---

## 11. Screening Criteria Config

A versioned config defining the plausibility filters used during longlist generation. A city must satisfy all criteria to be admitted and have a City Core record created. These are lighter than hard requirements — existence checks, not confirmed facts.

| Field | Type | Notes |
|---|---|---|
| configVersion | string | Incremented when criteria change |
| criteria | string[] | Ordered list of criteria. See below. |
| lastUpdated | timestamp | |

### Screening Criteria (v1.0)

- Located in Spain
- Not Madrid or Barcelona
- Small-to-mid sized, walkable, character city
- Has at least one competitive swimming pool or club (existence, not guest policy)
- Has at least one Spanish language school operating in summer
- Plausibly car-free livable — not a rural village or isolated resort

---

## 12. Spec Status Summary

| Component | Status |
|---|---|
| City Core schema | **Locked** |
| Hard Requirement schema | **Locked** |
| Discovery Attribute list & schema | **Locked** |
| Rental Neighbourhoods schema | **Locked** |
| Language Programmes schema | **Locked** |
| Contact Tracking schema | **Locked** |
| Screening Criteria config structure | **Locked** |
| Screening Log schema | **Locked** |
| Scoring Config structure | **Locked** |
| Scoring weights (values) | **Defined — see Scoring Brief v1.1** |
| City longlist | Deferred — Research Pipeline |
| Technology stack | Deferred — Build Phase |

### Version History

| Version | Date | Changes |
|---|---|---|
| 0.1 | March 2026 | Initial draft — core schema, hard requirements, attributes, contact tracking, composite score |
| 0.2 | March 2026 | Contact tracking simplified to notes. Attribute scores agent-populated. Scoring Config structure added. Longlist provenance fields added. |
| 0.3 | March 2026 | Facility location fields added to Hard Requirements. Rental Neighbourhoods section added (neighbourhood-level, not address-level). Screening Log added with admitted + rejected cities. Screening Criteria Config formalised. |
| 0.4 | March 2026 | train_connectivity attribute added to Discovery Attributes (Practical category) — travel time by train to major Spanish tourist destinations. |
| 0.5 | March 2026 | Scoring Brief alignment: added swim_club_quality, language_program_quality, rental_quality_proximity, car_free_quality, european_rail_access attributes; removed train_connectivity; moorish_architecture reclassified as boolean display field, removed from Scoring Config; scoring weights status updated to Defined. |
| 0.6 | March 2026 | Added Language Programmes sub-table (§5); reclassified day_trip_quality as unscored text display field, removed from Scoring Config; updated language_program_quality scoring criteria to programme count and summer availability; updated walkability_transit description to reflect transit-focused scoring; updated car_free_quality description to specify daily errand scope; updated swim_club_quality description to reference RFEN tier; updated scoring weights (avg_june_july_temp 0.09→0.12, scuba_diving_access 0.08→0.10); section numbers updated throughout; scoring weights now reference Scoring Brief v1.1. |

---

*Spain Summer 2027 Project · Data Spec v0.6 · March 2026 · Confidential*
