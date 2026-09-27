# ERA5-NEW-Analysis

**ERA5-Augmented Ensemble Learning for Multi-Horizon Tropical Cyclone Track Prediction over the Bay of Bengal: A Leakage-Aware Benchmark**

**Bay of Bengal · North Indian Ocean · IBTrACS v4 + ERA5 · 3 / 12 / 24 / 48 h**

This directory is the **locked, reproducible** code and data export line for the IEEE conference paper (and aligned journal / AMS WAF manuscripts). It implements **eight** tree/hybrid systems, **SECE v2 Phase 3** with a dedicated **environ + ERA5** subset expert, and a **development vs held-out seed** protocol that corrects **test-set leakage** from earlier SECE iterations.

**Parent repo (legacy IBTrACS-only benchmark):** [`../README.md`](../README.md)  
**Full narrative (maintainer guide):** [`docs/PROJECT_COMPLETE_GUIDE.md`](docs/PROJECT_COMPLETE_GUIDE.md)  
**Numbers tied to LaTeX tables:** [`docs/paper_writeup_data/README.md`](docs/paper_writeup_data/README.md)

---

## Key results (held-out confirm, pooled)

**442** distinct test storms across **nine held-out seeds**; metric: **median great-circle (Haversine) error (km)**; **95% CIs** from 10,000 storm resamples; **Wilcoxon** on paired per-storm medians with **Bonferroni** threshold **p < 0.0071** (7 comparisons).

Source: [`docs/paper_writeup_data/01_heldout_comparison_ci_wilcoxon.csv`](docs/paper_writeup_data/01_heldout_comparison_ci_wilcoxon.csv)

| Horizon | SECE v2 Phase 3 (median km) | Significance vs seven baselines |
|--------:|----------------------------:|--------------------------------|
| **3 h** | **4.895** (CI 4.71–5.08) | Significantly **better than all** |
| **12 h** | **35.538** (CI 34.2–36.9) | Significantly **better than all** |
| **24 h** | **101.186** (CI 97.3–104.8) | **Parity** with Stacking / XGB / LGB / PRC; not worse than any baseline |
| **48 h** | **246.331** (CI 235.5–257.6) | **Parity** with top tree stacks; not worse than any baseline |

**Operational context (not a scoreboard match):** Mohapatra et al. (2013, *J. Earth Syst. Sci.*, Table 3, 2009–2011 NIO verification) reports mean direct position error ~**140 km @ 24 h** and ~**262 km @ 48 h** — different protocol from this ML hindcast.

**CNN-GRU / BLSTM:** explored under the same fixed budget in development; **not** in the locked held-out table (trailed tree leaders at 3–24 h).

---

## Scientific contributions (paper-aligned)

1. **Eight-system benchmark** at 3, 12, 24, and 48 h with bootstrap CIs and paired significance tests.  
2. **SECE Phase 3** with a dedicated **environ** subset for **14 ERA5 point** fields (not only dispersed into kinematic subsets).  
3. **Documented leakage mode** (architecture advanced while inspecting test rank tables) and **correction** via frozen design on dev seeds + **one-shot** held-out evaluation.  
4. **Controlled ablations:** track-only → point ERA5 → environ expert (**locked**); **5° / 3° spatial patches rejected** at 24–48 h (reported negative result).  
5. **Genesis window locked to 1940–2024** after date-window ablation ([`docs/date_window_decision.md`](docs/date_window_decision.md)).

---

## Data and features

### IBTrACS QC (after 3-hourly filtering)

| Quantity | Count |
|----------|------:|
| Storms (3 h origins) | **852** |
| Forecast origins @ 3 h | **27,728** |
| Storms with 12/24/48 h supervision | **583** |
| Multi-horizon origins | **15,605** |

Paste-ready methods text: [`docs/paper_writeup_data/07_methods_storm_counts_paragraph.md`](docs/paper_writeup_data/07_methods_storm_counts_paragraph.md)

