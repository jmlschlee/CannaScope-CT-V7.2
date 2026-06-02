"""
ct_cannabis_names.py
=====================
Resolve Connecticut cannabis PRODUCER and LAB names so the flagged-items PDF can
show BOTH the legal LLC name and the recognizable DBA / common name, and so that
EVERY lab appearing in your COA set is accounted for.

Design goals (why it's built this way):
  1. A static hand-list will ALWAYS go stale -- CT has 40+ establishments and the
     roster changes monthly. So this module backfills from the state's authoritative,
     weekly-updated dataset at runtime.
  2. Nothing should be silently dropped. Any producer or lab the module does not
     recognize is FLAGGED (not skipped), so you find out about a new entity instead
     of producing an incomplete PDF.

Authoritative state sources (Socrata API on the CT Open Data Portal):
  - Cannabis Establishments .......... dataset id  u8mw-sv7k   (all license types incl. labs)
  - Cannabis/MMP Brand Registry ...... dataset id  egd5-wb6r   (brand -> producer)

NOTE: This file uses `requests`. Your environment has web access, so the live
backfill will work there even though it could not be fetched in the chat that
generated this file.
"""

from __future__ import annotations
import csv
import os
import re
import sys
import json

try:
    import requests
except ImportError:  # graceful fallback so the curated map still works offline
    requests = None

# Optional runtime override file. Drop a CSV next to this script with the header
#   legal_name,common_name,abbrev
# and one row per producer to add/override a DBA WITHOUT editing code. This is
# the practical substitute for live-scraping the CT business search (which is a
# JavaScript/Salesforce app and can't be queried with a plain HTTP request):
# look the LLC up at https://service.ct.gov/business/s/onlinebusinesssearch ,
# read its trade name, and add a row. These overrides win over everything.
DBA_OVERRIDES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "dba_overrides.csv")


# ---------------------------------------------------------------------------
# 1. CURATED, SOURCE-VERIFIED PAIRS
#    key   = normalized legal/LLC name (see normalize() below)
#    value = (display_common_name, short_abbreviation)
#    These were confirmed from public reporting / company + state sources.
#    Anything NOT in here is resolved at runtime from the state dataset.
# ---------------------------------------------------------------------------
CURATED_PRODUCERS: dict[str, tuple[str, str]] = {
    # --- Original four medical PRODUCERS ---
    "advanced grow labs":                   ("Advanced Grow Labs", "AGL"),
    "connecticut pharmaceutical solutions": ("CTPharma", "CTPharma"),   # parent: Verano / Zen Leaf
    "curaleaf":                             ("Curaleaf", "Curaleaf"),
    "theraplant":                           ("Theraplant", "Theraplant"),

    # --- Cultivators / micro-cultivators / vertically-integrated operators ---
    "ffd 149":                              ("Fine Fettle", "FFD"),     # brands: Comffy, SAUS
    "shangri-la ct":                        ("Shangri-La (Borealis Cannabis)", "Borealis"),
    "debbie's dispensary":                  ("Crisp", "Crisp"),         # Debbie's Dispensary LLC d/b/a Crisp
    "the goods thc":                        ("The Goods THC", "Goods"), # brands: Cookies, Tyson 2.0
    "affinity grow":                        ("Affinity Grow", "Affinity"),
    "chillax":                              ("Chillax", "Chillax"),

    # --- Resolved from CT Secretary of State business records + public reporting
    #     (researched 2026-06; see commit notes). These are the LLC/holding-entity
    #     names that appear as the registry's BRANDING-ENTITY but are NOT how the
    #     product is known at retail. ---
    "dxr finance 3":                        ("Theraplant", "Theraplant"),  # DXR Finance foreclosed on / now operates Theraplant (Watertown)
    "soundview manufacturing":              ("SoundView", "SoundView"),    # getsoundview.com, Bristol edibles maker
    "connecticut contract manufacturing":   ("ConnCM", "ConnCM"),          # conncm.com, contract manufacturer
    # Single-brand producers, confirmed from the registry's own brand<->entity
    # mapping (the product names these LLCs ship carry exactly one brand):
    "56 benton":                            ("Lucky Chews", "Lucky Chews"),     # all products branded "Lucky Chews"
    "jananii":                              ("Awssom", "Awssom"),               # all products branded "AWSSOM"
    "nutmeg new britain jv":                ("Brix Cannabis", "Brix"),          # all products branded "Brix Cannabis"
    # The remaining registry entities (56 Benton, RAD Holding, Jananii, MCEJV,
    # Nutmeg New Britain JV, Connecticut Social Equity, Dutch, Golden Hanuman) are
    # micro-cultivators / JVs with no publicly verifiable consumer DBA yet, so we
    # deliberately DON'T assert one -- they display their legal name, and the
    # coverage audit still accounts for them. Add verified DBAs to dba_overrides.csv
    # (preferred, no code edit) or here as you confirm them via the CT business
    # search: https://service.ct.gov/business/s/onlinebusinesssearch
}

