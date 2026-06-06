# CannaScope CT V16.3.4

**Multi-product COA data integrity: parse once, cache every product block separately, never
cross-attribute.** A COA PDF is never assumed to be one product. This release turns multi-product
handling into a structured, cached, per-product pipeline with audited block-level isolation.

## Core requirement (met)
For every COA PDF:
1. **Detect** whether it holds one product or many.
2. **Split** a multi-product document into separate per-product blocks.
3. **Match** each registry record to the single block that uniquely matches it, by strongest
   identifier first: **Laboratory ID → registration number (MMBR) → sample ID → batch → product
   description → unique unit marker**.
4. If a record **cannot** be uniquely matched, do not guess — **suppress the finding and route it to
   “COA Needs Manual Review.”**
5. **Never** cross-attribute microbials, potency, contaminants, or pass/fail from one block to another
   product that merely shares the same PDF URL.

## Parse once, cache per product block
A multi-product PDF is read **once**. Each product block is extracted with its **own identifiers**
(lab ID, sample ID, batch, product description/name, registration numbers, test date) **and its own
measurements** (cannabinoids, microbials, pesticides, heavy metals, solvents, pass/fail, mold/yeast
CFU), then cached as a structured list keyed by the **PDF content hash** (`Multi-Product COA Cache.json`,
modeled on the existing content-hash caches). Every registry record sharing that PDF reuses its matched
block from cache — **faster on future runs without losing per-product separation.**

A strong identifier that matches more than one block is treated as **ambiguous and fails** (no fallback
to a weaker heuristic that could pick the wrong product).

## Source audit binds to the matched block
The COA source audit now re-verifies every published flagged value against **its own product block’s
text**, not merely “somewhere in the shared PDF.” New metric
`multi_product_rows_verified_against_matched_block`; the binding survives cache rehydration via the
stored block id. This is the proof that no value was lifted from a different product in the same document.

## Safety & scope
- Engages **only** when 2+ resolvable product blocks exist — ordinary single-product COAs (even ones
  that merely mention two registration numbers) are never suppressed.
- **Cache hits preserve the same per-product isolation as fresh parses.**
- Only cold/online reads are affected; cache-path runs are byte-identical (the multi-product path is
  dormant on cache hits — verified across an all-time offline run: 33,688 reviewed / 3,041 published
  unchanged, self-audit 0, source audit re-verified all 1,691 flagged values).
- `ANALYSIS_VERSION` → 16.3.4 (legacy-clean ledger entries re-evaluate under the new rules).
- The OCR page cap fixed in 16.3.3 (read the whole document, bounded to 40 pages) is retained.

## Tests
- `_test_multiproduct.py` (19 checks) and `_test_multiproduct_cache.py` (19 data-integrity checks,
  including an **11-product** COA) prove: all products returned (not just the first); a shared URL never
  assigns A’s values to B; the first product’s failing microbials are not pinned to others;
  single-product COAs still work; ambiguous matches route to manual review; cache hits preserve
  isolation; and the audit confirms each value came from the matched block.
- `_test_report_integrity.py` passes.

## Note for operators
The bundled offline COA cache should be **rebuilt online** (`build-cache`) so any multi-product records
that were cached by the older single-product parser are re-extracted under the new per-block logic. The
mechanism takes effect immediately on cold/online reads.

All prior releases remain live.