### Splits

- **Storm-wise** 70% train / 15% val / 15% test (per seed).  
- **Development seeds (design only):** `3, 4, 5, 6, 8, 9, 10, 11, 14`  
- **Held-out seeds (confirm once):** `0, 1, 2, 7, 13, 99, 123, 2024, 2026`  

Defined in [`../Final_Cyclone_Pred_Results_P-3/eval_protocol.py`](../Final_Cyclone_Pred_Results_P-3/eval_protocol.py).

### 63-D input vector

- **49** kinematic / track / physics features (lags, motion, seasonality, land proximity, recurvature proxy, etc.).  
- **14 ERA5 point** fields at storm centre: u/v at 850, 500, 200 hPa; MSL; SST; deep-layer steering; shear components and magnitude; **`sst_missing`** flag after nearest-ocean SST fill ([`docs/sst_missingness.md`](docs/sst_missingness.md)).

Domain for ERA5 extraction: 30°N–5°N, 70°E–102°E, 3-hourly, joined to each track row ([`docs/era5_cds_setup.md`](docs/era5_cds_setup.md)).

---

## SECE v2 Phase 3 (locked architecture)

Diagram: [`docs/figures/sece_phase3_architecture.png`](docs/figures/sece_phase3_architecture.png)  
Spec: [`docs/paper_writeup_data/02_architecture_hyperparameters.md`](docs/paper_writeup_data/02_architecture_hyperparameters.md)

| Stage | Description |
|-------|-------------|
| Subset experts | **Four** horizon-specific feature views; **16** tree models per horizon (4 algorithms × 4 subsets) |
| Subset fusion | **NNLS** per subset (separate lat/lon weights) |
| Champions | Seven baselines in parallel (Stacking, PRC, RF, LGB, XGB, CatBoost, CB+MotionNN) |
| Phase 3 router | Per seed and horizon, pick fusion candidate with **lowest validation median km**; test evaluated **once** |

**Subset slots:**

| Slot | **3 h** | **12 / 24 / 48 h** |
|------|---------|---------------------|
| 1 | Position | Motion |
| 2 | Motion | Physics |
| 3 | Environ + ERA5 | Environ + ERA5 |
| 4 | Full 63-D | Full 63-D |

Tree budget (all tree systems): **300** estimators, max depth **6**, lr **0.01**.

### Development ablation (rank-1 / 9 dev seeds, mean median km)

| Configuration | 3 h | 12 h | 24 h | 48 h |
|---------------|-----|------|------|------|
| Track-only | 5/9, 4.84 | 3/9, 35.48 | 3/9, 100.48 | 0/9, 250.26 |
| + point ERA5 | 5/9, 4.93 | 7/9, 35.59 | 2/9, 99.86 | 1/9, 246.80 |
| **+ environ expert (locked)** | **5/9, 4.93** | **6/9, 35.56** | **3/9, 99.43** | **2/9, 246.94** |
| + spatial 5° | 7/9, 4.93 | 7/9, 35.56 | 1/9, 99.74 | 1/9, 246.55 |
| + spatial 3° | 7/9, 4.93 | 7/9, 35.66 | 2/9, 99.42 | 3/9, 247.00 |
| Held-out confirm | 6/9, 4.90 | 6/9, 35.63 | 2/9, 101.21 | 1/9, 246.99 |

Comparisons: [`docs/era5_vs_trackonly_dev_comparison.md`](docs/era5_vs_trackonly_dev_comparison.md), [`docs/era5_point_vs_environ_dev_comparison.md`](docs/era5_point_vs_environ_dev_comparison.md), [`docs/era5_spatial_final_dev_comparison.md`](docs/era5_spatial_final_dev_comparison.md).

---

## Eight benchmark systems (held-out table)

