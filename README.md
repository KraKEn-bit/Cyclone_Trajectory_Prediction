# Horizon-Consistent Multi-Step Cyclone Trajectory Prediction

**Bay of Bengal · North Indian Ocean · IBTrACS · multi-horizon track forecasting**

This GitHub repository holds **two related but distinct** research lines on **tropical cyclone track (position) prediction**:

| Line | Paper / venue | Where in this repo |
|------|----------------|-------------------|
| **IBTrACS-only benchmark (ICCACCESS lineage)** | Multi-model benchmark with SECE, deep learning, zero-shot transfer (revision track) | **`Data/`**, **`Datasets/`**, **`Notebook/`**, **`Outputs/`** |
| **ERA5-augmented leakage-aware benchmark** | *ERA5-Augmented Ensemble Learning for Multi-Horizon Tropical Cyclone Track Prediction over the Bay of Bengal* (IEEE conference draft; journal + AMS WAF variants) | **[`ERA5-NEW-Analysis/`](ERA5-NEW-Analysis/)** — **start with [`ERA5-NEW-Analysis/README.md`](ERA5-NEW-Analysis/README.md)** |

**LaTeX manuscripts are not stored in git** (private / Overleaf). Numbers for the ERA5 papers are frozen under `ERA5-NEW-Analysis/docs/paper_writeup_data/`.

---

## Repository layout (top level)

| Path | Role |
|------|------|
| **[`ERA5-NEW-Analysis/`](ERA5-NEW-Analysis/)** | Locked **IBTrACS + ERA5 point** pipeline, eight-system held-out confirm, docs, figures, modeling CSVs, evaluation scripts |
| **[`Final_Cyclone_Pred_Results_P-3/`](Final_Cyclone_Pred_Results_P-3/)** | Shared **SECE v2 trainer** and **seed protocol** used by the ERA5 line (`pipeline_common.py`, `sece_v2_train.py`, `eval_protocol.py`) |
| **[`Data/`](Data/)** | IBTrACS v4 **download instructions** and notes for the legacy notebook workflow |
| **[`Datasets/`](Datasets/)** | Curated CSV extracts: Bangladesh-filtered tracks, regional subsets, original IBTrACS copies, finalized modeling tables |
| **[`Notebook/`](Notebook/)** | **`multi-horizon-finalized-experiment.ipynb`** — end-to-end legacy multi-horizon experiment |
| **[`Outputs/`](Outputs/)** | Saved **metrics**, **plots**, **predictions**, and **trajectory maps** from legacy runs |
| **`README.md`** | This file (legacy + navigation) |

Do **not** treat `ERA5-NEW-Analysis/` as a rename of the old root README content: the **long ERA5 methods, tables, and reproduction steps live only in that subfolder**.

---

## Legacy line: IBTrACS-only 15-model benchmark

### Summary

> A comprehensive **23-candidate** benchmark (11 classical, 9 deep, 3 proposed architectures), reporting the **top 15 per horizon** under a **uniform training protocol** (lr = 0.01, 300 epochs/estimators, batch 128, dropout 0.2, storm-wise **70 : 15 : 15** split, seed 42). The headline system is **SECE (Subset-Expert Context-Aware Ensemble)** — hierarchical stacking with **28 base learners** across physics-informed subsets plus **BLSTM / CNN-GRU** sequence models, fused by horizon-specific meta-learners (LightGBM router at 3 h / 12 h, Ridge at 24 h), trained on **out-of-fold** base predictions only.

### Key results (Bay of Bengal, in-distribution)

Evaluated on **312 Bay of Bengal cyclones (1990–2022)** after filtering; primary metric: **median Haversine error (km)**.

| Horizon | SECE median | Notes |
|--------:|------------:|-------|
| **3 h** | **4.42 km** | Lowest in benchmark (~4.40 km in revised table wording) |
| **12 h** | **29.77 km** | Statistically tied with smaller stacking ensemble |
| **24 h** | **86.28 km** | Lowest median among reported systems |

### Zero-shot cross-basin (Western Pacific)

Models evaluated on **South China Sea / WNP** typhoon data **without retraining**:

| Horizon | Best transfer (reported) |
|--------:|--------------------------|
| **3 h** | Random Forest (~6.99 km) |
| **12 h** | CB+MotionNN (~54.02 km) |
| **24 h** | CB+MotionNN (~166.30 km) |

### Proposed architectures (legacy narrative)

1. **SECE** — Tier-1: CatBoost, XGBoost, LightGBM, Random Forest on **six** feature subsets + BLSTM/CNN-GRU; Tier-2: context-aware fusion (9 storm-level router features at short lead).
2. **PRC (Persistence Residual Cascade)** — Persistence prior + LightGBM residual in **km**, mapped back to ?lat/?lon.
3. **CB+MotionNN** — CatBoost + **64-32-16** MLP kinematic residual correction; strongest **cross-basin** performer in this study.

### Dataset (legacy `Data/` workflow)

