import json, subprocess, sys
from PIL import Image
from pathlib import Path

BASE = Path(r"c:\Users\foo\Downloads\soshageshin")
PDF_DIR = Path(r"C:\Users\foo\Music\soshageshin-pdfs\pdf_add\out\pdf")
CONVERT = BASE / "scripts" / "convert-pdf.py"
LOGO = Image.open(BASE / "testpy" / "unnamed (5).png").convert("RGBA").resize((140, 24), Image.LANCZOS)

NEW_GAMES = [
    ("splatoon2", "2026-02-25", "スプラトゥーン2", "スプラトゥーン2最新情報＋攻略まとめ", ["シューター", "最新情報"], "スプラトゥーン2"),
    ("gbo2", "2026-02-25", "バトオペ2", "バトオペ2攻略＋アップデート＋キャンペーン最新情報", ["アクション", "攻略ガイド"], "バトオペ2"),
]

for slug, date, game_name, summary, tags, search_key in NEW_GAMES:
    issue_dir = BASE / "games" / slug / "issues" / date
    pdf_path = [p for p in PDF_DIR.iterdir() if search_key in p.name]
    if not pdf_path:
        print(f"SKIP: {game_name} (PDF not found)")
        continue
    pdf_path = pdf_path[0]

    print(f"Processing: {slug}/{date}...", end=" ", flush=True)

    subprocess.run([sys.executable, str(CONVERT), str(pdf_path), str(issue_dir)],
                   capture_output=True, text=True, cwd=str(BASE))

    pages = sorted(issue_dir.glob("page-*.webp"))
    if not pages:
        print("CONVERT FAILED")
        continue

    title = pdf_path.stem
    with open(issue_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump({"title": title, "game": game_name, "date": date,
                   "pageCount": len(pages), "summary": summary, "tags": tags},
                  f, ensure_ascii=False, indent=2)

    for p in pages:
        img = Image.open(p).convert("RGBA")
        img.paste(LOGO, (img.width - 140, img.height - 24), LOGO)
        img.convert("RGB").save(p, "WEBP", quality=90)

    Image.open(issue_dir / "page-01.webp").convert("RGB").save(
        issue_dir / "og-image.jpg", "JPEG", quality=85)

    print(f"OK ({len(pages)}p)")

print("Done!")
