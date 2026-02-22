#!/usr/bin/env python3
"""
SOSHAGESHIN — PDF to WebP Converter
====================================
Converts a PDF file into individual WebP page images for the
vertical scroll viewer.

Requirements:
    pip install pymupdf Pillow

Usage:
    python convert-pdf.py input.pdf output_dir/ [--width 1080] [--quality 85]

Examples:
    python convert-pdf.py newsletter.pdf games/blue-archive/issues/2026-02-13/
    python convert-pdf.py report.pdf games/nikke/issues/2026-02-10/ --width 1440 --quality 90
"""

import sys
import os
import json
import shutil
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF to WebP page images for SOSHAGESHIN viewer"
    )
    parser.add_argument("pdf", help="Path to input PDF file")
    parser.add_argument("outdir", help="Output directory (e.g. games/blue-archive/issues/2026-02-13/)")
    parser.add_argument("--width", type=int, default=1080, help="Output image width in pixels (default: 1080)")
    parser.add_argument("--quality", type=int, default=85, help="WebP quality 1-100 (default: 85)")
    parser.add_argument("--title", type=str, default=None, help="Issue title for meta.json")
    parser.add_argument("--game", type=str, default=None, help="Game name for meta.json")

    args = parser.parse_args()

    # Validate input
    if not os.path.isfile(args.pdf):
        print(f"[ERROR] PDF not found: {args.pdf}")
        sys.exit(1)

    # Create output directory
    os.makedirs(args.outdir, exist_ok=True)

    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("[ERROR] PyMuPDF not installed. Run: pip install pymupdf")
        sys.exit(1)

    try:
        from PIL import Image
    except ImportError:
        print("[ERROR] Pillow not installed. Run: pip install Pillow")
        sys.exit(1)

    # Open PDF
    print(f"[INFO] Opening: {args.pdf}")
    doc = fitz.open(args.pdf)
    page_count = len(doc)
    print(f"[INFO] Pages: {page_count}")

    # Convert each page
    for i, page in enumerate(doc):
        page_num = i + 1
        page_name = f"page-{page_num:02d}.webp"

        # Calculate zoom for target width
        zoom = args.width / page.rect.width
        matrix = fitz.Matrix(zoom, zoom)

        # Render to pixmap
        pix = page.get_pixmap(matrix=matrix, alpha=False)

        # Convert to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Save as WebP
        out_path = os.path.join(args.outdir, page_name)
        img.save(out_path, "WEBP", quality=args.quality)

        size_kb = os.path.getsize(out_path) / 1024
        print(f"  [OK] {page_name} ({pix.width}x{pix.height}, {size_kb:.0f} KB)")

    doc.close()

    # Copy original PDF
    pdf_dest = os.path.join(args.outdir, "original.pdf")
    shutil.copy2(args.pdf, pdf_dest)
    print(f"  [OK] original.pdf copied")

    # Generate / update meta.json
    meta_path = os.path.join(args.outdir, "meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        meta["pageCount"] = page_count
        print(f"  [OK] meta.json updated (pageCount: {page_count})")
    else:
        meta = {
            "title": args.title or os.path.splitext(os.path.basename(args.pdf))[0],
            "game": args.game or "Unknown",
            "date": os.path.basename(args.outdir.rstrip('/\\')),
            "codename": "",
            "pageCount": page_count,
            "summary": "",
            "tags": []
        }
        print(f"  [OK] meta.json created (fill in details manually)")

    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # Update the viewer HTML data attribute
    viewer_path = os.path.join(args.outdir, "index.html")
    if os.path.exists(viewer_path):
        with open(viewer_path, 'r', encoding='utf-8') as f:
            html = f.read()

        html = html.replace('data-hasimages="false"', 'data-hasimages="true"')
        html = html.replace(f'data-pagecount="{page_count}"', f'data-pagecount="{page_count}"')

        # Update pagecount if it was different
        import re
        html = re.sub(r'data-pagecount="\d+"', f'data-pagecount="{page_count}"', html)

        with open(viewer_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"  [OK] index.html updated (hasimages=true, pagecount={page_count})")

    print(f"\n[DONE] {page_count} pages converted to {args.outdir}")
    print(f"       Total size: {sum(os.path.getsize(os.path.join(args.outdir, f'page-{i+1:02d}.webp')) for i in range(page_count)) / 1024:.0f} KB")

if __name__ == "__main__":
    main()
