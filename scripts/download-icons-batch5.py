"""Download icons for new batch 5 real games."""
import urllib.request, re, os, ssl, time

BASE = r"c:\Users\foo\Downloads\soshageshin"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

NEW_PACKAGES = {
    "bdo-mobile": "com.pearlabyss.blackdesertm.gl",
    "efootball": "jp.konami.pesam",
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
    except Exception as e:
        print(f"  Error: {e}")
    return None

for slug, pkg in NEW_PACKAGES.items():
    save_path = os.path.join(BASE, "games", slug, "icon.png")
    if os.path.exists(save_path) and os.path.getsize(save_path) > 1000:
        print(f"SKIP: {slug}")
        continue
    print(f"Fetching: {slug} ({pkg})...", end=" ", flush=True)
    icon_url = get_icon_url(pkg)
    if icon_url:
        req = urllib.request.Request(icon_url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                data = resp.read()
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(data)
            print(f"OK ({len(data)//1024} KB)")
        except Exception as e:
            print(f"Download failed: {e}")
    else:
        print("Not found")
    time.sleep(1)
print("Done!")
