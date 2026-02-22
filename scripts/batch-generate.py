"""Batch generate viewer + game pages for all new games."""
import os, json

GAMES = [
    {
        "slug": "5th-anniversary", "name": "5周年記念ゲーム", "nameEn": "5th Anniversary",
        "genre": "記念イベント", "icon": "🎉", "color": "#f39c12",
        "issue": {"date": "2026-02-14", "title": "5周年速報 号外", "pages": 11,
                  "summary": "5周年記念大型アップデート＋無料ガチャ100連＋コラボ情報解禁",
                  "tags": ["記念イベント", "無料ガチャ", "コラボ"], "codename": "Operation Golden Jubilee"}
    },
    {
        "slug": "grand-open", "name": "グランドオープン", "nameEn": "Grand Open",
        "genre": "サバイバルRPG", "icon": "🏕️", "color": "#27ae60",
        "issue": {"date": "2026-02-14", "title": "グランドオープン サバイバルガイド", "pages": 15,
                  "summary": "新サーバー開放＋初心者向け攻略ガイド＋最強キャラTier表",
                  "tags": ["新サーバー", "攻略ガイド", "Tier表"], "codename": "Operation Wild Frontier"}
    },
    {
        "slug": "memento-mori", "name": "メメントモリ", "nameEn": "Memento Mori",
        "genre": "放置系RPG", "icon": "💀", "color": "#8e44ad",
        "issue": {"date": "2026-02-14", "title": "メメントモリ 戦略レビュー", "pages": 12,
                  "summary": "新章追加＋PvPメタ分析＋キャラ育成効率ランキング",
                  "tags": ["新章", "PvP", "育成"], "codename": "Operation Memento"}
    },
    {
        "slug": "monster-strike", "name": "モンスト", "nameEn": "Monster Strike",
        "genre": "ひっぱりアクション", "icon": "🔮", "color": "#e74c3c",
        "issue": {"date": "2026-02-14", "title": "モンスト2月戦報", "pages": 10,
                  "summary": "新超絶クエスト追加＋獣神化改キャラ情報＋コラボイベント速報",
                  "tags": ["超絶クエスト", "獣神化改", "コラボ"], "codename": "Operation Strike Force"}
    },
    {
        "slug": "pad", "name": "パズドラ", "nameEn": "Puzzle & Dragons",
        "genre": "パズルRPG", "icon": "🐉", "color": "#d35400",
        "issue": {"date": "2026-02-14", "title": "パズドラZERO ガチャフリーの未来", "pages": 15,
                  "summary": "ガチャ廃止宣言＋新育成システム「錬成」実装＋ランキングダンジョン改革",
                  "tags": ["ガチャ改革", "新システム", "ランキング"], "codename": "Operation Dragon Zero"}
    },
    {
        "slug": "pokemon", "name": "ポケモン", "nameEn": "Pokémon",
        "genre": "RPG / コレクション", "icon": "⚡", "color": "#f1c40f",
        "issue": {"date": "2026-02-14", "title": "ポケモン30周年カウントダウン", "pages": 12,
                  "summary": "30周年記念イベント詳細＋新ポケモン先行公開＋歴代シリーズ振り返り",
                  "tags": ["30周年", "新ポケモン", "記念イベント"], "codename": "Operation Thunder Anniversary"}
    },
    {
        "slug": "project-sekai", "name": "プロセカ", "nameEn": "Project SEKAI",
        "genre": "リズムゲーム", "icon": "🎵", "color": "#3498db",
        "issue": {"date": "2026-02-14", "title": "セカイニュース 2026年2月号", "pages": 9,
                  "summary": "バレンタインイベント＋新楽曲5曲追加＋ランキング結果発表",
                  "tags": ["イベント", "新楽曲", "ランキング"], "codename": "Operation Harmony"}
    },
    {
        "slug": "shadowverse", "name": "シャドウバース", "nameEn": "Shadowverse",
        "genre": "デジタルカードゲーム", "icon": "🃏", "color": "#2c3e50",
        "issue": {"date": "2026-02-14", "title": "シャドバ Worlds Beyond 新秩序", "pages": 12,
                  "summary": "新拡張パック「Worlds Beyond」全カード評価＋環境予測＋デッキレシピ",
                  "tags": ["新拡張", "カード評価", "デッキレシピ"], "codename": "Operation Dark Arcana"}
    },
    {
        "slug": "version64", "name": "原神 Ver.6.4", "nameEn": "Genshin Impact",
        "genre": "オープンワールドRPG", "icon": "🌟", "color": "#1abc9c",
        "issue": {"date": "2026-02-14", "title": "原神 Ver.6.4 帰郷作戦ブリーフィング", "pages": 12,
                  "summary": "Ver.6.4新エリア＋新キャラ2体＋螺旋攻略＋復帰勢向けガイド",
                  "tags": ["新バージョン", "新キャラ", "攻略"], "codename": "Operation Homecoming"}
    },
    {
        "slug": "walker", "name": "ニケ×ウォーカー", "nameEn": "Walker Collab",
        "genre": "コラボ特集", "icon": "🚶", "color": "#e67e22",
        "issue": {"date": "2026-02-14", "title": "ウォーカー戦略＆コラボ特報", "pages": 12,
                  "summary": "大型コラボ発表＋コラボキャラ性能解析＋イベント攻略マップ",
                  "tags": ["コラボ", "新キャラ", "攻略マップ"], "codename": "Operation Walker"}
    },
    {
        "slug": "wuthering-waves", "name": "鳴潮", "nameEn": "Wuthering Waves",
        "genre": "アクションRPG", "icon": "🌊", "color": "#2980b9",
        "issue": {"date": "2026-02-14", "title": "鳴潮 Ver.3.1 始動ガイド", "pages": 11,
                  "summary": "Ver.3.1新エリア＋新共鳴者＋深淵攻略＋ガチャ分析",
                  "tags": ["新バージョン", "新キャラ", "ガチャ分析"], "codename": "Operation Tidal Wave"}
    },
]

