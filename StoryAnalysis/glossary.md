<!-- scripts/terms.py で自動生成。手で編集しない（用語は data/terms.json を編集する）。 -->

# 用語対応表（英語 ⇔ 日本語）

考察は英語原文（`sources/`）を根拠にするので、英語表記と日本語版の表記を対応させておく。
日本語はゲームの日本語ローカライズ（`dict.ja.json`）から自動で引いている。用語を足すときは `data/terms.json` を編集して `python StoryAnalysis/scripts/terms.py` を実行する。

- **根拠** 列の意味
  - `公式`: 英語がその語だけで辞書にあり、対応する日本語訳がある
  - `公式(文中) N 件`: 単独の訳語はないが、その英語を含む N 件の文の日本語版で使われている訳
  - `未確認`: ゲーム内で確認できない（コミュニティでの呼び方など）
- 日本語版では、キャラクター名や Warframe 名の多くを英字のまま表記している（例: `Ordis`, `Ballas`）。

## 基本概念

| English | 日本語 | 根拠 | メモ |
| --- | --- | --- | --- |
| Tenno | Tenno | 公式 | 文中はテンノ、単独表記は Tenno のことが多い |
| Operator | オペレーター | 公式 |  |
| Drifter | 漂流者 | 公式(文中) 166 件 | Duviri 以降の主人公の別の姿 |
| Warframe | WARFRAME / Warframe | 公式(文中) 523 件 |  |
| Transference | 転移 | 公式 | オペレーターが Warframe を操る仕組み |
| Somatic Link | ソマティックリンク | 公式(文中) 3 件 |  |
| Reservoir | リザーバー | 公式(文中) 3 件 | ルアで子供たちが眠っていた装置 |
| Void | Void | 公式 | 訳さない |
| Void Angel | 天使 | 公式 | Zariman の天使 |
| Indifference | 無関心 | 公式(文中) 6 件 | Man in the Wall と関係する存在 |
| Man in the Wall | 壁の中のモノ | 公式(文中) 2 件 | 愛称 Wally |
| Kuva | クバ | 公式 |  |
| Kuva Lich | クバ・リッチ | 公式(文中) 24 件 |  |
| Sisters of Parvos | Parvos シスター | 公式(文中) 11 件 |  |
| Archon | アルコン | 公式(文中) 43 件 | 例: Boreal アルコン |
| Archon Shard | アルコンの欠片 | 公式(文中) 13 件 |  |
| Helminth | Helminth | 公式(文中) 26 件 |  |
| Steel Path | 鋼の道のり | 公式(文中) 107 件 |  |
| Continuity | Continuity | 公式 | Orokin の不死の技術。関連外装コレクションは「永遠」と訳されている |
| Relay | リレー | 公式(文中) 40 件 |  |
| Railjack | レールジャック | 公式 |  |
| Leverian | レベリアン | 公式(文中) 4 件 | 表記揺れあり（レべリアン） |
| Netracell | ネットセル | 公式 |  |
| Mirror Defense | ミラー防衛 | 公式 |  |

## 勢力・種族

| English | 日本語 | 根拠 | メモ |
| --- | --- | --- | --- |
| Orokin | オロキン | 公式 | ほかの表記: Orokin |
| Orokin Empire | オロキン帝国 | 公式(文中) 4 件 | 文中では「オロキン時代」とも |
| Sentient | センティエント | 公式(文中) 217 件 |  |
| Grineer | グリニア | 公式 | ほかの表記: Grineer |
| Grineer Queens | グリニア両女帝 | 公式(文中) 2 件 |  |
| Twin Queens | 両女帝 | 未確認 |  |
| Corpus | コーパス | 公式 | ほかの表記: Corpus |
| Infested | 感染体 | 公式 | ほかの表記: Infested |
| Infestation | 感染 | 公式 | ほかの表記: 感染体 |
| Mutalist | ミュータリスト | 公式(文中) 28 件 |  |
| Narmer | Narmer | 公式 | 文中はナルメル; ほかの表記: ナルメル |
| Entrati | エントラティ | 公式 |  |
| Necraloid | ネクロロイド | 公式 |  |
| Ostron | オストロン | 公式 |  |
| Solaris United | ソラリス連合 | 公式 |  |
| Ventkids | ベントキッド | 公式 |  |
| The Quills | クイル | 公式 |  |
| Vox Solaris | Vox Solaris | 公式 |  |
| Unum | Unum | 公式(文中) 21 件 |  |
| Techrot | テックロット | 公式 | 1999 の敵勢力 |
| Scaldra | スカルドラ | 公式 | 1999 の敵勢力 |
| Anarch | アナーク | 公式(文中) 27 件 | Tau 側の勢力（The Old Peace） |
| Dax | ダクス | 公式(文中) 72 件 | Tau の Dax |
| Thrax | スラックス | 公式(文中) 12 件 | 例: スラックス・レガトス |
| Arbiters of Hexis | アービターズ・オブ・ヘクシス | 公式 |  |
| Cephalon Suda | セファロン・スーダ | 公式 |  |
| Steel Meridian | スティール・メリディアン | 公式 |  |
| New Loka | ニュー・ロカ | 公式 |  |
| Perrin Sequence | ペリン・シークエンス | 公式(文中) 23 件 |  |
| Red Veil | レッド・ベール | 公式 |  |
| Cephalon Simaris | セファロン・シマリス | 公式 |  |

