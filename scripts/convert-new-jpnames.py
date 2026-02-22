"""Convert 3 new Japanese-named PDFs + download Play Store icons + regenerate site."""
import subprocess, os, json, ssl, urllib.request, re, time

BASE = r"c:\Users\foo\Downloads\soshageshin"
CONVERT_SCRIPT = os.path.join(BASE, "scripts", "convert-pdf.py")

NEW_PDFS = {
    "ファンパレ：2周年記念と2月最新攻略情報まとめ.pdf": {
        "slug": "fanpare",
        "date": "2026-02-15",
        "meta": {
            "title": "ファンパレ 2周年記念＆2月最新攻略",
            "game": "ファンパレ",
            "date": "2026-02-15",
            "codename": "Operation Fan Parade",
            "summary": "ファンパレ2周年記念イベント＋2月の最新攻略情報まとめ",
            "tags": ["RPG", "周年記念", "攻略情報"]
        },
        "package": "com.bandainamcoent.dbzfanpare"
    },
    "ラストウォー：サバイバル 2月最新攻略ガイド.pdf": {
        "slug": "last-war",
        "date": "2026-02-15",
        "meta": {
            "title": "ラストウォー：サバイバル 2月攻略ガイド",
            "game": "ラストウォー：サバイバル",
            "date": "2026-02-15",
            "codename": "Operation Last Stand",
            "summary": "ラストウォー：サバイバル最新攻略ガイド＋2月アプデ情報＋おすすめ編成",
            "tags": ["ストラテジー", "サバイバル", "攻略ガイド"]
        },
        "package": "com.fun.lastwar.gp"
    },
    "崩壊：スターレイル Ver.4.0 アップデート完全攻略ガイド.pdf": {
        "slug": "starrail",
        "date": "2026-02-15",
        "meta": {
            "title": "崩壊：スターレイル Ver.4.0 完全攻略",
            "game": "崩壊：スターレイル",
            "date": "2026-02-15",
            "codename": "Operation Astral Express",
            "summary": "崩壊スターレイルVer.4.0大型アップデート完全攻略＋新キャラ評価＋システム変更点",
            "tags": ["RPG", "大型アプデ", "攻略ガイド"]
        },
        "package": "com.HoYoverse.hkrpgoversea"
    }
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
            print(f"  Icon: OK ({len(data)//1024} KB)")
            return True
    except Exception as e:
        print(f"  Icon: Failed ({e})")
    return False

# Convert PDFs
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
        else:
            print("FAILED")
            continue

    # Download icon
    if info.get("package"):
        download_icon(slug, info["package"])
        time.sleep(0.5)

# Regenerate site
print("\nRegenerating site...")
result = subprocess.run(["python", os.path.join(BASE, "scripts", "generate-site.py")],
                       capture_output=True, text=True, cwd=BASE)
lines = result.stdout.strip().split('\n')
for line in lines[-5:]:
    print(line)
print("DONE!" if result.returncode == 0 else f"FAILED: {result.stderr[-200:]}")
