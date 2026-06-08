#!/usr/bin/env python3
"""Data-integrity regression for multi-product COA handling — the per-PDF block cache, ranked
identifier matching, isolate-or-suppress, and source-audit block binding (cannascope_ct_v17_src).

Proves the requirements:
  - a 10+ product COA returns ALL products, not just the first;
  - a shared COA URL never assigns product A's values to product B;
  - failing microbial values from the first product are not pinned to unrelated products;
  - single-product COAs still work normally;
  - ambiguous multi-product matches are routed to manual review (suppressed);
  - cache hits preserve the same per-product isolation as fresh parses;
  - the source audit confirms a flagged value came from the MATCHED block, not the shared PDF.

Run:  python3 _test_multiproduct_cache.py
"""
import os
import sys
import tempfile

import cannascope_multiproduct as mp
import cannascope_ct_v4 as v4
import cannascope_ct_v5 as v5
import cannascope_ct_v17_src as cc

# Isolate the multi-product cache to a temp file so the test never touches the real cache.
cc.MULTIPRODUCT_PDF_CACHE = os.path.join(tempfile.gettempdir(), "_test_mp_cache.json")
try:
    os.remove(cc.MULTIPRODUCT_PDF_CACHE)
except OSError:
    pass
cc._MP_CACHE = None

WATCH = 80.0
_fails = []


def check(cond, msg):
    print(("ok  " if cond else "FAIL") + "  " + msg)
    if not cond:
        _fails.append(msg)


def _page(n, N, prod, labid, aer, tym, res, reg=""):
    reg_line = f"Registration: {reg}\n" if reg else ""
    return (f"Northeast Laboratories, Inc.\nAnalytical Report\nDate Tested: 7/08/2015\n"
            f"Laboratory Report#:\nN1600000\nReport Date: 7/14/2015\nPage {n} of {N}\n"
            f"Report To:\nConnecticut Pharmaceutical Solutions\nSample Site:\nLaboratory ID #:\n{labid}\n"
            f"{reg_line}Product Description:\n{prod}\n"
            f"Total Aerobic Microbial Count: {aer} per gram {res}\n"
            f"Total Yeast & Mold Count: {tym} per gram {res}\n"
            f"Recommended Limits *\n100,000\n10,000\n")


# 11 distinct products; product 0 (Blue Dream) FAILS microbials, the rest pass with unique values.
STRAINS = ["Blue Dream", "OG Kush", "Sour Diesel", "Gelato", "Wedding Cake", "GSC",
           "Runtz", "Zkittlez", "Jack Herer", "Durban", "Haze"]
N = len(STRAINS)
PAGES = []
for i, s in enumerate(STRAINS):
    reg = "MMBR.0090007" if i == 6 else ""   # give product 6 (Runtz) a registration number
    PAGES.append(_page(i + 1, N, s, f"1600000-{i + 1:02d}",
                       "3,500,000" if i == 0 else f"{1000 + i * 111}",
                       "3,000,000" if i == 0 else f"{900 + i * 97}",
                       "FAIL" if i == 0 else "PASS", reg=reg))
DOC = "\n".join(PAGES)
URL = "http://example.test/shared-multiproduct.pdf"


def _newp(name="", reg="", url=URL):
    p = v5.ProductV5()
    p.product_name = name
    p.registration_number = reg
    p.report_url = url
    p.analytes = {}
    p.cannabinoids = {}
    return p


# ---- 1. a 10+ product COA returns ALL products ----
recs, key = cc._blocks_for_pdf("", DOC, URL, WATCH)
check(len(recs) == 11, f"10+ product COA returns all 11 blocks (got {len(recs)})")
descs = {r["product_description"] for r in recs}
check("Blue Dream" in descs and "Haze" in descs, "first AND last product both present (not just the first)")

# each block carries its own structured measurements
blue = next(r for r in recs if r["product_description"] == "Blue Dream")
ogk = next(r for r in recs if r["product_description"] == "OG Kush")
check(blue["analytes"].get("tymc", {}).get("value") == 3000000.0, "Blue Dream block has its own FAIL Y&M (3,000,000)")
check(ogk["analytes"].get("tymc", {}).get("value") == 997.0, "OG Kush block has its own passing Y&M (997)")

