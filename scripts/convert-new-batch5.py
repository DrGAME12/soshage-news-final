"""
Convert new batch 5 PDFs to WebP + generate meta.json.
Then run generate-site.py to rebuild everything.
"""
import subprocess, os, json, sys

BASE = r"c:\Users\foo\Downloads\soshageshin"
CONVERT_SCRIPT = os.path.join(BASE, "scripts", "convert-pdf.py")

# New PDFs to process (skip duplicates like "7th_Anniversary_Scoop (1).pdf")
NEW_PDFS = {
    "BDO_Mobile_Daily_News.pdf": {
        "slug": "bdo-mobile",
        "date": "2026-02-15",
        "meta": {
            "title": "黒い砂漠モバイル 日刊ニュース",
            "game": "黒い砂漠モバイル",
            "date": "2026-02-15",
            "codename": "Operation Desert Storm",
            "summary": "黒い砂漠モバイル最新アップデート情報＋新コンテンツ解禁レポート",
            "tags": ["MMORPG", "アプデ速報", "新コンテンツ"]
        }
    },
    "eFootball_Essential_Updates.pdf": {
        "slug": "efootball",
        "date": "2026-02-15",
        "meta": {
            "title": "eFootball 必読アップデート速報",
            "game": "eFootball",
            "date": "2026-02-15",
            "codename": "Operation Kickoff",
            "summary": "eFootball最新シーズンアップデート＋選手データ更新＋新機能レビュー",
            "tags": ["スポーツ", "アプデ速報", "シーズン更新"]
        }
    },
    "Mid-February_Operations_Update.pdf": {
        "slug": "mid-feb-ops",
        "date": "2026-02-15",
        "meta": {
            "title": "2月中旬 作戦アップデート総括",
            "game": "合同作戦報",
            "date": "2026-02-15",
            "codename": "Operation Midwinter",
            "summary": "2月中旬のソシャゲ業界動向＋主要タイトル横断アップデートまとめ",
            "tags": ["業界動向", "横断まとめ", "作戦報"]
        }
    },
    "Update_86_Must_Read.pdf": {
        "slug": "update86",
        "date": "2026-02-15",
        "meta": {
            "title": "アプデ86号 必読レポート",
            "game": "アップデート総合",
            "date": "2026-02-15",
            "codename": "Operation Briefing 86",
            "summary": "第86号アップデート特集＋注目タイトルの変更点総まとめ",
            "tags": ["総合特集", "必読", "アプデまとめ"]
        }
    },
    "VALORANT_Mobile_China_Success_Japan_Silence.pdf": {
        "slug": "valorant",
        "date": "2026-02-15",
        "meta": {
            "title": "VALORANT Mobile 中国成功・日本沈黙",
            "game": "VALORANT Mobile",
            "date": "2026-02-15",
            "codename": "Operation Silent Storm",
            "summary": "VALORANT Mobile中国展開の成功事例＋日本市場の課題分析＋最新Act情報",
            "tags": ["FPS", "グローバル展開", "市場分析"]
        }
    },
    "Ver_4.0_Extra_Edition.pdf": {
        "slug": "ver40-extra",
        "date": "2026-02-15",
        "meta": {
            "title": "Ver.4.0 号外",
            "game": "Ver.4.0特報",
            "date": "2026-02-15",
            "codename": "Operation New Dawn",
            "summary": "Ver.4.0大型アップデート速報＋新システム解説＋先行レビュー",
            "tags": ["大型アプデ", "号外", "新システム"]
        }
    },
    "Version_64_Homecoming_Briefing.pdf": {
        "slug": "version64",
        "date": "2026-02-15",
        "meta": {
            "title": "原神 Ver.6.4 帰郷ブリーフィング",
            "game": "原神",
            "date": "2026-02-15",
            "codename": "Operation Homecoming",
            "summary": "原神Ver.6.4帰郷アップデート詳細＋新キャラ＋イベント情報",
            "tags": ["オープンワールド", "大型アプデ", "新キャラ"]
        }
    },
    "Walker_Strategy_and_Collaboration.pdf": {
        "slug": "walker",
        "date": "2026-02-15",
        "meta": {
            "title": "ウォーカー戦略＆コラボレポート",
            "game": "ウォーカーコラボ",
            "date": "2026-02-15",
            "codename": "Operation Joint Venture",
            "summary": "最新ウォーカーコラボ戦略ガイド＋限定コンテンツ情報＋攻略ポイント",
            "tags": ["コラボ", "戦略ガイド", "限定コンテンツ"]
        }
    },
    "Weekly_Strategy_Forecast.pdf": {
        "slug": "weekly-forecast",
        "date": "2026-02-15",
        "meta": {
            "title": "週間戦略フォーキャスト",
            "game": "週間作戦予報",
            "date": "2026-02-15",
            "codename": "Operation Weekly Intel",
            "summary": "今週のソシャゲ業界予測＋注目イベントカレンダー＋戦略アドバイス",
            "tags": ["週間まとめ", "イベント予報", "戦略"]
        }
    },
    "Wuthering_Waves_31_Launch_Guide.pdf": {
        "slug": "wuthering-waves",
        "date": "2026-02-15",
        "meta": {
            "title": "鳴潮 Ver.3.1 ローンチガイド",
            "game": "鳴潮",
            "date": "2026-02-15",
            "codename": "Operation Tidal Wave",
            "summary": "鳴潮Ver.3.1大型アプデ＋新キャラ＋新エリア攻略ガイド",
            "tags": ["アクションRPG", "大型アプデ", "新キャラ"]
        }
    },
}

success = 0
failed = []

for pdf_name, info in NEW_PDFS.items():
    slug = info["slug"]
    date = info["date"]
    pdf_path = os.path.join(BASE, pdf_name)
    out_dir = os.path.join(BASE, "games", slug, "issues", date)
    
    if not os.path.exists(pdf_path):
        print(f"SKIP (file not found): {pdf_name}")
        failed.append(pdf_name)
        continue
    
    # Check if already converted
    if os.path.exists(os.path.join(out_dir, "page-01.webp")):
        print(f"SKIP (already done): {slug}/{date}")
        success += 1
        continue
    
    print(f"Converting: {pdf_name} -> {slug}/{date}...", end=" ", flush=True)
    
    # Convert PDF
    os.makedirs(out_dir, exist_ok=True)
    result = subprocess.run(
        ["python", CONVERT_SCRIPT, pdf_path, out_dir],
        capture_output=True, text=True, cwd=BASE
    )
    
    # Count pages
    pages = len([f for f in os.listdir(out_dir) if f.startswith("page-") and f.endswith(".webp")])
    
    if pages > 0:
        # Write meta.json
        meta = info["meta"].copy()
        meta["pageCount"] = pages
        with open(os.path.join(out_dir, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        print(f"OK ({pages} pages)")
        success += 1
    else:
        print(f"FAILED (0 pages)")
        failed.append(pdf_name)

print(f"\n{'='*50}")
print(f"Success: {success}, Failed: {len(failed)}")
if failed:
    print(f"Failed: {failed}")

# Run generate-site.py to rebuild everything
if success > 0:
    print("\nRegenerating site...")
    result = subprocess.run(
        ["python", os.path.join(BASE, "scripts", "generate-site.py")],
        capture_output=True, text=True, cwd=BASE
    )
    print(result.stdout[-200:] if result.stdout else "No output")
    if result.returncode == 0:
        print("Site regeneration complete!")
    else:
        print(f"Site generation failed: {result.stderr[-200:]}")
