"""
Generate viewer + game HTML pages for ALL games that have converted pages but no index.html.
Also rebuild games-registry.js, sitemap.xml, and feed.xml from meta.json files.
"""
import os, json, glob

BASE = r"c:\Users\foo\Downloads\soshageshin"
GAMES_DIR = os.path.join(BASE, "games")

# Game metadata not in meta.json (icon, color, genre, nameEn)
GAME_EXTRA = {
    "5th-anniversary": ("🎉", "#f39c12", "記念イベント", "5th Anniversary"),
    "all-star": ("⭐", "#ff9800", "クロスオーバー", "All Star"),
    "arknights": ("🛡️", "#1abc9c", "タワーディフェンス", "Arknights"),
    "ask-kingdom": ("🏰", "#795548", "ストラテジー", "Ash Kingdom"),
    "battlegrounds": ("🪖", "#795548", "バトルロイヤル", "Battlegrounds"),
    "blue-archive": ("🎓", "#4a90d9", "学園RPG", "Blue Archive"),
    "codm": ("🎯", "#4caf50", "FPS", "Call of Duty Mobile"),
    "dereste": ("🎤", "#e91e63", "リズムゲーム", "CINDERELLA GIRLS"),
    "dingjun": ("⛰️", "#4e342e", "三国志SLG", "Mt. Dingjun"),
    "dokkan": ("🐉", "#ff5722", "アクションRPG", "Dokkan Battle"),
    "dqtact": ("🐲", "#4caf50", "タクティクスRPG", "Dragon Quest Tact"),
    "dual-ambition": ("🗡️", "#607d8b", "戦略RPG", "Dual Ambition"),
    "durability-warfare": ("⚔️", "#e67e22", "耐久バトルRPG", "Durability Warfare"),
    "enstars": ("🌟", "#ff4081", "リズム＆ADV", "Ensemble Stars!!"),
    "ex-rarity": ("💎", "#9c27b0", "大型アプデ特報", "EX Rarity Update"),
    "feb-dual": ("📋", "#455a64", "合同特報", "Dual Game Briefing"),
    "garupa": ("🎸", "#e91e63", "リズムゲーム", "BanG Dream!"),
    "grand-open": ("🏕️", "#27ae60", "サバイバルRPG", "Grand Open"),
    "granblue": ("⚓", "#03a9f4", "RPG", "Granblue Fantasy"),
    "heban": ("🔥", "#d32f2f", "ドラマRPG", "Heaven Burns Red"),
    "identity-v": ("🎭", "#37474f", "非対称対戦", "Identity V"),
    "idolish7": ("🎶", "#7b1fa2", "アイドル育成", "IDOLiSH7"),
    "kingdom": ("👑", "#ffd600", "ストラテジー", "The Kingdom"),
    "lineage": ("🏹", "#827717", "MMORPG", "Lineage"),
    "mahjongsoul": ("🀄", "#1b5e20", "麻雀", "Mahjong Soul"),
    "masterduel": ("🃏", "#f57f17", "カードゲーム", "Master Duel"),
    "mecha-frontline": ("🤖", "#3498db", "メカアクション", "Mecha Frontline"),
    "memento-mori": ("💀", "#8e44ad", "放置系RPG", "Memento Mori"),
    "monster-strike": ("🔮", "#e74c3c", "ひっぱりアクション", "Monster Strike"),
    "naruto-ninja": ("🍥", "#ff6600", "忍者アクションRPG", "Naruto Ninja"),
    "nikke": ("🔫", "#e74c3c", "TPS / RPG", "NIKKE"),
    "nyanko": ("🐱", "#ff9800", "タワーディフェンス", "The Battle Cats"),
    "origin": ("⚡", "#ff6f00", "アクションRPG", "Seven Deadly Sins"),
    "othellonia": ("⚫", "#263238", "ボードゲームRPG", "Othellonia"),
    "pad": ("🐉", "#d35400", "パズルRPG", "Puzzle & Dragons"),
    "pawaspo": ("⚾", "#1565c0", "スポーツ", "Power Sports"),
    "pokopoko": ("🍀", "#4caf50", "パズル", "LINE PokoPoko"),
    "pokemon": ("⚡", "#f1c40f", "RPG / コレクション", "Pokémon"),
    "pokemon-go": ("📍", "#4caf50", "位置情報ゲーム", "Pokémon GO"),
    "port": ("⚓", "#0277bd", "海洋SLG", "Port News"),
    "priconne": ("👸", "#e91e63", "RPG", "Princess Connect!"),
    "project-sekai": ("🎵", "#3498db", "リズムゲーム", "Project SEKAI"),
    "proseka-extra": ("🎵", "#00bcd4", "リズムゲーム号外", "Project SEKAI Extra"),
    "ragnador": ("👹", "#9b59b6", "妖怪アクションRPG", "RAGNADOR"),
    "romasaga": ("⚔️", "#c62828", "RPG", "Romancing SaGa RS"),
    "sages": ("📜", "#4e342e", "RPG", "The Sages Times"),
    "scapes": ("🏡", "#66bb6a", "パズル＆建設", "The Scapes"),
    "shadowverse": ("🃏", "#2c3e50", "デジタルカードゲーム", "Shadowverse"),
    "7th-anniv": ("🎂", "#e91e63", "記念特報", "7th Anniversary"),
    "toonblast": ("💥", "#ffab00", "パズル", "Toon Blast"),
    "touken": ("⚔️", "#5d4037", "刀剣育成SLG", "Touken Ranbu"),
    "twisted": ("🐦‍⬛", "#311b92", "ADV", "Twisted Wonderland"),
    "unite": ("⚡", "#7c4dff", "MOBA", "Pokémon UNITE"),
    "utapri": ("🎤", "#e040fb", "リズム＆恋愛", "Uta no Prince-sama"),
    "valorant": ("🎯", "#ff4655", "タクティカルFPS", "VALORANT Mobile"),
    "version64": ("🌟", "#1abc9c", "オープンワールドRPG", "Genshin Impact"),
    "walker": ("🚶", "#e67e22", "コラボ特集", "Walker Collab"),
    "wuthering-waves": ("🌊", "#2980b9", "アクションRPG", "Wuthering Waves"),
}

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
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Oswald:wght@400;600;700&family=Share+Tech+Mono&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../../../css/style.css">
</head>
<body>
  <div id="viewerMeta" data-title="{title}" data-pagecount="{pages}" data-date="{date}" data-basepath="./" data-pdffile="original.pdf" data-hasimages="true" data-game="{gameName}" data-gameslug="{slug}" data-summary="{summary}" data-tags="{tagsStr}"></div>

  <!-- ═══════════════════ APP BAR ═══════════════════ -->
  <header class="app-bar" id="viewerAppBar">
    <button class="app-bar__hamburger" id="hamburgerBtn" aria-label="メニュー">
      <span></span><span></span><span></span>
    </button>
    <a class="app-bar__title" href="../../../../index.html" style="text-decoration:none;color:inherit">ソシャゲ新聞</a>
    <button class="app-bar__search-btn" id="searchBtn" aria-label="検索">🔍</button>
  </header>

  <!-- ═══════════════════ HAMBURGER MENU ═══════════════════ -->
  <div class="menu-overlay" id="menuOverlay"></div>
  <nav class="slide-menu" id="slideMenu">
    <div class="slide-menu__header">
      <span class="slide-menu__brand">SOSHAGESHIN</span>
      <button class="slide-menu__close" id="menuClose">✕</button>
    </div>
    <div class="slide-menu__section-label">メニュー</div>
    <a class="slide-menu__link" href="../../../../index.html#recommendSection">🔥 急上昇</a>
    <a class="slide-menu__link" href="../../../../index.html#rankingList">👑 人気ランキング</a>
    <a class="slide-menu__link" href="../../../../index.html#dispatchFeed">❤️ 高評価数</a>
    <div class="slide-menu__section-label">最新ゲーム一覧</div>
    <div class="slide-menu__game-list" id="menuGameList"></div>
    <div class="slide-menu__footer">
      <button class="slide-menu__theme-btn" id="menuThemeToggle" onclick="toggleTheme()">🌙 テーマ切替</button>
    </div>
  </nav>

  <!-- ═══════════════════ SEARCH OVERLAY ═══════════════════ -->
  <div class="search-popup-overlay" id="searchOverlay">
    <div class="search-popup">
      <div class="search-popup__title">検索</div>
      <div class="search-popup__bar">
        <input type="text" class="search-popup__input" id="searchInput" placeholder="" autocomplete="off">
        <button class="search-popup__icon" aria-label="検索">🔍</button>
      </div>
      <div class="search-popup__results" id="searchResults"></div>
      <button class="search-popup__close" id="searchClose">✕</button>
    </div>
  </div>

  <!-- ═══════════════════ VIEWER ═══════════════════ -->
  <div class="viewer-header" id="viewerHeader">
    <div class="viewer-header__left">
      <span class="viewer-header__title" id="viewerTitle">{title}</span>
    </div>
    <div class="viewer-header__right">
      <span class="viewer-header__page" id="pageIndicator">1 / {pages}</span>
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
      <div class="issue-list">{issueItems}</div>
    </section>
  </main>
  <footer class="footer"><div class="footer__stamp">SOSHAGESHIN HQ</div><p>SOSHAGESHIN FIELD INTELLIGENCE — ALL RIGHTS RESERVED</p></footer>
  <script src="../../js/storage.js"></script>
  <script src="../../js/theme.js"></script>