BASE = r"c:\Users\foo\Downloads\soshageshin"

VIEWER_TEMPLATE = '''<!DOCTYPE html>
<html lang="ja" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>{title} — ソシャゲ新聞</title>
  <meta name="description" content="{summary}">
  <meta property="og:title" content="{title} — ソシャゲ新聞">
  <meta property="og:description" content="{summary}">
  <meta property="og:type" content="article">
  <meta property="og:image" content="page-01.webp">
  <meta name="twitter:card" content="summary_large_image">
  <script type="application/ld+json">{{"@context":"https://schema.org","@type":"Article","headline":"{title}","datePublished":"{date}","publisher":{{"@type":"Organization","name":"ソシャゲ新聞"}},"image":"page-01.webp"}}</script>
  <link rel="stylesheet" href="../../../../css/style.css">
</head>
<body>
  <div id="viewerMeta" data-title="{title}" data-pagecount="{pages}" data-date="{date}" data-basepath="./" data-pdffile="original.pdf" data-hasimages="true" data-game="{gameName}" data-gameslug="{slug}" data-summary="{summary}" data-tags="{tagsStr}"></div>
  <div class="viewer-header">
    <div class="viewer-header__left">
      <a class="viewer-header__back" href="../../index.html">◀</a>
      <span class="viewer-header__title" id="viewerTitle">{title}</span>
    </div>
    <div class="viewer-header__right">
      <span class="viewer-header__page" id="pageIndicator">1 / {pages}</span>
      <a class="viewer-header__dl" id="viewerDownload" href="./original.pdf" download>📥 <span>PDF</span></a>
      <button class="theme-toggle" id="themeToggle" onclick="toggleTheme()">☀️</button>
    </div>
  </div>
  <div class="viewer-progress"><div class="viewer-progress__bar" id="progressBar"></div></div>
  <main class="viewer-page">
    <div class="viewer-pages" id="viewerPages"></div>
    <div class="viewer-footer">
      <div class="viewer-footer__nav"><a class="viewer-footer__btn" href="../../index.html">◀ {gameName}一覧</a></div>
      <a class="viewer-footer__btn" href="./original.pdf" download>📥 PDFダウンロード</a>
    </div>
  </main>
  <footer class="footer"><div class="footer__stamp">END OF DISPATCH</div><p>SOSHAGESHIN FIELD INTELLIGENCE</p></footer>
  <script src="../../../../js/storage.js"></script>
  <script src="../../../../js/theme.js"></script>
  <script src="../../../../js/sns.js"></script>
  <script src="../../../../js/games-registry.js"></script>
  <script src="../../../../js/viewer.js"></script>
</body>
</html>'''

