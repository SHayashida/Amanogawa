# 天の川バンド構造解析結果

## 概要
IMG_5991.jpgの天の川画像に対する統計解析結果です。

## 解析日時
2025年10月02日 23:04

## 生成ファイル

### 結果データ (results/)
- band_width_analysis.json
- band_roi_contrast_summary.json
- dark_morphology_summary.json
- sample_detection_summary.json
- complete_analysis_summary.json
- magnitude_analysis.json
- spatial_statistics_detailed.json
- sample_analysis_summary.json
- detection_summary.json

### 図表 (figures/)  
- magnitude_correlation_analysis.png
- FigC_CCDF_band_vs_outside.png
- parameter_sensitivity_analysis.png
- magnitude_distribution.png
- two_point_correlation.png
- milky_way_band_profile.png
- nearest_neighbor_distribution.png
- magnitude_spatial_distribution.png
- correlation_function_detailed.png
- nearest_neighbor_detailed.png
- star_density_map.png
- star_distribution_map.png
- FigB_star_dark_correlation.png
- FigA_ROI_mask.png
- fractal_dimension_plot.png
- fractal_dimension_detailed.png

### 座標データ
- IMG_5991_star_coords.csv

## 解析手法
1. LoG (Laplacian of Gaussian) による星検出
2. 最近傍距離分布解析
3. フラクタル次元測定 (ボックスカウント法)
4. 2点相関関数計算
5. 等級別空間分布解析
6. PCA主成分分析による天の川バンド幅測定

## 再現性
このノートブック (01_band_analysis.ipynb) を実行することで、
すべての結果を再現できます。

## Zenodo対応
このデータセットはZenodo公開に対応しており、
完全に実行可能な状態で提供されています。