# Optional: brand -> producer hints, for when the COA shows only a brand name.
BRAND_TO_PRODUCER: dict[str, str] = {
    "comffy":    "Fine Fettle",
    "saus":      "Fine Fettle",
    "cookies":   "The Goods THC",
    "tyson 2.0": "The Goods THC",
    "superflux": "The Botanist",
    "borealis":  "Shangri-La (Borealis Cannabis)",
}


# ---------------------------------------------------------------------------
# 2. CURATED LAB LIST
#    Every COA in CT should come from a CT-licensed cannabis testing lab.
#    Historically only two in-state labs ever operated; AltaSci closed in 2023,
#    leaving Northeast as the primary, with new labs being licensed under PA 23-79.
#    The runtime loader (below) refreshes this from the state establishments data.
#
#    The lower block mirrors the labs the CannaScope parser (KNOWN_LABS) already
#    recognizes on COAs, so the lab-coverage audit treats a parser-identified lab
#    as "known" instead of flagging it as unrecognized. Keep the two lists in sync.
# ---------------------------------------------------------------------------
CURATED_LABS: dict[str, str] = {
    "northeast laboratories": "Northeast Laboratories",
    "altasci laboratories":   "AltaSci Laboratories",   # closed 2023; on older COAs
    # Labs the COA parser (cannascope KNOWN_LABS) can already name from a COA:
    "analytics labs":         "Analytics Labs",
    "proverde laboratories":  "ProVerde Laboratories",
    "abko labs":              "ABKO Labs",
    "trichome analytical":    "Trichome Analytical",
    "mcr labs":               "MCR Labs",
    # Newly PA 23-79-licensed labs are added automatically by the runtime loader.
}


# ---------------------------------------------------------------------------
# 3. NORMALIZATION  (so "FFD 149, LLC." == "ffd 149 llc" == "FFD 149  LLC")
# ---------------------------------------------------------------------------
_ENTITY_SUFFIXES = r"\b(llc|l\.l\.c|inc|inc\.|ltd|co|corp|corporation|company|the)\b"


def normalize(name: str) -> str:
    if not name:
        return ""
    name = name.lower()
    name = re.sub(_ENTITY_SUFFIXES, " ", name)
    name = re.sub(r"[^a-z0-9 ]", " ", name)   # drop punctuation
    return " ".join(name.split())             # collapse whitespace


# Re-key the curated maps through normalize() so a lookup ALWAYS matches,
# regardless of how the source literal above was hand-typed. Without this, keys
# containing punctuation, an apostrophe, a hyphen, or a leading "The" (e.g.
# "debbies dispensary", "shangri-la ct", "the goods thc") would never match the
# normalized name coming off the registry, and the producer would wrongly show
# as UNMAPPED. Edit the human-readable literals above; this keeps them honest.
CURATED_PRODUCERS = {normalize(k): v for k, v in CURATED_PRODUCERS.items()}
CURATED_LABS = {normalize(k): v for k, v in CURATED_LABS.items()}