GAME_TEMPLATE = '''<!DOCTYPE html>
<html lang="ja" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>{gameName} — ソシャゲ新聞</title>
  <meta name="description" content="{gameName}の最新アップデート情報">
  <meta property="og:title" content="{gameName} — ソシャゲ新聞">
  <meta property="og:image" content="issues/{date}/page-01.webp">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="stylesheet" href="../../css/style.css">
</head>
<body>
  <header class="masthead masthead--compact">
    <a href="../../index.html" style="text-decoration:none"><h1 class="masthead__title">ソシャゲ新聞</h1></a>
    <hr class="masthead__divider">
  </header>
  <button class="theme-toggle" id="themeToggle" onclick="toggleTheme()">☀️</button>
  <main class="game-page">
    <nav class="breadcrumb"><a href="../../index.html">TOP</a> / {gameName}</nav>
    <div class="game-hero">
      <div class="game-hero__icon">{icon}</div>
      <div class="game-hero__info">
        <h2 class="game-hero__name">{gameName}</h2>
        <div class="game-hero__name-en">{nameEn}</div>
        <div class="game-hero__meta">{genre} ─ ACTIVE</div>
      </div>
    </div>
    <section class="index-section">
      <div class="section__header">
        <span class="section__badge">ARCHIVE</span>
        <h2 class="section__title">発行済み戦報<span class="section__title-jp">Past Dispatches</span></h2>
      </div>
      <div class="issue-list">
        <a class="issue-item" href="issues/{date}/index.html">
          <span class="issue-item__date">{dateShort}</span>
          <div>
            <div class="issue-item__title">{title}</div>
            <div class="issue-item__summary">{summary}</div>
          </div>
          <span class="issue-item__pages">{pages} pages</span>
        </a>
      </div>
    </section>
  </main>
  <footer class="footer"><div class="footer__stamp">SOSHAGESHIN HQ</div><p>SOSHAGESHIN FIELD INTELLIGENCE — ALL RIGHTS RESERVED</p></footer>
  <script src="../../js/storage.js"></script>
  <script src="../../js/theme.js"></script>
</body>
</html>'''

for g in GAMES:
    i = g["issue"]
    slug = g["slug"]
    
    # Viewer page
    viewer_dir = os.path.join(BASE, "games", slug, "issues", i["date"])
    viewer_path = os.path.join(viewer_dir, "index.html")
    with open(viewer_path, "w", encoding="utf-8") as f:
        f.write(VIEWER_TEMPLATE.format(
            title=i["title"], summary=i["summary"], date=i["date"],
            pages=i["pages"], gameName=g["name"], slug=slug,
            tagsStr=",".join(i["tags"])
        ))
    
    # Game page
    game_path = os.path.join(BASE, "games", slug, "index.html")
    with open(game_path, "w", encoding="utf-8") as f:
        f.write(GAME_TEMPLATE.format(
            gameName=g["name"], nameEn=g["nameEn"], genre=g["genre"],
            icon=g["icon"], title=i["title"], summary=i["summary"],
            date=i["date"], dateShort=i["date"][5:], pages=i["pages"]
        ))
    
    # Update meta.json
    meta_path = os.path.join(viewer_dir, "meta.json")
    meta = {
        "title": i["title"], "game": g["name"], "date": i["date"],
        "codename": i["codename"], "pageCount": i["pages"],
        "summary": i["summary"], "tags": i["tags"]
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    print(f"OK: {slug} ({i['pages']} pages)")

print("\nAll done!")
