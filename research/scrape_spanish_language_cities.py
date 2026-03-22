#!/usr/bin/env python3
"""
Scrape city names from Spanish language school directories; output one deduplicated CSV.

Goal: A single file listing every Spanish city that has at least one Spanish language
program, from FEDELE, SACIC, languagecourse.net, Expatica, and a static list
(languageinternational.com facets — no scraping).

Output: output/cities_spanish_language_programs.csv
  Single column: city

Usage:
  pip install -r requirements-scraper.txt
  playwright install chromium
  python research/scrape_spanish_language_cities.py
"""

from __future__ import annotations

import csv
import os
import random
import re
import time
import traceback
import unicodedata
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
ERROR_LOG = OUTPUT_DIR / "scrape_errors.log"
OUTPUT_FILE = OUTPUT_DIR / "cities_spanish_language_programs.csv"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

# Display priority: when deduping, prefer this source's spelling for the city name.
DISPLAY_PRIORITY = ["fedele", "sacic", "languagecourse", "languageinternational", "expatica"]

FEDELE_LIST = "https://fedele.org/en/escuelas/"
SACIC_URL = "https://acreditacion.cervantes.es/centros_espana.htm"
LC_BASE = "https://www.languagecourse.net"
LC_SPAIN = f"{LC_BASE}/schools--spain.php3"
EXPATICA_URL = "https://www.expatica.com/es/directory/education/language-schools/"

# Facets from languageinternational.com course-search (no scraping).
LANGUAGE_INTERNATIONAL_CITIES: tuple[str, ...] = (
    "A Coruña",
    "Albacete",
    "Alicante",
    "Almería",
    "Almuñécar",
    "Barbate",
    "Barcelona",
    "Bilbao",
    "Blanes",
    "Burgos",
    "Cadiz",
    "Castelldefels",
    "Córdoba",
    "Dénia",
    "Gijón",
    "Girona",
    "Granada",
    "Ibiza",
    "Jaen",
    "Jerez de la Frontera",
    "Las Palmas de Gran Canaria",
    "León",
    "Madrid",
    "Malaga",
    "Marbella",
    "Murcia",
    "Nerja",
    "Palma de Mallorca",
    "Pamplona",
    "Puerto de Santa Maria",
    "Ronda",
    "Salamanca",
    "San Sebastián",
    "Santander",
    "Santiago de Compostela",
    "Seville",
    "Tarifa",
    "Tarragona",
    "Tenerife",
    "Teruel",
    "Toledo",
    "Valencia",
    "Valladolid",
    "Vejer de la Frontera",
    "Zaragoza",
)

# Slugs/names that are schools or fragments, not cities.
CITY_BLOCKLIST: frozenset[str] = frozenset(
    {
        "academy", "aifp", "alcantara", "azul", "brava", "castellano", "castila",
        "bcn", "bcnlip", "centro", "international", "spanish", "language",
        "escuela", "school", "instituto", "languages", "idiomas",
        "center", "ciam", "contacto", "continental", "dice", "education",
        "espana", "espanol", "euroace", "flavia", "flores", "gabriel",
        "hemingway", "hispalense", "iberico", "idealog", "inhispania", "inmsol",
        "institute", "intereuropa", "intern", "internacional", "maestromio",
        "maravillas", "mester", "mlg", "pagoda", "real", "rey", "space",
        "sv", "tclanguages", "tenidiomas", "tlcdenia", "tula", "unamuno",
        "valjunquera", "v", "debla", "delibes", "euroace",
    }
)

