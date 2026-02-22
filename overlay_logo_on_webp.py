#!/usr/bin/env python3
"""
Overlay a logo PNG onto existing WebP images at the bottom-right corner.
Usage:
  python overlay_logo_on_webp.py --logo assets/soshageshin_logo.png --dirs games/zzz/issues/2026-02-16 games/vivid-army/issues/2026-02-18
"""
from PIL import Image
import argparse
import sys
from pathlib import Path


def overlay_logo_on_webp(img_path: Path, logo: Image.Image, width_ratio=0.135, margin_x_ratio=0.018, margin_y_ratio=0.015):
    img = Image.open(img_path).convert("RGBA")
    
    # Calculate logo size
    logo_w = int(img.width * width_ratio)
    logo_h = int(logo_w * (logo.height / logo.width))
    max_h = int(img.height * 0.12)
    if logo_h > max_h:
        logo_h = max_h
        logo_w = int(logo_h / (logo.height / logo.width))
    
    logo_resized = logo.resize((logo_w, logo_h), Image.LANCZOS)
    
    # Position at bottom-right
    margin_x = int(img.width * margin_x_ratio)
    margin_y = int(img.height * margin_y_ratio)
    x = img.width - logo_w - margin_x
    y = img.height - logo_h - margin_y
    
    # Paste with transparency
    img.paste(logo_resized, (x, y), logo_resized)
    
    # Save back as WebP
    img = img.convert("RGB")
    img.save(img_path, "WEBP", quality=90)
    return True


def main():
    parser = argparse.ArgumentParser(description="Overlay logo on WebP images")
    parser.add_argument("--logo", required=True, help="Path to logo PNG")
    parser.add_argument("--dirs", nargs="+", required=True, help="Directories containing WebP images")
    args = parser.parse_args()
    
    logo_path = Path(args.logo)
    if not logo_path.exists():
        print(f"[ERROR] Logo not found: {logo_path}", file=sys.stderr)
        return 1
    
    logo = Image.open(logo_path).convert("RGBA")
    ok = 0
    failed = 0
    
    for d in args.dirs:
        dir_path = Path(d)
        if not dir_path.exists():
            print(f"[WARN] Directory not found: {dir_path}")
            continue
        
        for webp_file in sorted(dir_path.glob("page-*.webp")):
            try:
                overlay_logo_on_webp(webp_file, logo)
                ok += 1
                print(f"[OK] {webp_file}")
            except Exception as e:
                failed += 1
                print(f"[FAIL] {webp_file}: {e}")
    
    print(f"\nDone: {ok} OK, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
