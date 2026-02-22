#!/usr/bin/env python3
"""Add Google Analytics gtag.js to all index.html files."""
import os
import glob

GTAG = """<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-0HP0L0X5P1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-0HP0L0X5P1');
</script>
"""

def main():
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    count = 0
    for f in glob.glob("**/index.html", recursive=True):
        with open(f, "r", encoding="utf-8") as fh:
            content = fh.read()
        if "gtag" in content:
            print(f"SKIP (already has gtag): {f}")
            continue
        # Try to insert after <head> preserving line endings
        if "<head>\r\n" in content:
            new_content = content.replace("<head>\r\n", "<head>\r\n" + GTAG, 1)
        elif "<head>\n" in content:
            new_content = content.replace("<head>\n", "<head>\n" + GTAG, 1)
        else:
            new_content = content.replace("<head>", "<head>\n" + GTAG, 1)
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(new_content)
        count += 1
        print(f"Updated: {f}")
    print(f"\nTotal updated: {count}")

if __name__ == "__main__":
    main()
