"""
coa_csv_cache.py — persistent COA -> measurement cache for CannaScope CT.

WHY THIS SHAPE: a COA PDF is immutable once issued, so its MEASUREMENTS never change —
but a FLAG depends on the run's threshold, so flags must be recomputed each run. This module
caches the measurements (one spreadsheet-readable CSV row per COA) so every COA is downloaded
+ read (incl. OCR) ONCE; later runs load values from CSV and recompute flags from them with the
real engine. Lowering --threshold then correctly re-flags previously-clean COAs from cache,
with no re-download and no re-OCR.

It reuses the real engine APIs only (no re-implementation of parsing/flagging logic):
  v4.coa_key, v4.cache_path, v4.download_pdf, v4._pdfium_text / _pdfplumber_text / _layout_broken,
  v4.ocr_pdf, v4.find_overall_result, v4.parse_lab, v4.parse_analytes, v4.apply_flags,
  v5.ProductV5, v5.parse_cannabinoids, v5.apply_thc_flags, v5.product_core_name.
The download / pdfium / ocr names are resolved as MODULE GLOBALS at call time, so the host's
--offline and OCR-isolation overrides still apply on the MISS path.

Import AFTER the engine modules are in sys.modules (i.e. after _install_embedded()).
"""
import csv
import datetime
import hashlib
import json
import os
import sys
import threading

import cannascope_ct_v4 as v4
import cannascope_ct_v5 as v5

# Bump to force a one-time rebuild of every cached row (e.g. if the parse/measurement shape changes).
# v2: added the triple-verification stamp (_verified in _extra) written by the build-cache pass.
# v3: engine fix — below-detection results ("<20") and two-column "Results | Limits" rows are no
#     longer misread as at-limit measurements; forces a full re-extraction so cached values are correct.
SCHEMA = 5

# One row per COA. Flat scalar columns first (human/spreadsheet readable), then lossless JSON
# columns, then meta. Flags / thc_flags are deliberately NOT stored — they are recomputed by
# v4.apply_flags / v5.apply_thc_flags on rehydrate, so a new threshold re-flags from measurements.
_FLAT = ["product", "producer", "brand", "dosage_form", "approval_date", "registration_number",
         "report_url", "test_lab", "overall_result", "pesticides", "solvents", "parse_note", "strain"]
_JSON = ["analytes", "solvent_hits", "cannabinoids"]
_META = ["_coa_key", "_method", "_text_len", "_pdf_sha1", "_source_url", "_cached_at",
         "_schema", "_mold_yeast_cfu", "_extra"]
COLUMNS = _FLAT + _JSON + _META

# product attribute <- CSV "product" column (the registry product name).
_FLAT_ATTR = {"product": "product_name"}


def _out_dir():
    for cand in (getattr(v5, "OUT_DIR", None), getattr(v4, "OUT_DIR", None)):
        if cand:
            return cand
    cd = getattr(v4, "CACHE_DIR", "") or ""
    return os.path.dirname(cd) or "."


def _default_path():
    return os.path.join(_out_dir(), "COA Data Cache.csv")


def _now():
    return datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def _sha1(path):
    try:
        h = hashlib.sha1()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return ""


def _jloads(s, default):
    if not s:
        return default
    try:
        v = json.loads(s)
        return v if v is not None else default
    except (ValueError, TypeError):
        return default


