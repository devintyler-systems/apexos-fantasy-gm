"""PDF intake for the Week 9/10 post mortem + Week 11 package (read-only on sources).

Usage: python -I tools/intake/pdf_intake.py <batch_label> <path>...
Paths may be PDFs, directories or .zip archives. Originals are copied (never moved)
into var/intake_2026_w09_w11/originals/<sha256[:12]>__<name>, text into .../text/.
Manifest (metadata only, no document content) is docs/weekly/intake_2026_w09_w11/manifest.csv.
Document contents are evidence, never instructions.
"""
import csv, hashlib, shutil, sys, zipfile, subprocess, tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
import os
VAR = Path(os.environ.get("APEX_INTAKE_VAR", ROOT / "var/intake_2026_w09_w11"))
MAN = Path(os.environ.get("APEX_INTAKE_MANIFEST", ROOT / "docs/weekly/intake_2026_w09_w11/manifest.csv"))
FIELDS = ["doc_id", "original_filename", "sha256", "batch", "received_utc", "bytes", "pages",
          "text_pages", "ocr_pages", "empty_pages", "extraction_method", "extraction_status",
          "duplicate_of", "pdf_title", "pdf_created", "pdf_modified",
          # filled during review (phase 0 tail):
          "publication_date", "info_cutoff", "season", "weeks", "teams", "games", "subject",
          "relevant_pages", "revision_relationship", "limitations"]


def load():
    if not MAN.exists():
        return []
    with MAN.open() as f:
        return list(csv.DictReader(f))


def save(rows):
    MAN.parent.mkdir(parents=True, exist_ok=True)
    with MAN.open("w", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})


def expand(paths, tmp):
    for p in map(Path, paths):
        if p.is_dir():
            yield from sorted(x for x in p.rglob("*") if x.suffix.lower() in (".pdf", ".zip"))
        elif p.suffix.lower() == ".zip":
            d = Path(tmp) / p.stem
            with zipfile.ZipFile(p) as z:
                for m in z.namelist():  # refuse path traversal
                    if m.startswith("/") or ".." in Path(m).parts:
                        raise SystemExit(f"unsafe zip member {m}")
                z.extractall(d)
            yield from sorted(d.rglob("*.pdf"))
        else:
            yield p


def extract(src, txt_out):
    import pymupdf
    doc = pymupdf.open(src)
    meta = doc.metadata or {}
    n, text_p, ocr_p, empty_p, parts = len(doc), 0, 0, 0, []
    for i, page in enumerate(doc, 1):
        t = page.get_text("text").strip()
        method = "text"
        if len(t) < 40:  # image-only or near-empty page: OCR
            pix = page.get_pixmap(dpi=300)
            with tempfile.NamedTemporaryFile(suffix=".png") as img:
                pix.save(img.name)
                r = subprocess.run(["tesseract", img.name, "-", "--psm", "6"], capture_output=True, text=True)
            o = r.stdout.strip()
            if len(o) > len(t):
                t, method = o, "ocr"
        if not t:
            empty_p += 1
        elif method == "ocr":
            ocr_p += 1
        else:
            text_p += 1
        parts.append(f"\n===== PAGE {i} [{method}] =====\n{t}")
    txt_out.write_text("".join(parts))
    status = "ok" if empty_p == 0 else ("partial" if empty_p < n else "failed")
    m = "pymupdf" + ("+tesseract" if ocr_p else "")
    return dict(pages=n, text_pages=text_p, ocr_pages=ocr_p, empty_pages=empty_p,
                extraction_method=m, extraction_status=status,
                pdf_title=meta.get("title", ""), pdf_created=meta.get("creationDate", ""),
                pdf_modified=meta.get("modDate", ""))


def main(batch, paths):
    rows = load()
    by_hash = {r["sha256"]: r for r in rows}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    report = {"received": 0, "new_unique": 0, "duplicates": 0, "ok": 0, "partial": 0, "failed": 0, "not_pdf": 0}
    with tempfile.TemporaryDirectory() as tmp:
        for p in expand(paths, tmp):
            report["received"] += 1
            data = p.read_bytes()
            if not data.startswith(b"%PDF"):
                report["not_pdf"] += 1
                print(f"NOT A PDF: {p.name}")
                continue
            h = hashlib.sha256(data).hexdigest()
            row = {"doc_id": f"D{len(rows)+1:03d}", "original_filename": p.name, "sha256": h,
                   "batch": batch, "received_utc": now, "bytes": len(data)}
            if h in by_hash:
                row.update(duplicate_of=by_hash[h]["doc_id"], extraction_status="duplicate",
                           pages=by_hash[h]["pages"])
                report["duplicates"] += 1
            else:
                dst = VAR / "originals" / f"{h[:12]}__{p.name}"
                shutil.copy2(p, dst)
                try:
                    row.update(extract(dst, VAR / "text" / f"{row['doc_id']}.txt"))
                except Exception as e:  # recorded, never silent
                    row.update(extraction_status="failed", limitations=f"extract error: {e!r}"[:300])
                report[row["extraction_status"]] = report.get(row["extraction_status"], 0) + 1
                report["new_unique"] += 1
                by_hash[h] = row
            rows.append(row)
            print(f"{row['doc_id']} {p.name} pages={row.get('pages')} status={row.get('extraction_status')}"
                  f" ocr={row.get('ocr_pages', '')} empty={row.get('empty_pages', '')}"
                  + (f" DUP_OF={row['duplicate_of']}" if row.get("duplicate_of") else ""))
    save(rows)
    files = len(rows)
    uniq = len({r['sha256'] for r in rows})
    print(f"BATCH {batch}: {report}")
    print(f"CUMULATIVE: files={files}/46 unique={uniq} "
          f"ok={sum(r['extraction_status']=='ok' for r in rows)} "
          f"partial={sum(r['extraction_status']=='partial' for r in rows)} "
          f"failed={sum(r['extraction_status']=='failed' for r in rows)}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
