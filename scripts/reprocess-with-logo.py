"""
Re-process all game issues:
1. Convert original.pdf -> clean WebP (no logo)
2. Overlay logo at fixed 140x24 pixels, bottom-right
"""
import os, subprocess, json, sys
from pathlib import Path
from PIL import Image

BASE = Path(r"c:\Users\foo\Downloads\soshageshin")
GAMES_DIR = BASE / "games"
LOGO_PATH = BASE / "testpy" / "unnamed (5).png"
CONVERT_SCRIPT = BASE / "scripts" / "convert-pdf.py"

LOGO_W = 140
LOGO_H = 24
MARGIN_X = 16
MARGIN_Y = 12

if not LOGO_PATH.exists():
    print(f"[ERROR] Logo not found: {LOGO_PATH}")
    sys.exit(1)

# Pre-resize logo to 140x24
logo_src = Image.open(LOGO_PATH).convert("RGBA")
logo_resized = logo_src.resize((LOGO_W, LOGO_H), Image.LANCZOS)


def overlay_webp(webp_path: Path):
    img = Image.open(webp_path).convert("RGBA")
    x = img.width - LOGO_W - MARGIN_X
    y = img.height - LOGO_H - MARGIN_Y
    img.paste(logo_resized, (x, y), logo_resized)
    img.convert("RGB").save(webp_path, "WEBP", quality=90)


# Find all issue directories with original.pdf
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
    print(f"Processing: {slug}/{date}...", end=" ", flush=True)

    # Step 1: Remove old WebP pages
    for old in out_dir.glob("page-*.webp"):
        old.unlink()

    # Step 2: Convert clean PDF -> WebP (no logo)
    result = subprocess.run(
        [sys.executable, str(CONVERT_SCRIPT), str(original_pdf), str(out_dir)],
        capture_output=True, text=True, cwd=str(BASE)
    )

    pages = sorted(out_dir.glob("page-*.webp"))
    if not pages:
        print("CONVERT FAILED")
        failed += 1
        continue

    # Step 3: Overlay 140x24 logo on each WebP page
    for p in pages:
        overlay_webp(p)

    # Step 4: Update meta.json pageCount
    meta_path = out_dir / "meta.json"
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        meta["pageCount"] = len(pages)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"OK ({len(pages)}p)")
    success += 1

print(f"\n{'='*50}")
print(f"Done: {success} OK, {failed} failed, {len(issues)} total")