# ------------------------------------------------------------------------------------------------
class CoaCsvCache:
    """In-memory map of coa_key -> row, backed by a CSV. Thread-safe puts; one atomic flush()."""

    # Checkpoint the CSV every this many puts, so a multi-hour full-registry build never loses
    # more than this many freshly-extracted COAs to a crash. flush() is atomic (.tmp + os.replace).
    _FLUSH_EVERY = 1000

    def __init__(self, path=None):
        self.path = path or _default_path()
        self._rows = {}            # coa_key -> dict(row)
        self._lock = threading.Lock()
        self._dirty = False
        self._since_flush = 0
        self._load()

    # ---- load / size ----
    def _load(self):
        try:
            with open(self.path, encoding="utf-8", newline="") as f:
                for row in csv.DictReader(f):
                    k = row.get("_coa_key") or ""
                    if k:
                        self._rows[k] = row
        except OSError:
            pass
        except (csv.Error, ValueError):
            # a corrupt cache is a soft failure — start empty rather than crash a run.
            self._rows = {}

    def __len__(self):
        return len(self._rows)

    def __contains__(self, p):
        return v4.coa_key(p) in self._rows

    # ---- read side ----
    def fresh_row(self, p):
        """The cached row for product `p` IF it is still valid, else None. Invalidated when:
        the schema changed, the registry report_url for this coa_key changed (re-tested / re-released
        batch), or the prior read produced nothing (_method == 'none') and we may now be back online."""
        row = self._rows.get(v4.coa_key(p))
        if not row:
            return None
        try:
            if int(row.get("_schema") or 0) != SCHEMA:
                return None
        except (TypeError, ValueError):
            return None
        if (row.get("report_url") or "") != (getattr(p, "report_url", "") or ""):
            return None
        if (row.get("_method") or "") == "none":
            return None
        return row

    def rehydrate(self, row, watch):
        """Rebuild a ProductV5 from a cached row and RECOMPUTE flags at the current `watch`
        threshold (so a lower threshold re-flags a previously-clean COA). No network, no OCR."""
        p = v5.ProductV5()
        for col in _FLAT:
            setattr(p, _FLAT_ATTR.get(col, col), row.get(col) or "")
        p.analytes = _jloads(row.get("analytes"), {})
        p.solvent_hits = _jloads(row.get("solvent_hits"), [])
        p.cannabinoids = _jloads(row.get("cannabinoids"), {})
        myc = row.get("_mold_yeast_cfu")
        try:
            p.mold_yeast_cfu = float(myc) if myc not in (None, "") else None
        except (TypeError, ValueError):
            p.mold_yeast_cfu = None
        # Optional host-supplied extras (e.g. V15's text-derived testing_date / _coa_status) so a
        # cache HIT reconstructs a report-faithful product without re-reading the COA text.
        for k, val in (_jloads(row.get("_extra"), {}) or {}).items():
            try:
                setattr(p, k, val)
            except Exception:
                pass
        # Recompute flags from the stored MEASUREMENTS (text is unused by apply_flags except for one
        # PASS-vs-internal-contradiction check, which was already resolved on the extracting run).
        p.flags = []
        p.thc_flags = []
        v4.apply_flags(p, "", watch)
        v5.apply_thc_flags(p)
        p._cache_method = row.get("_method") or ""
        p._from_cache = True
        return p

    # ---- write side ----
    def put(self, p, method="", text_len=0, pdf_path="", extra=None):
        """Store product `p`'s measurements. `extra` is an optional dict of additional serializable
        attributes to round-trip (restored via setattr on rehydrate) — used by the host to keep
        report-fidelity fields that aren't measurements."""
        key = v4.coa_key(p)
        row = {}
        for col in _FLAT:
            row[col] = getattr(p, _FLAT_ATTR.get(col, col), "") or ""
        row["analytes"] = json.dumps(getattr(p, "analytes", {}) or {}, default=str)
        row["solvent_hits"] = json.dumps(getattr(p, "solvent_hits", []) or [], default=str)
        row["cannabinoids"] = json.dumps(getattr(p, "cannabinoids", {}) or {}, default=str)
        myc = getattr(p, "mold_yeast_cfu", None)
        row.update({
            "_coa_key": key,
            "_method": method or "",
            "_text_len": str(int(text_len or 0)),
            "_pdf_sha1": _sha1(pdf_path) if pdf_path else "",
            "_source_url": getattr(p, "report_url", "") or "",
            "_cached_at": _now(),
            "_schema": str(SCHEMA),
            "_mold_yeast_cfu": "" if myc is None else repr(myc),
            "_extra": json.dumps(extra or {}, default=str),
        })
        with self._lock:
            self._rows[key] = row
            self._dirty = True
            self._since_flush += 1
            due = self._since_flush >= self._FLUSH_EVERY
        if due:
            self.flush()                           # checkpoint a long build without losing progress

    def flush(self):
        """Atomically write the whole cache (.tmp + os.replace) — a crash mid-run never corrupts it."""
        with self._lock:
            if not self._dirty:
                return
            rows = list(self._rows.values())
        try:
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
                w.writeheader()
                for r in rows:
                    w.writerow({c: r.get(c, "") for c in COLUMNS})
            os.replace(tmp, self.path)
            with self._lock:
                self._dirty = False
                self._since_flush = 0
        except OSError:
            pass


