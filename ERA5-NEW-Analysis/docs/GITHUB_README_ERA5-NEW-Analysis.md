# ERA5-NEW-Analysis

**Bay of Bengal · North Indian Ocean · IBTrACS + ERA5 · 3 / 12 / 24 / 48 h forecasting**

**SECE v2 Phase 3** with **ERA5** reanalysis (storm-centre point features), a **leakage-corrected** evaluation protocol, and **held-out** statistical confirmation.

---

## Key results (locked held-out confirm)

**Setting:** Eight tree/hybrid systems · genesis **1940–2024** · **63-D** features (49 track/physics + 14 ERA5 point at storm centre) · storm-wise **70 / 15 / 15** split · **nine held-out seeds** pooled (**442** distinct test storms) · metric: **median great-circle (Haversine) error (km)**.

**Source:** [`docs/paper_writeup_data/01_heldout_comparison_ci_wilcoxon.csv`](docs/paper_writeup_data/01_heldout_comparison_ci_wilcoxon.csv)

| Horizon | SECE v2 Phase 3 (median km) | vs. seven baselines (Bonferroni) |
|--------:|----------------------------:|----------------------------------|
| **3 h** | **4.895** | Significantly **better than all** |
| **12 h** | **35.538** | Significantly **better than all** |
| **24 h** | **101.186** | **Statistical parity** with leading stacks (Stacking, XGB, LGB, PRC); not worse than any baseline |
| **48 h** | **246.331** | **Parity** with top tree methods; not worse than any baseline |

Wilcoxon signed-rank tests on paired per-storm medians; family-wise threshold **p < 0.0071** (7 comparisons). Full table and 95% bootstrap CIs in [`docs/paper_writeup_data/`](docs/paper_writeup_data/).

**Context (not a direct scoreboard match):** Official NIO track verification (Mohapatra et al., 2013, *J. Earth Syst. Sci.*) reports mean direct position error about **140 km @ 24 h** and **262 km @ 48 h** over **2009–2011** (Table 3)—a **different** protocol than this ML hindcast.

---

## Read first

- **[`docs/PROJECT_COMPLETE_GUIDE.md`](docs/PROJECT_COMPLETE_GUIDE.md)** — end-to-end project guide
- **[`docs/paper_writeup_data/README.md`](docs/paper_writeup_data/README.md)** — CSV/MD tables tied to published numbers

---

## Dependency

Training imports from **sibling** directory (repo root):

```text
../Final_Cyclone_Pred_Results_P-3/
  pipeline_common.py
  sece_v2_train.py
  eval_protocol.py
```

---

## Proposed system: SECE v2 Phase 3 (ERA5 environ expert)

**Subset-Expert Context-Aware Ensemble (SECE)** — hierarchical **tree** ensemble with horizon-specific feature subsets and validation-only fusion routing (no deep sequence models in the **locked** held-out table).

### Pipeline (summary)

1. **Input:** 63-D vector per forecast origin (kinematic/track/physics + ERA5 point fields).
2. **Four subset experts per horizon** (each trained with CatBoost, XGBoost, LightGBM, Random Forest → **16** models / horizon):
   - **3 h:** Position · Motion · **Environ + ERA5** · Full 63-D
   - **12 / 24 / 48 h:** Motion · Physics · **Environ + ERA5** · Full 63-D
3. **NNLS fusion** within each subset (separate latitude / longitude weights) → subset-consensus signal.
4. **Seven champion baselines** in parallel (see below).
5. **Fusion candidate menu** (degree-space NNLS, km-NNLS, horizon-specific stacks) — chosen on **validation median km only**.
6. **Phase 3 hard router:** per seed and horizon, pick lowest validation error; **test evaluated once**.

Diagram: [`docs/figures/sece_phase3_architecture.png`](docs/figures/sece_phase3_architecture.png)

Spec: [`docs/paper_writeup_data/02_architecture_hyperparameters.md`](docs/paper_writeup_data/02_architecture_hyperparameters.md)

