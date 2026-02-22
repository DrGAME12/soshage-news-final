"""Convert batch 11: all new PDFs from pdf_add/out/pdf folder."""
import subprocess, os, json, re, time

BASE = r"c:\Users\foo\Downloads\soshageshin"
PDF_DIR = r"C:\Users\foo\Music\soshageshin-pdfs\pdf_add\out\pdf"
CONVERT_SCRIPT = os.path.join(BASE, "scripts", "convert-pdf.py")

def slugify(name):
    """Generate a URL-friendly slug from a game name."""
    # Remove common suffixes
    name = re.sub(r'\s*ユーザーが欲しい最新情報.*$', '', name)
    name = re.sub(r'\s*\d{4}-\d{2}-\d{2}$', '', name)
    name = name.strip()
    # Transliterate common Japanese game names
    slug_map = {
        "2XKO": "2xko",
        "AYANEO NEXT 2": "ayaneo-next-2",
        "Elysia_ アストラルフォール": "elysia-astral-fall",
        "Necesse_ ネセス": "necesse",
        "unVEIL the world（アンベイル ザ ワールド）": "unveil-the-world",
        "ぽこ あ ポケモン": "poko-a-pokemon",
        "ウルトラマン パズルシュワッチ!!": "ultraman-puzzle",
        "エスターバニーポップガール": "ester-bunny-pop-girl",
        "ステラソラ": "stellasola",
        "トリッカル・もちもちほっペ大作戦": "trickle-mochimochi",
        "ブラウザ三国志 天": "browser-sangoku-ten",
        "ブレイブ フロンティア バーサス": "brave-frontier-versus",
        "メンヘラカノジョ": "menhera-kanojo",
        "ルミナ・アークの最弱無双": "lumina-arc",
        "ワールドウィッチーズX": "world-witches-x",
        "思い出のラーメン食堂　～心にしみる昭和シリーズ～": "ramen-shokudo",
        "龍が如く 極3": "yakuza-kiwami-3",
    }
    return slug_map.get(name, re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-'))

def extract_date(filename):
    """Extract date from filename like '... 2026-02-22.pdf'."""
    m = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    return m.group(1) if m else "2026-02-22"

def extract_game_name(filename):
    """Extract clean game name from filename."""
    name = filename.replace('.pdf', '')
    name = re.sub(r'\s*ユーザーが欲しい最新情報.*$', '', name)
    name = re.sub(r'\s*\d{4}-\d{2}-\d{2}$', '', name)
    return name.strip()

# Meta info for each game
GAME_META = {
    "2xko": {
        "game_jp": "2XKO",
        "game_en": "2XKO",
        "genre": "格闘ゲーム",
        "summary": "2XKO最新情報＋ゲームシステム＋キャラクター情報まとめ",
        "tags": ["格闘", "新作", "最新情報"],
    },
    "ayaneo-next-2": {
        "game_jp": "AYANEO NEXT 2",
        "game_en": "AYANEO NEXT 2",
        "genre": "ゲーミングデバイス",
        "summary": "AYANEO NEXT 2最新スペック＋レビュー＋発売情報",
        "tags": ["ハードウェア", "携帯ゲーム機", "最新情報"],
    },
    "elysia-astral-fall": {
        "game_jp": "Elysia アストラルフォール",
        "game_en": "Elysia Astral Fall",
        "genre": "RPG",
        "summary": "Elysiaアストラルフォール最新情報＋ゲームシステム＋事前登録情報",
        "tags": ["RPG", "新作", "最新情報"],
    },
    "necesse": {
        "game_jp": "Necesse ネセス",
        "game_en": "Necesse",
        "genre": "サバイバルサンドボックス",
        "summary": "Necesse最新アップデート＋攻略＋ゲーム情報まとめ",
        "tags": ["サンドボックス", "サバイバル", "最新情報"],
    },
    "unveil-the-world": {
        "game_jp": "unVEIL the world",
        "game_en": "unVEIL the world",
        "genre": "RPG",
        "summary": "unVEIL the world最新情報＋世界観＋ゲームシステムまとめ",
        "tags": ["RPG", "新作", "最新情報"],
    },
    "poko-a-pokemon": {
        "game_jp": "ぽこ あ ポケモン",
        "game_en": "Poko a Pokemon",
        "genre": "パズル",
        "summary": "ぽこあポケモン最新情報＋攻略＋イベントまとめ",
        "tags": ["パズル", "ポケモン", "最新情報"],
    },
    "ultraman-puzzle": {
        "game_jp": "ウルトラマン パズルシュワッチ!!",
        "game_en": "Ultraman Puzzle Schwach",
        "genre": "パズル",
        "summary": "ウルトラマンパズルシュワッチ最新情報＋攻略＋イベントまとめ",
        "tags": ["パズル", "ウルトラマン", "最新情報"],
    },
    "ester-bunny-pop-girl": {
        "game_jp": "エスターバニーポップガール",
        "game_en": "Ester Bunny Pop Girl",
        "genre": "カジュアル",
        "summary": "エスターバニーポップガール最新情報＋攻略まとめ",
        "tags": ["カジュアル", "新作", "最新情報"],
    },
    "stellasola": {
        "game_jp": "ステラソラ",
        "game_en": "StellaSola",
        "genre": "RPG",
        "summary": "ステラソラ最新アップデート＋攻略＋イベント情報まとめ",
        "tags": ["RPG", "攻略", "最新情報"],
    },
    "trickle-mochimochi": {
        "game_jp": "トリッカル・もちもちほっペ大作戦",
        "game_en": "Trickle Mochimochi",
        "genre": "カジュアル",
        "summary": "トリッカルもちもちほっペ大作戦最新情報＋攻略まとめ",
        "tags": ["カジュアル", "新作", "最新情報"],
    },
    "browser-sangoku-ten": {
        "game_jp": "ブラウザ三国志 天",
        "game_en": "Browser Sangokushi Ten",
        "genre": "ストラテジー",
        "summary": "ブラウザ三国志天最新情報＋攻略＋アップデートまとめ",
        "tags": ["ストラテジー", "三国志", "最新情報"],
    },
    "brave-frontier-versus": {
        "game_jp": "ブレイブ フロンティア バーサス",
        "game_en": "Brave Frontier Versus",
        "genre": "RPG",
        "summary": "ブレイブフロンティアバーサス最新情報＋攻略＋イベントまとめ",
        "tags": ["RPG", "対戦", "最新情報"],
    },
    "menhera-kanojo": {
        "game_jp": "メンヘラカノジョ",
        "game_en": "Menhera Kanojo",
        "genre": "ADV",
        "summary": "メンヘラカノジョ最新情報＋攻略＋ストーリーまとめ",
        "tags": ["ADV", "恋愛", "最新情報"],
    },
    "lumina-arc": {
        "game_jp": "ルミナ・アークの最弱無双",
        "game_en": "Lumina Arc",
        "genre": "RPG",
        "summary": "ルミナ・アーク最弱無双最新情報＋攻略＋キャラクター情報まとめ",
        "tags": ["RPG", "ファンタジー", "最新情報"],
    },
    "world-witches-x": {
        "game_jp": "ワールドウィッチーズX",
        "game_en": "World Witches X",
        "genre": "アクション",
        "summary": "ワールドウィッチーズX最新情報＋攻略＋イベントまとめ",
        "tags": ["アクション", "シューティング", "最新情報"],
    },
    "ramen-shokudo": {
        "game_jp": "思い出のラーメン食堂",
        "game_en": "Ramen Shokudo",
        "genre": "シミュレーション",
        "summary": "思い出のラーメン食堂最新情報＋攻略＋レシピまとめ",
        "tags": ["シミュレーション", "経営", "最新情報"],
    },
    "yakuza-kiwami-3": {
        "game_jp": "龍が如く 極3",
        "game_en": "Yakuza Kiwami 3",
        "genre": "アクションADV",
        "summary": "龍が如く極3最新情報＋攻略＋新要素まとめ",
        "tags": ["アクション", "ADV", "最新情報"],
    },
}

# ═══════════ MAIN ═══════════
print("=" * 60)
print(f"Processing {len(os.listdir(PDF_DIR))} PDFs from: {PDF_DIR}")
print("=" * 60)

success = 0
total = 0
for filename in sorted(os.listdir(PDF_DIR)):
    if not filename.endswith('.pdf'):
        continue
    total += 1
    pdf_path = os.path.join(PDF_DIR, filename)
    game_name = extract_game_name(filename)
    slug = slugify(game_name)
    date = extract_date(filename)

    out_dir = os.path.join(BASE, "games", slug, "issues", date)

    # Skip if already converted
    if os.path.exists(os.path.join(out_dir, "page-01.webp")):
        print(f"SKIP (done): {slug}")
        success += 1
        continue

    print(f"Converting: {slug} ({game_name})...", end=" ", flush=True)
    os.makedirs(out_dir, exist_ok=True)

    result = subprocess.run(
        ["python", CONVERT_SCRIPT, pdf_path, out_dir],
        capture_output=True, text=True, cwd=BASE
    )
    if result.returncode != 0:
        print(f"FAILED\n  {result.stderr[:200]}")
        continue

    pages = len([f for f in os.listdir(out_dir)
                 if f.startswith("page-") and f.endswith(".webp")])
    if pages > 0:
        meta_info = GAME_META.get(slug, {})
        meta = {
            "title": f"{game_name} 最新情報",
            "game": meta_info.get("game_jp", game_name),
            "date": date,
            "codename": "",
            "pageCount": pages,
            "summary": meta_info.get("summary", f"{game_name}の最新情報まとめ"),
            "tags": meta_info.get("tags", ["最新情報"])
        }
        with open(os.path.join(out_dir, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        print(f"OK ({pages}p)")
        success += 1
    else:
        print("FAILED (0 pages)")

print(f"\nConverted: {success}/{total}")

# ═══════════ Regenerate site ═══════════
print("\n" + "=" * 60)
print("Regenerating site...")
print("=" * 60)
result = subprocess.run(
    ["python", os.path.join(BASE, "scripts", "generate-site.py")],
    capture_output=True, text=True, cwd=BASE
)
for line in result.stdout.strip().split('\n')[-10:]:
    print(line)
if result.returncode != 0:
    print("STDERR:", result.stderr[:500])

# ═══════════ Add gtag to new HTMLs ═══════════
print("\n" + "=" * 60)
print("Adding gtag to new HTML files...")
print("=" * 60)
result = subprocess.run(
    ["python", os.path.join(BASE, "scripts", "add_gtag.py")],
    capture_output=True, text=True, cwd=BASE
)
# Count updated
updated = result.stdout.count("Updated:")
skipped = result.stdout.count("SKIP")
print(f"gtag: {updated} updated, {skipped} already had gtag")

print("\nAll done!")
