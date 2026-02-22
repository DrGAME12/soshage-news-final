#!/usr/bin/env python3
"""
Overlay a logo image onto PDFs at the bottom-right corner.

Example:
  python scripts/overlay_logo_on_pdfs.py \
    --input-dir out/pdf \
    --output-dir out/pdf_logo_overlay \
    --logo C:/path/to/soshageshin_logo.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

import fitz  # PyMuPDF


def parse_color_hex(value: str) -> tuple[float, float, float]:
    s = value.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    if len(s) != 6:
        raise ValueError(f"Invalid color: {value}")
    return (
        int(s[0:2], 16) / 255.0,
        int(s[2:4], 16) / 255.0,
        int(s[4:6], 16) / 255.0,
    )


def iter_pdf_files(input_dir: Path, recursive: bool) -> Iterable[Path]:
    pattern = "**/*.pdf" if recursive else "*.pdf"
    return sorted(p for p in input_dir.glob(pattern) if p.is_file())


def overlay_logo(
    in_pdf: Path,
    out_pdf: Path,
    logo_bytes: bytes,
    logo_aspect: float,
    width_ratio: float,
    margin_x_ratio: float,
    margin_y_ratio: float,
    erase_under: bool,
    erase_padding_ratio: float,
    erase_color: tuple[float, float, float],
    first_page_only: bool,
) -> None:
    doc = fitz.open(in_pdf)
    image_xref = 0

    page_indices = [0] if first_page_only else range(len(doc))
    for page_index in page_indices:
        if page_index >= len(doc):
            continue
        page = doc[page_index]
        rect = page.rect

        logo_w = rect.width * width_ratio
        logo_h = logo_w * logo_aspect
        max_h = rect.height * 0.12
        if logo_h > max_h:
            logo_h = max_h
            logo_w = logo_h / logo_aspect

        margin_x = rect.width * margin_x_ratio
        margin_y = rect.height * margin_y_ratio
        x1 = rect.x1 - margin_x
        y1 = rect.y1 - margin_y
        logo_rect = fitz.Rect(x1 - logo_w, y1 - logo_h, x1, y1)

        if erase_under:
            pad_x = logo_w * erase_padding_ratio
            pad_y = logo_h * erase_padding_ratio
            erase_rect = fitz.Rect(
                logo_rect.x0 - pad_x,
                logo_rect.y0 - pad_y,
                logo_rect.x1 + pad_x,
                logo_rect.y1 + pad_y,
            )
            page.draw_rect(
                erase_rect,
                color=erase_color,
                fill=erase_color,
                width=0,
                overlay=True,
            )

        image_xref = page.insert_image(
            logo_rect,
            stream=logo_bytes,
            keep_proportion=True,
            overlay=True,
            xref=image_xref,
        )

    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out_pdf, garbage=3, deflate=True)
    doc.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Overlay a logo image onto PDFs at bottom-right."
    )
    parser.add_argument("--input-dir", required=True, help="Input PDF directory")
    parser.add_argument("--output-dir", required=True, help="Output PDF directory")
    parser.add_argument("--logo", required=True, help="Logo image path (PNG recommended)")
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Read PDFs recursively from input-dir",
    )
    parser.add_argument(
        "--first-page-only",
        action="store_true",
        help="Overlay only page 1 (default: all pages)",
    )
    parser.add_argument(
        "--width-ratio",
        type=float,
        default=0.135,
        help="Logo width ratio to page width (default: 0.135)",
    )
    parser.add_argument(
        "--margin-x-ratio",
        type=float,
        default=0.018,
        help="Right margin ratio to page width (default: 0.018)",
    )
    parser.add_argument(
        "--margin-y-ratio",
        type=float,
        default=0.015,
        help="Bottom margin ratio to page height (default: 0.015)",
    )
    parser.add_argument(
        "--erase-under",
        action="store_true",
        help="Draw background rectangle under logo before overlay",
    )
    parser.add_argument(
        "--erase-padding-ratio",
        type=float,
        default=0.08,
        help="Background padding ratio relative to logo size (default: 0.08)",
    )
    parser.add_argument(
        "--erase-color",
        default="#ffffff",
        help="Erase background color when --erase-under is set (default: #ffffff)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Process first N PDFs only (0 = all)",
    )
    parser.add_argument(
        "--skip-if-exists",
        action="store_true",
        help="Skip output file if already exists",
    )
    args = parser.parse_args()

    in_dir = Path(args.input_dir)
    out_dir = Path(args.output_dir)
    logo_path = Path(args.logo)

    if not in_dir.exists():
        print(f"[ERROR] input-dir not found: {in_dir}", file=sys.stderr)
        return 1
    if not logo_path.exists():
        print(f"[ERROR] logo image not found: {logo_path}", file=sys.stderr)
        return 1
    if args.width_ratio <= 0:
        print("[ERROR] width-ratio must be > 0", file=sys.stderr)
        return 1

    try:
        erase_color = parse_color_hex(args.erase_color)
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    logo_pix = fitz.Pixmap(str(logo_path))
    if logo_pix.width <= 0 or logo_pix.height <= 0:
        print("[ERROR] invalid logo image dimensions", file=sys.stderr)
        return 1
    logo_aspect = logo_pix.height / logo_pix.width
    logo_bytes = logo_pix.tobytes("png")

    pdfs = list(iter_pdf_files(in_dir, args.recursive))
    if args.limit > 0:
        pdfs = pdfs[: args.limit]
    if not pdfs:
        print("[WARN] no PDFs found")
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    ok = 0
    skipped = 0
    failed = 0

    for src in pdfs:
        rel = src.relative_to(in_dir) if args.recursive else Path(src.name)
        dst = out_dir / rel
        if args.skip_if_exists and dst.exists():
            skipped += 1
            continue
        try:
            overlay_logo(
                in_pdf=src,
                out_pdf=dst,
                logo_bytes=logo_bytes,
                logo_aspect=logo_aspect,
                width_ratio=args.width_ratio,
                margin_x_ratio=args.margin_x_ratio,
                margin_y_ratio=args.margin_y_ratio,
                erase_under=args.erase_under,
                erase_padding_ratio=args.erase_padding_ratio,
                erase_color=erase_color,
                first_page_only=args.first_page_only,
            )
            ok += 1
            print(f"[OK] {src.name}")
        except Exception as exc:
            failed += 1
            print(f"[FAIL] {src.name}: {exc}")

    print(f"overlay_ok={ok}")
    print(f"overlay_skipped={skipped}")
    print(f"overlay_failed={failed}")
    print(f"output_dir={out_dir}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
