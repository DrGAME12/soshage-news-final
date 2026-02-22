"""
Batch convert PDFs from pdf_new/ directory.
- Auto-generates slug from PDF filename
- Converts pages to WebP
- Applies logo overlay (unnamed (5).png) at 140x24px bottom-right
- Creates meta.json
- Adds new entries to games-registry.js if missing
"""
import subprocess, os, json, re, sys, shutil, unicodedata
import fitz  # PyMuPDF
from PIL import Image

BASE = r"c:\Users\foo\Downloads\soshageshin"
PDF_DIR = os.path.join(BASE, "pdf_new")
LOGO_PATH = os.path.join(BASE, "assets", "unnamed (5).png")
GAMES_DIR = os.path.join(BASE, "games")

def slugify(text):
    """Generate a URL slug from text."""
    # Remove date suffix like ' 2026-02-17' or ' 2026-02-18'
    text = re.sub(r'\s+\d{4}-\d{2}-\d{2}$', '', text)
    # Remove '  ユーザーが欲しい最新情報' suffix
    text = re.sub(r'\s*ユーザーが欲しい最新情報.*$', '', text)
    # Also remove suffixes like '：初動攻略ガイド'
    text = re.sub(r'[：:].*$', '', text)
    # For Japanese text, romanize common words or just use as-is
    # Simple approach: transliterate to ASCII-safe slug
    text = text.strip()
    # Replace common separators
    text = re.sub(r'[｜|＿_\s～~]+', '-', text)
    # Remove special chars but keep CJK
    text = re.sub(r'[!！?？。、・]+', '', text)
    # For mostly ASCII text, lowercase and slugify
    if re.match(r'^[A-Za-z0-9\s\-_:]+$', text):
        return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')[:50]
    # For Japanese text, try to extract English name if present
    en_match = re.search(r'[A-Za-z][A-Za-z0-9\s\-]+', text)
    if en_match and len(en_match.group()) > 3:
        return re.sub(r'[^a-z0-9]+', '-', en_match.group().lower()).strip('-')[:50]
    # Fallback: use romaji-like simplification
    # Map common Japanese game words
    jp_map = {
        'アーク': 'ark', 'ナイツ': 'knights', 'エンドフィールド': 'endfield',
        'カオス': 'chaos', 'ゼロ': 'zero', 'ナイトメア': 'nightmare',
        'クローズ': 'crows', 'サンシャイン': 'sunshine', '牧場': 'farm',
        'ダーク': 'dark', 'ニャン': 'nyan', 'バイオ': 'bio', 'ハザード': 'hazard',
        'バグ': 'bug', '三国': 'sangoku', 'ブイ': 'vlife', 'ブラウザ': 'browser',
        'ブルー': 'blue', 'プロトコル': 'protocol', 'スター': 'star',
        'ブレイブ': 'brave', 'マージ': 'merge', 'キャット': 'cat',
        'モエモエ': 'moemoe', '百花': 'hyakka', '百勇': 'hyakuyu',
        'レガリア': 'regalia', '終境': 'shukyou', '英雄': 'eiyuu',
        'シンフォニー': 'symphony', '逆水': 'gyakusui', '銀魂': 'gintama',
        '遙か': 'haruka', '伝説': 'densetsu', '信長': 'nobunaga',
        '仮面ライダー': 'kamen-rider', '刃牙': 'baki', '地獄楽': 'jigokuraku',
        '戦隊': 'sentai', '大失格': 'daishikkaku', '忍たま': 'nintama',
        '忍者': 'ninja', 'フルール': 'fleur', 'ハート': 'heart',
        'スター': 'star', 'セイヴァー': 'saver', 'ドラベル': 'dravel',
        'カオスゼロ': 'chaos-zero',
    }
    slug = text
    for jp, en in jp_map.items():
        slug = slug.replace(jp, en)
    slug = re.sub(r'[^a-z0-9]+', '-', slug.lower()).strip('-')
    return slug[:50] if slug else 'unknown'


def extract_date_from_filename(filename):
    """Extract date from filename like '... 2026-02-17.pdf'"""
    m = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    return m.group(1) if m else '2026-02-18'


def extract_title_from_filename(filename):
    """Extract readable title from filename."""
    name = os.path.splitext(filename)[0]
    # Remove date
    name = re.sub(r'\s*\d{4}-\d{2}-\d{2}$', '', name)
    return name.strip()