CITY_SLUG_HINTS: tuple[tuple[str, str], ...] = (
    ("san-sebastian", "San Sebastián"),
    ("jerez-de-la-frontera", "Jerez de la Frontera"),
    ("la-laguna", "La Laguna"),
    ("las-palmas", "Las Palmas de Gran Canaria"),
    ("palma-de-mallorca", "Palma de Mallorca"),
    ("santiago-de-compostela", "Santiago de Compostela"),
    ("puerto-de-santa-maria", "Puerto de Santa María"),
    ("alcala-de-henares", "Alcalá de Henares"),
    ("vejer-de-la-frontera", "Vejer de la Frontera"),
    ("granada", "Granada"),
    ("barcelona", "Barcelona"),
    ("valencia", "Valencia"),
    ("salamanca", "Salamanca"),
    ("sevilla", "Seville"),
    ("madrid", "Madrid"),
    ("malaga", "Málaga"),
    ("bilbao", "Bilbao"),
    ("cadiz", "Cádiz"),
    ("cordoba", "Córdoba"),
    ("alicante", "Alicante"),
    ("murcia", "Murcia"),
    ("pamplona", "Pamplona"),
    ("tenerife", "Tenerife"),
    ("nerja", "Nerja"),
    ("marbella", "Marbella"),
    ("gijon", "Gijón"),
    ("almeria", "Almería"),
    ("zaragoza", "Zaragoza"),
    ("valladolid", "Valladolid"),
    ("toledo", "Toledo"),
    ("segovia", "Segovia"),
)


def log_error(source: str, message: str, exc: BaseException | None = None) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} [{source}] {message}\n"
    if exc is not None:
        line += traceback.format_exc() + "\n"
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(line)


def throttle() -> None:
    time.sleep(random.uniform(1.0, 2.0))


def normalize_city_key(city: str) -> str:
    s = unicodedata.normalize("NFKD", (city or "").strip())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^\w\s]", " ", s.lower())
    s = re.sub(r"\s+", " ", s).strip()
    return s


def city_from_slug(slug: str) -> str:
    slug_l = slug.lower().replace("_", "-")
    for hint, name in CITY_SLUG_HINTS:
        if hint in slug_l:
            return name
    parts = slug.split("-")
    while parts and parts[-1].isdigit():
        parts.pop()
    if len(parts) >= 2:
        tail = parts[-1]
        if len(tail) > 2 and not tail.isdigit() and tail.lower() not in CITY_BLOCKLIST:
            return tail.replace("-", " ").title()
    if parts and parts[-1].lower() not in CITY_BLOCKLIST:
        return parts[-1].replace("-", " ").title()
    return ""


def collect_fedele_cities() -> set[tuple[str, str]]:
    """Returns {(normalized_key, display_name), ...}"""
    seen: set[tuple[str, str]] = set()
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.9,es;q=0.8",
    })
    url_re = re.compile(r"https://fedele\.org/en/escuelas/([^/#?\"']+)/?", re.I)
    page_url = FEDELE_LIST
    try:
        while page_url:
            throttle()
            resp = session.get(page_url, timeout=60)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")
            for a in soup.select('a[href*="fedele.org"]'):
                m = url_re.match((a.get("href") or "").split("#")[0])
                if not m:
                    continue
                slug = m.group(1).lower()
                if slug in ("feed", "page", "escuelas") or slug.startswith("page"):
                    continue
                city = city_from_slug(slug)
                if not city:
                    continue
                key = normalize_city_key(city)
                if key and key != "spain":
                    seen.add((key, city))
            nxt = soup.find("link", rel="next")
            page_url = nxt.get("href") if nxt and nxt.get("href") else ""
    except Exception as e:
        log_error("fedele", str(e), e)
    return seen


