"""Convert batch 7 new PDFs + download icons + regenerate site."""
import subprocess, os, json, ssl, urllib.request, re, time

BASE = r"c:\Users\foo\Downloads\soshageshin"
CONVERT_SCRIPT = os.path.join(BASE, "scripts", "convert-pdf.py")

NEW_PDFS = {
    "DQウォーク：まほうのカギと竜の秘宝 攻略全書.pdf": {
        "slug": "dq-walk",
        "date": "2026-02-15",
        "meta": {
            "title": "DQウォーク まほうのカギ＆竜の秘宝攻略",
            "game": "ドラクエウォーク",
            "date": "2026-02-15",
            "codename": "Operation Dragon Quest",
            "summary": "DQウォーク新機能まほうのカギ＋竜の秘宝イベント攻略＋おすすめ装備",
            "tags": ["位置情報RPG", "新コンテンツ", "攻略ガイド"]
        },
        "package": "com.square_enix.android_googleplay.dqwalk"
    },
    "FGOバレンタイン2026攻略と新章開幕ロードマップ.pdf": {
        "slug": "fgo",
        "date": "2026-02-15",
        "meta": {
            "title": "FGO バレンタイン2026＆新章ロードマップ",
            "game": "Fate/Grand Order",
            "date": "2026-02-15",
            "codename": "Operation Grand Order",
            "summary": "FGOバレンタイン2026イベント攻略＋新章開幕ロードマップ＋新サーヴァント評価",
            "tags": ["RPG", "イベント攻略", "新章"]
        },
        "package": "com.aniplex.fategrandorder"
    },
    "Kingshot 2026年2月最新イベント・コード攻略ガイド.pdf": {
        "slug": "kingshot",
        "date": "2026-02-15",
        "meta": {
            "title": "Kingshot 2月イベント＆コード攻略",
            "game": "Kingshot",
            "date": "2026-02-15",
            "codename": "Operation King's Shot",
            "summary": "Kingshot 2月最新イベント情報＋最新コード一覧＋攻略ガイド",
            "tags": ["カジュアルRPG", "イベント", "コード"]
        },
        "package": "com.special.kingshot"
    },
    "Roblox：安全対策の最前線と開発アップデートの要諦.pdf": {
        "slug": "roblox",
        "date": "2026-02-15",
        "meta": {
            "title": "Roblox 安全対策＆開発アップデート要諦",
            "game": "Roblox",
            "date": "2026-02-15",
            "codename": "Operation Roblox Shield",
            "summary": "Roblox最新安全対策＋開発者向けアップデート＋トレンドゲーム情報",
            "tags": ["プラットフォーム", "安全対策", "開発アプデ"]
        },
        "package": "com.roblox.client"
    },
    "Top Heroes：2026年2月最新戦術指令書.pdf": {
        "slug": "top-heroes",
        "date": "2026-02-15",
        "meta": {
            "title": "Top Heroes 2月戦術指令書",
            "game": "Top Heroes",
            "date": "2026-02-15",
            "codename": "Operation Top Command",
            "summary": "Top Heroes最新戦術ガイド＋2月イベント攻略＋おすすめ編成",
            "tags": ["放置系RPG", "戦術ガイド", "イベント"]
        },
        "package": "com.jigsaw.heroes"
    },
    "Township：2026年2月イベント攻略カレンダー.pdf": {
        "slug": "township",
        "date": "2026-02-15",
        "meta": {
            "title": "Township 2月イベント攻略カレンダー",
            "game": "Township",
            "date": "2026-02-15",
            "codename": "Operation Township Calendar",
            "summary": "Township 2月イベントカレンダー＋攻略ポイント＋効率的な進め方",
            "tags": ["街づくり", "イベント攻略", "カレンダー"]
        },
        "package": "com.playrix.township"
    },
    "アズールレーン 2026年2月戦略概報とイベント計画.pdf": {
        "slug": "azurlane",
        "date": "2026-02-15",
        "meta": {
            "title": "アズールレーン 2月戦略概報＆イベント計画",
            "game": "アズールレーン",
            "date": "2026-02-15",
            "codename": "Operation Azure Fleet",
            "summary": "アズールレーン2月戦略概報＋新イベント計画＋新艦船評価",
            "tags": ["シューティングRPG", "戦略概報", "新キャラ"]
        },
        "package": "com.YostarJP.AzurLane"
    },
    "ウィザードリィ ダフネ：2026年2月更新ロードマップ.pdf": {
        "slug": "wizardry-daphne",
        "date": "2026-02-15",
        "meta": {
            "title": "ウィザードリィ ダフネ 2月更新ロードマップ",
            "game": "ウィザードリィ ダフネ",
            "date": "2026-02-15",
            "codename": "Operation Dungeon Master",
            "summary": "ウィザードリィダフネ2月ロードマップ＋新ダンジョン＋攻略ポイント",
            "tags": ["ダンジョンRPG", "ロードマップ", "攻略"]
        },
        "package": "com.drecom.wizardry"
    },
    "ゴシップ・ハーバー：最新イベント攻略と配布情報まとめ.pdf": {
        "slug": "gossip-harbor",
        "date": "2026-02-15",
        "meta": {
            "title": "ゴシップ・ハーバー イベント攻略＆配布情報",
            "game": "ゴシップ・ハーバー",
            "date": "2026-02-15",
            "codename": "Operation Harbor Intel",
            "summary": "ゴシップ・ハーバー最新イベント攻略＋配布情報＋効率的な進め方",
            "tags": ["パズル", "イベント攻略", "配布情報"]
        },
        "package": "com.sixwaves.gossipMerge"
    },
    "パズル＆サバイバル：2026年2月最新攻略ガイド.pdf": {
        "slug": "puzzle-survival",
        "date": "2026-02-15",
        "meta": {
            "title": "パズル＆サバイバル 2月最新攻略",
            "game": "パズル＆サバイバル",
            "date": "2026-02-15",
            "codename": "Operation Puzzle Tactics",
            "summary": "パズル＆サバイバル2月攻略ガイド＋最新イベント＋おすすめ育成",
            "tags": ["パズルRPG", "攻略ガイド", "育成"]
        },
        "package": "com.games37.PuzzleAndSurvival"
    },
    "まおりゅう：2月攻略ロードマップと劇場版連動情報.pdf": {
        "slug": "maoryu",
        "date": "2026-02-15",
        "meta": {
            "title": "まおりゅう 2月攻略＆劇場版連動",
            "game": "転スラ まおりゅう",
            "date": "2026-02-15",
            "codename": "Operation Slime Conquest",
            "summary": "転生したらスライムだった件まおりゅう2月攻略＋劇場版連動情報＋新キャラ評価",
            "tags": ["RPG", "攻略", "劇場版連動"]
        },
        "package": "com.bandainamcoent.tensura_mrd"
    },
    "ロイヤルマッチ最新攻略・アップデート完全ガイド.pdf": {
        "slug": "royal-match",
        "date": "2026-02-15",
        "meta": {
            "title": "ロイヤルマッチ 最新攻略完全ガイド",
            "game": "ロイヤルマッチ",
            "date": "2026-02-15",
            "codename": "Operation Royal Crown",
            "summary": "ロイヤルマッチ最新攻略＋アップデート情報＋効率的なクリア方法",
            "tags": ["パズル", "攻略ガイド", "アプデ情報"]
        },
        "package": "com.dreamgames.royalmatch"
    },
    "学園アイドルマスター：2026年2月最新動向まとめ.pdf": {
        "slug": "gakumas",
        "date": "2026-02-15",
        "meta": {
            "title": "学マス 2月最新動向まとめ",
            "game": "学園アイドルマスター",
            "date": "2026-02-15",
            "codename": "Operation Idol Academy",
            "summary": "学園アイドルマスター2月最新動向＋新アイドル＋イベント情報",
            "tags": ["アイドル育成", "新キャラ", "イベント"]
        },
        "package": "com.bandainamcoent.idolmaster_gakuen"
    },
    "勝利の女神：NIKKE 2026年戦略ロードマップ.pdf": {
        "slug": "nikke",
        "date": "2026-02-15",
        "meta": {
            "title": "NIKKE 2026年戦略ロードマップ",
            "game": "勝利の女神：NIKKE",
            "date": "2026-02-15",
            "codename": "Operation Goddess Victory",
            "summary": "NIKKE 2026年戦略ロードマップ＋新キャラ情報＋攻略ポイント",
            "tags": ["TPS/RPG", "ロードマップ", "新キャラ"]
        },
        "package": "com.proximabeta.nikke"
    },
    "杖と剣の伝説：2026年2月最新攻略アップデート.pdf": {
        "slug": "wand-and-sword",
        "date": "2026-02-15",
        "meta": {
            "title": "杖と剣の伝説 2月攻略アップデート",
            "game": "杖と剣の伝説",
            "date": "2026-02-15",
            "codename": "Operation Wand & Sword",
            "summary": "杖と剣の伝説2月攻略＋新コンテンツ＋おすすめ育成ガイド",
            "tags": ["RPG", "攻略", "新コンテンツ"]
        },
        "package": "com.supercent.swd"
    },
    "信長の野望 出陣：2026年2月攻略ガイド最新版.pdf": {
        "slug": "nobunaga-shutsujin",
        "date": "2026-02-15",
        "meta": {
            "title": "信長の野望 出陣 2月攻略ガイド",
            "game": "信長の野望 出陣",
            "date": "2026-02-15",
            "codename": "Operation Warring States",
            "summary": "信長の野望出陣2月攻略ガイド＋新シナリオ＋おすすめ武将編成",
            "tags": ["歴史SLG", "攻略ガイド", "新シナリオ"]
        },
        "package": "jp.co.koeitecmo.nobunaga_shutsujin"
    },
    "旦那様の一発逆転人生：リブランディングと最新運営情報屋.pdf": {
        "slug": "danna-sama",
        "date": "2026-02-15",
        "meta": {
            "title": "旦那様の一発逆転人生 最新運営情報",
            "game": "旦那様の一発逆転人生",
            "date": "2026-02-15",
            "codename": "Operation Comeback",
            "summary": "旦那様の一発逆転人生リブランディング情報＋最新運営アップデート",
            "tags": ["シミュレーション", "運営情報", "リブランディング"]
        },
        "package": "com.clicktorich.master"
    },
    "放置少女：2026年バレンタイン攻略詳報.pdf": {
        "slug": "houchi-shoujo",
        "date": "2026-02-15",
        "meta": {
            "title": "放置少女 バレンタイン2026攻略詳報",
            "game": "放置少女",
            "date": "2026-02-15",
            "codename": "Operation Idle Valentine",
            "summary": "放置少女バレンタイン2026イベント攻略＋新キャラ評価＋最新メタ分析",
            "tags": ["放置系RPG", "バレンタイン", "攻略"]
        },
        "package": "com.c4games.hsjp"
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
