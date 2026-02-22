import json
from PIL import Image
from pathlib import Path

BASE = Path(r"c:\Users\foo\Downloads\soshageshin")
LOGO = Image.open(BASE / "testpy" / "unnamed (5).png").convert("RGBA").resize((140, 24), Image.LANCZOS)

games = [
    ("games/among-us/issues/2026-02-23", {
        "title": "Among Us 2026 最新ロードマップ＆攻略統計ガイド",
        "game": "Among Us",
        "date": "2026-02-23",
        "pageCount": 8,
        "summary": "Among Us 2026年最新ロードマップ＋攻略統計情報まとめ",
        "tags": ["マルチプレイ", "攻略ガイド", "最新情報"]
    }),
    ("games/apex-legends/issues/2026-02-23", {
        "title": "Apex Legends シーズン28 攻略・最新情報まとめ",
        "game": "Apex Legends",
        "date": "2026-02-23",
        "pageCount": 13,
        "summary": "Apex Legendsシーズン28攻略＋最新アプデ情報＋メタ分析",
        "tags": ["FPS", "バトルロイヤル", "攻略ガイド"]
    }),
    ("games/splatoon3/issues/2026-02-23", {
        "title": "スプラトゥーン3 攻略・最新アップデート完全ガイド",
        "game": "スプラトゥーン3",
        "date": "2026-02-23",
        "pageCount": 11,
        "summary": "スプラトゥーン3最新アプデ＋攻略完全ガイド＋新ステージ情報",
        "tags": ["シューター", "攻略ガイド", "最新情報"]
    }),
]

for issue_dir_rel, meta in games:
    issue_dir = BASE / issue_dir_rel

    # Write meta.json
    with open(issue_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # Add 140x24 logo
    pages = sorted(issue_dir.glob("page-*.webp"))
    for p in pages:
        img = Image.open(p).convert("RGBA")
        img.paste(LOGO, (img.width - 140, img.height - 24), LOGO)
        img.convert("RGB").save(p, "WEBP", quality=90)

    # Generate og-image.jpg
    Image.open(issue_dir / "page-01.webp").convert("RGB").save(
        issue_dir / "og-image.jpg", "JPEG", quality=85
    )

    print(f"OK: {issue_dir_rel} ({len(pages)}p)")

print("All done!")
