"""
Download Google Play Store icons for all registered games.
Saves as games/<slug>/icon.png
"""
import urllib.request, urllib.error
import re, os, json, ssl

BASE = r"c:\Users\foo\Downloads\soshageshin"

# Map slug -> Google Play package ID
PACKAGE_MAP = {
    "monster-strike": "jp.co.mixi.monsterstrike",
    "pad": "jp.gungho.pad",
    "blue-archive": "com.YostarJP.BlueArchive",
    "nikke": "com.proximabeta.nikke",
    "arknights": "com.YostarJP.Arknights",
    "version64": "com.miHoYo.GenshinImpact",
    "wuthering-waves": "com.kurogame.wutheringwaves.global",
    "project-sekai": "com.sega.pjsekai",
    "proseka-extra": "com.sega.pjsekai",
    "memento-mori": "jp.co.bankofinnov.mementomori",
    "dokkan": "com.bandainamcogames.dbzdokkanww",
    "granblue": "jp.mbga.a12016007.lite",
    "heban": "jp.wrightflyer.hbr",
    "enstars": "com.happyelements.ensemblestars_music_jp",
    "idolish7": "com.bandainamcoent.idolish7",
    "nyanko": "jp.co.ponos.battlecatsen",
    "touken": "jp.co.dmm.games.tourabu",
    "twisted": "com.aniplex.twistedwonderland",
    "garupa": "jp.co.craftegg.band",
    "priconne": "jp.co.cygames.princessconnectredive",
    "romasaga": "com.square_enix.android_googleplay.RSRS",
    "shadowverse": "com.cygames.Shadowverse",
    "identity-v": "com.netease.idv.jp",
    "unite": "jp.pokemon.pokemonunite",
    "masterduel": "jp.konami.masterduel",
    "mahjongsoul": "com.YostarJP.MajSoul",
    "ragnador": "com.grams.ragnador",
    "dqtact": "com.square_enix.android_googleplay.dqtactj",
    "othellonia": "com.DeNA.Othellonia",
    "pokemon-go": "com.nianticlabs.pokemongo",
    "pokemon": "jp.pokemon.pokemontrading",
    "codm": "com.activision.callofduty.shooter",
    "dereste": "jp.co.bandainamcoent.BNEI0242",
    "lineage": "com.ncsoft.lineagew",
    "origin": "com.netmarble.nanagb",
    "toonblast": "net.peakgames.toonblast",
    "pokopoko": "com.linecorp.LGPKPK",
    "scapes": "com.playrix.gardenscapes",
    "battlegrounds": "com.pubg.imobile",
    "5th-anniversary": None,
    "7th-anniv": None,
    "all-star": None,
    "ask-kingdom": "com.lilithgames.rok.gp",
    "dingjun": None,
    "dual-ambition": None,
    "durability-warfare": None,
    "ex-rarity": None,
    "feb-dual": None,
    "kingdom": None,
    "mecha-frontline": None,
    "naruto-ninja": "com.bandainamcoent.narutox",
    "pawaspo": "jp.konami.prospia",
    "port": None,
    "sages": None,
    "walker": None,
    "grand-open": None,
}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def get_icon_url(package_id):
    """Fetch Google Play page and extract icon URL."""
    url = f"https://play.google.com/store/apps/details?id={package_id}&hl=ja"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        # Look for icon URL in the page - typically in an img tag
        # Pattern: src="https://play-lh.googleusercontent.com/..." with size params
        matches = re.findall(r'(https://play-lh\.googleusercontent\.com/[^"\']+)', html)
        if matches:
            # First large image is usually the icon
            icon_url = matches[0]
            # Request a reasonable size
            icon_url = re.sub(r'=w\d+', '=w240', icon_url)
            icon_url = re.sub(r'=s\d+', '=s240', icon_url)
            if '=w' not in icon_url and '=s' not in icon_url:
                icon_url += '=s240'
            return icon_url
    except Exception as e:
        print(f"  Error fetching page: {e}")
    return None

def download_icon(url, save_path):
    """Download icon image."""
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
        print(f"  Error downloading: {e}")
        return 0

success = 0
failed = []

for slug, pkg in sorted(PACKAGE_MAP.items()):
    if pkg is None:
        print(f"SKIP (no package): {slug}")
        continue
    
    save_path = os.path.join(BASE, "games", slug, "icon.png")
    if os.path.exists(save_path) and os.path.getsize(save_path) > 1000:
        print(f"SKIP (exists): {slug}")
        success += 1
        continue
    
    print(f"Fetching: {slug} ({pkg})...", end=" ", flush=True)
    icon_url = get_icon_url(pkg)
    if icon_url:
        size = download_icon(icon_url, save_path)
        if size > 0:
            print(f"OK ({size//1024} KB)")
            success += 1
        else:
            print("DOWNLOAD FAILED")
            failed.append(slug)
    else:
        print("NO ICON FOUND")
        failed.append(slug)

print(f"\n{'='*50}")
print(f"Success: {success}")
print(f"Failed: {len(failed)} - {failed}")
