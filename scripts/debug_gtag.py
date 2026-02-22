#!/usr/bin/env python3
"""Debug: show lines around dataLayer occurrences."""

f = 'games/8-ball-pool/index.html'
with open(f, 'r', encoding='utf-8') as fh:
    lines = fh.readlines()

for i, line in enumerate(lines):
    if 'dataLayer' in line or 'gtag' in line.lower() or 'Google tag' in line:
        print(f"Line {i+1}: {repr(line)}")
