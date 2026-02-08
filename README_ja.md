<!-- NOTE: English README.md is canonical. / 英語版 README.md を正とします -->
# Amanogawa（日本語）

単一のスマホ長時間露光画像から、天の川構造を再現可能に定量化します。

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](#license)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18213565.svg)](https://doi.org/10.5281/zenodo.18213565)

[Colab で開く: Band Analysis](https://colab.research.google.com/github/SHayashida/Amanogawa/blob/main/notebooks/01_band_analysis.ipynb)

[Colab で開く: Dark Morphology](https://colab.research.google.com/github/SHayashida/Amanogawa/blob/main/notebooks/02_dark_morphology.ipynb)

## Statement of need（必要性）

Amanogawa は、オープンソース（MIT ライセンス）の Python パッケージと再現可能なワークフローで、単一の広視野スマホ長時間露光画像から天の川の構造を定量的に要約します。市民科学・教育・小規模研究に適した、透明で検証可能な測定を提供します。1 枚の画像から、候補点光源の検出、座標カタログの出力、スケールにまたがるクラスタリングを要約する空間統計を実行します。並行して、画像座標系で天の川バンドの主軸を推定し、直交プロファイルから帯幅を測定して、画像内・画像間で一貫した比較を可能にします。完全なアストロメトリ（WCS 等）が無くても意味のある分析となるよう設計されています。ワークフローはノートブックとコマンドラインの両方をサポートし、CSV/JSON/PNG のアーカイブ向け成果物（星カタログ、閾値スイープ要約、フィット済み帯幅パラメータ、診断/出版品質の図）を生成します。

## What is included（構成）

- **コアライブラリ:** `src/amanogawa/`（pip インストール可能）
- **CLI:** `amanogawa-*` のコマンド群
- **ノートブック:** `notebooks/`（チュートリアル/再現用）
- **JOSS 原稿:** `paper/paper.md`（+ `paper/paper.bib`）

## Installation（インストール）

> 推奨: **Python 3.10.x**。動作確認済み: **3.10〜3.12**。現状 **3.13** は避けてください。

```bash
python -m venv .venv
source .venv/bin/activate

# ruff/pytest を含む dev extras をデフォルトでインストール
pip install -e ".[dev]"

# 任意: iPhone の .heif/.heic 原画像を直接読む場合
pip install -e ".[dev,heif]"
```

### Docker ベースのインストール（レビュア向け）

Mac などでビルドに詰まる場合やクリーン環境で検証したい場合:

```bash
docker run -it --rm python:3.10-slim /bin/bash
```

コンテナ内で:

```bash
# 1. 必要なビルド用パッケージ
apt-get update
apt-get install -y gcc g++ build-essential python3-dev git

# 2. リポジトリを取得
git clone https://github.com/SHayashida/Amanogawa.git
cd Amanogawa

# 3. 依存関係込みでインストール（ruff/pytest を含む dev extras）
pip install -e ".[dev]"
```

## Quick start（CLI）

`data/raw/` に画像を置いて実行します（リポジトリには `data/raw/IMG_5991.jpg` が同梱されています）。

1. 星検出（座標 CSV と閾値スイープの要約を出力）:

```bash
amanogawa-detect --image data/raw/IMG_5991.jpg --out outputs/ \
  --threshold-min 0.03 --threshold-max 0.08 --steps 10
```

1. 空間統計（2 点相関・最近傍距離・ボックスカウント次元など）:

```bash
amanogawa-stats --coords outputs/star_coords.csv --out outputs/
```

1. バンド幾何（主軸推定 + ガウス/ローレンツ幅フィット）:

```bash
amanogawa-band --coords outputs/star_coords.csv --width 3024 --height 4032 --out outputs/
```

1. 暗黒帯形態（暗黒帯マスク + 形態メトリクス）:

```bash
amanogawa-dark --image data/raw/IMG_5991.jpg --out outputs/dark_morphology/results
```

出力例:

- `outputs/dark_morphology/results/improved_dark_detection.json`
- `outputs/dark_morphology/results/dark_lane_mask.png`

## Notebooks（ノートブック）

ノートブックはチュートリアルとして提供しています（実装の本体は `src/amanogawa/`）。

- `notebooks/01_band_analysis.ipynb`: バンド幾何 + クラスタリング
- `notebooks/02_dark_morphology.ipynb`: 暗黒帯形態解析
- `notebooks/03_astronomical_validity.ipynb`: `outputs/` を読み込む統合クロスチェック

## Tests and code quality（テスト/品質）

テスト:

```bash
pytest
```

Lint:

```bash
ruff check src tests
```

CI でも lint + tests を実行します。

## Citation（引用）

JOSS 原稿ソース: `paper/paper.md` と `paper/paper.bib`。

Zenodo DOI 発行後は、英語版 README.md の Citation 節を更新してください。

## Data license（画像データ）

`data/raw/IMG_5991.jpg`（サンプルのスマホ天体写真）:

- Copyright: © 2025 Shunya Hayashida
- License: CC BY 4.0

詳細は `DATA_LICENSE.md` を参照してください。

## License

ソフトウェアは MIT License です（`LICENSE` を参照）。

## Contributing

`CONTRIBUTING.md` と `CODE_OF_CONDUCT.md` を参照してください。

## Contact

- Shunya Hayashida: [1720067169@campus.ouj.ac.jp](mailto:1720067169@campus.ouj.ac.jp)
- X: [https://x.com/HayashidaLynda](https://x.com/HayashidaLynda)