---

## Benchmark systems (eight, locked confirm)

| System | Role |
|--------|------|
| **SECE v2 Phase 3** | Subset experts + NNLS + champion fusion + val router |
| **Stacking** | RF + XGB + LGB → Ridge stack |
| **PRC** | Persistence + LightGBM residual in **km**, mapped to Δlat/Δlon |
| **Random Forest / LightGBM / XGBoost / CatBoost** | Single multi-output tree on full features |
| **CB+MotionNN** | CatBoost + MLP (64-32-16) kinematic residual correction |

Shared tree budget: **300** estimators, depth **6**, lr **0.01** (see guide).

**Deep learning (CNN-GRU, BLSTM):** explored under the same budget in development; **not** re-run on the locked ERA5 held-out protocol — omitted from the confirm table (see [`docs/PROJECT_COMPLETE_GUIDE.md`](docs/PROJECT_COMPLETE_GUIDE.md) §12).

---

## Other architectures (in the benchmark)

### PRC — Persistence Residual Cascade

Persistence displacement plus a LightGBM correction in kilometre space, then mapped back to degrees. Strong, interpretable baseline; competitive at **24–48 h**.

### CB+MotionNN — CatBoost with neural residual correction

CatBoost track prediction corrected by **MotionNN** on instantaneous kinematics. Often weaker at **short** lead in the NIO confirm; useful as an ensemble diversifier.

---

## Dataset and features

| Item | Locked setting |
|------|----------------|
| Tracks | **IBTrACS** North Indian Ocean, genesis **1940–2024** |
| After QC | **852** storms, **27 728** origins @ 3 h; **583** storms, **15 605** multi-horizon origins |
| ERA5 | **14** point variables at storm centre (winds, MSL, SST, steering, shear, `sst_missing`) |
| Features | **49** engineered track/physics + **14** ERA5 → **63-D** |
| Split | Storm-wise 70% train / 15% val / 15% test, **seed-specific** |
| Dev seeds (design only) | 3, 4, 5, 6, 8, 9, 10, 11, 14 |
| Held-out seeds (confirm once) | 0, 1, 2, 7, 13, 99, 123, 2024, 2026 |

ERA5 download and join: [`docs/era5_cds_setup.md`](docs/era5_cds_setup.md).

Raw NetCDF is **not** in git; modeling CSV `datasets/bangladesh_nextstep_dataset_era5.csv` is provided for reproduction.

**Ablations (development):** track-only → + point ERA5 → + dedicated **environ** expert (locked); **5°/3° spatial patches rejected** at 24–48 h (reported negative result).

---

## Evaluation integrity

Earlier SECE iterations suffered **test-set leakage** (architecture phases advanced using test leaderboard feedback). This line **freezes** Phase 3 + environ expert on **development seeds**, then runs **held-out seeds once**. Details: [`docs/PROJECT_COMPLETE_GUIDE.md`](docs/PROJECT_COMPLETE_GUIDE.md).

---

## Quick start

```bash
git clone https://github.com/KraKEn-bit/Cyclone_Trajectory_Prediction.git
cd Cyclone_Trajectory_Prediction/ERA5-NEW-Analysis
pip install -r requirements.txt
python scripts/build_paper_writeup_data.py
```

Re-run full held-out training (long, CPU-heavy):

```bash
python scripts/sece_era5_environ_heldout_eval.py
```

---

## Papers and manuscripts

**LaTeX sources are not in this repository** (private/local). Reproduce numbers from [`docs/paper_writeup_data/`](docs/paper_writeup_data/) and figures from [`docs/figures/`](docs/figures/).

The **legacy IBTrACS-only 15-model benchmark** (1990–2022, zero-shot transfer) is described in the **[repository root README](../README.md)**.

---

## License and data terms

Parent repo license applies. ERA5: [Copernicus CDS terms](https://cds.climate.copernicus.eu/); IBTrACS: [NOAA NCEI](https://www.ncei.noaa.gov/products/international-best-track-archive).
