# ERA5-NEW-Analysis

**SECE v2 Phase 3 · ERA5-point environ expert · Bay of Bengal / NIO track benchmark**

This folder is the **frozen, reproducible** line for:

- IBTrACS + **ERA5** (storm-centre point features)
- **Eight** tree/hybrid systems at **3 / 12 / 24 / 48 h**
- **Leakage-aware** dev vs held-out seed protocol
- Exported predictions, significance tests, and paper tables

## Read first

- **[`docs/PROJECT_COMPLETE_GUIDE.md`](docs/PROJECT_COMPLETE_GUIDE.md)** — end-to-end project guide
- **[`docs/paper_writeup_data/README.md`](docs/paper_writeup_data/README.md)** — CSV/MD tables tied to manuscript numbers

## Dependency

Training imports from **sibling** directory (repo root):

```text
../Final_Cyclone_Pred_Results_P-3/
  pipeline_common.py
  sece_v2_train.py
  eval_protocol.py
```

## Install and verify

```bash
pip install -r requirements.txt
python scripts/build_paper_writeup_data.py
```

## Held-out SECE medians (km)

| 3 h | 12 h | 24 h | 48 h |
|----:|-----:|-----:|-----:|
| 4.895 | 35.538 | 101.186 | 246.331 |

See `docs/paper_writeup_data/01_heldout_comparison_ci_wilcoxon.csv`.

## Do not expect in this folder

- `datasets/era5_raw/` NetCDF (download locally; see `docs/era5_cds_setup.md`)
- CNN-GRU / BLSTM held-out rows (scoped out after exploratory dev)

Parent repo overview: [`../README.md`](../README.md).
