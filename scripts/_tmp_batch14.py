"""Batch 14: Convert 16 new PDFs, add logo, og-image, meta.json"""
import json, subprocess, sys
from PIL import Image
from pathlib import Path

BASE = Path(r"c:\Users\foo\Downloads\soshageshin")
PDF_DIR = Path(r"C:\Users\foo\Music\soshageshin-pdfs\pdf_add\out\pdf")
CONVERT = BASE / "scripts" / "convert-pdf.py"
LOGO = Image.open(BASE / "testpy" / "unnamed (5).png").convert("RGBA").resize((140, 24), Image.LANCZOS)

NEW_GAMES = [
    ("Call of Duty_ Mobile ユーザーが欲しい最新情報 2026-02-24.pdf",
     "cod-mobile", "2026-02-24", "Call of Duty: Mobile", "CoDモバイル最新アプデ＋攻略情報まとめ", ["FPS", "最新情報"]),
    ("Fortnite ユーザーが欲しい最新情報 2026-02-23.pdf",
     "fortnite", "2026-02-23", "フォートナイト", "フォートナイト最新アプデ＋攻略情報まとめ", ["バトルロイヤル", "最新情報"]),
    ("Identity V ユーザーが欲しい最新情報 2026-02-23.pdf",
     "identity-v", "2026-02-23", "第五人格", "第五人格最新アプデ＋攻略情報まとめ", ["非対称対戦", "最新情報"]),
    ("Minecraft ユーザーが欲しい最新情報 2026-02-23.pdf",
     "minecraft", "2026-02-23", "Minecraft", "Minecraft最新アプデ＋攻略情報まとめ", ["サンドボックス", "最新情報"]),
    ("Pokemon TCG Pocket ユーザーが欲しい最新情報 2026-02-23.pdf",
     "pokemon-tcg-pocket", "2026-02-23", "ポケモンTCGポケット", "ポケモンTCGポケット最新情報＋攻略まとめ", ["カードゲーム", "最新情報"]),
    ("VALORANT ユーザーが欲しい最新情報 2026-02-23.pdf",
     "valorant", "2026-02-23", "VALORANT", "VALORANT最新アプデ＋攻略情報まとめ", ["FPS", "最新情報"]),
    ("ブロスタ ユーザーが欲しい最新情報 2026-02-23.pdf",
     "brawl-stars", "2026-02-23", "ブロスタ", "ブロスタ最新アプデ＋攻略情報まとめ", ["アクション", "最新情報"]),
    ("プロ野球スピリッツA ユーザーが欲しい最新情報 2026-02-23.pdf",
     "prospi-a", "2026-02-23", "プロ野球スピリッツA", "プロスピA最新アプデ＋攻略情報まとめ", ["スポーツ", "最新情報"]),
    ("モバイル・レジェンド_ Bang Bang ユーザーが欲しい最新情報 2026-02-23.pdf",
     "mobile-legends", "2026-02-23", "モバイル・レジェンド", "モバレジェ最新アプデ＋攻略情報まとめ", ["MOBA", "最新情報"]),
    ("モンスターストライク ユーザーが欲しい最新情報 2026-02-23.pdf",
     "monster-strike", "2026-02-23", "モンスト", "モンスト最新アプデ＋攻略情報まとめ", ["アクションRPG", "最新情報"]),
    ("モンハンライズ：サンブレイク ユーザーが欲しい最新情報 2026-02-23.pdf",
     "mh-rise-sunbreak", "2026-02-23", "モンハンライズ：サンブレイク", "モンハンライズ：サンブレイク最新情報＋攻略まとめ", ["アクション", "最新情報"]),
    ("レインボーシックス モバイル：2026年グローバル展開の全貌.pdf",
     "rainbow-six-mobile", "2026-02-23", "レインボーシックス モバイル", "R6モバイル2026年グローバル展開＋最新情報", ["FPS", "最新情報"]),
    ("原神 ユーザーが欲しい最新情報 2026-02-23.pdf",
     "version64", "2026-02-23", "原神", "原神最新アプデ＋攻略情報まとめ", ["オープンワールド", "最新情報"]),
    ("大乱闘スマッシュブラザーズ SPECIAL ユーザーが欲しい最新情報 2026-02-23.pdf",
     "smash-bros-sp", "2026-02-23", "大乱闘スマッシュブラザーズ SPECIAL", "スマブラSP最新情報＋攻略まとめ", ["格闘アクション", "最新情報"]),
    ("荒野行動 ユーザーが欲しい最新情報 2026-02-23.pdf",
     "knives-out", "2026-02-23", "荒野行動", "荒野行動最新アプデ＋攻略情報まとめ", ["バトルロイヤル", "最新情報"]),
    ("雀魂 ユーザーが欲しい最新情報 2026-02-24.pdf",
     "mahjongsoul", "2026-02-24", "雀魂", "雀魂最新アプデ＋攻略情報まとめ", ["麻雀", "最新情報"]),
]

ok = 0
failed = 0

for pdf_name, slug, date, game_name, summary, tags in NEW_GAMES:
    issue_dir = BASE / "games" / slug / "issues" / date
    pdf_path = PDF_DIR / pdf_name

    if not pdf_path.exists():
        # Try to find by partial match
        matches = [p for p in PDF_DIR.iterdir() if slug.replace("-", " ") in p.name.lower() or game_name[:4] in p.name]
        if matches:
            pdf_path = matches[0]
        else:
            print(f"SKIP (not found): {pdf_name}")
            failed += 1
            continue

    print(f"Processing: {slug}/{date}...", end=" ", flush=True)

    # 1. Convert PDF to WebP
    r = subprocess.run(
        [sys.executable, str(CONVERT), str(pdf_path), str(issue_dir)],
        capture_output=True, text=True, cwd=str(BASE)
    )

    pages = sorted(issue_dir.glob("page-*.webp"))
    if not pages:
        print(f"CONVERT FAILED")
        failed += 1
        continue

    # 2. Write meta.json
    title = pdf_name.replace(".pdf", "").strip()
    meta = {
        "title": title,
        "game": game_name,
        "date": date,
        "pageCount": len(pages),
        "summary": summary,
        "tags": tags,
    }
    with open(issue_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # 3. Add 140x24 logo (bottom-right, 0 margin)
    for p in pages:
        img = Image.open(p).convert("RGBA")
        img.paste(LOGO, (img.width - 140, img.height - 24), LOGO)
        img.convert("RGB").save(p, "WEBP", quality=90)

    # 4. Generate og-image.jpg
    Image.open(issue_dir / "page-01.webp").convert("RGB").save(
        issue_dir / "og-image.jpg", "JPEG", quality=85
    )

    print(f"OK ({len(pages)}p)")
    ok += 1

print(f"\n{'='*50}")
print(f"Done: {ok} OK, {failed} failed")