## 人物

| English | 日本語 | 根拠 | メモ |
| --- | --- | --- | --- |
| Lotus | Lotus | 公式 |  |
| Natah | Natah | 公式 | Lotus の Sentient としての名 |
| Margulis | Margulis | 公式 | Lotus の人間としての姿 |
| Ordis | Ordis | 公式 |  |
| Cephalon | セファロン | 公式(文中) 66 件 |  |
| Cephalon Cy | Cephalon Cy | 公式 |  |
| Executor Ballas | 執行官 Ballas | 公式(文中) 2 件 |  |
| Hunhow | Hunhow | 公式 |  |
| Erra | Erra | 公式 |  |
| Archon Boreal | Boreal アルコン | 公式 |  |
| Archon Amar | Amar アルコン | 公式 |  |
| Archon Nira | Nira アルコン | 公式 |  |
| Teshin | Teshin | 公式 |  |
| Dominus Thrax | Dominus Thrax | 公式 |  |
| Stalker | Stalker | 公式 |  |
| Shadow Stalker | Shadow Stalker | 公式 |  |
| Acolyte | アコライト | 公式(文中) 5 件 | Stalker の従者 |
| Rell | Rell | 公式 |  |
| Albrecht Entrati | Albrecht Entrati | 公式(文中) 29 件 |  |
| Loid | Loid | 公式 |  |
| Fibonacci | Fibonacci | 公式 |  |
| Tagfer | Tagfer | 公式(文中) 6 件 |  |
| Kaya | Kaya | 公式(文中) 13 件 |  |
| Arthur | Arthur | 公式 | The Hex のメンバー |
| Eleanor | Eleanor | 公式 |  |
| Lettie | Lettie | 公式 |  |
| Amir | Amir | 公式 |  |
| Aoi | Aoi | 公式 |  |
| Quincy | Quincy | 公式 |  |
| The Hex | ヘックス | 公式 |  |
| Kahl-175 | Kahl-175 | 公式(文中) 10 件 |  |
| Parvos Granum | Parvos Granum | 公式 |  |
| Nef Anyo | Nef Anyo | 公式 |  |
| Alad V | Alad V | 公式 |  |
| Vay Hek | Vay Hek | 公式(文中) 15 件 |  |
| Tyl Regor | Tyl Regor | 公式 |  |
| Ergo Glast | Ergo Glast | 公式 |  |
| Baro Ki'Teer | Baro Ki'Teer | 公式 |  |
| Darvo | Darvo | 公式 |  |
| Clem | Clem | 公式(文中) 21 件 |  |
| Maroo | Maroo | 公式 |  |
| Palladino | Palladino | 公式 |  |
| Nora Night | Nora Night | 公式 |  |
| Eudico | Eudico | 公式 |  |
| Konzu | Konzu | 公式(文中) 7 件 |  |
| Nakak | Nakak | 公式(文中) 4 件 |  |
| Amaryn | Amaryn | 公式 |  |
| Nihil | Nihil | 公式(文中) 9 件 |  |
| Otak | Otak | 公式 |  |
| Grandmother | Grandmother | 公式 | ダイモスの Entrati 家 |
| Father | Father | 公式 |  |
| Daughter | Daughter | 公式 |  |
| Jordas | Jordas | 公式 |  |
| Lephantis | Lephantis | 公式 |  |
| Ryoku | Ryoku | 公式 | Jade Shadows: Constellations |
| Sirius | Sirius | 公式 |  |
| Marie | Marie | 公式 |  |
| Wolf of Saturn Six | サターン・シックスの狼 | 公式 |  |
| Worm Queen | Worm Queen | 公式 |  |
| Oraxia | Oraxia | 公式 |  |