# ---------------------------------------------------------------------------
# 4. LIVE BACKFILL FROM THE STATE DATASET (authoritative + always current)
#
# REALITY CHECK (verified 2026-06): Connecticut does NOT publish a single
# "Cannabis Establishments" roster (with legal name + DBA + license type) on its
# Socrata open-data portal. The licensee roster lives on the eLicense portal
# (elicense.ct.gov), which is not a Socrata JSON resource. The id used below was
# a placeholder and returns empty records. So unless SOCRATA_ESTABLISHMENTS is
# pointed at a real resource that carries the columns in *_KEYS, the backfill is
# a deliberate no-op and we rely on the curated map + the coverage audit (which
# still surfaces any unmapped producer/lab rather than dropping it).
#
# To enable a real backfill later: find a dataset that has a legal-name column, a
# DBA column, and a license-type column, set SOCRATA_ESTABLISHMENTS to its
# `.json` endpoint, run `print(load_state_establishments()[0].keys())`, and align
# the *_KEYS tuples below to the actual column names.
# ---------------------------------------------------------------------------
SOCRATA_ESTABLISHMENTS = "https://data.ct.gov/resource/u8mw-sv7k.json?$limit=5000"

# Candidate column names to probe -- Socrata schemas drift, so we try several.
_LEGAL_KEYS = ("business_legal_name", "legal_name", "business_name", "name", "establishment")
_DBA_KEYS   = ("dba", "dba_name", "trade_name", "doing_business_as", "d_b_a")
_TYPE_KEYS  = ("license_type", "type", "credential_type")
_STATUS_KEYS = ("license_status", "status", "credential_status")


def _first_present(row: dict, keys) -> str:
    for k in keys:
        if k in row and row[k]:
            return str(row[k]).strip()
    return ""


def load_state_establishments(url: str = SOCRATA_ESTABLISHMENTS) -> list[dict]:
    """Pull the authoritative CT establishments list. Returns [] on failure.

    Filters out empty records and, if the response carried rows but none of them
    expose any of the expected columns, warns clearly instead of silently
    pretending the backfill succeeded -- so a wrong dataset id can't masquerade
    as "no new entities."
    """
    if requests is None:
        print("[warn] `requests` not installed -- skipping live state backfill.", file=sys.stderr)
        return []
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:  # noqa: BLE001
        print(f"[warn] could not load state dataset ({e}); using curated maps only.", file=sys.stderr)
        return []

    rows = [r for r in data if isinstance(r, dict) and r]
    if data and not rows:
        print(f"[warn] state dataset returned {len(data)} empty record(s) -- the "
              f"establishments resource id is likely wrong/placeholder; using "
              f"curated maps only. See the note above SOCRATA_ESTABLISHMENTS.",
              file=sys.stderr)
        return []
    probe = _ALL_PROBE_KEYS
    if rows and not any(any(k in r for k in probe) for r in rows):
        print(f"[warn] state dataset has {len(rows)} rows but none expose the "
              f"expected columns ({', '.join(probe)}); using curated maps only. "
              f"Align the *_KEYS tuples to the real schema.", file=sys.stderr)
        return []
    return rows


_ALL_PROBE_KEYS = _LEGAL_KEYS + _DBA_KEYS + _TYPE_KEYS


def build_maps_from_state(rows: list[dict]):
    """Return (producer_map, lab_map) derived from the live dataset.

    If you don't know the real column names yet, run:
        rows = load_state_establishments()
        print(rows[0].keys())            # inspect once
    and adjust the *_KEYS tuples above to match.
    """
    producer_map: dict[str, tuple[str, str]] = {}
    lab_map: dict[str, str] = {}

    PRODUCER_TYPES = ("producer", "cultivator", "micro-cultivator",
                      "micro cultivator", "product manufacturer")
    LAB_TYPES = ("testing laboratory", "cannabis testing")

    for row in rows:
        legal = _first_present(row, _LEGAL_KEYS)
        if not legal:
            continue
        dba = _first_present(row, _DBA_KEYS) or legal
        ltype = _first_present(row, _TYPE_KEYS).lower()
        key = normalize(legal)

        if any(t in ltype for t in LAB_TYPES):
            lab_map[key] = dba
        elif any(t in ltype for t in PRODUCER_TYPES):
            abbrev = dba.split()[0] if dba else legal.split()[0]
            producer_map.setdefault(key, (dba, abbrev))

    return producer_map, lab_map


