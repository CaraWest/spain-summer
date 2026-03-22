# Project Brief
## Spain Summer 2027 — City Discovery & Planning Tool

**Prepared:** March 2026 · **Status:** Draft · **Version:** 1.2

---

## 1. Project Overview

This project will discover and rank the optimal Spanish city to serve as the base for a 6–8 week summer 2027 adventure. The trip is for Cara, working full-time remotely from Spain, and her daughter Abigail, who will be completing elite swim training and beginner Spanish immersion before entering university in fall 2027. Travis (Abigail's father) will visit but is working stateside. The output is a data-driven, ranked shortlist of candidate cities supported by a purpose-built research and decision-tracking application.

| | |
|---|---|
| **Trip window** | Summer 2027 — approximately 6–8 weeks |
| **Travelers** | Cara (full-time remote worker) + Abigail (elite swimmer, beginner Spanish). Travis will visit from the US. |
| **Base of operations** | A single Spanish city — to be determined by this project |
| **City size preference** | Small-to-mid sized — walkable character cities (e.g. San Sebastián, Málaga range). Not Madrid or Barcelona. |
| **Users of the app** | Cara and Abigail — collaborative research and decision-making |

---

## 2. Hard Requirements

Every candidate city must satisfy all five of the following requirements to remain in consideration. Failure on any single requirement eliminates the city from the shortlist.

| # | Requirement | Specification |
|---|---|---|
| **1** | **Swim Club** | Competitive club willing to accept a guest swimmer for 6–8 weeks. Must offer structured coaching and a competitive training environment suitable for an elite pre-collegiate swimmer. Pool type and training quality to be assessed during the research phase. |
| **2** | **Spanish Language Program** | Beginner-level immersive Spanish program running 6–8 weeks. Ideally structured for young adults her age to facilitate peer connection alongside language learning. |
| **3** | **Rental Housing** | 1–2 month rental available, reachable by foot or public transit to both the swim club and the language program. No car required for daily living. |
| **4** | **Broadband Internet** | Reliable, fast internet suitable for full-time remote work. Must be confirmed for the specific rental, not just assumed for the city. |
| **5** | **Car-Free Daily Living** | All daily essentials — training, classes, food, errands — must be accessible on foot or by transit. Car rental reserved for weekend excursions only. |

---

## 3. Discovery Attributes

Cities that pass all hard requirements will be scored and ranked against the following discovery attributes. These attributes capture the quality of life, cultural richness, and practical livability of each candidate city and will feed the weighting and scoring system defined in Scoring Brief v1.1.

| Category | Attribute | Scored |
|---|---|---|
| **Outdoor** | Distance and access to quality scuba diving / snorkeling sites | Yes |
| **Outdoor** | Distance and access to mountain hiking trails | Yes |
| **Climate** | Average June/July high temperature | Yes |
| **Cultural** | Presence of or proximity to Moorish / Andalusian architecture | No — boolean display field |
| **Cultural** | Distinctive local food and market culture | Yes |
| **Cultural** | Quality and variety of day trips within 1–2 hours | No — text display field |
| **Practical** | Cost of a 1–2 month rental | Yes |
| **Practical** | Walkability and public transit quality | Yes |
| **Practical** | Rail access to major European destinations — whether a major European hub is reachable within a day by train (direct or with connections) | Yes |
| **Livability** | Summer tourist density and overtourism risk | Yes |

*Note: Scoring and weighting methodology for these attributes is defined in Scoring Brief v1.1 (March 2026). Weights reflect relative importance to the travelers and produce a ranked composite score per city. Unscored display fields appear on city detail pages and comparison views but do not contribute to the composite score.*

---

## 4. Application Requirements

A purpose-built local web application will serve as the research hub and decision-tracking tool for this project. The application is intended for use by Cara and Abigail collaboratively and will run locally (no hosted deployment required).

### 4.1 Views

| Feature | Description |
|---|---|
| **City List** | Table or card grid showing all candidate cities with summary status — pass/fail on hard requirements, composite score, and research status flag. |
| **Dashboard / Overview** | High-level view across all cities showing scores, rankings, and progress of research completion. |
| **City Detail Page** | Deep-dive view per city with all attribute data, hard requirement status, contact tracking notes, and AI-generated executive summary. |
| **Comparison View** | Side-by-side comparison of 2 or more cities across all attributes and scores. |
| **Map — Country Level** | Map of Spain showing all candidate cities as pins with summary status. |
| **Map — City Level** | City-level map showing swim club, language program, and candidate rental locations with proximity indicators. |

### 4.2 Actions & Interactions

| Feature | Description |
|---|---|
| **Hard Requirement Tracking** | Mark each hard requirement as pass / fail / unknown per city. Cities failing any requirement are flagged or filtered out. |
| **Score & Rank** | Score each city against discovery attributes. System calculates weighted composite scores and produces a ranked list. |
| **Research Notes** | Free-text notes field per city to record research findings, decisions made, and open questions. |
| **Contact Tracking** | Notes field per contact type (swim club, language program, rental) to track outreach, responses, and status per city. |
| **Flag for Follow-up** | Ability to flag a city for further research or mark it as active, pending, or eliminated. |
| **AI Executive Summary** | On-demand AI-generated summary of each city based on collected data — surfacing key strengths, weaknesses, and open items. |

### 4.3 Data Population

- Data is populated by an automated research tool or agent — not manually entered by the user
- The application must accept structured data input from external research pipelines
- Manual override or annotation of agent-populated data must be possible

### 4.4 Platform & Constraints

- Runs locally — no hosted deployment or cloud infrastructure required
- Accessible via web browser on desktop
- Two users: Cara and Abigail (no authentication system required for local use)

---

## 5. Out of Scope

The following items are explicitly excluded from this project brief and will be addressed separately:

- Scoring and weighting methodology — defined in Scoring Brief v1.1 (March 2026)
- Data sources and research pipeline — to be defined separately
- Technology stack and implementation approach — to be decided during build phase
- Sports medicine or injury support logistics
- Social scene or nightlife research (Abigail's social life is expected to emerge naturally from swim club and language program participation)

---

## 6. Open Questions

- Which cities form the initial candidate longlist for research? (To be determined by research phase)
- What data sources and research tools will be used to populate city data?
- What technology stack will be used to build the local application?
- What university will Abigail attend? (May influence optimal city for language preparation)

---

## Version History

| Version | Date | Changes |
|---|---|---|
| 1.0 | March 2026 | Initial release — project overview, hard requirements, discovery attributes, application requirements. |
| 1.1 | March 2026 | Corrected traveler from father to mother; added `european_rail_access` to discovery attributes; removed Spanish rail connectivity attribute; scoring methodology marked as resolved. |
| 1.2 | March 2026 | Added Scored column to discovery attributes table; `moorish_architecture` and `day_trip_quality` reclassified as unscored display fields; Scoring Brief reference updated to v1.1. |

---

*Spain Summer 2027 Project · Project Brief v1.2 · March 2026 · Confidential*