| # | System | Role |
|---|--------|------|
| 1 | **SECE v2 Phase 3** | Subset experts + NNLS + champion fusion + val router |
| 2 | **Stacking** | RF + XGB + LGB → Ridge |
| 3 | **PRC** | Persistence + LGB residual in km |
| 4 | **Random Forest** | Single multi-output RF |
| 5 | **LightGBM** | Single multi-output LGB |
| 6 | **XGBoost** | Single multi-output XGB |
| 7 | **CatBoost** | Single multi-output CatBoost |
| 8 | **CB+MotionNN** | CatBoost + 64-32-16 MLP on kinematic residuals |

Full leaderboard with CIs: [`docs/paper_writeup_data/01_heldout_comparison_ci_wilcoxon.md`](docs/paper_writeup_data/01_heldout_comparison_ci_wilcoxon.md).  
Wilcoxon detail: [`docs/heldout_task_a_significance.md`](docs/heldout_task_a_significance.md).

---

## Folder and file map

```
ERA5-NEW-Analysis/
├── README.md                          ← this file
├── requirements.txt                   ← Python deps (pip install -r)
├── pipeline_era5.py                   ← Locked point-ERA5 modeling pipeline
├── pipeline_trackonly_1940.py         ← Track-only ablation path
├── pipeline_era5_spatial.py           ← Spatial patch experiment (not locked)
├── datasets/
│   ├── bangladesh_nextstep_dataset_era5.csv          ← Main 63-D modeling table (in git)
│   ├── bangladesh_nextstep_dataset_era5_spatial_*.csv ← Spatial dev ablations
│   ├── tracks_era5.csv / tracks_era5_spatial_*.csv   ← Track + ERA5 joins (tracks_era5 often local-only)
│   └── era5_raw/                      ← NetCDF cache (gitignored; download locally)
├── docs/
│   ├── PROJECT_COMPLETE_GUIDE.md      ← End-to-end maintainer guide
│   ├── paper_writeup_data/            ← CSV/MD exports = paper Table 1, ablation, case study
│   ├── figures/                       ← PNG/PDF for manuscripts (architecture, benchmark, t-SNE, Laila)
│   ├── era5_cds_setup.md              ← CDS API setup
│   ├── date_window_decision.md        ← Why genesis 1940–2024
│   ├── sst_missingness.md             ← SST over-land handling
│   ├── ibtracs_quality_by_era.md      ← Era mixing / QC notes
│   └── era5_environ_heldout_final_report.md
├── scripts/                           ← See script index below
├── results/                           ← Held-out predictions & flags (often local / gitignored)
├── run_*_resilient.ps1 / .bat         ← Long-run wrappers with resume
├── resume_*.cmd                       ← Checkpoint resume shortcuts
└── *_STATUS.txt                       ← Last known pipeline status (dev / held-out / spatial)
```

**Trainer dependency (repo root sibling):**

```
../Final_Cyclone_Pred_Results_P-3/
  pipeline_common.py
  sece_v2_train.py
  eval_protocol.py
```

---

## Script index

### Reproduce paper tables and figures

| Script | Output |
|--------|--------|
| `build_paper_writeup_data.py` | Refreshes `docs/paper_writeup_data/*` from `results/` |
| `generate_paper_figures.py` | `docs/figures/` (benchmark, architecture, t-SNE, Laila trajectories) |
| `generate_waf_figures.py` | WAF-specific figure copies |
| `heldout_task_a_significance.py` | Significance exports |
| `write_environ_heldout_report.py` | Final held-out narrative report |

### Locked and ablation evaluations

| Script | Purpose |
|--------|---------|
| `sece_era5_environ_heldout_eval.py` | **Held-out confirm** (run once after freeze) |
| `sece_era5_environ_dev_eval.py` | Dev seeds, environ expert |
| `sece_era5_dev_eval.py` | Dev seeds, point ERA5 |
| `sece_trackonly_dev_eval.py` | Dev seeds, no ERA5 |
| `sece_era5_spatial_dev_eval.py` | Spatial patch dev runs |

