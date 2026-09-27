# Horizon-Consistent Multi-Step Cyclone Trajectory Prediction over the Bay of Bengal

**IBTrACS v4 | North Indian Ocean | 3 h / 12 h / 24 h track forecasting**

> **Anonymous repository.** Code release: full source, configs, and reproduction scripts will be published upon paper acceptance. Until then, this repository documents the research contribution without releasing implementation details.

We report a **23-model** benchmark (11 classical, 9 deep, 3 proposed) on multi-horizon cyclone **track** prediction, with the **top 15 models per horizon** under a **uniform training protocol**. The primary system is the **Subset-Expert Context-Aware Ensemble (SECE)**: 28 base learners (tree models on five physics-informed feature subsets plus the full 49-D set, together with Bidirectional LSTM and CNN-GRU) fused by a context-aware **LightGBM** meta-learner at 3 h / 12 h and **Ridge** regression at 24 h, using **out-of-fold** base predictions only at the meta stage. Supplementary architectures **PRC** (Persistence Residual Cascade) and **CB+MotionNN** (CatBoost + kinematic MLP residual) are included as physics-informed baselines. A **zero-shot** evaluation on Western Pacific IBTrACS data (no retraining) assesses cross-basin transfer.

---

## Key results (Bay of Bengal test split)

**Metric:** median great-circle (Haversine) error (km).  
**Test frame:** **3,696** multi-horizon origins from **156** held-out storms (storm-wise **70 : 15 : 15**, seed **42**). Same test origins for all models and horizons (revision manuscript Table I).

| Horizon | SECE median | Best comparator (median) | Note |
|--------:|------------:|---------------------------:|------|
| **3 h** | **4.40** | Stacking (RF+XGB+LGB) **4.43** | SECE lowest; paired Wilcoxon vs. stacking *p* = 0.14 |
| **12 h** | **30.00** | Stacking **29.88** | Statistically tied (*p* = 0.15 vs. stacking) |
| **24 h** | **86.44** | LightGBM **88.12** | SECE lowest; vs. stacking *p* = 0.12 |

SECE is significantly better than single LightGBM at 3 h (*p* < 0.001). Under the fixed budget, **tree-based models outperform standalone deep learning** at every horizon; CNN-GRU 24 h median **102.17 km** vs. LightGBM **88.12 km**.

---

## Zero-shot cross-basin (Western Pacific)

Models applied **without retraining** to a Western Pacific IBTrACS extract (**4,140** storms; South China Sea region). Median Haversine error (km):

| Model | 3 h (WP) | 12 h (WP) | 24 h (WP) |
|-------|---------:|----------:|----------:|
| Random Forest | **6.99** | 59.81 | 180.80 |
| CB+MotionNN | 7.92 | **54.02** | **166.30** |
| SECE | 7.47 | 59.53 | 172.38 |
| CNN-GRU | 27.21 | 109.59 | 223.69 |

Trees transfer with modest degradation; **CB+MotionNN** achieves the strongest among proposed architectures at **12 h** and **24 h** in WP. Deep sequence models degrade more sharply under domain shift.

---

## Dataset and features

**Source:** IBTrACS v4, North Indian Ocean ([NOAA NCEI](https://www.ncei.noaa.gov/products/international-best-track-archive)).

After quality control: **46,053** points, **1,519** storms (**1,427** Bay of Bengal genesis). Multi-horizon targets (3 / 12 / 24 h) require sufficient forward track: **1,031** storms, **24,287** origins. Storm-wise split (seed 42): **721 / 154 / 156** train / val / test storms; reported BoB medians use the **3,696**-origin test set (**149** BoB genesis, **7** non-BoB).

**Download (North Indian Ocean CSV):**

```bash
wget https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.NI.list.v04r01.csv
```

Place the file under **`Data/`**, then run **`Notebook/multi-horizon-finalized-experiment.ipynb`**. Processed tables may appear under **`Datasets/`**; run outputs under **`Outputs/`** (metrics, plots, predictions, trajectory maps).

### 49 engineered features

Four physics-informed groups plus missingness indicators (revision manuscript Section II):

| Group | Count | Content |
|-------|------:|---------|
| **Position** | 9 | Lat/lon, interaction, lags t-1 to t-3 |
| **Motion** | 16 | Displacements, speed, bearing sin/cos, acceleration, trends |
| **Physics** | 7 | Curvature, stability, consistency, seasonality, recurvature proxy |
| **Environment** | 8 | Distance to land, landfall, wind estimate, speed/dir, BoB centroid distance, rates of change |
| **Missingness** | 9 | Flags for imputed lags and wind |

**t-SNE** on the 49-D training space (Fig. 2 in the paper) motivates subset-expert design.

---

## Method summary

### SECE (Tier 1 + Tier 2)

- **Tier 1:** 28 predictive signals: CatBoost, XGBoost, LightGBM, Random Forest on **five** subset views **plus full features**, plus BLSTM and CNN-GRU.
- **Tier 2:** LightGBM **context router** (9 storm-level features) at **3 h / 12 h**; **Ridge** stack at **24 h**. Meta-learners trained on **validation out-of-fold** base predictions only.

### PRC

Persistence extrapolation + LightGBM residual in **km**, mapped back to degree-space displacements.

### CB+MotionNN

CatBoost trajectory + **64-32-16** MLP (**MotionNN**) on kinematic residuals in km space.

### Fair comparison protocol

All **23** candidates share: lr **0.01**, **300** epochs/estimators, batch **128**, dropout **0.2**, storm-wise **70 : 15 : 15**, seed **42**.

---

## Reproducing experiments

1. Install dependencies from the notebook / project environment used in **`Notebook/multi-horizon-finalized-experiment.ipynb`**.
2. Ensure IBTrACS NI CSV is in **`Data/`** (see above).
3. Execute the notebook pipeline or saved artifacts in **`Outputs/`** for benchmark figures and tables aligned with the submission.

Figures referenced in the paper (3 h benchmark bar chart, SECE architecture diagram, t-SNE, Cyclone Titli case study) correspond to assets under **`Outputs/`** and **`Notebook/`** when regenerated locally.

---


## License and data

See the repository license file. **IBTrACS** use is subject to [NOAA NCEI terms](https://www.ncei.noaa.gov/products/international-best-track-archive).
