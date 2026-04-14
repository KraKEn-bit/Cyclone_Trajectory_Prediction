# 🌀 Horizon-Consistent Multi-Step Cyclone Trajectory Prediction
### Bay of Bengal · IBTrACS 1990–2022 · 3h / 12h / 24h Forecasting

> A comprehensive 15-model benchmark for multi-horizon cyclone track prediction, featuring the **Subset-Expert Context-Aware Ensemble (SECE)** - a hybrid system achieving state-of-the-art positional accuracy across all forecasting horizons.

---

## **Key Results**

| Horizon | SECE Median Error | 2nd Best | Gap |
|---------|:-----------------:|----------|-----|
| **3h**  | **4.42 km**       | Stacking Ens. (4.64 km) | 5% |
| **12h** | **29.77 km**      | Stacking Ens. (29.88 km) | 0.4% |
| **24h** | **86.28 km**      | LightGBM (88.12 km) | 2% |

> Evaluated on 312 Bay of Bengal cyclones using a **leak-free storm-wise split** (70/15/15). Primary metric: Median Haversine Distance (km).

---

## **Proposed Architectures**

### 1. SECE - Subset-Expert Context-Aware Ensemble
A two-tier hierarchical stacking framework with 28 base learners:
- **Tier 1:** CatBoost, XGBoost, LightGBM, Random Forest trained across 6 physics-informed feature subsets + BLSTM and CNN-GRU sequential models
- **Tier 2:** Context-aware LightGBM meta-learner (3h/12h) + Ridge regularization (24h), trained exclusively on out-of-fold validation predictions to prevent label leakage

### 2. PRC - Persistence Residual Cascade
A two-stage physics-informed corrector: persistence baseline + LightGBM residual rectification. Highly efficient for operational deployment.

### 3. CB+MotionNN - CatBoost with Neural Residual Correction
CatBoost base predictor coupled with a 64-32-16 feedforward MotionNN that corrects kinematic residual bias in kilometer space using 9 kinematic features.

---

## 📁 Repository Structure

```
cyclone-trajectory-prediction/
│
├── notebook/
│   └── multi-horizon-experiment.ipynb   # Full pipeline: features → models → evaluation
│
├── outputs/
│   ├── plots/                           # Model comparison, error vs horizon, catropy plots
│   ├── trajectory_maps/                 # Per-cyclone predicted vs actual track maps
│   └── metrics/                         # Standardized metrics CSVs (3h, rollout)
│
├── data/
│   └── README.md                        # Instructions to download IBTrACS data
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🗃️ Dataset

We use **IBTrACS v4** (North Indian Ocean basin), filtered to 312 Bay of Bengal cyclones (1990–2022).

**Download IBTrACS data:**
```bash
# North Indian Ocean basin CSV
wget https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.NI.list.v04r01.csv
```

After downloading, place the file in the `data/` directory and run the notebook from Cell 1.

**Engineered Features (49 total):**

| Subset | Count | Description |
|--------|-------|-------------|
| Position | 9 | Current lat/lon, interaction term, lags t-1 to t-3 |
| Motion | 16 | Displacements, translation speed, bearing sin/cos, acceleration |
| Physics | 7 | Curvature, bearing/speed stability, recurvature proxy, seasonal encoding |
| Environment | 8 | Distance to land, landfall flag, wind estimate, BoB centroid distance |
| Missingness | 9 | Binary flags for imputed lag values and wind observations |

---

##  **Standardized Training Protocol**

All 23 models use **uniform hyperparameters** to ensure fair cross-architecture comparison:

| Parameter | Value |
|-----------|-------|
| Learning rate | 0.01 |
| Max iterations / epochs | 300 |
| Batch size (DL) | 128 |
| Dropout (DL) | 0.2 |
| Optimizer (DL) | AdamW |
| Max depth (trees) | 6 |
| Early stopping | OFF |
| Random seed | 42 |

---

## **Installation Procedures**

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/cyclone-trajectory-prediction.git
cd cyclone-trajectory-prediction
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Download the data
Follow the instructions in `data/README.md` to download IBTrACS.

### 4. Run the notebook
```bash
jupyter notebook notebook/multi-horizon-experiment.ipynb
```

---

## **Requirements**

See `requirements.txt`. Main dependencies:
- `pandas`, `numpy`, `scikit-learn`
- `lightgbm`, `xgboost`, `catboost`
- `tensorflow` / `keras`
- `cartopy` (for trajectory map visualizations)
- `matplotlib`, `seaborn`

---

## 📈 Outputs

The notebook generates:
- **`outputs/metrics/`** — Standardized metrics CSVs for all models across all horizons
- **`outputs/plots/`** — Model comparison charts, error-vs-horizon curves, catropy analysis
- **`outputs/trajectory_maps/`** — Satellite-overlaid predicted vs. actual track maps for key cyclones (Titli, Burevi, Michaung, Midhili, Ward, Nilam)

---

## 🔬 Findings

- **Tree-based models consistently outperform deep learning** on this tabular trajectory dataset under uniform hyperparameter constraints, consistent with Grinsztajn et al. (NeurIPS 2022)
- **SECE achieves the lowest median error at all three horizons simultaneously** — the only architecture to do so
- **Deep learning contributes meaningfully as SECE base learners** despite lower standalone accuracy, particularly at 12h
- **PRC is highly competitive for operational use** — simple, fast, and ranks in the top 6 at every horizon

---

## ⚠️ Limitations

- Evaluation confined to the North Indian Ocean basin
- Feature set is purely kinematic (IBTrACS-derived); no atmospheric reanalysis fields (ERA5 SST, wind shear)
- Fixed hyperparameter protocol prevents individual models from reaching tuned performance ceiling
- Maximum evaluated horizon is 24h (48h+ would require architectural modifications)

