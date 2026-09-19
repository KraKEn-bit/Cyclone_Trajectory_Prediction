# Horizon-Consistent Multi-Step Cyclone Trajectory Prediction

**Bay of Bengal · North Indian Ocean · IBTrACS + ERA5 · 3 / 12 / 24 / 48 h forecasting**

This repository contains cyclone **track** (position) prediction research for the **Bay of Bengal** and wider **North Indian Ocean**. The **current, reproducible benchmark** lives in **[`ERA5-NEW-Analysis/`](ERA5-NEW-Analysis/)** — SECE v2 Phase 3 with **ERA5** reanalysis, a **leakage-corrected** evaluation protocol, and **held-out** statistical confirmation.

Older notebooks, figures, and IBTrACS-only experiments remain under [`Notebook/`](Notebook/), [`Outputs/`](Outputs/), [`Data/`](Data/), and [`Datasets/`](Datasets/) for reference.

---

## Key results (locked held-out confirm)

**Setting:** Eight tree/hybrid systems · genesis **1940–2024** · **63-D** features (49 track/physics + 14 ERA5 point at storm centre) · storm-wise **70 / 15 / 15** split · **nine held-out seeds** pooled (**442** distinct test storms) · metric: **median great-circle (Haversine) error (km)**.

**Source:** [`ERA5-NEW-Analysis/docs/paper_writeup_data/01_heldout_comparison_ci_wilcoxon.csv`](ERA5-NEW-Analysis/docs/paper_writeup_data/01_heldout_comparison_ci_wilcoxon.csv)

| Horizon | SECE v2 Phase 3 (median km) | vs. seven baselines (Bonferroni) |
|--------:|----------------------------:|----------------------------------|
| **3 h** | **4.895** | Significantly **better than all** |
| **12 h** | **35.538** | Significantly **better than all** |
| **24 h** | **101.186** | **Statistical parity** with leading stacks (Stacking, XGB, LGB, PRC); not worse than any baseline |
| **48 h** | **246.331** | **Parity** with top tree methods; not worse than any baseline |

Wilcoxon signed-rank tests on paired per-storm medians; family-wise threshold **p < 0.0071** (7 comparisons). Full table and 95% bootstrap CIs in the paper writeup data folder above.

**Context (not a direct scoreboard match):** Official NIO track verification (Mohapatra et al., 2013) reports ~124 km @ 24 h and ~202 km @ 48 h under a **different** operational protocol than this ML hindcast.

---

## Repository layout

| Path | Contents |
|------|----------|
| **[`ERA5-NEW-Analysis/`](ERA5-NEW-Analysis/)** | **Main line:** pipelines, scripts, datasets (modeling CSV), held-out exports, docs, manuscripts |
| **[`Final_Cyclone_Pred_Results_P-3/`](Final_Cyclone_Pred_Results_P-3/)** | Minimal **SECE trainer** (`pipeline_common.py`, `sece_v2_train.py`, `eval_protocol.py`) — must stay **sibling** of `ERA5-NEW-Analysis/` |
| `Notebook/`, `Outputs/`, `Data/`, `Datasets/` | Earlier IBTrACS-centric experiments and assets |
| `README.md` | This file |

**Start here:** [`ERA5-NEW-Analysis/docs/PROJECT_COMPLETE_GUIDE.md`](ERA5-NEW-Analysis/docs/PROJECT_COMPLETE_GUIDE.md) (full project story, architecture, and file map).

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

Diagram: [`ERA5-NEW-Analysis/docs/figures/sece_phase3_architecture.png`](ERA5-NEW-Analysis/docs/figures/sece_phase3_architecture.png)

Spec: [`ERA5-NEW-Analysis/docs/paper_writeup_data/02_architecture_hyperparameters.md`](ERA5-NEW-Analysis/docs/paper_writeup_data/02_architecture_hyperparameters.md)

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

**Deep learning (CNN-GRU, BLSTM):** explored under the same budget in development; **not** re-run on the locked ERA5 held-out protocol — omitted from the confirm table (see [`PROJECT_COMPLETE_GUIDE.md`](ERA5-NEW-Analysis/docs/PROJECT_COMPLETE_GUIDE.md) §12).

---

## Other architectures (still in the benchmark)

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

ERA5 download and join: [`ERA5-NEW-Analysis/docs/era5_cds_setup.md`](ERA5-NEW-Analysis/docs/era5_cds_setup.md).  
Raw NetCDF is **not** in git; modeling CSV `datasets/bangladesh_nextstep_dataset_era5.csv` is provided for reproduction.

**Ablations (development):** track-only → + point ERA5 → + dedicated **environ** expert (locked); **5°/3° spatial patches rejected** at 24–48 h (reported negative result).

---

## Evaluation integrity

Earlier SECE iterations suffered **test-set leakage** (architecture phases advanced using test leaderboard feedback). The ERA5 line **freezes** Phase 3 + environ expert on **development seeds**, then runs **held-out seeds once**. This failure mode and fix are documented transparently in the manuscripts and in [`Full_Project_Story_Plain_Language.md`](ERA5-NEW-Analysis/Paper%20Writing/Read%20MADE/Full_Project_Story_Plain_Language.md).

---

## Quick start (reproduce tables)

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

Requires sibling folder `../Final_Cyclone_Pred_Results_P-3/`.

---

## Legacy README content (pre-ERA5 benchmark)

The **original** repository README described a **15-model** IBTrACS-only benchmark (**312** Bay of Bengal storms, **1990–2022**), SECE with **28** base learners including **BLSTM / CNN-GRU**, meta-learners, and **zero-shot** evaluation on **South China Sea / WNP** typhoons (e.g. CB+MotionNN transfer numbers).

That work remains in `Notebook/` and related paths. It is **not** superseded line-for-line by the ERA5 held-out medians above:

| Topic | Legacy (IBTrACS-only) | Current (`ERA5-NEW-Analysis`) |
|-------|------------------------|-------------------------------|
| Sample | 312 storms, 1990–2022 (paper wording) | 852 QC storms, genesis 1940–2024 |
| Features | 49-D track engineering | **63-D** (+ ERA5 point) |
| Horizons | 3 / 12 / 24 h | 3 / 12 / 24 / **48 h** |
| SECE medians (example) | 4.42 / 29.77 / 86.28 km | 4.895 / 35.538 / 101.186 / 246.331 km |
| Confirm | Single-split / pre-leakage-fix | **Dev vs held-out seeds**, Wilcoxon + Bonferroni |
| Cross-basin | Reported zero-shot China/WNP | **Not** part of locked ERA5 confirm |
| Deep models | In ensemble narrative | **Out of scope** for locked held-out table |

Use **ERA5-NEW-Analysis** for citations and reproduction of the **current** benchmark; cite legacy notebooks separately if you compare to the older 15-model study.

---

## Papers

LaTeX sources (journal, IEEE conference, AMS WAF) are under [`ERA5-NEW-Analysis/Paper Writing/`](ERA5-NEW-Analysis/Paper%20Writing/) (if present in your clone). Numbers must match `docs/paper_writeup_data/`.

---

## Citation

If you use this code or the held-out exports, cite the accompanying manuscript (when published) and point to this repository and commit hash. Until DOI is available, use the GitHub URL: `https://github.com/KraKEn-bit/Cyclone_Trajectory_Prediction`.

---

## License

See repository license file. ERA5 data subject to [Copernicus CDS terms](https://cds.climate.copernicus.eu/); IBTrACS from [NOAA NCEI](https://www.ncei.noaa.gov/products/international-best-track-archive).