## 場所

| English | 日本語 | 根拠 | メモ |
| --- | --- | --- | --- |
| Lua | ルア | 公式 |  |
| Zariman | Zariman | 公式 |  |
| Zariman Ten Zero | Zariman | 公式(文中) 1 件 |  |
| Chrysalith | クリサリス | 公式 | Zariman の拠点 |
| Duviri | デュヴィリ | 公式 |  |
| Deimos | ダイモス | 公式 |  |
| Necralisk | ネクロリスク | 公式 |  |
| Cambion Drift | カンビオン荒地 | 公式 |  |
| Sanctum Anatomica | サンクタム・アナトミカ | 公式 | ほかの表記: Sanctum Anatomica |
| Höllvania | ホルバニア | 公式 | 1999 の舞台 |
| Cetus | シータス | 公式 |  |
| Plains of Eidolon | エイドロンの草原 | 公式 |  |
| Fortuna | フォーチュナー | 公式 |  |
| Orb Vallis | オーブ峡谷 | 公式 |  |
| Kuva Fortress | クバ要塞 | 公式 |  |
| Tyana Pass | Tyana Pass | 公式 |  |
| Tau | Tau | 公式(文中) 43 件 | Tau 星系 |
| Isleweaver | 島々を織りしもの | 公式 |  |

## Eidolon

| English | 日本語 | 根拠 | メモ |
| --- | --- | --- | --- |
| Eidolon | エイドロン | 公式(文中) 211 件 |  |
| Teralyst | テラリスト | 公式(文中) 12 件 |  |
| Ropalolyst | ロパロリスト | 公式 |  |
| Orowyrm | オロワーム | 公式(文中) 11 件 |  |

## クエスト

ゲーム内のクエスト名（すべて公式訳）。

| English | 日本語 |
| --- | --- |
| A Man of Few Words | 寡黙な人物 |
| Angels of the Zariman | Zarimanの天使 |
| Apostasy Prologue | 背信のプロローグ |
| Call of the Tempestarii | 嵐を呼ぶ者テンペスタリ |
| Chains of Harrow | Harrowの鎖 |
| Chimera Prologue | キメラプロローグ |
| Erra | Erra |
| Heart of Deimos | ダイモスの心臓 |
| Hidden Messages | 隠されたメッセージ |
| Howl of the Kubrow | クブロウ獲得 |
| Jade Shadows | 翡翠の影 |
| Jade Shadows: Constellations | 翡翠の影：星座 |
| Mask of the Revenant | Revenantの仮面 |
| Natah | Natah |
| Octavia's Anthem | Octaviaの賛美歌 |
| Once Awake | 博士の計略 |
| Patient Zero | 感染起源は誰 |
| Rising Tide | 流転する形勢 |
| Sands of Inaros | Inaros の砂嵐 |
| Saya's Vigil | Sayaの眼 |
| Stolen Dreams | 奪われた野望 |
| The Archwing | アークウイング |
| The Deadlock Protocol | デッドロック・プロトコル |
| The Duviri Paradox | デュヴィリ・パラドックス |
| The Glast Gambit | グラスト・ギャンビット |
| The Hex | ヘックス |
| The Hex Finale | ヘックスフィナーレ |
| The Jordas Precept | Jordas の教訓 |
| The Limbo Theorem | Limbo セオリム |
| The Lotus Eaters | ロートパゴス |
| The New Strange | 新たな怪奇 |
| The New War | 新たな大戦 |
| The Old Peace | 古の同盟 |
| The Sacrifice | サクリファイス |
| The Second Dream | 二番目の夢 |
| The Silver Grove | 銀の果樹園 |
| The Teacher | 師範 |
| The War Within | 内なる紛争 |
| The Waverider | ウェーブライダー |
| Veilbreaker | ベールブレイカー |
| Vor's Prize | Vorの秘宝 |
| Vox Solaris | Vox Solaris |
| Whispers in the Walls | 壁の中の囁き |