# ---- 2 & 3. shared URL: A's failing values never land on B ----
pB = _newp("OG Kush")
blk, conf, reason, strat = mp.match_block(recs, product_name="OG Kush")
check(blk is not None and conf >= cc.MULTIPRODUCT_MIN_CONF, "OG Kush matches its block")
cc._apply_block_record(pB, blk, WATCH)
check(pB.analytes.get("tymc", {}).get("value") == 997.0, "OG Kush record gets OG Kush's Y&M (997)")
check(pB.mold_yeast_cfu != 3000000.0, "Blue Dream's FAILING Y&M (3,000,000) is NOT pinned to OG Kush")
check(pB.analytes.get("aerobic", {}).get("value") == 1111.0 and pB.analytes.get("aerobic", {}).get("value") != 3500000.0,
      "OG Kush aerobic is its own (1111), not Blue Dream's 3,500,000")

# ---- 4. single-product COA still works (n_products <= 1 -> whole doc) ----
single = ("ACME Labs COA\nProduct: Granddaddy Purple Flower\n"
          "Total Yeast & Mold: 1,500 CFU/g PASS\nLead: <0.1 ppm PASS\n")
srecs, _ = cc._blocks_for_pdf("", single, "http://example.test/single.pdf", WATCH)
sblk, sconf, sreason, _ = mp.match_block(srecs, product_name="Granddaddy Purple Flower")
# single-doc: analyze yields <=1 product; isolate_product returns whole doc
wtext, wconf, _ = mp.isolate_product(text=single, target_name="Granddaddy Purple Flower")
check(wtext == single and wconf == 1.0, "single-product COA parses the whole document (not suppressed)")

# ---- 5. ambiguous multi-product -> routed to manual review (suppress) ----
twins = "\n".join([_page(1, 2, "Mystery Strain", "1700000-01", "5,000", "5,000", "PASS"),
                   _page(2, 2, "Mystery Strain", "1700000-02", "6,000", "6,000", "PASS")])
trecs, _ = cc._blocks_for_pdf("", twins, "http://example.test/twins.pdf", WATCH)
tblk, tconf, treason, _ = mp.match_block(trecs, product_name="Mystery Strain")
check(tblk is None, "two same-named blocks -> ambiguous -> no match (route to manual review)")
check("multiple blocks" in treason or "ambiguous" in treason, "ambiguous match explains why")

# ---- registration-number matching (strong identifier) ----
rblk, rconf, rreason, rstrat = mp.match_block(recs, registration_number="MMBR.0090007", product_name="WRONG NAME")
check(rblk is not None and rblk["product_description"] == "Runtz" and rstrat == "registration_number",
      "registration number matches the right block even if the name is wrong")

# ---- 6. cache hits preserve per-product isolation ----
recs2, key2 = cc._blocks_for_pdf("", DOC, URL, WATCH)   # second call -> cache hit
check(key2 == key and key in cc._mp_cache_load(), "second read is a cache hit (same key, present in cache)")
check(len(recs2) == 11, "cache hit still returns all 11 blocks")
pB2 = _newp("OG Kush")
blk2, c2, _, _ = mp.match_block(recs2, product_name="OG Kush")
cc._apply_block_record(pB2, blk2, WATCH)
check(pB2.analytes.get("tymc", {}).get("value") == 997.0 and pB2.mold_yeast_cfu != 3000000.0,
      "cache-hit isolation matches fresh isolation (OG Kush still 997, not Blue Dream's 3,000,000)")

# ---- 7. source audit binds to the MATCHED block, not the shared PDF ----
# Blue Dream's failing value (3,000,000) IS in the shared PDF but must NOT verify against OG Kush's block.
check(cc._value_in_coa_text(997.0, blk["text"]) is True, "OG Kush value verifies against OG Kush's block text")
check(cc._value_in_coa_text(3000000.0, blk["text"]) is False,
      "Blue Dream's FAIL value does NOT verify against OG Kush's block (no cross-attribution in audit)")
check(cc._value_in_coa_text(3000000.0, DOC) is True,
      "...even though that value IS present elsewhere in the shared PDF (proves block-binding matters)")
# the binding helper recovers a block's text by id (cache-rehydrated path)
bt = cc._block_text_for(key, ogk["block_id"], DOC)
check("OG Kush" in bt and "3,500,000" not in bt, "_block_text_for returns ONLY the matched block's text")

print()
if _fails:
    print(f"{len(_fails)} FAILED")
    sys.exit(1)
print("ALL PASSED")
