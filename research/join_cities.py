#!/usr/bin/env python3
"""
Join cities from RFEN swim clubs (enriched) and Spanish language programs.

Output: output/cities_swim_and_language.csv
  Cities that appear in BOTH sources — i.e. have at least one swim club
  and at least one language program. These satisfy Phase 1 screening criteria 4 and 5.

Usage:
  python research/join_cities.py

Requires: pandas, openpyxl (for xlsx)
"""

from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SWIM_FILE = BASE_DIR / "research" / "rfen_swim_clubs_enriched.xlsx"
LANG_FILE = BASE_DIR / "output" / "cities_spanish_language_programs.csv"
OUTPUT_FILE = BASE_DIR / "output" / "cities_swim_and_language.csv"


def normalize_city_key(city: str) -> str:
    s = unicodedata.normalize("NFKD", (city or "").strip())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^\w\s]", " ", s.lower())
    s = re.sub(r"\s+", " ", s).strip()
    return s


def canonical_display(display: str) -> str:
    """Prefer consistent display forms for known variants."""
    d = (display or "").strip()
    lowers = d.lower()
    if lowers in ("sevilla", "seville"):
        return "Seville"
    if lowers == "denia":
        return "Dénia"
    if lowers == "ubeda":
        return "Úbeda"
    if lowers == "malaga":
        return "Málaga"
    if lowers == "cadiz":
        return "Cádiz"
    if lowers == "cordoba":
        return "Córdoba"
    if lowers == "almeria":
        return "Almería"
    if lowers == "leon":
        return "León"
    return d


def load_swim_cities() -> dict[str, str]:
    """Returns {normalized_key: display_name}."""
    import pandas as pd

    df = pd.read_excel(SWIM_FILE, header=3)
    cities: dict[str, str] = {}
    for raw in df["city"].dropna().astype(str).unique():
        c = raw.strip()
        if not c or c.lower() == "spain":
            continue
        key = normalize_city_key(c)
        if key and key not in cities:
            cities[key] = canonical_display(c)
    return cities


def load_lang_cities() -> dict[str, str]:
    """Returns {normalized_key: display_name}."""
    cities: dict[str, str] = {}
    with open(LANG_FILE, encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            raw = (row.get("city") or "").strip()
            if not raw:
                continue
            key = normalize_city_key(raw)
            if key and key not in cities:
                cities[key] = canonical_display(raw)
    return cities


def main() -> None:
    swim = load_swim_cities()
    lang = load_lang_cities()

    # Inner join: cities in both
    common_keys = set(swim.keys()) & set(lang.keys())
    # Prefer language-program display when available (that list is curated)
    joined = [lang.get(k) or swim.get(k) or k for k in sorted(common_keys)]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["city"])
        w.writerows([[c] for c in joined])

    print(f"Swim clubs: {len(swim)} unique cities")
    print(f"Language programs: {len(lang)} unique cities")
    print(f"Intersection (both): {len(joined)} cities")
    print(f"  → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
