---
description: PDFを新聞ページに変換してサイトに追加する手順
---

# PDF追加ワークフロー

## 前提
- ロゴ画像: `testpy/unnamed (5).png`
- ロゴサイズ: **140×24ピクセル**
- ロゴ配置: **一番右下（マージン0）**

## 手順

### 1. PDFをWebPに変換
```powershell
python scripts/convert-pdf.py <PDFファイルパス> games/<slug>/issues/<YYYY-MM-DD>
```

### 2. meta.json を作成
`games/<slug>/issues/<YYYY-MM-DD>/meta.json` に以下の形式で作成:
```json
{
  "title": "記事タイトル",
  "game": "ゲーム名",
  "date": "YYYY-MM-DD",
  "pageCount": 10,
  "summary": "記事の概要",
  "tags": ["タグ1", "タグ2"]
}
```

### 3. ロゴをWebPページに追加
// turbo
```powershell
python -c "
from PIL import Image
from pathlib import Path
BASE = Path(r'c:\Users\foo\Downloads\soshageshin')
logo = Image.open(BASE / 'testpy' / 'unnamed (5).png').convert('RGBA').resize((140, 24), Image.LANCZOS)
for p in sorted(Path('<issue_dir>').glob('page-*.webp')):
    img = Image.open(p).convert('RGBA')
    img.paste(logo, (img.width - 140, img.height - 24), logo)
    img.convert('RGB').save(p, 'WEBP', quality=90)
    print(f'OK: {p.name}')
"
```
`<issue_dir>` を実際のパスに置き換えること。

### 4. サイト再生成
// turbo
```powershell
python scripts/generate-site.py
```

### 5. Google Analytics タグ追加
// turbo
```powershell
python scripts/add_gtag.py
```

### 6. デプロイ
```powershell
git add -A
git commit -m "Add <ゲーム名> PDF"
git push
```

## 重要ポイント
- ロゴは **必ず** WebP変換後に追加する（PDF変換 → ロゴ追加の順）
- ロゴサイズは **140×24** 固定、配置は **右下隅マージン0**
- `original.pdf` は issue ディレクトリに保持しておく（将来の再変換用）
