"""Convert batch 10: new PDFs + copy original.pdf for existing games + regenerate site."""
import subprocess, os, json, ssl, urllib.request, re, time, shutil

BASE = r"c:\Users\foo\Downloads\soshageshin"
DOWNLOADS = r"c:\Users\foo\Downloads"
CONVERT_SCRIPT = os.path.join(BASE, "scripts", "convert-pdf.py")

# ── NEW GAMES (need full conversion) ──────────────────────────
NEW_PDFS = {
    "GBO2_Strategic_Update_2026.pdf": {
        "slug": "gbo2",
        "date": "2026-02-22",
        "meta": {
            "title": "ガンダムバトオペ2 戦略アップデート2026",
            "game": "ガンダムバトルオペレーション2",
            "date": "2026-02-22",
            "codename": "Operation Battle Operation",
            "summary": "ガンダムバトルオペレーション2最新戦略アップデート＋新機体＋環境分析",
            "tags": ["アクション", "アプデ情報", "新機体"]
        },
        "package": "jp.co.bandainamcoent.gbo2"
    },
    "Durability_Warfare_2026.pdf": {
        "slug": "durability-warfare",
        "date": "2026-02-15",
        "meta": {
            "title": "耐久戦争 2026年最新攻略ガイド",
            "game": "耐久戦争",
            "date": "2026-02-15",
            "codename": "Operation Durability",
            "summary": "耐久戦争2026年最新攻略＋イベント情報＋おすすめ編成",
            "tags": ["RPG", "攻略ガイド", "イベント"]
        },
        "package": None
    },
}

# ── EXISTING GAMES (just copy original.pdf) ────────────────────
COPY_PDFS = {
    "HUNTER×HUNTER NEN×SURVIVORネンサバ：初動攻略ガイド.pdf": {
        "slug": "hunter",
        "date": "2026-02-18",
    },
    "忍者と極道 沸闘戦祭（ブッコロフェスタ） ユーザーが欲しい最新情報 2026-02-18.pdf": {
        "slug": "ninja",
        "date": "2026-02-18",
    },
    "Ragnador_Yokai_World_Expansion.pdf": {
        "slug": "ragnador",
        "date": "2026-02-13",
    },
    "Shadowverse_Worlds_Beyond_A_New_Order.pdf": {
        "slug": "shadowverse",
        "date": "2026-02-14",
    },
    "Mecha_Frontline_Gazette_2026_Debrief.pdf": {
        "slug": "armored-frontline-warzone",
        "date": "2026-02-17",
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        matches = re.findall(r'(https://play-lh\.googleusercontent\.com/[^"\'>\\s]+)', html)
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

# ═══════════ STEP 1: Convert new PDFs ═══════════
print("=" * 60)
print("STEP 1: Converting new PDFs")
print("=" * 60)
success = 0
for pdf_name, info in NEW_PDFS.items():
    slug = info["slug"]
    date = info["date"]
    pdf_path = os.path.join(DOWNLOADS, pdf_name)
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
        result = subprocess.run(["python", CONVERT_SCRIPT, pdf_path, out_dir],
                       capture_output=True, text=True, cwd=BASE)
        if result.returncode != 0:
            print(f"FAILED\n  {result.stderr[:200]}")
            continue
        pages = len([f for f in os.listdir(out_dir) if f.startswith("page-") and f.endswith(".webp")])
        if pages > 0:
            meta = info["meta"].copy()
            meta["pageCount"] = pages
            with open(os.path.join(out_dir, "meta.json"), "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
            print(f"OK ({pages}p)")
            success += 1
        else:
            print("FAILED (0 pages)")
            continue
    if info.get("package"):
        download_icon(slug, info["package"])
        time.sleep(0.3)

print(f"\nNew conversions: {success}/{len(NEW_PDFS)}")

# ═══════════ STEP 2: Copy original.pdf to existing games ═══════════
print("\n" + "=" * 60)
print("STEP 2: Copying original.pdf to existing games")
print("=" * 60)
copied = 0
for pdf_name, info in COPY_PDFS.items():
    slug = info["slug"]
    date = info["date"]
    pdf_path = os.path.join(DOWNLOADS, pdf_name)
    out_dir = os.path.join(BASE, "games", slug, "issues", date)
    dest_pdf = os.path.join(out_dir, "original.pdf")
    if not os.path.exists(pdf_path):
        print(f"SKIP (not found): {pdf_name}")
        continue
    if os.path.exists(dest_pdf):
        print(f"SKIP (exists): {slug}/{date}/original.pdf")
        copied += 1
        continue
    if not os.path.isdir(out_dir):
        print(f"SKIP (no issue dir): {slug}/{date}/")
        continue
    shutil.copy2(pdf_path, dest_pdf)
    print(f"Copied: {slug}/{date}/original.pdf")
    copied += 1

print(f"\nCopied: {copied}/{len(COPY_PDFS)}")

# ═══════════ STEP 3: Regenerate site ═══════════
print("\n" + "=" * 60)
print("STEP 3: Regenerating site...")
print("=" * 60)
result = subprocess.run(["python", os.path.join(BASE, "scripts", "generate-site.py")],
                       capture_output=True, text=True, cwd=BASE)
for line in result.stdout.strip().split('\n')[-10:]:
    print(line)
if result.returncode != 0:
    print("STDERR:", result.stderr[:500])

print("\nDone!")
