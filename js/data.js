// ============================================================
//  SOSHAGESHIN — 構造化パッチノートデータ
//  架空の戦場レポート新聞用コンテンツ
// ============================================================

const PATCH_DATA = {

  // ────────────────────────────────────────────
  //  META — 発行情報
  // ────────────────────────────────────────────
  meta: {
    edition:   "Vol.47",
    date:      "2026-02-12",
    codename:  "Operation Crimson Viper",
    title:     "SOSHAGESHIN",
    subtitle:  "FIELD INTELLIGENCE DISPATCH",
    classification: "FOR OPERATORS ONLY"
  },

  // ────────────────────────────────────────────
  //  SECTION 1 ─ 一面：Top Strategic News
  // ────────────────────────────────────────────
  topNews: {
    headline: "新型決戦兵器「ヴァルキュリア Mk-IX」、本日より全戦域に実戦配備",
    subhead:  "高機動・対空特化フレーム――制空権争奪戦に新たな局面",
    summary:
      "本部統合作戦司令部は、次世代強襲型機体「ヴァルキュリア Mk-IX」の正式配備を発表した。" +
      "本機は従来の重装甲型とは一線を画す高機動フレームを採用し、対空戦闘におけるキルレシオを大幅に改善する設計思想を持つ。" +
      "初期運用データでは支配率18%向上が確認されており、現行メタの勢力図を塗り替える可能性が指摘されている。" +
      "加えて、大規模協力作戦「オペレーション：クリムゾンヴァイパー」が同時開催。" +
      "最大32名による共同戦線の構築が可能となり、限定支給品の獲得チャンスが設けられた。",
    keyPoints: [
      "新機体「ヴァルキュリア Mk-IX」参戦 ─ 対空特化・高機動フレーム",
      "大規模共同作戦「クリムゾンヴァイパー」開催（最大32名）",
      "限定支給品：専用カラーリング＆エンブレム",
      "新マップ「凍結港湾 ノルドヘイヴン」追加"
    ],
    imagePrompt:
      "A dramatic military war-room strategy table with holographic blue projection of a futuristic mecha silhouette, " +
      "tactical maps and red push-pins scattered around, dim amber overhead lighting, " +
      "worn leather-bound documents marked CLASSIFIED in red stamp, " +
      "cinematic composition, dark moody atmosphere, photorealistic digital art, 16:9 aspect ratio"
  },

  // ────────────────────────────────────────────
  //  SECTION 2 ─ 機体解析：Unit Intel
  // ────────────────────────────────────────────
  unitIntel: [
    {
      unitName: "グラディウス III 型",
      role: "前衛強襲",
      before: {
        hp: 12000,
        armor: 350,
        speed: 62,
        skill: "ブレードラッシュ：CT 12秒 / ダメージ 2800"
      },
      after: {
        hp: 13500,
        armor: 420,
        speed: 62,
        skill: "ブレードラッシュ：CT 9秒 / ダメージ 3200"
      },
      tacticalEval:
        "装甲値の20%増強とスキルCT短縮により、最前線での生存率が大幅に向上。" +
        "これまで中距離運用を余儀なくされていた本機が、本来の設計思想である「切り込み役」として復権する。" +
        "ランクマッチにおけるピック率は調整前の4.2%から推定12%超へ上昇する見込み。",
      changeType: "buff"
    },
    {
      unitName: "ファントム・レイス",
      role: "隠密狙撃",
      before: {
        hp: 7800,
        armor: 180,
        speed: 85,
        skill: "ゴーストショット：CT 18秒 / ダメージ 5200"
      },
      after: {
        hp: 7800,
        armor: 180,
        speed: 78,
        skill: "ゴーストショット：CT 22秒 / ダメージ 4600"
      },
      tacticalEval:
        "過剰な支配率（前期23.1%）を記録していた本機に対し、機動力と火力の両面からの下方修正が入った。" +
        "即時撃破能力は低下したが、依然として長距離制圧の主力であることに変わりはない。" +
        "運用には従来以上のポジショニング精度が求められる。",
      changeType: "nerf"
    },
    {
      unitName: "イージス・ガーディアン",
      role: "防衛支援",
      before: {
        hp: 18000,
        armor: 600,
        speed: 38,
        skill: "フォートレスシールド：CT 25秒 / 吸収量 8000"
      },
      after: {
        hp: 18000,
        armor: 600,
        speed: 42,
        skill: "フォートレスシールド：CT 20秒 / 吸収量 9500"
      },
      tacticalEval:
        "機動力の微増とシールド性能の強化により、味方部隊への追従能力が改善。" +
        "これまでの「拠点防衛専用」から「機動防御」への転換が可能に。" +
        "特に攻城戦モードでの採用率上昇が見込まれる。",
      changeType: "buff"
    }
  ],

  unitIntelImagePrompt:
    "Technical military blueprint schematic of a futuristic combat mech, " +
    "dark navy background with cyan wireframe lines, annotation callouts with Japanese text, " +
    "cross-section view showing internal components, damage assessment markers in red, " +
    "engineering drawing style, highly detailed, clean vector art, monochrome with accent cyan and red, 4:3 aspect ratio",

  // ────────────────────────────────────────────
  //  SECTION 3 ─ 戦線の声：Community Pulse
  // ────────────────────────────────────────────
  communityPulse: [
    {
      callsign: "WOLF-7",
      affiliation: "第3機甲師団",
      timestamp: "2026-02-12 08:42:31 JST",
      message: "グラディウス乗りとして言わせてもらう。この強化を3ヶ月待った。今夜からランクマ復帰する。",
      sentiment: "positive"
    },
    {
      callsign: "SPECTRE_ACE",
      affiliation: "独立遊撃隊",
      timestamp: "2026-02-12 09:15:07 JST",
      message: "ファントムのナーフは妥当。正直、使ってる側も壊れてると思ってた。ただしCT 22秒はやりすぎだ。",
      sentiment: "mixed"
    },
    {
      callsign: "IRON_MAIDEN_04",
      affiliation: "防衛旅団",
      timestamp: "2026-02-12 10:03:55 JST",
      message: "イージスの速度+4は地味に見えて革命。前線についていける防衛機は正義。",
      sentiment: "positive"
    },
    {
      callsign: "NULL_VECTOR",
      affiliation: "情報参謀部",
      timestamp: "2026-02-12 11:28:19 JST",
      message: "ヴァルキュリアの対空性能、テストサーバーで触った限りではかなりピーキー。使いこなせれば強い。",
      sentiment: "neutral"
    },
    {
      callsign: "RED_BARON_99",
      affiliation: "航空打撃群",
      timestamp: "2026-02-12 12:44:02 JST",
      message: "新マップ「ノルドヘイヴン」、射線の通りが良すぎて狙撃天国になりそう。要注視。",
      sentiment: "warning"
    }
  ],

  communityPulseImagePrompt:
    "Vintage military radio communication equipment on a worn wooden desk, " +
    "green phosphor CRT monitor displaying intercepted text messages in Japanese, " +
    "morse code tape scattered around, dim warm lamp lighting, " +
    "headphones hanging on the side, atmospheric dust particles in light beams, " +
    "1970s military intelligence aesthetic, photorealistic, moody cinematic lighting, 4:3 aspect ratio",

  // ────────────────────────────────────────────
  //  SECTION 4 ─ 作戦カレンダー：Operational Schedule
  // ────────────────────────────────────────────
  operationalSchedule: [
    {
      date: "2026-02-12",
      dateLabel: "本日",
      event: "v3.47 アップデート適用・メンテナンス完了",
      priority: "completed",
      time: "06:00 〜 10:00"
    },
    {
      date: "2026-02-12",
      dateLabel: "本日",
      event: "大規模共同作戦「クリムゾンヴァイパー」開戦",
      priority: "critical",
      time: "12:00 開始"
    },
    {
      date: "2026-02-14",
      dateLabel: "02/14 (土)",
      event: "期間限定：バレンタイン支給品キャンペーン",
      priority: "high",
      time: "00:00 〜 23:59"
    },
    {
      date: "2026-02-18",
      dateLabel: "02/18 (水)",
      event: "ランクマッチ シーズン12 開幕",
      priority: "critical",
      time: "18:00 開始"
    },
    {
      date: "2026-02-22",
      dateLabel: "02/22 (日)",
      event: "公式大会「IRONCLAD CUP」エントリー締切",
      priority: "high",
      time: "23:59 締切"
    },
    {
      date: "2026-02-28",
      dateLabel: "02/28 (金)",
      event: "クリムゾンヴァイパー作戦 終結予定",
      priority: "medium",
      time: "23:59 終了"
    }
  ],

  operationalScheduleImagePrompt:
    "Military operations planning board with pinned calendar dates and red string connections, " +
    "tactical markers and unit position flags on a dark green felt background, " +
    "handwritten notes in both English and Japanese, coffee-stained edges, " +
    "overhead fluorescent lighting casting harsh shadows, " +
    "cold war era intelligence aesthetic, photorealistic, top-down view, 16:9 aspect ratio"
};
