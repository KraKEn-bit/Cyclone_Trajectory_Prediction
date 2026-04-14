# Data

The dataset used in this project is derived from **IBTrACS v4** (International Best Track Archive for Climate Stewardship), North Indian Ocean basin.

## Download Instructions

```bash
wget https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.NI.list.v04r01.csv
```

Or download manually from:
👉 https://www.ncei.noaa.gov/products/international-best-track-archive

Place the downloaded CSV in this `data/` directory, then run the notebook from Cell 1.

## Dataset Statistics

| Property | Value |
|----------|-------|
| Source | IBTrACS v4, North Indian Ocean |
| Full record | 1842–2024 |
| Evaluation window | 1990–2022 (Bay of Bengal) |
| Total timesteps | 46,053 |
| Total storms | 1,519 |
| BoB evaluation storms | 312 |
| Training samples | 16,712 (721 storms) |
| Validation samples | 3,879 (154 storms) |
| Test samples | 3,696 (156 storms) |
