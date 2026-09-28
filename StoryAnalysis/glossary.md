<!-- scripts/terms.py で自動生成。手で編集しない（用語は data/terms.json を編集する）。 -->

# 用語対応表（英語 ⇔ 日本語）

考察は英語原文（`sources/`）を根拠にするので、英語表記と日本語版の表記を対応させておく。
日本語はゲームの日本語ローカライズ（`dict.ja.json`）から自動で引いている。用語を足すときは `data/terms.json` を編集して `python StoryAnalysis/scripts/terms.py` を実行する。

- **根拠** 列の意味
  - `公式`: 英語がその語だけで辞書にあり、対応する日本語訳がある
  - `公式(文中) N 件`: 単独の訳語はないが、その英語を含む N 件の文の日本語版で使われている訳
  - `日本語Wiki`: ゲーム内では確認できないが、[日本語版 Wiki](https://warframe.fandom.com/ja/wiki/)（Fandom）の記事名・定義文にある慣用表記（`日本語Wiki(本文) N 件` は N 件の記事の本文で使われている）。出典の記事はメモ列。取り込んだ資料は [fandom-ja/](fandom-ja/README.md)（CC BY-SA 3.0）
  - `未確認`: どれでも確認できない（コミュニティでの呼び方など）
- 日本語版では、キャラクター名や Warframe 名の多くを英字のまま表記している（例: `Ordis`, `Ballas`）。
- English 列のリンクは、このサイトのキャラクター・クエストのページ。

## 基本概念

| English | 日本語 | 根拠 | メモ |
| --- | --- | --- | --- |
| Tenno | Tenno | 公式 | 文中はテンノ、単独表記は Tenno のことが多い |
| [Operator](wiki/characters/operator.md) | オペレーター | 公式 |  |
| [Drifter](wiki/characters/drifter.md) | 漂流者 | 公式(文中) 166 件 | Duviri 以降の主人公の別の姿 |
| Warframe | WARFRAME / Warframe | 公式(文中) 523 件 |  |
| Transference | 転移 | 公式 | オペレーターが Warframe を操る仕組み |
| Somatic Link | ソマティックリンク | 公式(文中) 3 件 |  |
| Reservoir | リザーバー | 公式(文中) 3 件 | ルアで子供たちが眠っていた装置 |
| Void | Void | 公式 | 訳さない |
| Void Angel | 天使 | 公式 | Zariman の天使 |
| Indifference | 無関心 | 公式(文中) 6 件 | Man in the Wall と関係する存在 |
| Man in the Wall | 壁の中のモノ | 公式(文中) 2 件 | 愛称 Wally |
| Kuva | クバ | 公式 |  |
| [Kuva Lich](wiki/characters/kuva-lich.md) | クバ・リッチ | 公式(文中) 24 件 |  |
| [Sisters of Parvos](wiki/characters/sisters-of-parvos.md) | Parvos シスター | 公式(文中) 11 件 |  |
| Archon | アルコン | 公式(文中) 43 件 | 例: Boreal アルコン |
| Archon Shard | アルコンの欠片 | 公式(文中) 13 件 |  |
| [Helminth](wiki/characters/helminth.md) | Helminth | 公式(文中) 26 件 |  |
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
| [Grineer Queens](wiki/characters/grineer-queens.md) | グリニア両女帝 | 公式(文中) 2 件 |  |
| Twin Queens | 両女帝 | 日本語Wiki(本文) 6 件 | 出典: 本文 [Clem](https://warframe.fandom.com/ja/wiki/Clem)、[内なる紛争](https://warframe.fandom.com/ja/wiki/%E5%86%85%E3%81%AA%E3%82%8B%E7%B4%9B%E4%BA%89)、[Kuva](https://warframe.fandom.com/ja/wiki/Kuva) |
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
| [Vox Solaris](wiki/quests/vox-solaris.md) | Vox Solaris | 公式 |  |
| [Unum](wiki/characters/unum.md) | Unum | 公式(文中) 21 件 |  |
| [Techrot](wiki/characters/techrot.md) | テックロット | 公式 | 1999 の敵勢力 |
| [Scaldra](wiki/characters/scaldra.md) | スカルドラ | 公式 | 1999 の敵勢力 |
| Anarch | アナーク | 公式(文中) 27 件 | Tau 側の勢力（The Old Peace） |
| [Dax](wiki/characters/dax.md) | ダクス | 公式(文中) 72 件 | Tau の Dax |
| Thrax | スラックス | 公式(文中) 12 件 | 例: スラックス・レガトス |
| Arbiters of Hexis | アービターズ・オブ・ヘクシス | 公式 |  |
| [Cephalon Suda](wiki/characters/cephalon-suda.md) | セファロン・スーダ | 公式 |  |
| Steel Meridian | スティール・メリディアン | 公式 |  |
| New Loka | ニュー・ロカ | 公式 |  |
| Perrin Sequence | ペリン・シークエンス | 公式(文中) 23 件 |  |
| [Red Veil](wiki/characters/red-veil.md) | レッド・ベール | 公式 |  |
| [Cephalon Simaris](wiki/characters/cephalon-simaris.md) | セファロン・シマリス | 公式 |  |

## 人物

| English | 日本語 | 根拠 | メモ |
| --- | --- | --- | --- |
| [Lotus](wiki/characters/lotus.md) | Lotus | 公式 |  |
| [Natah](wiki/characters/natah.md) | Natah | 公式 | Lotus の Sentient としての名 |
| [Margulis](wiki/characters/margulis.md) | Margulis | 公式 | Lotus の人間としての姿 |
| [Ordis](wiki/characters/ordis.md) | Ordis | 公式 |  |
| Cephalon | セファロン | 公式(文中) 66 件 |  |
| [Cephalon Cy](wiki/characters/cephalon-cy.md) | Cephalon Cy | 公式 |  |
| Executor Ballas | 執行官 Ballas | 公式(文中) 2 件 |  |
| [Hunhow](wiki/characters/hunhow.md) | Hunhow | 公式 |  |
| [Erra](wiki/characters/erra-character.md) | Erra | 公式 |  |
| [Archon Boreal](wiki/characters/archon-boreal.md) | Boreal アルコン | 公式 |  |
| [Archon Amar](wiki/characters/archon-amar.md) | Amar アルコン | 公式 |  |
| [Archon Nira](wiki/characters/archon-nira.md) | Nira アルコン | 公式 |  |
| [Teshin](wiki/characters/teshin.md) | Teshin | 公式 |  |
| [Dominus Thrax](wiki/characters/dominus-thrax.md) | Dominus Thrax | 公式 |  |
| [Stalker](wiki/characters/stalker.md) | Stalker | 公式 |  |
| [Shadow Stalker](wiki/characters/shadow-stalker.md) | Shadow Stalker | 公式 |  |
| Acolyte | アコライト | 公式(文中) 5 件 | Stalker の従者 |
| [Rell](wiki/characters/rell.md) | Rell | 公式 |  |
| [Albrecht Entrati](wiki/characters/albrecht-entrati.md) | Albrecht Entrati | 公式(文中) 29 件 |  |
| [Loid](wiki/characters/loid.md) | Loid | 公式 |  |
| [Fibonacci](wiki/characters/fibonacci.md) | Fibonacci | 公式 |  |
| [Tagfer](wiki/characters/tagfer.md) | Tagfer | 公式(文中) 6 件 |  |
| [Kaya](wiki/characters/kaya.md) | Kaya | 公式(文中) 13 件 |  |
| [Arthur](wiki/characters/arthur.md) | Arthur | 公式 | The Hex のメンバー |
| [Eleanor](wiki/characters/eleanor.md) | Eleanor | 公式 |  |
| Lettie | Lettie | 公式 |  |
| [Amir](wiki/characters/amir.md) | Amir | 公式 |  |
| [Aoi](wiki/characters/aoi.md) | Aoi | 公式 |  |
| [Quincy](wiki/characters/quincy.md) | Quincy | 公式 |  |
| [The Hex](wiki/quests/the-hex.md) | ヘックス | 公式 |  |
| [Kahl-175](wiki/characters/kahl-175.md) | Kahl-175 | 公式(文中) 10 件 |  |
| [Parvos Granum](wiki/characters/parvos-granum.md) | Parvos Granum | 公式 |  |
| [Nef Anyo](wiki/characters/nef-anyo.md) | Nef Anyo | 公式 |  |
| [Alad V](wiki/characters/alad-v.md) | Alad V | 公式 |  |
| Vay Hek | Vay Hek | 公式(文中) 15 件 |  |
| [Tyl Regor](wiki/characters/tyl-regor.md) | Tyl Regor | 公式 |  |
| [Ergo Glast](wiki/characters/ergo-glast.md) | Ergo Glast | 公式 |  |
| [Baro Ki'Teer](wiki/characters/baro-ki-teer.md) | Baro Ki'Teer | 公式 |  |
| [Darvo](wiki/characters/darvo.md) | Darvo | 公式 |  |
| [Clem](wiki/characters/clem.md) | Clem | 公式(文中) 21 件 |  |
| [Maroo](wiki/characters/maroo.md) | Maroo | 公式 |  |
| [Palladino](wiki/characters/palladino.md) | Palladino | 公式 |  |
| [Nora Night](wiki/characters/nora-night.md) | Nora Night | 公式 |  |
| [Eudico](wiki/characters/eudico.md) | Eudico | 公式 |  |
| [Konzu](wiki/characters/konzu.md) | Konzu | 公式(文中) 7 件 |  |
| [Nakak](wiki/characters/nakak.md) | Nakak | 公式(文中) 4 件 |  |
| [Amaryn](wiki/characters/amaryn.md) | Amaryn | 公式 |  |
| [Nihil](wiki/characters/nihil.md) | Nihil | 公式(文中) 9 件 |  |
| [Otak](wiki/characters/otak.md) | Otak | 公式 |  |
| [Grandmother](wiki/characters/grandmother.md) | Grandmother | 公式 | ダイモスの Entrati 家 |
| [Father](wiki/characters/father.md) | Father | 公式 |  |
| [Daughter](wiki/characters/daughter.md) | Daughter | 公式 |  |
| Jordas | Jordas | 公式 |  |
| [Lephantis](wiki/characters/lephantis.md) | Lephantis | 公式 |  |
| [Ryoku](wiki/characters/ryoku.md) | Ryoku | 公式 | Jade Shadows: Constellations |
| Sirius | Sirius | 公式 |  |
| [Marie](wiki/characters/marie.md) | Marie | 公式 |  |
| [Wolf of Saturn Six](wiki/characters/wolf-of-saturn-six.md) | サターン・シックスの狼 | 公式 |  |
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
| [Orowyrm](wiki/characters/orowyrm.md) | オロワーム | 公式(文中) 11 件 |  |

## クエスト

ゲーム内のクエスト名（すべて公式訳）。

| English | 日本語 |
| --- | --- |
| [A Man of Few Words](wiki/quests/a-man-of-few-words.md) | 寡黙な人物 |
| [Angels of the Zariman](wiki/quests/angels-of-the-zariman.md) | Zarimanの天使 |
| [Apostasy Prologue](wiki/quests/apostasy-prologue.md) | 背信のプロローグ |
| [Call of the Tempestarii](wiki/quests/call-of-the-tempestarii.md) | 嵐を呼ぶ者テンペスタリ |
| [Chains of Harrow](wiki/quests/chains-of-harrow.md) | Harrowの鎖 |
| [Chimera Prologue](wiki/quests/chimera-prologue.md) | キメラプロローグ |
| [Erra](wiki/characters/erra-character.md) | Erra |
| [Heart of Deimos](wiki/quests/heart-of-deimos.md) | ダイモスの心臓 |
| [Hidden Messages](wiki/quests/hidden-messages.md) | 隠されたメッセージ |
| [Howl of the Kubrow](wiki/quests/howl-of-the-kubrow.md) | クブロウ獲得 |
| [Jade Shadows](wiki/quests/jade-shadows.md) | 翡翠の影 |
| [Jade Shadows: Constellations](wiki/quests/jade-shadows-constellations.md) | 翡翠の影：星座 |
| [Mask of the Revenant](wiki/quests/mask-of-the-revenant.md) | Revenantの仮面 |
| [Natah](wiki/characters/natah.md) | Natah |
| [Octavia's Anthem](wiki/quests/octavia-s-anthem.md) | Octaviaの賛美歌 |
| [Once Awake](wiki/quests/once-awake.md) | 博士の計略 |
| [Patient Zero](wiki/quests/patient-zero.md) | 感染起源は誰 |
| [Rising Tide](wiki/quests/rising-tide.md) | 流転する形勢 |
| [Sands of Inaros](wiki/quests/sands-of-inaros.md) | Inaros の砂嵐 |
| [Saya's Vigil](wiki/quests/saya-s-vigil.md) | Sayaの眼 |
| [Stolen Dreams](wiki/quests/stolen-dreams.md) | 奪われた野望 |
| [The Archwing](wiki/quests/the-archwing.md) | アークウイング |
| [The Deadlock Protocol](wiki/quests/the-deadlock-protocol.md) | デッドロック・プロトコル |
| [The Duviri Paradox](wiki/quests/the-duviri-paradox.md) | デュヴィリ・パラドックス |
| [The Glast Gambit](wiki/quests/the-glast-gambit.md) | グラスト・ギャンビット |
| [The Hex](wiki/quests/the-hex.md) | ヘックス |
| The Hex Finale | ヘックスフィナーレ |
| [The Jordas Precept](wiki/quests/the-jordas-precept.md) | Jordas の教訓 |
| [The Limbo Theorem](wiki/quests/the-limbo-theorem.md) | Limbo セオリム |
| [The Lotus Eaters](wiki/quests/the-lotus-eaters.md) | ロートパゴス |
| [The New Strange](wiki/quests/the-new-strange.md) | 新たな怪奇 |
| [The New War](wiki/quests/the-new-war.md) | 新たな大戦 |
| [The Old Peace](wiki/quests/the-old-peace.md) | 古の同盟 |
| [The Sacrifice](wiki/quests/the-sacrifice.md) | サクリファイス |
| [The Second Dream](wiki/quests/the-second-dream.md) | 二番目の夢 |
| [The Silver Grove](wiki/quests/the-silver-grove.md) | 銀の果樹園 |
| [The Teacher](wiki/quests/the-teacher.md) | 師範 |
| [The War Within](wiki/quests/the-war-within.md) | 内なる紛争 |
| [The Waverider](wiki/quests/the-waverider.md) | ウェーブライダー |
| [Veilbreaker](wiki/quests/veilbreaker.md) | ベールブレイカー |
| [Vor's Prize](wiki/quests/vor-s-prize.md) | Vorの秘宝 |
| [Vox Solaris](wiki/quests/vox-solaris.md) | Vox Solaris |
| [Whispers in the Walls](wiki/quests/whispers-in-the-walls.md) | 壁の中の囁き |
