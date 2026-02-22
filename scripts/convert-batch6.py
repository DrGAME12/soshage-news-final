"""Convert batch 6 new PDFs + download icons + regenerate site."""
import subprocess, os, json, ssl, urllib.request, re, time

BASE = r"c:\Users\foo\Downloads\soshageshin"
CONVERT_SCRIPT = os.path.join(BASE, "scripts", "convert-pdf.py")

NEW_PDFS = {
    "DBレジェンズ：新レアリティLEGENDと超ベジット参戦.pdf": {
        "slug": "db-legends",
        "date": "2026-02-15",
        "meta": {
            "title": "DBレジェンズ LEGEND実装＆超ベジット参戦",
            "game": "ドラゴンボール レジェンズ",
            "date": "2026-02-15",
            "codename": "Operation Saiyan Legend",
            "summary": "新レアリティLEGEND実装＋超ベジット参戦＋最新メタ環境分析",
            "tags": ["アクションRPG", "新キャラ", "新レアリティ"]
        },
        "package": "com.bandainamcoent.dblegends_ww"
    },
    "Gジェネエターナル：2026年2月最新攻略ガイド.pdf": {
        "slug": "ggene-eternal",
        "date": "2026-02-15",
        "meta": {
            "title": "Gジェネエターナル 2月最新攻略ガイド",
            "game": "SDガンダム Gジェネレーション エターナル",
            "date": "2026-02-15",
            "codename": "Operation Eternal Blaze",
            "summary": "Gジェネエターナル2月攻略＋新MSユニット評価＋おすすめ編成",
            "tags": ["シミュレーションRPG", "攻略ガイド", "新ユニット"]
        },
        "package": "com.bandainamcoent.gaboratory"
    },
    "ウマ娘5周年記念キャンペーン：最新アップデート情報集.pdf": {
        "slug": "umamusume",
        "date": "2026-02-15",
        "meta": {
            "title": "ウマ娘 5周年記念キャンペーン情報集",
            "game": "ウマ娘 プリティーダービー",
            "date": "2026-02-15",
            "codename": "Operation Derby Crown",
            "summary": "ウマ娘5周年記念キャンペーン全情報＋最新アプデ＋無料ガチャ情報",
            "tags": ["育成シミュレーション", "周年記念", "キャンペーン"]
        },
        "package": "jp.co.cygames.umamusume"
    },
    "プロスピA：7000万DL福袋と攻略必勝ガイド.pdf": {
        "slug": "prospi-a",
        "date": "2026-02-15",
        "meta": {
            "title": "プロスピA 7000万DL福袋＆必勝攻略",
            "game": "プロ野球スピリッツA",
            "date": "2026-02-15",
            "codename": "Operation Grand Slam",
            "summary": "プロスピA 7000万DL記念福袋＋攻略必勝ガイド＋おすすめ選手評価",
            "tags": ["スポーツ", "記念イベント", "攻略ガイド"]
        },
        "package": "jp.konami.prospia"
    },
    "ホワサバ：3周年と2月最新イベント攻略ガイド.pdf": {
        "slug": "whiteout-survival",
        "date": "2026-02-15",
        "meta": {
            "title": "ホワサバ 3周年＆2月イベント攻略",
            "game": "ホワイトアウト・サバイバル",
            "date": "2026-02-15",
            "codename": "Operation Frozen Frontier",
            "summary": "ホワイトアウト・サバイバル3周年記念＋2月最新イベント攻略ガイド",
            "tags": ["ストラテジー", "周年記念", "攻略ガイド"]
        },
        "package": "com.gof.global"
    },
    "荒野行動：2026年2月最新アップデートと感謝祭の全貌.pdf": {
        "slug": "knives-out",
        "date": "2026-02-15",
        "meta": {
            "title": "荒野行動 2月アプデ＆感謝祭の全貌",
            "game": "荒野行動",
            "date": "2026-02-15",
            "codename": "Operation Wild Thunder",
            "summary": "荒野行動2026年2月最新アップデート＋感謝祭イベント全情報＋新モード",
            "tags": ["バトルロイヤル", "アプデ速報", "イベント"]
        },
        "package": "com.netease.ko"
    },
}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def download_icon(slug, package_id):
    save_path = os.path.join(BASE, "games", slug, "icon.png")
    if os.path.exists(save_path) and os.path.getsize(save_path) > 1000:
        print(f"  Icon: already exists")
        return True
    url = f"https://play.google.com/store/apps/details?id={package_id}&hl=ja"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        matches = re.findall(r'(https://play-lh\.googleusercontent\.com/[^"\'>\s]+)', html)
        if matches:
            icon_url = re.sub(r'=w\d+', '=w240', matches[0])
            icon_url = re.sub(r'=s\d+', '=s240', icon_url)
            if '=w' not in icon_url and '=s' not in icon_url:
                icon_url += '=s240'
            req2 = urllib.request.Request(icon_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req2, timeout=15, context=ctx) as resp2:
                data = resp2.read()
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(data)
            print(f"  Icon: OK ({len(data)//1024} KB)")
            return True
    except Exception as e:
        print(f"  Icon: Failed ({e})")
    return False

success = 0
for pdf_name, info in NEW_PDFS.items():
    slug = info["slug"]
    date = info["date"]
    pdf_path = os.path.join(BASE, pdf_name)
    out_dir = os.path.join(BASE, "games", slug, "issues", date)

    if not os.path.exists(pdf_path):
        print(f"SKIP (not found): {pdf_name}")
        continue

    if os.path.exists(os.path.join(out_dir, "page-01.webp")):
        print(f"SKIP (done): {slug}")
        success += 1
    else:
        print(f"Converting: {slug}...", end=" ", flush=True)
        os.makedirs(out_dir, exist_ok=True)
        subprocess.run(["python", CONVERT_SCRIPT, pdf_path, out_dir],
                       capture_output=True, text=True, cwd=BASE)
        pages = len([f for f in os.listdir(out_dir) if f.startswith("page-") and f.endswith(".webp")])
        if pages > 0:
            meta = info["meta"].copy()
            meta["pageCount"] = pages
            with open(os.path.join(out_dir, "meta.json"), "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
            print(f"OK ({pages}p)")
            success += 1
        else:
            print("FAILED")
            continue

    if info.get("package"):
        download_icon(slug, info["package"])
        time.sleep(0.5)

print(f"\nConverted: {success}/{len(NEW_PDFS)}")

# Regenerate site
print("\nRegenerating site...")
result = subprocess.run(["python", os.path.join(BASE, "scripts", "generate-site.py")],
                       capture_output=True, text=True, cwd=BASE)
for line in result.stdout.strip().split('\n')[-5:]:
    print(line)
