"""
Batch convert ALL unprocessed PDFs and generate viewer/game pages.
Skips any game slug that already has page-01.webp.
"""
import subprocess, os, json, re, sys

BASE = r"c:\Users\foo\Downloads\soshageshin"

# Map PDF filenames -> (slug, game name JP, name EN, genre, icon, color, title, summary, tags, codename)
PDF_MAP = {
    "60_Million_Strong_Ninja_Meta.pdf": ("naruto-ninja", "NARUTO×BORUTO 忍者", "Naruto Ninja", "忍者アクションRPG", "🍥", "#ff6600", "忍者メタ 6000万人突破号", "6000万DL突破記念＋最強忍者ランキング＋新章追加", ["記念", "ランキング", "新章"], "Operation Ninja Storm"),
    "7th_Anniversary_Scoop.pdf": ("7th-anniv", "7周年記念", "7th Anniversary", "記念特報", "🎂", "#e91e63", "7周年記念スクープ", "7周年大型アップデート＋記念ガチャ＋限定イベント開催", ["記念", "ガチャ", "限定イベント"], "Operation Seven Stars"),
    "All_Star_News_Snapshot.pdf": ("all-star", "オールスター", "All Star", "クロスオーバー", "⭐", "#ff9800", "オールスターニュース速報", "全キャラ集結イベント＋コラボ情報＋最新バランス調整", ["イベント", "コラボ", "バランス調整"], "Operation All Star"),
    "Ask_Kingdom_Daily_9th_Anniversary.pdf": ("ask-kingdom", "アスキン", "Ash Kingdom", "ストラテジー", "🏰", "#795548", "アスキン9周年デイリー", "9周年記念＋新王国システム＋大型コンテンツ追加", ["記念", "新システム", "大型アプデ"], "Operation Kingdom Nine"),
    "CODM_Season_Two_Report.pdf": ("codm", "CoDモバイル", "Call of Duty Mobile", "FPS", "🎯", "#4caf50", "CODM シーズン2レポート", "シーズン2新マップ＋新武器＋ランク報酬まとめ", ["新シーズン", "新マップ", "新武器"], "Operation Warzone"),
    "Daily_RomSaGa_RS.pdf": ("romasaga", "ロマサガRS", "Romancing SaGa Re;univerSe", "RPG", "⚔️", "#c62828", "ロマサガRS デイリー速報", "新キャラ追加＋イベントボス攻略＋ガチャ分析", ["新キャラ", "攻略", "ガチャ"], "Operation Saga"),
    "Dereste_Producer_Briefing.pdf": ("dereste", "デレステ", "THE IDOLM@STER Cinderella Girls", "リズムゲーム", "🎤", "#e91e63", "デレステ プロデューサーブリーフィング", "新楽曲＋フェス限定＋イベント攻略まとめ", ["新楽曲", "フェス限定", "イベント"], "Operation Stage"),
    "Dokkan_Battle_11th_Anniversary_Report.pdf": ("dokkan", "ドッカンバトル", "Dragon Ball Z Dokkan Battle", "アクションRPG", "🐉", "#ff5722", "ドッカン11周年レポート", "11周年記念＋新LR追加＋超激戦イベント開催", ["記念", "新キャラ", "超激戦"], "Operation Dragon Power"),
    "Dual_Ambition_War_Plan.pdf": ("dual-ambition", "デュアルアンビション", "Dual Ambition", "戦略RPG", "🗡️", "#607d8b", "デュアルアンビション作戦計画", "新章開幕＋PvP大会結果＋新ユニット実装", ["新章", "PvP", "新ユニット"], "Operation Dual Strike"),
    "EX_Rarity_Mega_Update_2026.pdf": ("ex-rarity", "EXレアリティ", "EX Rarity Update", "大型アプデ特報", "💎", "#9c27b0", "EXレアリティ メガアップデート2026", "新レアリティ「EX」実装＋育成システム刷新＋バランス調整", ["新レアリティ", "育成", "バランス調整"], "Operation EX Rank"),
    "Ensemble_Stars_10th_Anniversary.pdf": ("enstars", "あんスタ", "Ensemble Stars!!", "リズム＆ADV", "🌟", "#ff4081", "あんスタ10周年特報", "10周年記念イベント＋新ユニット結成＋コラボ発表", ["10周年", "新ユニット", "コラボ"], "Operation Starlight"),
    "February_Dual_Game_Briefing.pdf": ("feb-dual", "2月デュアルゲーム", "February Dual Game", "合同特報", "📋", "#455a64", "2月デュアルゲームブリーフィング", "2タイトル合同アップデート＋クロスオーバーイベント開催", ["合同アプデ", "クロスオーバー", "イベント"], "Operation Dual Brief"),
    "Garupa_Daily_News_All_Updates.pdf": ("garupa", "ガルパ", "BanG Dream! Girls Band Party!", "リズムゲーム", "🎸", "#e91e63", "ガルパデイリー 全アプデまとめ", "新楽曲追加＋限定ガチャ＋イベントストーリー公開", ["新楽曲", "限定ガチャ", "ストーリー"], "Operation Band"),
    "Granblue_Times_February_Update_Summary.pdf": ("granblue", "グラブル", "Granblue Fantasy", "RPG", "⚓", "#03a9f4", "グラブルタイムズ 2月号", "古戦場結果＋新ジョブ追加＋バランス調整20体", ["古戦場", "新ジョブ", "バランス調整"], "Operation Skybound"),
    "Heban_4th_Anniversary_Festival.pdf": ("heban", "ヘブバン", "Heaven Burns Red", "ドラマRPG", "🔥", "#d32f2f", "ヘブバン4周年フェスティバル", "4周年記念＋新章追加＋PvE新コンテンツ実装", ["4周年", "新章", "新コンテンツ"], "Operation Heaven"),
    "Honmaru_Extra_Unju_Alert.pdf": ("touken", "刀剣乱舞", "Touken Ranbu", "刀剣育成SLG", "⚔️", "#5d4037", "本丸号外 温重警報", "新刀剣男士＋大型イベント＋極実装", ["新キャラ", "イベント", "極"], "Operation Blade"),
    "IDOLiSH7_DECENNIUM_Report.pdf": ("idolish7", "アイナナ", "IDOLiSH7", "アイドル育成", "🎶", "#7b1fa2", "アイナナ DECENNIUM レポート", "10周年記念＋新楽曲＋限定イベント開催", ["10周年", "新楽曲", "限定"], "Operation Idol"),
    "Identity_V_Times_Weekly_Report.pdf": ("identity-v", "第五人格", "Identity V", "非対称対戦", "🎭", "#37474f", "第五人格タイムズ 週報", "新サバイバー＋ランクマッチ調整＋シーズンイベント", ["新キャラ", "ランクマッチ", "シーズン"], "Operation Masquerade"),
    "Lineage_Observer_February_14_Edition.pdf": ("lineage", "リネージュ", "Lineage", "MMORPG", "🏹", "#827717", "リネージュオブザーバー 2月14日版", "大型攻城戦結果＋新装備＋バレンタインイベント", ["攻城戦", "新装備", "イベント"], "Operation Siege"),
    "Mahjong_Soul_Times_Extra_Edition.pdf": ("mahjongsoul", "雀魂", "Mahjong Soul", "麻雀", "🀄", "#1b5e20", "雀魂タイムズ 号外", "大型大会結果＋新キャラ＋段位戦調整", ["大会", "新キャラ", "段位戦"], "Operation Riichi"),
    "Master_Duel_Anniversary_Report.pdf": ("masterduel", "マスターデュエル", "Yu-Gi-Oh! Master Duel", "カードゲーム", "🃏", "#f57f17", "マスターデュエル 周年レポート", "周年記念＋新パック＋リミットレギュレーション改定", ["周年", "新パック", "レギュ改定"], "Operation Duel"),
    "Mt_Dingjun_Scenario_Briefing.pdf": ("dingjun", "定軍山", "Mt. Dingjun", "三国志SLG", "⛰️", "#4e342e", "定軍山シナリオブリーフィング", "新シナリオ「定軍山の戦い」＋武将追加＋同盟戦改修", ["新シナリオ", "武将追加", "同盟戦"], "Operation Dingjun"),
    "Night_Raven_Weekly_Briefing.pdf": ("twisted", "ツイステ", "Twisted Wonderland", "ADV", "🐦‍⬛", "#311b92", "ナイトレイヴン週報", "新章公開＋限定ガチャ＋試験イベント開催", ["新章", "限定ガチャ", "イベント"], "Operation Raven"),
    "Nyanko_Sports_Latest_Scoop.pdf": ("nyanko", "にゃんこ大戦争", "The Battle Cats", "タワーディフェンス", "🐱", "#ff9800", "にゃんこスポーツ最新スクープ", "新レジェンドステージ＋超激レア追加＋コラボイベント", ["新ステージ", "超激レア", "コラボ"], "Operation Nyanko"),
    "Origin_Launch_Briefing.pdf": ("origin", "七つの大罪Origin", "Seven Deadly Sins Origin", "アクションRPG", "⚡", "#ff6f00", "Origin ローンチブリーフィング", "サービス開始＋リセマラTier表＋序盤攻略ガイド", ["ローンチ", "リセマラ", "攻略"], "Operation Origin"),
    "Othellonia_10th_Anniversary_Extra.pdf": ("othellonia", "オセロニア", "Othellonia", "ボードゲームRPG", "⚫", "#263238", "オセロニア10周年号外", "10周年＋新S+駒追加＋記念カップ開催", ["10周年", "新駒", "記念カップ"], "Operation Reversi"),
    "PawaSpo_Weekly_Game_Update.pdf": ("pawaspo", "パワスポ", "Power Sports", "スポーツ", "⚾", "#1565c0", "パワスポ 週刊ゲームアプデ", "新選手追加＋イベントマッチ＋育成システム改修", ["新選手", "イベント", "育成"], "Operation Power"),
    "PokoPoko_News_Flash.pdf": ("pokopoko", "ポコポコ", "LINE PokoPoko", "パズル", "🍀", "#4caf50", "ポコポコ ニュースフラッシュ", "新ステージ100面追加＋コラボイベント＋新ギミック実装", ["新ステージ", "コラボ", "新ギミック"], "Operation Clover"),
    "Pokémon_GO_February_Event_Forecast.pdf": ("pokemon-go", "ポケモンGO", "Pokémon GO", "位置情報ゲーム", "📍", "#4caf50", "ポケモンGO 2月イベント予報", "コミュニティデイ＋レイドボス更新＋新シーズン開幕", ["コミュデイ", "レイド", "新シーズン"], "Operation Catch"),
    "Port_News_Special_Edition.pdf": ("port", "ポートニュース", "Port News", "海洋SLG", "⚓", "#0277bd", "ポートニュース特別版", "新港追加＋艦隊編成ガイド＋大海戦イベント", ["新港", "編成", "大海戦"], "Operation Port"),
    "Priconne_Fes_2026_Day_One_Edition.pdf": ("priconne", "プリコネ", "Princess Connect! Re:Dive", "RPG", "👸", "#e91e63", "プリコネフェス2026 初日版", "フェス限定情報＋新キャラ＋アニメ新シーズン発表", ["フェス", "新キャラ", "アニメ"], "Operation Princess"),
    "ProSeka_Daily_Extra.pdf": ("proseka-extra", "プロセカ号外", "Project SEKAI Extra", "リズムゲーム号外", "🎵", "#00bcd4", "プロセカデイリー号外", "緊急メンテ報告＋新機能追加＋ランキングイベント開幕", ["緊急", "新機能", "ランキング"], "Operation Encore"),
    "Tact_Daily_Extra.pdf": ("dqtact", "DQタクト", "Dragon Quest Tact", "タクティクスRPG", "🐲", "#4caf50", "DQタクト デイリー号外", "新高難度クエスト＋才能開花追加＋闘技場シーズン更新", ["高難度", "才能開花", "闘技場"], "Operation Tactics"),
    "The_Battlegrounds_Gazette.pdf": ("battlegrounds", "バトルグラウンド", "Battlegrounds", "バトルロイヤル", "🪖", "#795548", "バトルグラウンドガゼット", "新マップ追加＋新武器＋シーズンパス報酬一覧", ["新マップ", "新武器", "シーズンパス"], "Operation Grounds"),
    "The_Kingdom_Strategy_Brief.pdf": ("kingdom", "キングダム", "The Kingdom", "ストラテジー", "👑", "#ffd600", "キングダム戦略ブリーフ", "新王国システム＋同盟戦リニューアル＋英雄追加", ["新システム", "同盟戦", "新英雄"], "Operation Crown"),
    "The_Sages_Times.pdf": ("sages", "賢者タイムズ", "The Sages Times", "RPG", "📜", "#4e342e", "賢者タイムズ", "新ダンジョン＋クラス覚醒＋ワールドボスイベント", ["新ダンジョン", "覚醒", "ボスイベント"], "Operation Wisdom"),
    "The_Scapes_Daily_Optimization.pdf": ("scapes", "スケープス", "The Scapes", "パズル＆建設", "🏡", "#66bb6a", "スケープス最適化デイリー", "新エリア開放＋パズルイベント＋デコレーション追加", ["新エリア", "パズル", "デコレーション"], "Operation Scapes"),
    "Toon_Blast_Essential_Report.pdf": ("toonblast", "トゥーンブラスト", "Toon Blast", "パズル", "💥", "#ffab00", "トゥーンブラスト必須レポート", "新ステージ200面＋チームイベント＋新ブースター実装", ["新ステージ", "チーム", "ブースター"], "Operation Toon"),
    "UNITE_Times_Breaking_News.pdf": ("unite", "ポケモンユナイト", "Pokémon UNITE", "MOBA", "⚡", "#7c4dff", "ユナイトタイムズ速報", "新ポケモン参戦＋バランスパッチ＋ランクシーズン更新", ["新ポケモン", "バランス", "ランクシーズン"], "Operation Unite"),
    # These 3 are untruncated from the find results
    "Uta_no_Prince_sama_Love_Live.pdf": ("utapri", "うたプリ", "Uta no Prince-sama", "リズム＆恋愛", "🎤", "#e040fb", "うたプリ ラブライブ速報", "新イベント＋限定カード＋コンサート情報", ["イベント", "限定", "コンサート"], "Operation Prince"),
    "VALORANT_Mobile_Debut_Report.pdf": ("valorant", "ヴァロラント", "VALORANT Mobile", "タクティカルFPS", "🎯", "#ff4655", "ヴァロラントモバイルデビューレポート", "モバイル版正式リリース＋新エージェント＋ランク仕様", ["リリース", "新エージェント", "ランク"], "Operation Radiant"),
    "Walker_Strategy_and_Collaboration.pdf": None,  # Already done
    "Version_64_Homecoming_Briefing.pdf": None,  # Already done
}