### Data build and ERA5 ingest

| Script | Purpose |
|--------|---------|
| `prepare_tracks_era5.py` | IBTrACS → ERA5-ready tracks |
| `era5_download.py` | CDS download helper |
| `era5_join.py` | Point ERA5 join → modeling CSV |
| `era5_spatial_join.py` | Spatial patch join (dev) |
| `build_modeling_dataset.py` | Build `bangladesh_nextstep_dataset_era5.csv` |
| `build_modeling_dataset_spatial.py` | Spatial modeling CSVs |

### Analysis and audits

| Script | Purpose |
|--------|---------|
| `compare_era5_vs_trackonly_dev.py` | Track-only vs ERA5 dev comparison |
| `compare_era5_point_vs_environ_dev.py` | Point vs environ expert |
| `compare_era5_spatial_final_dev.py` | Spatial rejection evidence |
| `date_window_ablation.py` / `date_window_fixed_test_control.py` | Genesis window decision |
| `ibtracs_quality_by_era.py` / `position_vs_wind_quality.py` | Data quality studies |
| `build_full_experiment_summary_table.py` | `docs/full_experiment_summary_table.*` |

### Manuscript utilities (local)

| Script | Purpose |
|--------|---------|
| `convert_journal_to_waf.py` | Journal → WAF structure helper |
| `waf_wordcount.py` | WAF length check |

---

## Figures and case studies

| File | Paper role |
|------|------------|
| `docs/figures/sece_phase3_architecture.png` | Method figure (Phase 3 pipeline) |
| `docs/figures/benchmark_3h_heldout.png` | 3 h held-out benchmark |
| `docs/figures/tsne_era5_63d.png` / `.pdf` | Feature-space motivation (63-D) |
| `docs/figures/case_study_laila_trajectories.png` | Cyclone Laila (2010) multi-lead case study |

Case study metadata: [`docs/paper_writeup_data/05_case_study_storms.md`](docs/paper_writeup_data/05_case_study_storms.md).

Regenerate:

```bash
pip install -r requirements.txt
python scripts/build_paper_writeup_data.py
python scripts/generate_paper_figures.py
```

---

## Quick start

```bash
git clone https://github.com/KraKEn-bit/Cyclone_Trajectory_Prediction.git
cd Cyclone_Trajectory_Prediction/ERA5-NEW-Analysis
pip install -r requirements.txt
python scripts/build_paper_writeup_data.py
```

**Re-run full held-out training** (CPU-heavy, hours–days):

```bash
python scripts/sece_era5_environ_heldout_eval.py
```

Or use `run_sece_era5_environ_heldout_resilient.ps1` on Windows for resume. Requires **`../Final_Cyclone_Pred_Results_P-3/`**.

**ERA5 NetCDF:** not in git. Follow [`docs/era5_cds_setup.md`](docs/era5_cds_setup.md); do not commit `.cdsapirc`.

---

## Manuscripts

LaTeX sources (**`Conference_Paper.tex`**, **`Journal_Paper.tex`**, **`WAF/waf_manuscript.tex`**) are **not** in this repository. All reported scalars should match [`docs/paper_writeup_data/`](docs/paper_writeup_data/).

---

## Limitations (as stated in papers)

- Single-basin (NIO / BoB focus); no locked cross-basin transfer.  
- Point (and rejected patch) ERA5 collocations — not full gridded encoders.  
- Deterministic point forecasts; no calibrated ensemble spread.  
- Environ **feature importance** illustrative (seed 0; collinear steering/shear).  
- IMD verification numbers are **context only**.

---

## License and data terms

Parent repo license. **ERA5:** [Copernicus CDS](https://cds.climate.copernicus.eu/). **IBTrACS:** [NOAA NCEI](https://www.ncei.noaa.gov/products/international-best-track-archive).
