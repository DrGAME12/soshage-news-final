"""Convert batch 9 new PDFs + download icons + regenerate site."""
import subprocess, os, json, ssl, urllib.request, re, time

BASE = r"c:\Users\foo\Downloads\soshageshin"
CONVERT_SCRIPT = os.path.join(BASE, "scripts", "convert-pdf.py")

NEW_PDFS = {
    "Age of Origins：バレンタイン＆春節イベント攻略最新情報.pdf": {
        "slug": "age-of-origins",
        "date": "2026-02-16",
        "meta": {
            "title": "Age of Origins バレンタイン＆春節攻略",
            "game": "Age of Origins",
            "date": "2026-02-16",
            "codename": "Operation Origins",
            "summary": "Age of Originsバレンタイン＆春節イベント攻略＋最新情報",
            "tags": ["ストラテジー", "イベント攻略", "季節限定"]
        },
        "package": "com.camelgames.aoz"
    },
    "Dark War Survival 最新アプデと攻略コードまとめ.pdf": {
        "slug": "dark-war-survival",
        "date": "2026-02-16",
        "meta": {
            "title": "Dark War Survival 最新攻略＆コード",
            "game": "Dark War Survival",
            "date": "2026-02-16",
            "codename": "Operation Dark War",
            "summary": "Dark War Survival最新アプデ＋攻略コードまとめ＋戦術ガイド",
            "tags": ["サバイバル", "攻略コード", "アプデ情報"]
        },
        "package": "com.darkwar.survival"
    },
    "FEH 9周年記念キャンペーンと最新攻略ガイド.pdf": {
        "slug": "feh",
        "date": "2026-02-16",
        "meta": {
            "title": "FEH 9周年キャンペーン＆攻略",
            "game": "ファイアーエムブレム ヒーローズ",
            "date": "2026-02-16",
            "codename": "Operation Emblem",
            "summary": "FEH 9周年記念キャンペーン＋最新攻略ガイド＋新英雄評価",
            "tags": ["タクティクスRPG", "周年記念", "新キャラ"]
        },
        "package": "com.nintendo.zaba"
    },
    "KOF AFK：メタスラ3コラボと最新アップデート情報.pdf": {
        "slug": "kof-afk",
        "date": "2026-02-16",
        "meta": {
            "title": "KOF AFK メタスラコラボ＆最新アプデ",
            "game": "KOF AFK",
            "date": "2026-02-16",
            "codename": "Operation King of Fighters",
            "summary": "KOF AFKメタルスラッグ3コラボ＋最新アップデート情報＋攻略ポイント",
            "tags": ["放置系RPG", "コラボ", "アプデ情報"]
        },
        "package": "com.fingeratip.kofafk"
    },
    "LINE POP2：2月イベント攻略カレンダー.pdf": {
        "slug": "line-pop2",
        "date": "2026-02-16",
        "meta": {
            "title": "LINE POP2 2月イベント攻略",
            "game": "LINE POP2",
            "date": "2026-02-16",
            "codename": "Operation Pop",
            "summary": "LINE POP2 2月イベント攻略カレンダー＋効率的な進め方ガイド",
            "tags": ["パズル", "イベント攻略", "カレンダー"]
        },
        "package": "com.linecorp.LGPOP2"
    },
    "P5X最新アップデート・イベント攻略ガイド.pdf": {
        "slug": "p5x",
        "date": "2026-02-16",
        "meta": {
            "title": "P5X 最新アプデ＆イベント攻略",
            "game": "ペルソナ5：The Phantom X",
            "date": "2026-02-16",
            "codename": "Operation Phantom",
            "summary": "ペルソナ5 The Phantom X最新アプデ＋イベント攻略＋おすすめ編成",
            "tags": ["RPG", "アプデ速報", "イベント攻略"]
        },
        "package": "com.perfectworld.p5x"
    },
    "Royal Kingdom：攻略と最新アップデートの全貌.pdf": {
        "slug": "royal-kingdom",
        "date": "2026-02-16",
        "meta": {
            "title": "Royal Kingdom 攻略＆最新アプデ",
            "game": "Royal Kingdom",
            "date": "2026-02-16",
            "codename": "Operation Royal",
            "summary": "Royal Kingdom攻略ガイド＋最新アップデート全貌＋おすすめ戦略",
            "tags": ["ストラテジー", "攻略ガイド", "アプデ情報"]
        },
        "package": "com.playtika.royalkingdom"
    },
    "Seaside Escape 最新攻略・イベント速報ガイド.pdf": {
        "slug": "seaside-escape",
        "date": "2026-02-16",
        "meta": {
            "title": "Seaside Escape 攻略＆イベント速報",
            "game": "Seaside Escape",
            "date": "2026-02-16",
            "codename": "Operation Seaside",
            "summary": "Seaside Escape最新攻略＋イベント速報＋効率的な進め方",
            "tags": ["パズル", "攻略ガイド", "イベント"]
        },
        "package": "com.gamecircus.seaside"
    },
    "エバーテイル 2026年2月最新攻略ガイド.pdf": {
        "slug": "evertale",
        "date": "2026-02-16",
        "meta": {
            "title": "エバーテイル 2月最新攻略ガイド",
            "game": "エバーテイル",
            "date": "2026-02-16",
            "codename": "Operation Evertale",
            "summary": "エバーテイル2月最新攻略＋新キャラ評価＋おすすめ編成ガイド",
            "tags": ["RPG", "攻略ガイド", "新キャラ"]
        },
        "package": "com.zigzagame.evertale"
    },
    "エボニー：2026年2月最新イベント・アップデート情報まとめ.pdf": {
        "slug": "evony",
        "date": "2026-02-16",
        "meta": {
            "title": "エボニー 2月最新イベント＆アプデ",
            "game": "エボニー",
            "date": "2026-02-16",
            "codename": "Operation Evony Empire",
            "summary": "エボニー2月最新イベント＋アップデート情報まとめ＋攻略ポイント",
            "tags": ["ストラテジー", "イベント", "アプデ情報"]
        },
        "package": "com.topgamesinc.evony"
    },
    "キノコ伝説：最新イベント攻略と交換コードまとめ.pdf": {
        "slug": "kinoko-densetsu",
        "date": "2026-02-16",
        "meta": {
            "title": "キノコ伝説 イベント攻略＆コード",
            "game": "キノコ伝説",
            "date": "2026-02-16",
            "codename": "Operation Mushroom",
            "summary": "キノコ伝説最新イベント攻略＋交換コードまとめ＋育成ガイド",
            "tags": ["放置系RPG", "イベント攻略", "交換コード"]
        },
        "package": "com.joymax.mushroom"
    },
    "キャンディクラッシュ：バレンタイン大会と最新運営情報.pdf": {
        "slug": "candy-crush",
        "date": "2026-02-16",
        "meta": {
            "title": "キャンディクラッシュ バレンタイン大会",
            "game": "キャンディクラッシュ",
            "date": "2026-02-16",
            "codename": "Operation Sweet Crush",
            "summary": "キャンディクラッシュバレンタイン大会＋最新運営情報＋攻略ポイント",
            "tags": ["パズル", "バレンタイン", "大会情報"]
        },
        "package": "com.king.candycrushsaga"
    },
    "スパロボDD 6.5周年直前イベント・ガシャ攻略要報.pdf": {
        "slug": "srw-dd",
        "date": "2026-02-16",
        "meta": {
            "title": "スパロボDD 6.5周年直前イベント攻略",
            "game": "スーパーロボット大戦DD",
            "date": "2026-02-16",
            "codename": "Operation Robot Wars",
            "summary": "スパロボDD 6.5周年直前イベント＋ガシャ攻略＋おすすめユニット",
            "tags": ["シミュレーションRPG", "周年イベント", "ガシャ攻略"]
        },
        "package": "jp.co.bandainamcoent.SRWDD"
    },
    "セガNET麻雀 MJ：最新イベント＆攻略情報まとめ.pdf": {
        "slug": "sega-mj",
        "date": "2026-02-16",
        "meta": {
            "title": "セガNET麻雀 MJ 最新イベント＆攻略",
            "game": "セガNET麻雀 MJ",
            "date": "2026-02-16",
            "codename": "Operation Mahjong Master",
            "summary": "セガNET麻雀MJ最新イベント＋攻略情報まとめ＋段位戦ガイド",
            "tags": ["麻雀", "イベント", "攻略情報"]
        },
        "package": "jp.sega.mjmobile"
    },
    "ゼンレスゾーンゼロ：Ver.2.6攻略最新情報まとめ.pdf": {
        "slug": "zzz",
        "date": "2026-02-16",
        "meta": {
            "title": "ゼンレスゾーンゼロ Ver.2.6攻略",
            "game": "ゼンレスゾーンゼロ",
            "date": "2026-02-16",
            "codename": "Operation Zenless Zone",
            "summary": "ゼンレスゾーンゼロVer.2.6攻略＋新キャラ＋新コンテンツ情報",
            "tags": ["アクションRPG", "大型アプデ", "攻略"]
        },
        "package": "com.HoYoverse.Nap"
    },
    "ドット勇者：2.5周年前夜祭と最新攻略ガイド.pdf": {
        "slug": "dot-yusha",
        "date": "2026-02-16",
        "meta": {
            "title": "ドット勇者 2.5周年前夜祭＆攻略",
            "game": "ドット勇者",
            "date": "2026-02-16",
            "codename": "Operation Pixel Hero",
            "summary": "ドット勇者2.5周年前夜祭＋最新攻略ガイド＋おすすめキャラ",
            "tags": ["放置系RPG", "周年イベント", "攻略"]
        },
        "package": "com.efun.dotyusha.jp"
    },
    "ドラゴンエッグ：10周年記念攻略と最新イベント情報.pdf": {
        "slug": "dragon-egg",
        "date": "2026-02-16",
        "meta": {
            "title": "ドラゴンエッグ 10周年記念攻略",
            "game": "ドラゴンエッグ",
            "date": "2026-02-16",
            "codename": "Operation Dragon Egg",
            "summary": "ドラゴンエッグ10周年記念攻略＋最新イベント情報＋おすすめ編成",
            "tags": ["RPG", "周年記念", "攻略"]
        },
        "package": "jp.rudel.dragonegg"
    },
    "ヒーローウォーズ：新シーズン開幕と攻略の要諦.pdf": {
        "slug": "hero-wars",
        "date": "2026-02-16",
        "meta": {
            "title": "ヒーローウォーズ 新シーズン攻略",
            "game": "ヒーローウォーズ",
            "date": "2026-02-16",
            "codename": "Operation Hero Wars",
            "summary": "ヒーローウォーズ新シーズン開幕＋攻略の要諦＋おすすめヒーロー",
            "tags": ["RPG", "新シーズン", "攻略"]
        },
        "package": "com.nexters.herowars"
    },
    "ピクミンブルーム：2026年2月最新イベント攻略まとめ.pdf": {
        "slug": "pikmin-bloom",
        "date": "2026-02-16",
        "meta": {
            "title": "ピクミンブルーム 2月イベント攻略",
            "game": "ピクミン ブルーム",
            "date": "2026-02-16",
            "codename": "Operation Pikmin Walk",
            "summary": "ピクミンブルーム2月最新イベント攻略まとめ＋おすすめプレイガイド",
            "tags": ["位置情報", "イベント攻略", "ウォーキング"]
        },
        "package": "com.nianticlabs.pikmin"
    },
    "ビビッドアーミー：2026年2月最新攻略まとめ.pdf": {
        "slug": "vivid-army",
        "date": "2026-02-16",
        "meta": {
            "title": "ビビッドアーミー 2月最新攻略",
            "game": "ビビッドアーミー",
            "date": "2026-02-16",
            "codename": "Operation Vivid",
            "summary": "ビビッドアーミー2月最新攻略まとめ＋イベント情報＋おすすめ編成",
            "tags": ["ストラテジー", "攻略", "イベント"]
        },
        "package": "com.supernovagame.vividarmy.jp"
    },
    "ぷにぷに：ギアスコラボ終盤と次イベントへの指針.pdf": {
        "slug": "punipuni",
        "date": "2026-02-16",
        "meta": {
            "title": "ぷにぷに ギアスコラボ終盤攻略",
            "game": "妖怪ウォッチ ぷにぷに",
            "date": "2026-02-16",
            "codename": "Operation Puni Puni",
            "summary": "ぷにぷにギアスコラボ終盤攻略＋次イベント指針＋おすすめ妖怪",
            "tags": ["パズル", "コラボ", "攻略"]
        },
        "package": "com.Level5.YWP"
    },
    "ブロスタ：トロフィー大改修と2026年2月最新動向.pdf": {
        "slug": "brawl-stars",
        "date": "2026-02-16",
        "meta": {
            "title": "ブロスタ トロフィー大改修＆最新動向",
            "game": "ブロスタ",
            "date": "2026-02-16",
            "codename": "Operation Brawl",
            "summary": "ブロスタトロフィー大改修＋2月最新動向＋おすすめブロウラー",
            "tags": ["アクション", "大型アプデ", "最新動向"]
        },
        "package": "com.supercell.brawlstars"
    },
    "モンハンNow：2月イベント・新要素攻略まとめ.pdf": {
        "slug": "mh-now",
        "date": "2026-02-16",
        "meta": {
            "title": "モンハンNow 2月イベント＆新要素攻略",
            "game": "モンスターハンターNow",
            "date": "2026-02-16",
            "codename": "Operation Monster Hunt",
            "summary": "モンハンNow 2月イベント＋新要素攻略まとめ＋おすすめ武器",
            "tags": ["アクション", "イベント攻略", "新要素"]
        },
        "package": "com.nianticlabs.monsterhunter"
    },
    "ローグウィズデッド：期間限定エイルと最新更新まとめ.pdf": {
        "slug": "rogue-with-dead",
        "date": "2026-02-16",
        "meta": {
            "title": "ローグウィズデッド 限定エイル＆最新更新",
            "game": "ローグウィズデッド",
            "date": "2026-02-16",
            "codename": "Operation Rogue Dead",
            "summary": "ローグウィズデッド期間限定エイル＋最新更新まとめ＋攻略ポイント",
            "tags": ["ローグライク", "限定キャラ", "アプデ情報"]
        },
        "package": "com.and.rog"
    },
    "ローモバ：10周年と春節イベントの攻略ToDoガイド.pdf": {
        "slug": "lords-mobile",
        "date": "2026-02-16",
        "meta": {
            "title": "ローモバ 10周年＆春節攻略ToDo",
            "game": "ロードモバイル",
            "date": "2026-02-16",
            "codename": "Operation Lords",
            "summary": "ロードモバイル10周年＋春節イベント攻略ToDoガイド＋おすすめ戦略",
            "tags": ["ストラテジー", "周年記念", "春節イベント"]
        },
        "package": "com.igg.android.lordsmobile"
    },
    "異世界のんびりライフ：2026年2月攻略・最新情報まとめ.pdf": {
        "slug": "isekai-nonbiri",
        "date": "2026-02-16",
        "meta": {
            "title": "異世界のんびりライフ 2月攻略",
            "game": "異世界のんびりライフ",
            "date": "2026-02-16",
            "codename": "Operation Isekai Life",
            "summary": "異世界のんびりライフ2月攻略＋最新情報まとめ＋効率育成ガイド",
            "tags": ["放置系RPG", "攻略", "最新情報"]
        },
        "package": "com.uika.isekainonbiri"
    },
    "荒野行動：二月大型アップデートと最新攻略指針.pdf": {
        "slug": "knives-out",
        "date": "2026-02-16",
        "meta": {
            "title": "荒野行動 2月大型アプデ＆攻略指針",
            "game": "荒野行動",
            "date": "2026-02-16",
            "codename": "Operation Wild Storm",
            "summary": "荒野行動2月大型アップデート＋最新攻略指針＋新モード情報",
            "tags": ["バトルロイヤル", "大型アプデ", "攻略指針"]
        },
        "package": "com.netease.ko"
    },
    "三國志 真戦：定軍山の戦いと40周年記念祭攻略ガイド.pdf": {
        "slug": "sangokushi-shinsen",
        "date": "2026-02-16",
        "meta": {
            "title": "三國志 真戦 定軍山＆40周年攻略",
            "game": "三國志 真戦",
            "date": "2026-02-16",
            "codename": "Operation Three Kingdoms",
            "summary": "三國志真戦定軍山の戦い＋40周年記念祭攻略ガイド＋おすすめ編成",
            "tags": ["ストラテジー", "周年記念", "攻略"]
        },
        "package": "com.qookka.sangokushi.jp"
    },
    "三國志 覇道：2月度アップデートと攻略ToDoまとめ.pdf": {
        "slug": "sangokushi-hadou",
        "date": "2026-02-16",
        "meta": {
            "title": "三國志 覇道 2月アプデ＆攻略ToDo",
            "game": "三國志 覇道",
            "date": "2026-02-16",
            "codename": "Operation Hegemon Road",
            "summary": "三國志覇道2月度アップデート＋攻略ToDoまとめ＋おすすめ武将",
            "tags": ["MMORPG", "アプデ情報", "攻略"]
        },
        "package": "jp.co.koeitecmo.sangokushihadou"
    },
    "東京ディバンカー：2026年2月最新動向まとめ.pdf": {
        "slug": "tokyo-debunker",
        "date": "2026-02-16",
        "meta": {
            "title": "東京ディバンカー 2月最新動向",
            "game": "東京ディバンカー",
            "date": "2026-02-16",
            "codename": "Operation Debunker",
            "summary": "東京ディバンカー2月最新動向＋新シナリオ＋イベント情報",
            "tags": ["ADV/RPG", "最新動向", "新シナリオ"]
        },
        "package": "com.kakaogames.tokyodebunker"
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
