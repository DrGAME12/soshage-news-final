"""
Add new games from _new_games.json to games-registry.js
"""
import json, os, re

BASE = r"c:\Users\foo\Downloads\soshageshin"
NEW_GAMES_JSON = os.path.join(BASE, "pdf_new", "_new_games.json")
REGISTRY_FILE = os.path.join(BASE, "js", "games-registry.js")

# Load new games 
with open(NEW_GAMES_JSON, 'r', encoding='utf-8') as f:
    new_games = json.load(f)

# Read current registry to find existing slugs
with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
    registry_content = f.read()

existing_slugs = set(re.findall(r'slug:\s*"([^"]+)"', registry_content))
print(f"Existing slugs: {len(existing_slugs)}")

# Generate JS entries for new games
entries = []
for g in new_games:
    slug = g['slug']
    if slug in existing_slugs:
        print(f"  SKIP (exists): {slug}")
        continue
    
    name = g['name']
    date = g['date']
    title = g['title']
    page_count = g['pageCount']
    
    # Check if game directory actually exists
    issue_dir = os.path.join(BASE, "games", slug, "issues", date)
    if not os.path.isdir(issue_dir):
        print(f"  SKIP (no dir): {slug}")
        continue
    
    # Determine icon image (check for icon files)
    icon_image = ""
    icon_dir = os.path.join(BASE, "assets", "icons")
    possible_icons = [f"{slug}.webp", f"{slug}.png", f"{slug}.jpg"]
    for ic in possible_icons:
        if os.path.exists(os.path.join(icon_dir, ic)):
            icon_image = f"assets/icons/{ic}"
            break
    
    # Determine thumbnail
    thumb = f"games/{slug}/issues/{date}/page-01.webp"
    
    entry = {
        'slug': slug,
        'name': name,
        'nameEn': '',
        'genre': '最新情報',
        'icon': '📰',
        'iconImage': icon_image,
        'color': '#c9a03f',
        'latestIssue': {
            'date': date,
            'title': title,
            'thumbnail': thumb,
            'summary': f'{name}の最新情報まとめ',
            'tags': ['最新情報'],
            'pages': page_count,
        }
    }
    entries.append(entry)
    print(f"  ADD: {slug} ({name})")

print(f"\nNew entries to add: {len(entries)}")

if entries:
    # Generate JS code
    js_entries = []
    for e in entries:
        li = e['latestIssue']
        js = f"""  {{
    slug: "{e['slug']}",
    name: "{e['name']}",
    nameEn: "{e['nameEn']}",
    genre: "{e['genre']}",
    icon: "{e['icon']}",
    iconImage: "{e['iconImage']}",
    color: "{e['color']}",
    latestIssue: {{
      date: "{li['date']}",
      title: "{li['title']}",
      thumbnail: "{li['thumbnail']}",
      summary: "{li['summary']}",
      tags: {json.dumps(li['tags'], ensure_ascii=False)},
      pages: {li['pages']}
    }}
  }}"""
        js_entries.append(js)
    
    # Find the closing bracket of the GAMES array
    # Insert before the last "];"
    insert_text = ",\n" + ",\n".join(js_entries)
    
    # Find last "];" in registry
    last_bracket = registry_content.rfind("];")
    if last_bracket == -1:
        print("[ERROR] Could not find end of GAMES array")
    else:
        new_content = registry_content[:last_bracket] + insert_text + "\n" + registry_content[last_bracket:]
        with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"[OK] Added {len(entries)} entries to games-registry.js")
