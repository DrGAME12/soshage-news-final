"""
Retry downloading icons with corrected package IDs.
For fictional games without Play Store presence, skip.
"""
import urllib.request, re, os, ssl, time

BASE = r"c:\Users\foo\Downloads\soshageshin"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Corrected package IDs for real games that failed
RETRY_MAP = {
    "arknights": "com.YostarJP.Arknights",
    "enstars": "jp.happyelements.ensemblestars",
    "heban": "jp.wrightflyer.hbr",
    "identity-v": "com.netease.idv",
    "idolish7": "com.bandainamcoent.BNEI0166",
    "mahjongsoul": "com.YostarJP.MajSoul",
    "memento-mori": "jp.co.bankofinnov.mementomori",
    "naruto-ninja": "com.bandainamcoent.BNEI0277",
    "othellonia": "com.DeNA.Othellonia",
    "pokemon": "jp.pokemon.pokemontcgp",
    "ragnador": "jp.co.grams.ragnador",
    "touken": "jp.co.nitroplus.toukenranbuonline",
    "twisted": "com.aniplex.twistedwonderland",
    "ask-kingdom": "com.lilithgames.roc.gp",
}

# Alternative package IDs to try if primary fails
ALT_PACKAGES = {
    "arknights": ["com.hypergryph.arknights", "com.YostarJP.Arknights"],
    "enstars": ["jp.happyelements.ensemblestars", "com.happyelements.ensemblestars_music_jp", "com.happyelements.ensemblestarsjp"],
    "heban": ["jp.wrightflyer.hbr", "com.wrightflyerstudios.hbr"],
    "identity-v": ["com.netease.idv", "com.netease.idv.jp", "com.netease.idv.googleplay"],
    "idolish7": ["com.bandainamcoent.BNEI0166", "com.bandainamcoent.idolish7"],
    "mahjongsoul": ["com.YostarJP.MajSoul", "com.yostar.mahjongsoul"],
    "memento-mori": ["jp.co.bankofinnov.mementomori", "com.bankofinnov.mementomori"],
    "naruto-ninja": ["com.bandainamcoent.BNEI0277", "com.bandainamcoent.narutoborutox"],
    "othellonia": ["com.DeNA.Othellonia", "com.dena.a12021455"],
    "pokemon": ["jp.pokemon.pokemontcgp", "jp.pokemon.pokemontradingcardgamepocket"],
    "ragnador": ["jp.co.grams.ragnador", "com.grams.ragnador"],
    "touken": ["jp.co.nitroplus.toukenranbuonline", "jp.co.dmm.games.touranbu", "jp.dmmgames.touken"],
    "twisted": ["com.aniplex.twistedwonderland", "com.aniplex.twisted"],
    "ask-kingdom": ["com.lilithgames.roc.gp", "com.lilithgame.roc.gp"],
}

def get_icon_url(package_id):
    url = f"https://play.google.com/store/apps/details?id={package_id}&hl=ja"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        matches = re.findall(r'(https://play-lh\.googleusercontent\.com/[^"\'>\s]+)', html)
        if matches:
            icon_url = matches[0]
            icon_url = re.sub(r'=w\d+', '=w240', icon_url)
            icon_url = re.sub(r'=s\d+', '=s240', icon_url)
            if '=w' not in icon_url and '=s' not in icon_url:
                icon_url += '=s240'
            return icon_url
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        print(f"  HTTP {e.code}")
    except Exception as e:
        print(f"  Error: {e}")
    return None

def download_icon(url, save_path):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            data = resp.read()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(data)
        return len(data)
    except Exception as e:
        print(f"  Download error: {e}")
        return 0

success = 0
failed = []

for slug in sorted(ALT_PACKAGES.keys()):
    save_path = os.path.join(BASE, "games", slug, "icon.png")
    if os.path.exists(save_path) and os.path.getsize(save_path) > 1000:
        print(f"SKIP (exists): {slug}")
        success += 1
        continue
    
    packages = ALT_PACKAGES[slug]
    found = False
    for pkg in packages:
        print(f"Trying: {slug} ({pkg})...", end=" ", flush=True)
        icon_url = get_icon_url(pkg)
        if icon_url:
            size = download_icon(icon_url, save_path)
            if size > 1000:
                print(f"OK ({size//1024} KB)")
                success += 1
                found = True
                break
            else:
                print("too small")
        else:
            print("not found")
        time.sleep(0.5)
    
    if not found:
        failed.append(slug)
    time.sleep(0.5)

print(f"\n{'='*50}")
print(f"Success: {success}")
print(f"Failed: {len(failed)} - {failed}")