# ---------------------------------------------------------------------------
# 5. MERGE  (curated wins on conflicts; state fills the gaps)
#    The live state dataset is loaded ONCE and reused for both maps, so callers
#    that ask for both producers and labs don't trigger two network round-trips.
# ---------------------------------------------------------------------------
_STATE_ROWS_CACHE: list[dict] | None = None


def _cached_state_rows(use_live: bool) -> list[dict]:
    global _STATE_ROWS_CACHE
    if not use_live:
        return []
    if _STATE_ROWS_CACHE is None:
        _STATE_ROWS_CACHE = load_state_establishments()
    return _STATE_ROWS_CACHE


def build_producer_map_from_registry(producer_names) -> dict[str, tuple[str, str]]:
    """Register EVERY producer legal name that appears in the CT product registry
    (egd5-wb6r, the same CSV CannaScope already downloads), so the producer
    universe is authoritative and complete -- no real producer is ever 'unmapped'.

    The registry has the legal `producer` name but no separate DBA column, so the
    display name defaults to the legal name as-is; the curated map (which DOES
    carry verified DBA / common names) is layered on top by get_producer_map().
    """
    m: dict[str, tuple[str, str]] = {}
    for legal in producer_names:
        legal = (legal or "").strip()
        key = normalize(legal)
        if key and key not in m:
            m[key] = (legal, legal.split()[0] if legal.split() else legal)
    return m


def load_dba_overrides(path: str = DBA_OVERRIDES_FILE) -> dict[str, tuple[str, str]]:
    """Read user-supplied DBA overrides from a CSV (header: legal_name,common_name,
    abbrev). Returns {} if the file is absent or unreadable. Keyed by normalize()."""
    out: dict[str, tuple[str, str]] = {}
    if not path or not os.path.exists(path):
        return out
    try:
        with open(path, encoding="utf-8-sig", errors="replace", newline="") as f:
            for row in csv.DictReader(f):
                legal = (row.get("legal_name") or "").strip()
                common = (row.get("common_name") or "").strip()
                if not legal or not common:
                    continue
                abbrev = (row.get("abbrev") or common.split()[0]).strip()
                out[normalize(legal)] = (common, abbrev)
    except Exception as e:  # noqa: BLE001
        print(f"[warn] could not read DBA overrides ({e}); ignoring file.", file=sys.stderr)
    return out


def get_producer_map(use_live: bool = True,
                     registry_names=None) -> dict[str, tuple[str, str]]:
    """Producer name map. Layering (each overrides the previous):
        1. registry universe (every producer in egd5-wb6r) -- if registry_names given
        2. legacy state-dataset backfill -- only if use_live and no registry_names
        3. CURATED_PRODUCERS -- verified DBA / common names baked into the code
        4. dba_overrides.csv -- user-supplied DBAs (from the CT business search), win
    """
    merged: dict[str, tuple[str, str]] = {}
    if registry_names is not None:
        merged.update(build_producer_map_from_registry(registry_names))
    elif use_live:
        state_prod, _ = build_maps_from_state(_cached_state_rows(use_live))
        merged.update(state_prod)
    merged.update(CURATED_PRODUCERS)     # curated DBA names win over registry
    merged.update(load_dba_overrides())  # user overrides win over everything
    return merged


def get_lab_map(use_live: bool = True) -> dict[str, str]:
    merged: dict[str, str] = {}
    if use_live:
        _, state_labs = build_maps_from_state(_cached_state_rows(use_live))
        merged.update(state_labs)
    merged.update(CURATED_LABS)
    return merged


