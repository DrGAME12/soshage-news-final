"""Convert batch 8 new PDFs + download icons + regenerate site."""
import subprocess, os, json, ssl, urllib.request, re, time

BASE = r"c:\Users\foo\Downloads\soshageshin"
CONVERT_SCRIPT = os.path.join(BASE, "scripts", "convert-pdf.py")

NEW_PDFS = {
    "Fishdom：2026年2月最新アップデート情報まとめ.pdf": {
        "slug": "fishdom",
        "date": "2026-02-15",
        "meta": {
            "title": "Fishdom 2月最新アップデート情報",
            "game": "Fishdom",
            "date": "2026-02-15",
            "codename": "Operation Aquarium",
            "summary": "Fishdom 2月最新アップデート＋新イベント攻略＋効率的な進め方",
            "tags": ["パズル", "アプデ情報", "イベント攻略"]
        },
        "package": "com.playrix.fishdomdd.gplay"
    },
    "Last Z：生存者のための最新攻略ガイド 2026.pdf": {
        "slug": "last-z",
        "date": "2026-02-15",
        "meta": {
            "title": "Last Z 生存者のための最新攻略ガイド",
            "game": "Last Z",
            "date": "2026-02-15",
            "codename": "Operation Last Survivor",
            "summary": "Last Z最新攻略ガイド＋サバイバル戦術＋おすすめ装備構成",
            "tags": ["サバイバル", "攻略ガイド", "戦術"]
        },
        "package": "com.joymax.lastz"
    },
    "スターシード：アスニアトリガー 2月最新情報まとめ集.pdf": {
        "slug": "starseed-asnia",
        "date": "2026-02-15",
        "meta": {
            "title": "スターシード：アスニアトリガー 2月最新情報",
            "game": "スターシード：アスニアトリガー",
            "date": "2026-02-15",
            "codename": "Operation Starseed",
            "summary": "スターシード：アスニアトリガー2月最新情報＋新キャラ＋イベント攻略",
            "tags": ["RPG", "新キャラ", "イベント"]
        },
        "package": "com.ngelgames.starseed"
    },
    "トレクル最新攻略：2026年2月イベント情報まとめ.pdf": {
        "slug": "optc",
        "date": "2026-02-15",
        "meta": {
            "title": "トレクル 2月イベント攻略まとめ",
            "game": "ONE PIECE トレジャークルーズ",
            "date": "2026-02-15",
            "codename": "Operation Treasure Cruise",
            "summary": "トレクル2月イベント情報まとめ＋新キャラ評価＋攻略ポイント",
            "tags": ["アクションRPG", "イベント", "新キャラ"]
        },
        "package": "com.namcobandaigames.spmoja010E"
    },
    "バウンティラッシュ7周年：黒ひげ参戦と報酬攻略の全貌.pdf": {
        "slug": "bounty-rush",
        "date": "2026-02-15",
        "meta": {
            "title": "バウンティラッシュ 7周年＆黒ひげ参戦",
            "game": "ONE PIECE バウンティラッシュ",
            "date": "2026-02-15",
            "codename": "Operation Bounty",
            "summary": "バウンティラッシュ7周年記念＋黒ひげ参戦情報＋報酬攻略ガイド",
            "tags": ["アクション", "周年記念", "新キャラ"]
        },
        "package": "com.bandainamcoent.opbr"
    },
    "ブルアカ最新攻略：デカグラマトン決戦と戦術指針録.pdf": {
        "slug": "blue-archive",
        "date": "2026-02-15",
        "meta": {
            "title": "ブルアカ デカグラマトン決戦＆戦術指針録",
            "game": "ブルーアーカイブ",
            "date": "2026-02-15",
            "codename": "Operation Blue Archive",
            "summary": "ブルアカ最新攻略デカグラマトン決戦＋戦術指針＋おすすめ編成",
            "tags": ["RPG", "高難易度攻略", "戦術指針"]
        },
        "package": "com.YostarJP.BlueArchive"
    },
    "マフィア・シティ：2026年2月最新攻略ガイド.pdf": {
        "slug": "mafia-city",
        "date": "2026-02-15",
        "meta": {
            "title": "マフィア・シティ 2月最新攻略ガイド",
            "game": "マフィア・シティ",
            "date": "2026-02-15",
            "codename": "Operation Mafia Boss",
            "summary": "マフィア・シティ2月攻略ガイド＋最新イベント＋効率的な勢力拡大",
            "tags": ["ストラテジー", "攻略ガイド", "イベント"]
        },
        "package": "com.yottagames.mafiawar"
    },
    "駅メモ！最新イベント・キャンペーン攻略まとめ2026.pdf": {
        "slug": "ekimemo",
        "date": "2026-02-15",
        "meta": {
            "title": "駅メモ！2026イベント＆キャンペーン攻略",
            "game": "駅メモ！",
            "date": "2026-02-15",
            "codename": "Operation Station Master",
            "summary": "駅メモ！最新イベント・キャンペーン攻略まとめ＋効率的なプレイガイド",
            "tags": ["位置情報", "イベント攻略", "キャンペーン"]
        },
        "package": "jp.ekimemo"
    },
    "怪獣8号 THE GAME：ハーフアニバーサリー最新攻略情報まとめ.pdf": {
        "slug": "kaiju-no8",
        "date": "2026-02-15",
        "meta": {
            "title": "怪獣8号 THE GAME ハーフアニバ攻略",
            "game": "怪獣8号 THE GAME",
            "date": "2026-02-15",
            "codename": "Operation Kaiju Strike",
            "summary": "怪獣8号 THE GAMEハーフアニバーサリー攻略＋新キャラ評価＋イベント情報",
            "tags": ["アクションRPG", "ハーフアニバ", "新キャラ"]
        },
        "package": "com.sumzap.kaiju8"
    },
    "信長の野望 覇道：最新アップデート・イベント攻略指針.pdf": {
        "slug": "nobunaga-hadou",
        "date": "2026-02-15",
        "meta": {
            "title": "信長の野望 覇道 アプデ＆イベント攻略",
            "game": "信長の野望 覇道",
            "date": "2026-02-15",
            "codename": "Operation Warring Hegemon",
            "summary": "信長の野望覇道最新アップデート＋イベント攻略指針＋おすすめ武将",
            "tags": ["歴史MMO", "アプデ情報", "イベント攻略"]
        },
        "package": "jp.co.koeitecmo.nobunagahadou"
    },
    "聖霊伝説：最強への道 2月最新攻略ガイド.pdf": {
        "slug": "seirei-densetsu",
        "date": "2026-02-15",
        "meta": {
            "title": "聖霊伝説 2月最新攻略ガイド",
            "game": "聖霊伝説",
            "date": "2026-02-15",
            "codename": "Operation Spirit Legend",
            "summary": "聖霊伝説最新攻略ガイド＋育成ポイント＋おすすめ編成",
            "tags": ["RPG", "攻略ガイド", "育成"]
        },
        "package": "com.dpwind.seirei"
    },
}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def download_icon(slug, package_id):
    save_path = os.path.join(BASE, "games", slug, "icon.png")
    if os.path.exists(save_path) and os.path.getsize(save_path) > 1000:
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
            print(f"  Icon OK ({len(data)//1024}KB)")
            return True
    except Exception as e:
        print(f"  Icon fail: {e}")
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
        time.sleep(0.3)

print(f"\nConverted: {success}/{len(NEW_PDFS)}")
print("\nRegenerating site...")
result = subprocess.run(["python", os.path.join(BASE, "scripts", "generate-site.py")],
                       capture_output=True, text=True, cwd=BASE)
for line in result.stdout.strip().split('\n')[-5:]:
    print(line)