def collect_sacic_cities() -> set[tuple[str, str]]:
    seen: set[tuple[str, str]] = set()
    throttle()
    try:
        resp = requests.get(SACIC_URL, timeout=90, headers={"User-Agent": USER_AGENT})
        resp.raise_for_status()
        if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
            resp.encoding = resp.apparent_encoding or "utf-8"
    except Exception as e:
        log_error("sacic", str(e), e)
        return seen

    soup = BeautifulSoup(resp.text, "lxml")
    col = soup.select_one("#col")
    if not col:
        log_error("sacic", "no #col container found")
        return seen

    ccaa = prov = city = ""
    for el in col.find_all(["h2", "h3", "h4", "dl"], recursive=True):
        if el.name == "h2":
            ccaa = el.get_text(strip=True)
            prov = ""
            city = ""
        elif el.name == "h3":
            prov = el.get_text(strip=True)
            city = ""
        elif el.name == "h4":
            city = el.get_text(strip=True)
        elif el.name == "dl":
            display = (city or prov or ccaa or "").strip()
            if display and display.lower() != "spain":
                key = normalize_city_key(display)
                if key:
                    seen.add((key, display))
    return seen


def collect_languagecourse_cities() -> set[tuple[str, str]]:
    """City list from Spain index page only — no per-city page visits."""
    seen: set[tuple[str, str]] = set()
    try:
        from playwright.sync_api import sync_playwright

        p = sync_playwright().start()
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent=USER_AGENT, locale="en-GB")
        page = ctx.new_page()
        page.set_default_timeout(60_000)
        page.goto(LC_SPAIN, wait_until="networkidle")
        page.wait_for_timeout(2000)

        city_hrefs = page.evaluate(
            """() => {
              const xs = [...document.querySelectorAll('a[href^="/schools-"][href$=".php3"]')]
                .map(a => a.getAttribute('href'))
                .filter(h => h && h !== '/schools--spain.php3');
              return [...new Set(xs)];
            }"""
        )
        browser.close()
        p.stop()

        for ch in city_hrefs:
            city_slug = ch.replace("/schools-", "").replace(".php3", "")
            if "--" in city_slug or not city_slug:
                continue
            # Try slug hints first, else title-case
            display = city_from_slug(city_slug) or city_slug.replace("--", " ").replace("-", " ").title()
            key = normalize_city_key(display)
            if key and key != "spain":
                seen.add((key, display))
    except Exception as e:
        log_error("languagecourse", str(e), e)
    return seen


def collect_expatica_cities() -> set[tuple[str, str]]:
    seen: set[tuple[str, str]] = set()
    try:
        from playwright.sync_api import sync_playwright

        p = sync_playwright().start()
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent=USER_AGENT, locale="en-GB")
        page = ctx.new_page()
        page.set_default_timeout(90_000)

        max_pages = int(os.environ.get("MAX_EXPATICA_PAGES", "40"))
        seen_names: set[str] = set()
        stagnant = 0

        for page_num in range(1, max_pages + 1):
            url = EXPATICA_URL if page_num == 1 else f"{EXPATICA_URL}?page={page_num}"
            throttle()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(5000)

            batch = page.evaluate(
                """() => {
                  const root = document.querySelector('main') || document.body;
                  const hs = [...root.querySelectorAll('h2, h3')];
                  const out = [];
                  for (const h of hs) {
                    const name = (h.textContent||'').trim();
                    if (name.length < 3) continue;
                    if (name.includes('Add your') || name.includes('Other listings') || name === 'All Language Resources') continue;
                    const block = h.closest('section') || h.parentElement?.parentElement;
                    let city = '';
                    const txt = (block?.innerText || h.parentElement?.innerText || '').slice(0, 800);
                    const m = txt.match(/\\b(Madrid|Barcelona|Valencia|Seville|Sevilla|Bilbao|Granada|Salamanca|Málaga|Malaga|Murcia|Palma|Alicante|Zaragoza|Córdoba|Cordoba|San Sebastián|San Sebastian|Marbella|Nerja|Tenerife)\\b/i);
                    if (m) city = m[0].replace(/Sevilla/i, 'Seville');
                    if (!city) {
                      const ln = name.toLowerCase();
                      if (ln.includes('barcelona') || ln.includes('bcn')) city = 'Barcelona';
                      else if (ln.includes('madrid')) city = 'Madrid';
                      else if (ln.includes('valencia')) city = 'Valencia';
                    }
                    out.push({ name, city });
                  }
                  return out;
                }"""
            )
            if not batch:
                break

            new_count = sum(1 for item in batch if item.get("name") and item["name"] not in seen_names)
            for item in batch:
                if item.get("name"):
                    seen_names.add(item["name"])
                c = (item.get("city") or "").strip()
                if not c or c.lower() == "spain":
                    continue
                key = normalize_city_key(c)
                if key:
                    seen.add((key, c))

            if new_count == 0:
                stagnant += 1
                if stagnant >= 2:
                    break
            else:
                stagnant = 0

        browser.close()
        p.stop()
    except Exception as e:
        log_error("expatica", str(e), e)
    return seen


