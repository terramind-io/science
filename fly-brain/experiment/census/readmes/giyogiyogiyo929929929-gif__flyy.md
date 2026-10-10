# MaleCNS Fly for Minecraft Bedrock

オスのキイロショウジョウバエ全中枢神経系コネクトーム（neuPrint `male-cns:v1.0`）の部分ネットワークを、
leaky integrate-and-fire ニューロンとして実際に発火させて動くハエ Mob。Minecraft Bedrock Edition のアドオン
（ビヘイビアパック + リソースパック、Script API のみ、実験機能トグル不要の安定版 API）。

参照実装 [blendi-remade/fly-brain-minecraft](https://github.com/blendi-remade/fly-brain-minecraft)（Fabric/Java）の
移植ではなく、Bedrock の制約（スレッドなし・ファイル I/O なし・tick 予算数 ms）の下での再設計。

> **状態（2026-09-14）**: 全マイルストーンのコードを実装し、Node 上のベンチとモック統合テストで検証済み。
> **Minecraft 実機での動作確認はまだ**。何を確かめて何が未確認かは [docs/VALIDATION.md](docs/VALIDATION.md)。

## 何をするか

- ハエが感じたもの（匂い・味・迫る物体・風・雨・接触）が、実在の感覚ニューロン type の発火率になる。
- ネットワークを LIF で積分し、下行・運動ニューロンの発火率から行動（摂食・逃避ジャンプ・毛づくろい・歩行・後退・停止・飛行）を読み出す。
- 自発発火は無い。すべてのスパイクは感覚ニューロンに遡れる。
- 何がコネクトームから出てきて、何が手で書いた足場かは [docs/REFERENCE.md](docs/REFERENCE.md) の表に正直に書いてある。

## インストール

```
python tools/deploy.py
```

`%AppData%\Minecraft Bedrock\Users\Shared\games\com.mojang\development_behavior_packs\fly_brain_bp` と
`development_resource_packs\fly_brain_rp` にコピーされる（GDK 版の場所）。ワールドの設定で両方のパックを有効にする。
対象: Minecraft Bedrock 1.26.40 以降、`@minecraft/server` 2.9.0 / `@minecraft/server-ui` 2.1.0。

## 使い方

1. ワールドに入ると「コネクトーム読み込み完了」とチャットに出る。
2. `/fly:spawn` でハエを出す（`Fly-1 ♂` のネームタグ）。メスは `/fly:spawn 1 female`（`♀`。**脳はオスのコネクトームで代用**し、違うのは見た目と他のハエが感じる匂い・味だけ）。
3. 砂糖を持って右クリック（摂食）、ダッシュで突っ込む（逃避ジャンプ）、`/weather rain`、`/fly:stim MDN 60 3`（後退）。
4. アクションバーに `Fly-1 摂食 | MN9 40Hz | DNp01 0Hz | spk/t 1.4k | RT 0.52x`。`/fly:scope` でニューロスコープ。
5. `/fly:build` で脳をガラスブロックで建て、発火中のニューロンがシーランタンで光る。

コマンド一覧は `/fly:help` と [docs/REFERENCE.md §2](docs/REFERENCE.md)。

プロファイル: `tiny`（2,000 ニューロン、既定）、`small`（12,000）、`large`（40,000、既定では同梱しない）。
`/fly:profile small` → `/reload`。small は刺激後に活動が自己持続して停止しやすい（全ネットワークでも起きるモデルの性質。
[VALIDATION.md §5.3](docs/VALIDATION.md)）。そのときは `/fly:reset`。

## 開発

```
python tools/fetch_neuprint.py          # neuPrint から取得（匿名、約 2.5 分、約 40 MB）
python tools/prune_subnetwork.py        # tiny / small / large を抽出
python tools/build_connectome_js.py     # scripts/data/*.js を生成（既定 tiny,small）
python tools/gen_texture.py             # テクスチャ（Pillow）
node tools/check_syntax.mjs             # 全 JS の構文・JSON・BOM・絵文字の検査
node tools/bench/unitTests.mjs          # 積分器の単体テスト
node tools/bench/brainBench.mjs --profile tiny
node tools/bench/calibrate.mjs --profile tiny
node tools/bench/embodiedBench.mjs --profile tiny
node tools/bench/visionBench.mjs --profile tiny
node tools/bench/persistenceBench.mjs --profile small
node tools/bench/worldSmoke.mjs --profile tiny   # @minecraft/server をモックしてゲーム側コードを実行
```

構成は [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)、データの出どころは [docs/PROVENANCE.md](docs/PROVENANCE.md)。

## 限界

- 全ニューロンが同じパラメータ。触角葉は飽和し、匂い・looming・JO 風の刺激の後に活動が自己持続する（全ネットワークでも同じ）。
- 網膜は無い。looming は物体の角サイズから LC4/LPLC2 に解析的に書き込む。餌への接近は反射レイヤ。
- 枝刈りで保持しているシナプスは tiny 0.8%、small 8%、large 21%。ゲインはプロファイルごとに再較正した。
- 神経修飾、神経ペプチド、ギャップ結合、自発活動は無い。5 シナプス未満の結合は除外。
- 雌の脳は無い（メスもオスの脳で動く）。絶対発火率は信用せず、どの population が応答したかのパターンだけを見ること。

## データと引用

同梱データは neuPrint `male-cns:v1.0`（HHMI Janelia FlyEM Project Team、Drosophila Connectomics Group（University of
Cambridge / MRC LMB）、Google Research）の派生物で **CC BY 4.0**。改変: シナプス数閾値、部分ネットワーク抽出、再インデックス、
量子化（[docs/PROVENANCE.md](docs/PROVENANCE.md)）。

- Berg S, Beckett IR, Costa M, Schlegel P, Januszewski M, et al. *Cell* 189(18):5504-5526 (2026). doi:10.1016/j.cell.2026.08.015
- Shiu PK, Sterne GR, Spiller N, et al. *Nature* 634:210-219 (2024). doi:10.1038/s41586-024-07763-9
- Plaza SM, Clements J, Dolafi T, et al. *Front. Neuroinform.* 16:896292 (2022). doi:10.3389/fninf.2022.896292

本プロジェクトは HHMI、Janelia、Google、University of Cambridge、MRC LMB、Mojang / Microsoft とは無関係で、
これらの組織による承認を受けていない。Minecraft は Mojang / Microsoft の商標。

## ライセンス

コード: MIT（[LICENSE](LICENSE)）。同梱のコネクトーム派生データ: CC BY 4.0。