# Get the remaining truncated files
# Need to get the full list first

processed_slugs = set()
games_dir = os.path.join(BASE, "games")
for d in os.listdir(games_dir):
    p01 = os.path.join(games_dir, d, "issues")
    if os.path.isdir(p01):
        for issue_dir in os.listdir(p01):
            if os.path.exists(os.path.join(p01, issue_dir, "page-01.webp")):
                processed_slugs.add(d)

print(f"Already processed: {len(processed_slugs)} games")
print(f"PDF mappings defined: {len([v for v in PDF_MAP.values() if v is not None])}")

# Convert and generate
converted = 0
errors = []

pdfs_dir = BASE
for pdf_file in sorted(os.listdir(pdfs_dir)):
    if not pdf_file.endswith('.pdf'):
        continue
    if pdf_file not in PDF_MAP:
        print(f"SKIP (no mapping): {pdf_file}")
        continue
    mapping = PDF_MAP[pdf_file]
    if mapping is None:
        print(f"SKIP (already done): {pdf_file}")
        continue
    
    slug = mapping[0]
    if slug in processed_slugs:
        print(f"SKIP (converted): {pdf_file} -> {slug}")
        continue
    
    # Convert PDF
    out_dir = f"games/{slug}/issues/2026-02-14/"
    print(f"\nCONVERTING: {pdf_file} -> {out_dir}")
    result = subprocess.run(
        ["python", "scripts/convert-pdf.py", pdf_file, out_dir],
        cwd=BASE, capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        errors.append(f"{pdf_file}: {result.stderr}")
        print(f"  ERROR: {result.stderr[:100]}")
        continue
    
    # Count pages
    issue_path = os.path.join(BASE, out_dir)
    page_count = len([f for f in os.listdir(issue_path) if f.startswith("page-") and f.endswith(".webp")])
    
    slug, name_jp, name_en, genre, icon, color, title, summary, tags, codename = mapping
    
    # Update meta.json
    meta = {"title": title, "game": name_jp, "date": "2026-02-14",
            "codename": codename, "pageCount": page_count,
            "summary": summary, "tags": tags}
    with open(os.path.join(issue_path, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    converted += 1
    processed_slugs.add(slug)
    print(f"  OK: {page_count} pages")

print(f"\n{'='*50}")
print(f"Converted: {converted} new games")
print(f"Errors: {len(errors)}")
if errors:
    for e in errors:
        print(f"  - {e[:100]}")
print(f"Total processed: {len(processed_slugs)} games")