def collect_li_cities() -> set[tuple[str, str]]:
    return {(normalize_city_key(c), c) for c in LANGUAGE_INTERNATIONAL_CITIES}


def _skip_city(key: str, display: str) -> bool:
    if not key or key == "spain":
        return True
    if key in CITY_BLOCKLIST:
        return True
    # "X ciudad" -> treat as X; avoid duplicates by preferring non-ciudad form
    if display.endswith(" ciudad") and len(display) > 8:
        return False  # keep, we'll normalize below
    return False


def _normalize_display(display: str) -> str:
    if display.endswith(" ciudad"):
        return display[:-7].strip()
    d = display.strip()
    lowers = d.lower()
    if lowers == "bcn":
        return "Barcelona"
    if lowers in ("sevilla", "seville"):
        return "Seville"
    if lowers == "denia":
        return "Dénia"
    if lowers == "ubeda":
        return "Úbeda"
    return d


def merge_and_dedupe(
    fed: set[tuple[str, str]],
    sac: set[tuple[str, str]],
    lc: set[tuple[str, str]],
    ex: set[tuple[str, str]],
    li: set[tuple[str, str]],
) -> list[str]:
    """Merge all (key, display) pairs; for each key, pick display from highest-priority source."""
    by_key: dict[str, list[tuple[str, str]]] = {}
    for src_name, pairs in [
        ("fedele", fed),
        ("sacic", sac),
        ("languagecourse", lc),
        ("languageinternational", li),
        ("expatica", ex),
    ]:
        pri = DISPLAY_PRIORITY.index(src_name) if src_name in DISPLAY_PRIORITY else 99
        for key, display in pairs:
            if _skip_city(key, display):
                continue
            display = _normalize_display(display)
            key = normalize_city_key(display)
            if not key or key in CITY_BLOCKLIST:
                continue
            if key not in by_key:
                by_key[key] = []
            by_key[key].append((pri, display))

    result: list[str] = []
    for key in sorted(by_key.keys()):
        picks = by_key[key]
        picks.sort(key=lambda x: (x[0], -len(x[1])))
        display = picks[0][1]
        result.append(display)
    return result


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if ERROR_LOG.exists():
        ERROR_LOG.unlink()

    print("FEDELE …")
    fed = collect_fedele_cities()
    print(f"  {len(fed)} cities")

    print("SACIC …")
    sac = collect_sacic_cities()
    print(f"  {len(sac)} cities")

    print("languagecourse.net …")
    lc = collect_languagecourse_cities()
    print(f"  {len(lc)} cities")

    print("Language International (static list) …")
    li = collect_li_cities()
    print(f"  {len(li)} cities")

    print("Expatica …")
    ex = collect_expatica_cities()
    print(f"  {len(ex)} cities")

    print("Merging & deduping …")
    cities = merge_and_dedupe(fed, sac, lc, ex, li)
    print(f"  {len(cities)} unique cities")

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["city"])
        w.writerows([[c] for c in cities])

    print(f"  → {OUTPUT_FILE}")

    if ERROR_LOG.exists() and ERROR_LOG.stat().st_size > 0:
        print(f"Warnings/errors logged to {ERROR_LOG}")


if __name__ == "__main__":
    main()
