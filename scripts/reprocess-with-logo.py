"""
Re-process all game issues: overlay logo on original PDFs, then convert to WebP.
Uses the testpy/overlay_logo_on_pdfs.py approach (PDF-level overlay with PyMuPDF).
"""
import os, subprocess, json, shutil, tempfile, sys
from pathlib import Path

BASE = Path(r"c:\Users\foo\Downloads\soshageshin")
GAMES_DIR = BASE / "games"
LOGO = BASE / "testpy" / "unnamed (5).png"
CONVERT_SCRIPT = BASE / "scripts" / "convert-pdf.py"
OVERLAY_SCRIPT = BASE / "testpy" / "overlay_logo_on_pdfs.py"

if not LOGO.exists():
    print(f"[ERROR] Logo not found: {LOGO}")
    sys.exit(1)

# Find all issue directories that have an original.pdf
issues = []
for game_dir in sorted(GAMES_DIR.iterdir()):
    if not game_dir.is_dir():
        continue
    issues_dir = game_dir / "issues"
    if not issues_dir.is_dir():
        continue
    for date_dir in sorted(issues_dir.iterdir()):
        if not date_dir.is_dir():
            continue
        original_pdf = date_dir / "original.pdf"
        if original_pdf.exists():
            issues.append((game_dir.name, date_dir.name, date_dir, original_pdf))

print(f"Found {len(issues)} issues with original.pdf")

success = 0
failed = 0

for slug, date, out_dir, original_pdf in issues:
    print(f"\nProcessing: {slug}/{date}...", end=" ", flush=True)

    # Step 1: Create temp dir for logo-overlaid PDF
    with tempfile.TemporaryDirectory() as tmp:
        tmp_in = Path(tmp) / "in"
        tmp_out = Path(tmp) / "out"
        tmp_in.mkdir()
        tmp_out.mkdir()

        # Copy original PDF to temp input dir
        shutil.copy2(original_pdf, tmp_in / "doc.pdf")

        # Step 2: Overlay logo onto PDF using testpy approach
        result = subprocess.run(
            [
                sys.executable, str(OVERLAY_SCRIPT),
                "--input-dir", str(tmp_in),
                "--output-dir", str(tmp_out),
                "--logo", str(LOGO),
                "--width-ratio", "0.135",
                "--margin-x-ratio", "0.018",
                "--margin-y-ratio", "0.015",
                "--erase-under",
                "--erase-color", "#ffffff",
            ],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"OVERLAY FAILED: {result.stderr[:200]}")
            failed += 1
            continue

        logo_pdf = tmp_out / "doc.pdf"
        if not logo_pdf.exists():
            print("OVERLAY FAILED (no output)")
            failed += 1
            continue

        # Step 3: Remove old WebP pages
        for old_webp in out_dir.glob("page-*.webp"):
            old_webp.unlink()

        # Step 4: Convert logo-overlaid PDF to WebP
        result = subprocess.run(
            [sys.executable, str(CONVERT_SCRIPT), str(logo_pdf), str(out_dir)],
            capture_output=True, text=True, cwd=str(BASE)
        )

        pages = len(list(out_dir.glob("page-*.webp")))
        if pages > 0:
            # Update pageCount in meta.json
            meta_path = out_dir / "meta.json"
            if meta_path.exists():
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                meta["pageCount"] = pages
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(meta, f, ensure_ascii=False, indent=2)
            print(f"OK ({pages}p)")
            success += 1
        else:
            print("CONVERT FAILED (0 pages)")
            failed += 1

print(f"\n{'='*50}")
print(f"Done: {success} OK, {failed} failed, {len(issues)} total")
