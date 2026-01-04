# Notebook 01/02 のAPI化メモ（現状棚卸し）

この文書は、notebooks/01_band_analysis.ipynb と notebooks/02_dark_morphology.ipynb の処理を、現在の `src/amanogawa/` の API/CLI でどこまで再現できるか、そして今後どこからAPI化を進めるべきかを「記録」として残すものです。

## 結論（短く）

- **Notebook 01/02 の「コア計算」（検出・幾何・統計・暗黒帯マスク・簡易測光）は、概ね `src/amanogawa/` の API/CLI で再現可能**です。
- ただし、Notebook 由来で **まだ API 化されていない**要素があります（例：**bulge の放射プロファイル（annulus stats）**, **star detection quality のレポート**, **一部の統合サマリ生成/可視化**）。

---

## Notebook 01: band_analysis の対応表

### A) 既に API/CLI で代替できる（推奨：Notebookから関数定義を消して import に寄せる）

- **Star Detection（LoG / blob_log）**
  - API: `amanogawa.detection.detect_stars_log`
  - CLI: `amanogawa-detect --image ... --out ... --threshold ...`

- **Detection Threshold Sensitivity（しきい値スイープ）**
  - API: `amanogawa.detection.threshold_sweep`
  - CLI: `amanogawa-detect --threshold-min ... --threshold-max ... --steps ...`
  - 備考: Notebook 側の出力ファイル名・列名と完全一致させたい場合は、整形用の薄いラッパーを追加するのが最小です。

- **Band Geometry（PCA 軸推定 + バンド幅）**
  - API: `amanogawa.band_geometry.analyze_band_geometry`
  - CLI: `amanogawa-band --coords ... --width ... --height ... --out ...`

- **Spatial Statistics（NND / 2PCF / Box-counting）**
  - API: `amanogawa.spatial_stats.nearest_neighbor_distances`
  - API: `amanogawa.spatial_stats.two_point_correlation_function`
  - API: `amanogawa.spatial_stats.boxcount_fractal_dimension`
  - CLI: `amanogawa-stats --coords ... --width ... --height ... --out ...`

- **Photometry（簡易 aperture photometry + magnitude terciles）**
  - API: `amanogawa.photometry.aperture_photometry`, `assign_magnitude_bins_from_files`
  - CLI: `amanogawa-photometry --image ... --coords ... --out ...`
  - 連携: `amanogawa-stats --magnitude-bins <magnitude_bins.csv>`

### B) Notebook 01 にあるが、API にはまだ無い/不完全な可能性が高い

- **ROI contrast / band ROI 関連の集計**
  - `outputs/band_analysis/results/band_roi_contrast_summary.json` のような成果物を生成する処理は、現状 CLI/API 側に明示的に存在しません。

- **統合サマリ生成（complete_analysis_summary / master summary 的な統合JSON）**
  - 複数の解析結果 JSON を「1枚にまとめる」レポート処理は Notebook 側に寄っている可能性が高いです。

### C) Notebook 専用でよい（API化しなくてよいことが多い）

- 図生成、探索的可視化、パラメータをいじりながらのデバッグ用プロット

---

## Notebook 02: dark_morphology の対応表

### A) 既に API/CLI で代替できる

- **Improved Dark Lane Detection（multi-scale + multi-threshold + morphology + watershed）**
  - API: `amanogawa.dark_morphology.detect_dark_lane_mask`
  - CLI: `amanogawa-dark --image ... --out ...`
  - 備考: watershed / skeletonize / fractal dimension（mask と skeleton）まで含めて実装済みです。

### B) Notebook 02 にあるが、API にはまだ無い

- **Bulge radial profiles（annulus stats による surface brightness profile）**
  - Notebook 02 に `annulus_stats_surface_brightness(...)` があり、`outputs/dark_morphology/results/bulge_radial_profiles.csv` を保存しています。
  - 現状 `src/amanogawa/` 側にはこの「楕円/回転を含む annulus stats」の関数が見当たりません（少なくとも `dark_morphology.py` にはありません）。

- **Star detection quality report**
  - Notebook 02 は `outputs/dark_morphology/results/star_detection_quality.json` を出力します。
  - これは「検出結果の品質を定量化して JSON にする」レポート層なので、今の CLI 群には相当処理がありません。

### C) Notebook 専用でよい

- 図生成（segmentation の可視化、品質分析プロット等）

---

## どこから API 化を進めるべきか（最小コスト順）

1. **Notebook 01/02 内の “重複関数定義” を削って import に寄せる**
   - 例: LoG 検出・PCA・2PCF・boxcount などは `src/amanogawa/` を正として Notebook は呼び出し側にする。
   - これだけで「Notebookは実験場、実装はパッケージ」が明確になり、保守コストが落ちます。

2. **Notebook 02 の annulus profile（bulge_radial_profiles.csv）だけを小さく API 化**
   - これは “分析の再現性” に直結しやすく、図生成とも分離しやすいです。
   - 追加するなら `amanogawa.profiles` のような独立モジュールに `annulus_stats_surface_brightness` を置くのが安全です。

3. **Notebook 01 の ROI contrast / 統合サマリ生成を「レポート層」として API 化するか決める**
   - JOSS 的には「主張しているコア解析が CLI/API で再現できる」ことが重要なので、
     これらは *必須ではない* 可能性があります。
   - ただし Zenodo に「代表的な再現成果物」を含めたいなら、薄い `amanogawa.report` 的な集約関数を追加すると整理できます。

---

## 追加チェック（やると迷子になりにくい）

- Notebook 01/02 が最終的に生成したい成果物（JSON/CSV/PNG）のリストを確定する
- そのうち「論文の主要主張に必要な成果物」だけを “API/CLI で生成可能” にする
- 残り（探索図・デバッグ図・作業用集計）は Notebook 専用として割り切る