</body>
</html>'''

ISSUE_ITEM = '''
        <a class="issue-item" href="issues/{date}/index.html">
          <span class="issue-item__date">{dateShort}</span>
          <div>
            <div class="issue-item__title">{title}</div>
            <div class="issue-item__summary">{summary}</div>
          </div>
          <span class="issue-item__pages">{pages} pages</span>
        </a>'''

# Collect all games
all_games = []
for slug in sorted(os.listdir(GAMES_DIR)):
    game_path = os.path.join(GAMES_DIR, slug)
    if not os.path.isdir(game_path):
        continue
    issues_dir = os.path.join(game_path, "issues")
    if not os.path.isdir(issues_dir):
        continue
    
    extra = GAME_EXTRA.get(slug, ("🎮", "#607d8b", "ゲーム", slug.replace("-", " ").title()))
    icon, color, genre, name_en = extra
    
    issues = []
    for issue_date in sorted(os.listdir(issues_dir), reverse=True):
        meta_path = os.path.join(issues_dir, issue_date, "meta.json")
        if not os.path.exists(meta_path):
            continue
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        page_count = len([p for p in os.listdir(os.path.join(issues_dir, issue_date)) if p.startswith("page-") and p.endswith(".webp")])
        if page_count == 0:
            continue
        meta["pageCount"] = page_count
        meta["issueDate"] = issue_date
        issues.append(meta)
    
    if not issues:
        continue
    
    latest = issues[0]
    game_name = latest.get("game", slug)
    
    # Generate viewer pages
    for issue in issues:
        viewer_path = os.path.join(issues_dir, issue["issueDate"], "index.html")
        tags = issue.get("tags", [])
        with open(viewer_path, "w", encoding="utf-8") as f:
            f.write(VIEWER_TEMPLATE.format(
                title=issue["title"], summary=issue.get("summary", ""),
                date=issue["issueDate"], pages=issue["pageCount"],
                gameName=game_name, slug=slug,
                tagsStr=",".join(tags) if tags else ""
            ))
    
    # Generate game page
    issue_items_html = ""
    for issue in issues:
        issue_items_html += ISSUE_ITEM.format(
            date=issue["issueDate"], dateShort=issue["issueDate"][5:],
            title=issue["title"], summary=issue.get("summary", ""),
            pages=issue["pageCount"]
        )
    
    game_page_path = os.path.join(game_path, "index.html")
    with open(game_page_path, "w", encoding="utf-8") as f:
        f.write(GAME_TEMPLATE.format(
            gameName=game_name, nameEn=name_en, genre=genre, icon=icon,
            date=latest["issueDate"], issueItems=issue_items_html
        ))
    
    has_icon_img = os.path.exists(os.path.join(game_path, "icon.png")) and os.path.getsize(os.path.join(game_path, "icon.png")) > 1000
    all_games.append({
        "slug": slug, "name": game_name, "nameEn": name_en,
        "genre": genre, "icon": icon, "color": color,
        "hasIconImage": has_icon_img,
        "latest": latest
    })
    print(f"OK: {slug} ({game_name}) - {len(issues)} issue(s), {latest['pageCount']}p latest")

# Generate games-registry.js
registry_entries = []
for g in all_games:
    lat = g["latest"]
    tags_js = ", ".join([f'"{t}"' for t in lat.get("tags", [])])
    icon_img_line = f'\n        iconImage: "games/{g["slug"]}/icon.png",' if g['hasIconImage'] else ''
    entry = f'''    {{
        slug: "{g['slug']}",
        name: "{g['name']}",
        nameEn: "{g['nameEn']}",
        genre: "{g['genre']}",
        status: "active",
        color: "{g['color']}",
        icon: "{g['icon']}",{icon_img_line}
        latestIssue: {{
            date: "{lat['issueDate']}",
            title: "{lat['title']}",
            codename: "{lat.get('codename', '')}",
            pageCount: {lat['pageCount']},
            summary: "{lat.get('summary', '')}",
            tags: [{tags_js}],
            thumbnail: "games/{g['slug']}/issues/{lat['issueDate']}/page-01.webp"
        }}
    }}'''
    registry_entries.append(entry)

registry_js = f'''// ============================================================
//  SOSHAGESHIN — Games Registry (auto-generated)
//  {len(all_games)} games registered
// ============================================================

