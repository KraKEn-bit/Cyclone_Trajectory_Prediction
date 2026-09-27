# ?? Horizon-Consistent Multi-Step Cyclone Trajectory Prediction
### Bay of Bengal · IBTrACS 1990–2022 · 3h / 12h / 24h Forecasting

> A comprehensive 15-model benchmark for multi-horizon cyclone track prediction, featuring the **Subset-Expert Context-Aware Ensemble (SECE)** — a hybrid system achieving state-of-the-art positional accuracy across all forecasting horizons, alongside a robust zero-shot cross-basin evaluation.

---

## ?? Key Results

### Bay of Bengal (In-Distribution)
Evaluated on 312 Bay of Bengal cyclones using a **leak-free storm-wise split** (70/15/15). Primary metric: Median Haversine Distance (km).

| Horizon | SECE Median Error | 2nd Best |
|---------|:-----------------:|----------|
| **3h** | **4.42 km** | Stacking Ens. (4.64 km) |
| **12h** | **29.77 km** | Stacking Ens. (29.88 km) |
| **24h** | **86.28 km** | LightGBM (88.12 km) |

### Western Pacific (Zero-Shot Cross-Basin Transfer)
Models were directly evaluated on South China Sea typhoon data with **zero retraining** to measure out-of-distribution generalization.
* **Best 12h Transfer:** CB+MotionNN (54.02 km)
* **Best 24h Transfer:** CB+MotionNN (166.30 km)
* **Best 3h Transfer:** Random Forest (6.99 km)

---

## ??? Proposed Architectures

### 1. SECE - Subset-Expert Context-Aware Ensemble
A two-tier hierarchical stacking framework designed to prevent feature homogenization:
- **Tier 1 (Base Learners):** 28 distinct predictive signals utilizing CatBoost, XGBoost, LightGBM, and Random Forest trained independently across 6 physics-informed feature subsets, alongside Bidirectional LSTM and CNN-GRU sequential models.
- **Tier 2 (Meta-Learner):** A context-aware LightGBM router dynamically weights base learners for 3h/12h forecasts using 9 storm-level features (e.g., recurvature proxy, distance to land). A Ridge regression meta-learner regularizes 24h forecasts. Trained *exclusively* on out-of-fold inferences to ensure evaluation integrity.

### 2. PRC - Persistence Residual Cascade
A highly efficient two-stage operational framework: establishes a strong climatological persistence prior, followed by learned spatial residual rectification (in kilometers) via a dedicated LightGBM regressor.

### 3. CB+MotionNN - CatBoost with Neural Residual Correction
A hybrid pipeline coupling a CatBoost baseline trajectory with *MotionNN* (a 64-32-16 feedforward neural network). It rectifies residual bias using instantaneous kinematic features (speed, bearing, acceleration) mapped to geodetic degrees. **Demonstrated the strongest cross-basin generalization in the benchmark.**

---

## ??? Dataset & Feature Engineering

We use **IBTrACS v4** (North Indian Ocean basin), filtered to 312 Bay of Bengal cyclones (1990–2022).

**Engineered Features (49 total):**
The feature space is validated via t-SNE, confirming it encodes physically meaningful cyclone regimes (e.g., equatorial-to-extratropical dynamics).

| Subset | Count | Description |
|--------|-------|-------------|
| **Position** | 9 | Current lat/lon, interaction term, lags t-1 to t-3 |
| **Motion** | 16 | Displacements, translation speed, bearing sin/cos, acceleration |
| **Physics** | 7 | Curvature, bearing/speed stability, recurvature proxy, seasonal encoding |
| **Environment** | 8 | Distance to land, landfall flag, wind estimate, BoB centroid distance |
| **Missingness** | 9 | Binary flags for imputed lag values and wind observations |

---

## Repository layout

| Path | Contents |
|------|----------|
| `Notebook/`, `Outputs/`, `Data/`, `Datasets/` | IBTrACS-centric experiments, figures, and assets for this README |
| [`Final_Cyclone_Pred_Results_P-3/`](Final_Cyclone_Pred_Results_P-3/) | Shared SECE trainer (`pipeline_common.py`, `sece_v2_train.py`, `eval_protocol.py`) |
| **[`ERA5-NEW-Analysis/`](ERA5-NEW-Analysis/)** | **Separate line:** ERA5 environ expert, 48 h horizons, held-out confirm — see **[`ERA5-NEW-Analysis/README.md`](ERA5-NEW-Analysis/README.md)** (not summarized here) |

---

## Citation

If you use this code, cite the accompanying manuscript (when published) and this repository URL: `https://github.com/KraKEn-bit/Cyclone_Trajectory_Prediction`.