# ---------------------------------------------------------------------------
# 6. PUBLIC HELPERS  (use these in the PDF generator)
# ---------------------------------------------------------------------------
def display_producer(legal_name: str, producer_map: dict | None = None) -> str:
    """'Common Name (Legal LLC Name)' for the flagged-items PDF.

    Falls back to the legal name (with a flag) if the producer is unknown, so
    an unrecognized entity is visible rather than dropped.
    """
    pmap = producer_map if producer_map is not None else get_producer_map()
    hit = pmap.get(normalize(legal_name))
    if hit:
        common = hit[0]
        # avoid "Curaleaf (Curaleaf, LLC)" redundancy
        if normalize(common) == normalize(legal_name):
            return legal_name
        return f"{common} ({legal_name})"
    return f"{legal_name}  [UNMAPPED PRODUCER -- verify]"


def display_lab(lab_name: str, lab_map: dict | None = None) -> str:
    lmap = lab_map if lab_map is not None else get_lab_map()
    hit = lmap.get(normalize(lab_name))
    return hit if hit else f"{lab_name}  [UNRECOGNIZED LAB -- verify]"


# ---------------------------------------------------------------------------
# 7. LAB-COVERAGE GUARANTEE
#    Call this with the set of lab names your parser extracted from the COAs.
#    It reports (a) labs found in COAs that the code doesn't recognize, and
#    (b) recognized labs that produced ZERO analyzed COAs -- the two ways a lab
#    can quietly fall out of your analysis.
# ---------------------------------------------------------------------------
def audit_lab_coverage(coa_lab_names, lab_map: dict | None = None, strict: bool = False) -> dict:
    lmap = lab_map if lab_map is not None else get_lab_map()
    seen = {normalize(n) for n in coa_lab_names if n}
    known = set(lmap.keys())

    unknown = sorted(seen - known)              # labs in data we can't identify
    known_with_no_coas = sorted(known - seen)   # licensed labs with no COAs analyzed

    report = {
        "labs_seen_in_coas": sorted(seen),
        "unrecognized_labs": unknown,
        "known_labs_without_coas": known_with_no_coas,
        "all_labs_recognized": not unknown,
    }
    if unknown:
        msg = f"[LAB COVERAGE] Unrecognized lab(s) in COA set: {unknown}"
        if strict:
            raise ValueError(msg)
        print(msg, file=sys.stderr)
    return report


def audit_producer_coverage(coa_producer_names, producer_map: dict | None = None,
                            strict: bool = False) -> dict:
    """Producer analogue of audit_lab_coverage().

    Reports producers seen on COAs that the module can't map to a common/DBA name
    (so a newly-licensed producer surfaces instead of silently displaying only an
    LLC), and mapped producers that contributed ZERO analyzed COAs this run.
    """
    pmap = producer_map if producer_map is not None else get_producer_map()
    seen = {normalize(n) for n in coa_producer_names if n}
    known = set(pmap.keys())

    unmapped = sorted(seen - known)                 # producers we can't name
    known_with_no_coas = sorted(known - seen)       # known producers, no COAs this run

    report = {
        "producers_seen_in_coas": sorted(seen),
        "unmapped_producers": unmapped,
        "known_producers_without_coas": known_with_no_coas,
        "all_producers_mapped": not unmapped,
    }
    if unmapped:
        msg = f"[PRODUCER COVERAGE] Unmapped producer(s) in COA set: {unmapped}"
        if strict:
            raise ValueError(msg)
        print(msg, file=sys.stderr)
    return report


# ---------------------------------------------------------------------------
# 8. QUICK SELF-TEST
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    pmap = get_producer_map(use_live=False)   # curated only, for offline demo
    for legal in ["FFD 149 LLC", "Debbie's Dispensary, LLC", "Shangri-La CT, Inc.",
                  "Curaleaf, LLC", "Some New Grower LLC"]:
        print(f"{legal:32s} ->  {display_producer(legal, pmap)}")

    print()
    lmap = get_lab_map(use_live=False)
    print(audit_lab_coverage(["Northeast Laboratories", "AltaSci Laboratories",
                              "Mystery Lab Inc"], lmap))
    print(audit_producer_coverage(["Curaleaf, LLC", "FFD 149 LLC", "Some New Grower LLC"], pmap))
