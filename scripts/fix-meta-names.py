"""Fix game names in meta.json files for newly converted PDFs"""
import os, json

BASE = r"c:\Users\foo\Downloads\soshageshin"
new_games_json = os.path.join(BASE, "pdf_new", "_new_games.json")
with open(new_games_json, "r", encoding="utf-8") as f:
    new_games = json.load(f)

fixed = 0
for g in new_games:
    slug = g["slug"]
    name = g["name"]
    date = g["date"]
    meta_path = os.path.join(BASE, "games", slug, "issues", date, "meta.json")
    if not os.path.exists(meta_path):
        print(f"SKIP (no meta): {slug}")
        continue
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    old_game = meta.get("game", "")
    if old_game != name:
        meta["game"] = name
        meta["summary"] = f"{name}の最新情報まとめ"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        fixed += 1
        print(f'FIXED: {slug}: "{old_game}" -> "{name}"')
    else:
        print(f'OK: {slug}: "{name}"')

print(f"\nFixed: {fixed} meta.json files")