const GAMES = [
{(","+chr(10)).join(registry_entries)}
];

function getAllTags() {{
    const tags = new Set();
    GAMES.forEach(g => {{
        if (g.latestIssue.tags) g.latestIssue.tags.forEach(t => tags.add(t));
    }});
    return [...tags];
}}
'''

with open(os.path.join(BASE, "js", "games-registry.js"), "w", encoding="utf-8") as f:
    f.write(registry_js)

# Generate sitemap.xml
sitemap_urls = ['  <url><loc>https://soshageshin.pages.dev/</loc><lastmod>2026-02-14</lastmod><priority>1.0</priority></url>']
for g in all_games:
    lat = g["latest"]
    sitemap_urls.append(f'  <url><loc>https://soshageshin.pages.dev/games/{g["slug"]}/index.html</loc><lastmod>{lat["issueDate"]}</lastmod><priority>0.8</priority></url>')
    sitemap_urls.append(f'  <url><loc>https://soshageshin.pages.dev/games/{g["slug"]}/issues/{lat["issueDate"]}/index.html</loc><lastmod>{lat["issueDate"]}</lastmod><priority>0.9</priority></url>')

sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(sitemap_urls)}
</urlset>'''

with open(os.path.join(BASE, "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write(sitemap)

# Generate feed.xml
feed_items = []
sorted_games = sorted(all_games, key=lambda g: g["latest"]["issueDate"], reverse=True)
for g in sorted_games:
    lat = g["latest"]
    feed_items.append(f'''    <item>
      <title>{lat["title"]} — {g["name"]}</title>
      <link>https://soshageshin.pages.dev/games/{g["slug"]}/issues/{lat["issueDate"]}/index.html</link>
      <description>{lat.get("summary", "")}</description>
      <pubDate>{lat["issueDate"]}</pubDate>
      <guid>{g["slug"]}_{lat["issueDate"]}</guid>
    </item>''')

feed = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>ソシャゲ新聞 — SOSHAGESHIN</title>
    <link>https://soshageshin.pages.dev/</link>
    <description>ソシャゲのアップデート情報を軍事新聞風にまとめた戦域情報サイト</description>
    <language>ja</language>
    <atom:link href="https://soshageshin.pages.dev/feed.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(feed_items)}
  </channel>
</rss>'''

with open(os.path.join(BASE, "feed.xml"), "w", encoding="utf-8") as f:
    f.write(feed)

print(f"\n{'='*50}")
print(f"Total games: {len(all_games)}")
print(f"Registry: games-registry.js ({len(all_games)} entries)")
print(f"Sitemap: {len(sitemap_urls)} URLs")
print(f"Feed: {len(feed_items)} RSS items")
print("DONE!")