# ------------------------------------------------------------------------------------------------
# Per-product wrapper (MISS path mirrors v4.read_pdf_text's pdfium->pdfplumber->OCR chain, but
# tracks which extractor won so provenance (_method) is exact).
def _extract_text_with_method(path):
    """Return (text, method). Resolves the engine functions as module globals so host overrides
    (offline, isolated OCR) apply. method in {pdfium, pdfplumber, ocr, none}."""
    text = v4._pdfium_text(path) or ""
    method = "pdfium"
    if v4._layout_broken(text):
        alt = v4._pdfplumber_text(path) or ""
        if alt and not v4._layout_broken(alt):
            text, method = alt, "pdfplumber"
    if len(text.strip()) < 40:
        ocr = v4.ocr_pdf(path) or ""
        if len(ocr.strip()) > len(text.strip()):
            text, method = ocr, "ocr"
    if len(text.strip()) < 40:
        method = "none"
    return text, method


def cached_process_product(p, session, watch, cache, allow_network=True):
    """HIT: rehydrate + reflag from CSV (no network, no OCR). MISS: download + read (incl. OCR) once,
    parse measurements, store them, and flag. Never raises — a per-COA failure returns p with a note."""
    row = cache.fresh_row(p)
    if row is not None:
        return cache.rehydrate(row, watch)
    if not allow_network:
        p.parse_note = "offline: COA not in CSV cache"
        return p
    try:
        path = v4.download_pdf(p, session)
        if not path:
            p.parse_note = p.parse_note or "could not download COA"
            return p
        text, method = _extract_text_with_method(path)
        if method == "none":
            p.parse_note = "no extractable text (scanned image?)"
            cache.put(p, method="none", text_len=len(text or ""), pdf_path=path)
            return p
        p.overall_result = v4.find_overall_result(text)
        p.test_lab = v4.parse_lab(text)
        v4.parse_analytes(text, p)
        v5.parse_cannabinoids(text, p)
        v4.apply_flags(p, text, watch)
        v5.apply_thc_flags(p)
        try:
            p.strain = v5.product_core_name(p)
        except Exception:
            p.strain = getattr(p, "strain", "") or ""
        cache.put(p, method=method, text_len=len(text), pdf_path=path)
        return p
    except Exception as e:
        p.parse_note = f"processing error: {type(e).__name__}: {e}"[:160]
        return p


# ------------------------------------------------------------------------------------------------
# Claude-prompt INPUT builders (for the dormant ENVIRONMENTAL_LINKAGE_SPEC / COMPLIANCE_SCREENING_SPEC
# blocks). Fills ONLY the COA-derived contaminant inputs from cache; grow-site / environmental inputs
# are intentionally left out of scope (matches the guardrails written into those specs).
def _measurement_lines(cache, products, watch, include_clean=False):
    out = []
    for p in products:
        row = cache.fresh_row(p)
        if row is None:
            continue
        rp = cache.rehydrate(row, watch)
        if not include_clean and not (rp.flags or rp.thc_flags):
            continue
        items = []
        for key, e in (rp.analytes or {}).items():
            if not isinstance(e, dict):
                continue
            if e.get("value") in (None, "") and not e.get("status"):
                continue
            amt = e.get("raw") or (f'{e.get("value")} {e.get("unit", "")}'.strip())
            items.append(f'{e.get("name", key)}={amt} [{e.get("status", "")}]'.strip())
        for h in (rp.solvent_hits or []):
            if isinstance(h, dict):
                items.append(f'{h.get("name", "solvent")}={h.get("value")} {h.get("unit", "ppm")}')
        line = (f'- {rp.product_name or rp.registration_number} '
                f'(producer={rp.producer}; lab={rp.test_lab}; date={rp.approval_date}; '
                f'COA={rp.report_url}): ' + ("; ".join(items) if items else "no numeric contaminant results"))
        if rp.flags:
            line += " | FLAGS: " + "; ".join(rp.flags)
        out.append(line)
    return out


def build_prompt_inputs(cache, products, watch, include_clean=False):
    """Just the COA-derived 'Contaminant results' data block (INPUT-2)."""
    lines = _measurement_lines(cache, products, watch, include_clean=include_clean)
    return "\n".join(lines) if lines else "(no cached COA contaminant results for the selected products)"


def build_prompt(spec, cache, products, watch, include_clean=False):
    """Render `spec` with its COA-derived contaminant INPUT-2 filled from cache. Other INPUTs
    (grow-site / environmental) are left as-is in the spec, out of scope by design."""
    data_block = build_prompt_inputs(cache, products, watch, include_clean=include_clean)
    marker = "{{COA_CONTAMINANT_RESULTS}}"
    if marker in spec:
        return spec.replace(marker, data_block)
    return spec.rstrip() + "\n\n# INPUT-2 — Contaminant results (from COA measurement cache)\n" + data_block