def overlay_logo_on_pdf(pdf_path, logo_bytes, logo_w=140, logo_h=24, margin=10):
    """Stamp logo on all pages of a PDF in-place."""
    doc = fitz.open(pdf_path)
    for page in doc:
        pw, ph = page.rect.width, page.rect.height
        x0 = pw - logo_w - margin
        y0 = ph - logo_h - margin
        rect = fitz.Rect(x0, y0, x0 + logo_w, y0 + logo_h)
        page.insert_image(rect, stream=logo_bytes)
    doc.save(pdf_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
    doc.close()


def convert_pdf_to_webp(pdf_path, out_dir, width=1080, quality=85):
    """Convert PDF pages to WebP images."""
    os.makedirs(out_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    page_count = len(doc)

    for i, page in enumerate(doc):
        page_num = i + 1
        page_name = f"page-{page_num:02d}.webp"
        zoom = width / page.rect.width
        matrix = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        out_path = os.path.join(out_dir, page_name)
        img.save(out_path, "WEBP", quality=quality)

    doc.close()
    return page_count


def main():
    if not os.path.isdir(PDF_DIR):
        print(f"[ERROR] pdf_new not found: {PDF_DIR}")
        return 1

    # Load logo
    if not os.path.isfile(LOGO_PATH):
        print(f"[ERROR] Logo not found: {LOGO_PATH}")
        return 1
    logo_bytes = open(LOGO_PATH, 'rb').read()
    print(f"[INFO] Logo loaded: {LOGO_PATH}")

    # Get already processed slugs
    processed_slugs = set()
    if os.path.isdir(GAMES_DIR):
        for d in os.listdir(GAMES_DIR):
            issues_dir = os.path.join(GAMES_DIR, d, "issues")
            if os.path.isdir(issues_dir):
                for issue_dir in os.listdir(issues_dir):
                    if os.path.exists(os.path.join(issues_dir, issue_dir, "page-01.webp")):
                        processed_slugs.add(d)

    print(f"[INFO] Already processed: {len(processed_slugs)} games")

    # Process each PDF
    pdfs = sorted([f for f in os.listdir(PDF_DIR) if f.endswith('.pdf') and '_logo_test' not in f])
    print(f"[INFO] PDFs to process: {len(pdfs)}")

    converted = 0
    errors = []
    new_games = []  # For games-registry.js

    for pdf_file in pdfs:
        pdf_path = os.path.join(PDF_DIR, pdf_file)
        title = extract_title_from_filename(pdf_file)
        date = extract_date_from_filename(pdf_file)
        slug = slugify(title)

        # Check if already processed
        issue_dir = os.path.join(GAMES_DIR, slug, "issues", date)
        if os.path.exists(os.path.join(issue_dir, "page-01.webp")):
            print(f"SKIP (exists): {pdf_file} -> {slug}")
            continue

        print(f"\nCONVERTING: {pdf_file}")
        print(f"  slug: {slug}, date: {date}")

        try:
            # 1) Convert PDF to WebP pages
            os.makedirs(issue_dir, exist_ok=True)
            page_count = convert_pdf_to_webp(pdf_path, issue_dir)

            # 2) Copy original PDF and apply logo
            original_pdf = os.path.join(issue_dir, "original.pdf")
            shutil.copy2(pdf_path, original_pdf)
            overlay_logo_on_pdf(original_pdf, logo_bytes)

            # 3) Create meta.json
            meta = {
                "title": title,
                "game": title.split(' ')[0] if ' ' in title else title,
                "date": date,
                "codename": "",
                "pageCount": page_count,
                "summary": f"{title}の最新情報まとめ",
                "tags": ["最新情報"]
            }
            with open(os.path.join(issue_dir, "meta.json"), "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)

            new_games.append({
                "slug": slug,
                "name": title.split(' ユーザーが欲しい最新情報')[0] if 'ユーザーが欲しい最新情報' in title else title,
                "date": date,
                "title": title,
                "pageCount": page_count,
            })

            converted += 1
            print(f"  OK: {page_count} pages")

        except Exception as e:
            errors.append(f"{pdf_file}: {e}")
            print(f"  ERROR: {e}")

    print(f"\n{'='*60}")
    print(f"Converted: {converted}")
    print(f"Errors: {len(errors)}")
    if errors:
        for e in errors:
            print(f"  - {e[:120]}")
    print(f"\nNew games for registry:")
    for g in new_games:
        print(f"  {g['slug']}: {g['name']} ({g['pageCount']} pages)")

    # Output JSON for easy registry addition
    if new_games:
        registry_path = os.path.join(BASE, "pdf_new", "_new_games.json")
        with open(registry_path, "w", encoding="utf-8") as f:
            json.dump(new_games, f, ensure_ascii=False, indent=2)
        print(f"\nNew games list saved to: {registry_path}")

    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