From **`Data/readme.md`** (IBTrACS v4, North Indian Ocean):

| Item | Value |
|------|--------|
| Source | IBTrACS v4 CSV (`ibtracs.NI.list.v04r01.csv`) |
| Full archive span | 1842–2024 |
| **Evaluation window** | **1990–2022 (Bay of Bengal)** |
| BoB evaluation storms | **312** |
| Train / val / test (multi-horizon example) | 16,712 / 3,879 / 3,696 samples (721 / 154 / 156 storms) |

Download:

```bash
wget https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.NI.list.v04r01.csv
```

Place the CSV under **`Data/`**, then run **`Notebook/multi-horizon-finalized-experiment.ipynb`** from the top.

### Engineered features (49-D, legacy)

| Subset | Count | Content |
|--------|------:|---------|
| Position | 9 | Lat/lon, interaction, lags t?1…t?3 |
| Motion | 16 | Displacements, speed, bearing sin/cos, acceleration |
| Physics | 7 | Curvature, stability, recurvature proxy, seasonality |
| Environment | 8 | Distance to land, landfall, wind estimate, BoB centroid distance |
| Missingness | 9 | Imputation / wind observation flags |

t-SNE on this feature space is discussed in the legacy write-up as motivating subset experts.

### Where legacy artifacts live

| Folder | Typical contents |
|--------|------------------|
| **`Datasets/`** | `Original Dataset IBTRACS`, Bangladesh-filtered 1942–2025, South Asian 2010–2025, **`Final Dataset`** modeling exports |
| **`Outputs/Metrics`** | Error summaries by model and horizon |
| **`Outputs/Plots`** | Benchmark bar charts, comparisons |
| **`Outputs/Predictions`** | Per-storm or pooled prediction files |
| **`Outputs/Trajectory_Maps`** | Map overlays for case storms |

---

## Shared trainer: `Final_Cyclone_Pred_Results_P-3/`

The ERA5 benchmark **imports training logic from here** (sibling path `../Final_Cyclone_Pred_Results_P-3/`):

| File | Purpose |
|------|---------|
| `pipeline_common.py` | Shared data loading, feature columns, training utilities |
| `sece_v2_train.py` | SECE v2 Phase 3 subset-expert training and fusion |
| `eval_protocol.py` | **Locked seed lists:** dev `{3,4,5,6,8,9,10,11,14}`, held-out `{0,1,2,7,13,99,123,2024,2026}` |

Other Python modules may exist in your local clone from earlier experiments; the **minimal public set** above is what the ERA5 held-out scripts require.

---

## ERA5 line (current reproducible benchmark)

**Do not duplicate that documentation here.** The conference/journal/WAF claims — **852** QC storms, **63-D** inputs (49 kinematic + **14 ERA5 point**), **3 / 12 / 24 / 48 h**, leakage correction, Wilcoxon + Bonferroni, environ expert, negative spatial-patch result — are documented with **folder maps, script index, and reproduction commands** in:

**? [`ERA5-NEW-Analysis/README.md`](ERA5-NEW-Analysis/README.md)**  
**? [`ERA5-NEW-Analysis/docs/PROJECT_COMPLETE_GUIDE.md`](ERA5-NEW-Analysis/docs/PROJECT_COMPLETE_GUIDE.md)**

Held-out SECE medians (km): **4.895 · 35.538 · 101.186 · 246.331** @ 3 / 12 / 24 / 48 h (see `ERA5-NEW-Analysis/docs/paper_writeup_data/01_heldout_comparison_ci_wilcoxon.csv`).

---

## Relationship between the two lines

| Topic | Legacy (`Notebook/` / ICCACCESS) | ERA5 (`ERA5-NEW-Analysis/`) |
|-------|----------------------------------|-----------------------------|
| Features | 49-D track engineering | **63-D** (+ ERA5 at storm centre) |
| Sample framing | 312 BoB storms, 1990–2022 (paper wording) | **852** QC storms, genesis **1940–2024** |
| Horizons | 3 / 12 / 24 h | 3 / 12 / 24 / **48 h** |
| Deep models | In benchmark narrative (top-15 table) | **Scoped out** of locked held-out confirm |
| Evaluation | Single-split / pre-leakage-fix era | **Dev vs held-out seeds**, significance testing |
| Cross-basin | Zero-shot China/WNP reported | **Not** part of locked ERA5 confirm |

Both can coexist: cite **legacy notebooks + Outputs** for the older study; cite **`ERA5-NEW-Analysis/` + commit hash** for the ERA5-augmented papers.

---

## Citation

Until a DOI is available, cite the appropriate manuscript (when published) and:

`https://github.com/KraKEn-bit/Cyclone_Trajectory_Prediction`

---

## License and data terms

See repository license file. **IBTrACS:** [NOAA NCEI](https://www.ncei.noaa.gov/products/international-best-track-archive). **ERA5** (ERA5 line only): [Copernicus CDS terms](https://cds.climate.copernicus.eu/).
