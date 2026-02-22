#!/usr/bin/env python3
"""Definitive fix: remove ALL gtag blocks and insert exactly one, using line-by-line processing."""
import os
import glob

GTAG_LINES = [
    '<!-- Google tag (gtag.js) -->',
    '<script async src="https://www.googletagmanager.com/gtag/js?id=G-0HP0L0X5P1"></script>',
    '<script>',
    '  window.dataLayer = window.dataLayer || [];',
    '  function gtag(){dataLayer.push(arguments);}',
    "  gtag('js', new Date());",
    "  gtag('config', 'G-0HP0L0X5P1');",
    '</script>',
]

# Lines that indicate gtag content (to be removed)
GTAG_MARKERS = {
    '<!-- Google tag (gtag.js) -->',
    '<script async src="https://www.googletagmanager.com/gtag/js?id=G-0HP0L0X5P1"></script>',
    'window.dataLayer = window.dataLayer || [];',
    'function gtag(){dataLayer.push(arguments);}',
    "gtag('js', new Date());",
    "gtag('config', 'G-0HP0L0X5P1');",
}


def is_gtag_line(line):
    """Check if a line is part of the gtag block."""
    stripped = line.strip()
    if stripped in GTAG_MARKERS:
        return True
    # Also match the script open/close tags that are part of gtag (but not other scripts)
    # We handle this contextually below
    return False


def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Determine line ending
    if '\r\n' in content:
        newline = '\r\n'
    else:
        newline = '\n'

    lines = content.splitlines()
    
    # Remove all gtag-related lines
    cleaned_lines = []
    in_gtag_script = False
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        
        # Skip gtag comment lines
        if stripped == '<!-- Google tag (gtag.js) -->':
            i += 1
            continue
        
        # Skip the async script tag for gtag
        if stripped == '<script async src="https://www.googletagmanager.com/gtag/js?id=G-0HP0L0X5P1"></script>':
            i += 1
            continue
        
        # Detect start of inline gtag script block
        if stripped == '<script>' and i + 1 < len(lines) and 'window.dataLayer' in lines[i + 1]:
            # Skip until closing </script>
            while i < len(lines) and lines[i].strip() != '</script>':
                i += 1
            if i < len(lines):
                i += 1  # skip the </script> line
            continue
        
        # Also handle: window.dataLayer line (orphaned, not inside <script>)
        if 'window.dataLayer' in stripped and 'gtag' not in stripped:
            i += 1
            continue
        
        # Skip empty lines that were between gtag blocks
        # (we'll handle this by not adding extra blank lines)
        cleaned_lines.append(lines[i])
        i += 1
    
    # Remove consecutive blank lines that may result from removal
    final_lines = []
    prev_blank = False
    for line in cleaned_lines:
        is_blank = line.strip() == ''
        if is_blank and prev_blank:
            continue
        final_lines.append(line)
        prev_blank = is_blank
    
    # Now insert gtag block after <head>
    result_lines = []
    inserted = False
    for line in final_lines:
        result_lines.append(line)
        if not inserted and line.strip().startswith('<head'):
            # Insert gtag lines right after <head>
            for gtag_line in GTAG_LINES:
                result_lines.append(gtag_line)
            inserted = True
    
    new_content = newline.join(result_lines)
    # Ensure file ends with newline if original did
    if content.endswith('\n') and not new_content.endswith('\n'):
        new_content += newline
    
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        f.write(new_content)
    
    return content != new_content


def main():
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    fixed = 0
    for f in sorted(glob.glob("**/index.html", recursive=True)):
        changed = process_file(f)
        if changed:
            fixed += 1
    
    print(f"Processed files, {fixed} were modified")
    
    # Verify
    problems = 0
    for f in sorted(glob.glob("**/index.html", recursive=True)):
        with open(f, 'r', encoding='utf-8') as fh:
            content = fh.read()
        count = content.count('window.dataLayer')
        if count != 1:
            print(f"VERIFY FAIL ({count}): {f}")
            problems += 1
    
    if problems == 0:
        print("Verification PASSED: All files have exactly one gtag block!")
    else:
        print(f"Verification FAILED: {problems} files have incorrect count")


if __name__ == "__main__":
    main()
