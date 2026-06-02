#!/usr/bin/env python3
"""
CannaScope OCR worker — runs ONE COA's OCR in an isolated subprocess.

CannaScope's main run launches this as a short-lived child process for each
scanned / image-only COA. If a native OCR engine (e.g. Apple Vision via ocrmac)
segfaults on a malformed image, only this child dies — the parent run catches the
non-zero exit and continues, treating that single COA as unreadable instead of
crashing the entire scan. This is what makes 100% coverage safe on very large runs.

Usage:  python cannascope_ocr_worker.py <pdf_path> [max_pages]
Prints the recognized text to stdout. Prints nothing and exits 0 if no OCR
backend is available; a crash/segfault exits non-zero (handled by the parent).
"""
import sys


def _backend():
    try:
        import ocrmac.ocrmac  # noqa: F401  (Apple Vision, macOS)
        return "ocrmac"
    except Exception:
        import shutil
        if shutil.which("tesseract"):
            try:
                import pytesseract  # noqa: F401
                return "tesseract"
            except Exception:
                return ""
    return ""


def main():
    if len(sys.argv) < 2:
        return
    path = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    backend = _backend()
    if not backend:
        return
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(path)
    out = []
    for i in range(min(len(doc), max_pages)):
        img = doc[i].render(scale=2.0).to_pil()
        if backend == "ocrmac":
            from ocrmac import ocrmac
            res = ocrmac.OCR(img).recognize()
            out.append("\n".join(r[0] for r in res))
        else:
            import pytesseract
            out.append(pytesseract.image_to_string(img.convert("L")))
    doc.close()
    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
