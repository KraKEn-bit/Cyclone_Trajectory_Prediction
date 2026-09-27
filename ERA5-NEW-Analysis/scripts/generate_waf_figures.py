"""Publication figures for the AMS WAF manuscript.

Every panel is built from an already-computed file. Colour convention used
throughout: blue = kinematic / track-derived; orange = ERA5-derived.
Other encodings (model family, horizon) use the remaining Okabe–Ito colours
so they are not confused with that split.

Outputs (PNG 300 dpi + PDF vector) under Paper Writing/WAF/:
  fig03ablation.{png,pdf}  development ablation trend
  fig04bench4h.{png,pdf}   held-out benchmark 2x2
  fig05era5hist.{png,pdf}  per-storm ERA5 delta histograms
  fig06featimp.{png,pdf}   environ-expert gain shares
  fig08errorcdf.{png,pdf}  pooled error CDFs (24/48 h, SECE vs leaders)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import generate_paper_figures as gpf  # noqa: E402
import pipeline_era5  # noqa: E402
from pipeline_common import (  # noqa: E402
    _prepare_eval_frame,
    apply_physics_features,
    apply_qc,
    build_mh_df,
    sample_errors_for_model,
    storm_split,
)

OUT = ROOT / "Paper Writing" / "WAF"
DATA = ROOT / "docs" / "paper_writeup_data"
FIG_DOCS = ROOT / "docs" / "figures"

# Okabe–Ito; kinematic/ERA5 convention is locked for the whole paper.
BLUE_KIN = "#0072B2"
ORANGE_ERA5 = "#E69F00"
BLACK = "#000000"
GREEN = "#009E73"
VERM = "#D55E00"
PURPLE = "#CC79A7"
SKY = "#56B4E9"
GREY = "#5A5A5A"

HORIZON_COLOR = {"3h": BLUE_KIN, "12h": GREEN, "24h": VERM, "48h": PURPLE}
HORIZON_PANEL_TITLE = {"3h": "3 h held-out", "12h": "12 h held-out", "24h": "24 h held-out", "48h": "48 h held-out"}
HORIZON_LABEL = {"3h": "3 h", "12h": "12 h", "24h": "24 h", "48h": "48 h"}

FEATURE_LABELS = {
    "STORM_DIR": "Storm direction",
    "STORM_SPEED": "Storm speed",
    "LANDFALL": "Landfall flag",
    "DIST2LAND": "Distance to land",
    "NEWDELHI_WIND": "Wind estimate",
    "NEWDELHI_WIND_missing": "Wind missing flag",
    "sst": "SST",
    "sst_missing": "SST missing flag",
    "u200": "u 200 hPa",
    "v200": "v 200 hPa",
    "u500": "u 500 hPa",
    "v500": "v 500 hPa",
    "u850": "u 850 hPa",
    "v850": "v 850 hPa",
    "msl": "MSL pressure",
    "steer_u": "Steering u",
    "steer_v": "Steering v",
    "shear_u": "Shear u",
    "shear_v": "Shear v",
    "shear_mag": "Shear magnitude",
}

STYLE = {
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "axes.unicode_minus": False,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
}


def _apply_style() -> None:
    plt.rcParams.update(STYLE)


PANEL_LETTERS = "abcdefghijklmnopqrstuvwxyz"


def _panel_tag(ax, letter: str) -> None:
    ax.text(
        0.02,
        0.98,
        f"({letter})",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=12,
        fontweight="bold",
    )


def _pooled_eval_frame(horizon: str) -> pd.DataFrame:
    merge_keys = ["SID", "ISO_TIME", "LAT", "LON"]
    parts = []
    df_raw = pd.read_csv(pipeline_era5.DATA_PATH)
    df = apply_physics_features(apply_qc(df_raw))
    mh_df = build_mh_df(df)
    for seed in gpf.HELDOUT_SEEDS:
        _, _, test_storms = storm_split(mh_df, seed=seed)
        base = df[df["SID"].isin(test_storms)] if horizon == "3h" else mh_df[mh_df["SID"].isin(test_storms)]
        pred = pd.read_csv(gpf.PREDS_DIR / f"seed{seed}_predictions_{horizon}.csv")
        parts.append(_prepare_eval_frame(base, pred, merge_keys))
    return pd.concat(parts, ignore_index=True)


def _grid(ax) -> None:
    ax.grid(True, ls=":", alpha=0.3, color="#666666")
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_color("#444444")
        spine.set_linewidth(0.8)


def _save(fig, stem: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    png = OUT / f"{stem}.png"
    pdf = OUT / f"{stem}.pdf"
    fig.savefig(png, dpi=300, bbox_inches="tight", facecolor="white", pad_inches=0.08)
    fig.savefig(pdf, dpi=300, bbox_inches="tight", facecolor="white", pad_inches=0.08)
    plt.close(fig)
    print("wrote", png.name, "and", pdf.name)


def draw_feature_importance() -> None:
    """Figure A: 04_environ_expert_feature_importance.csv."""
    _apply_style()
    df = pd.read_csv(DATA / "04_environ_expert_feature_importance.csv")
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 7.2), sharey=False)

    for idx, (ax, horizon) in enumerate(zip(axes, ("24h", "48h"))):
        _panel_tag(ax, PANEL_LETTERS[idx])
        sub = df[df["horizon"] == horizon].sort_values("gain_share", ascending=True)
        colors = [ORANGE_ERA5 if bool(v) else BLUE_KIN for v in sub["is_era5"]]
        labels = [FEATURE_LABELS.get(f, f) for f in sub["feature"]]
        ax.barh(labels, sub["gain_share"] * 100.0, color=colors, edgecolor="none", height=0.78)
        ax.set_xlabel("Gain share (%)")
        ax.set_title(f"{HORIZON_LABEL[horizon]} environ expert")
        _grid(ax)
        ax.set_xlim(0, max(55.0, float(sub["gain_share"].max()) * 100.0 * 1.08))

    from matplotlib.patches import Patch

    fig.legend(
        handles=[
            Patch(facecolor=BLUE_KIN, edgecolor="none", label="Kinematic / track-derived"),
            Patch(facecolor=ORANGE_ERA5, edgecolor="none", label="ERA5-derived"),
        ],
        loc="upper center",
        ncol=2,
        frameon=False,
        bbox_to_anchor=(0.5, 1.02),
    )
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    _save(fig, "fig06featimp")


def draw_era5_histograms() -> None:
    """Figure B: 05_seed0_lgb_era5_vs_trackonly_per_storm.csv."""
    _apply_style()
    df = pd.read_csv(DATA / "05_seed0_lgb_era5_vs_trackonly_per_storm.csv")
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.6), sharey=False)

    for idx, (ax, horizon) in enumerate(zip(axes, ("24h", "48h"))):
        _panel_tag(ax, PANEL_LETTERS[idx])
        d = df.loc[df["horizon"] == horizon, "delta_km"].astype(float)
        n = int(d.size)
        n_imp = int((d > 0).sum())
        med = float(d.median())
        bins = np.histogram_bin_edges(d, bins="fd")
        ax.hist(d, bins=bins, color=ORANGE_ERA5, edgecolor="white", linewidth=0.4, alpha=0.92)
        ax.axvline(0.0, color=BLUE_KIN, lw=1.6, label="Zero (parity)")
        ax.axvline(med, color=BLACK, lw=1.6, ls="--", label=f"Median ({med:.1f} km)")
        ax.set_xlabel(r"Per-storm $\Delta$ (km)")
        ax.set_ylabel("Number of storms")
        ax.set_title(f"{HORIZON_LABEL[horizon]}  ({n_imp}/{n} improved)")
        _grid(ax)
        # 48 h bins peak under upper-right; keep 24 h legend on the right.
        leg_loc = "upper left" if horizon == "48h" else "upper right"
        ax.legend(loc=leg_loc, framealpha=0.92, edgecolor="#CCCCCC")

    fig.tight_layout()
    _save(fig, "fig05era5hist")


def _stats_to_records(rows) -> list[dict]:
    ranked = sorted(rows, key=lambda r: (r[4], r[3]))
    return [
        {
            "rank": i + 1,
            "label": row[0],
            "family": row[1],
            "full": row[2],
            "mean_km": round(row[3], 3),
            "median_km": round(row[4], 3),
        }
        for i, row in enumerate(ranked)
    ]


def _load_or_compute_horizon(horizon: str) -> list[dict]:
    cache = FIG_DOCS / f"benchmark_{horizon}_heldout_stats.json"
    if cache.exists():
        recs = json.loads(cache.read_text(encoding="utf-8"))
        if recs and "mean_km" in recs[0]:
            print("loaded", cache.name)
            return recs
    rows = gpf._benchmark_stats_horizon(horizon)
    recs = _stats_to_records(rows)
    cache.write_text(json.dumps(recs, indent=2), encoding="utf-8")
    print("computed and wrote", cache.name)
    return recs


def draw_benchmark_four_horizon() -> None:
    """Figure C: same label layout as benchmark_3h_heldout.png on each panel."""
    _apply_style()
    stats = {h: _load_or_compute_horizon(h) for h in ("3h", "12h", "24h", "48h")}
    audit = OUT / "fig04bench4h_stats.json"
    audit.write_text(json.dumps(stats, indent=2), encoding="utf-8")

    fig, axes = plt.subplots(2, 2, figsize=(15.2, 11.8))
    legend_handles = []

    for idx, (ax, horizon) in enumerate(zip(axes.ravel(), ("3h", "12h", "24h", "48h"))):
        _panel_tag(ax, PANEL_LETTERS[idx])
        rows = gpf._stats_rows_from_json(stats[horizon])
        handles = gpf.plot_benchmark_on_ax(
            ax,
            rows,
            panel_title=HORIZON_PANEL_TITLE[horizon],
            compact=True,
            fixed_3h_limits=(horizon == "3h"),
            fixed_12h_labels=(horizon == "12h"),
            fixed_24h_labels=(horizon == "24h"),
            fixed_48h_labels=(horizon == "48h"),
        )
        if not legend_handles:
            legend_handles = handles

    fig.legend(
        handles=legend_handles,
        loc="upper center",
        ncol=4,
        frameon=True,
        framealpha=0.95,
        bbox_to_anchor=(0.5, 1.01),
        title="Model family",
        fontsize=10,
        title_fontsize=10,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    _save(fig, "fig04bench4h")


def draw_ablation_trend() -> None:
    """Figure D: full_experiment_summary_table.csv."""
    _apply_style()
    df = pd.read_csv(ROOT / "docs" / "full_experiment_summary_table.csv")
    order = [
        "Track-only (no ERA5)",
        "Point ERA5",
        "Environ subset",
        "Spatial 5deg",
        "Spatial 3deg",
        "Held-out (locked environ)",
    ]
    xlabels = [
        "Track-only",
        "Point ERA5",
        "Environ expert",
        r"Spatial 5$^\circ$",
        r"Spatial 3$^\circ$",
        "Held-out confirm",
    ]
    fig, axes = plt.subplots(2, 2, figsize=(10.8, 7.4), sharex=True)

    for idx, (ax, horizon) in enumerate(zip(axes.ravel(), ("3h", "12h", "24h", "48h"))):
        _panel_tag(ax, PANEL_LETTERS[idx])
        ys = []
        for exp in order:
            row = df[(df["experiment"] == exp) & (df["horizon"] == horizon)]
            if row.empty:
                raise RuntimeError(f"Missing {exp} {horizon}")
            ys.append(float(row["sece_mean_median_km"].iloc[0]))
        ax.plot(
            range(len(order)),
            ys,
            color=HORIZON_COLOR[horizon],
            marker="o",
            ms=6.5,
            lw=2.0,
            markerfacecolor=HORIZON_COLOR[horizon],
            markeredgecolor="white",
            markeredgewidth=0.6,
        )
        for i, y in enumerate(ys):
            ax.annotate(f"{y:.2f}", (i, y), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=8)
        ax.set_xticks(range(len(order)))
        ax.set_xticklabels(xlabels, rotation=28, ha="right")
        ax.set_ylabel("Mean of seed medians (km)")
        ax.set_title(HORIZON_LABEL[horizon])
        _grid(ax)
        pad = 0.08 * (max(ys) - min(ys) if max(ys) > min(ys) else max(ys) * 0.02)
        ax.set_ylim(min(ys) - pad - 0.02, max(ys) + pad + 0.15)

    fig.tight_layout()
    _save(fig, "fig03ablation")


def _wilcoxon_vs_sece(horizon: str, model: str) -> tuple[float | None, str]:
    """Bonferroni-adjusted p for model vs SECE (stacking / XGBoost labels in CSV)."""
    df = pd.read_csv(DATA / "01_heldout_comparison_ci_wilcoxon.csv")
    row = df[(df["horizon"] == horizon) & (df["model"] == model)]
    if row.empty:
        return None, ""
    p = float(row["p_value_bonferroni_vs_sece"].iloc[0])
    if p < 0.001:
        ps = "<0.001"
    else:
        ps = f"{p:.3f}"
    sig = str(row["significant_bonferroni"].iloc[0]).upper() == "Y"
    return p, ps + ("*" if sig else "")


def draw_error_cdf() -> None:
    """Pooled origin-level error CDFs: SECE vs stacking vs XGBoost at 3--48 h."""
    _apply_style()
    cdf_models = [
        ("SECE v2 Phase3", "SECE", "#C48A00", 2.4),
        ("Stacking Ensemble", "Stacking", BLUE_KIN, 2.0),
        ("XGBoost", "XGBoost", VERM, 2.0),
    ]
    horizons = ("3h", "12h", "24h", "48h")
    fig, axes = plt.subplots(2, 2, figsize=(11.2, 9.2), sharey=True)

    for idx, (ax, horizon) in enumerate(zip(axes.ravel(), horizons)):
        _panel_tag(ax, PANEL_LETTERS[idx])
        frame = _pooled_eval_frame(horizon)
        n_origins = len(frame)
        medians: list[tuple[str, float, str]] = []
        for full, short, color, lw in cdf_models:
            err, _ = sample_errors_for_model(frame, horizon, full)
            err = np.sort(err.astype(float))
            med = float(np.median(err))
            pct = (np.arange(1, err.size + 1) / err.size) * 100.0
            ax.plot(err, pct, color=color, lw=lw, label=f"{short} ({med:.2f} km)")
            medians.append((short, med, color))
            ax.axvline(med, color=color, lw=0.9, ls="--", alpha=0.45)

        ax.set_xlabel("Great-circle error (km)")
        if idx % 2 == 0:
            ax.set_ylabel("Empirical CDF (%)")
        ax.set_title(f"{HORIZON_LABEL[horizon]} · nine held-out seeds pooled")
        ax.set_ylim(0, 100)
        ax.axhline(50, color=GREY, lw=0.8, ls=":", alpha=0.55)
        _grid(ax)

        _, p_stk = _wilcoxon_vs_sece(horizon, "Stacking Ensemble")
        _, p_xgb = _wilcoxon_vs_sece(horizon, "XGBoost")
        note = (
            f"n = {n_origins:,} origins\n"
            f"Wilcoxon vs SECE (Bonferroni):\n"
            f"  Stacking p = {p_stk}\n"
            f"  XGBoost p = {p_xgb}"
        )
        ax.text(
            0.98,
            0.04,
            note,
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=8,
            color="#333333",
            linespacing=1.25,
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="#CCCCCC", alpha=0.92),
        )

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        ncol=3,
        frameon=False,
        fontsize=9,
        bbox_to_anchor=(0.5, 1.01),
        title="Pooled median in legend; dashed vertical = same median",
        title_fontsize=9,
    )
    fig.suptitle(
        "Origin-level great-circle error CDFs (SECE Phase 3 vs two strongest long-lead baselines)",
        fontsize=12,
        y=1.04,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    _save(fig, "fig08errorcdf")


def main() -> None:
    only = set(sys.argv[1:])
    run_all = not only
    if run_all or "a" in only:
        draw_feature_importance()
    if run_all or "b" in only:
        draw_era5_histograms()
    if run_all or "d" in only:
        draw_ablation_trend()
    if run_all or "c" in only:
        draw_benchmark_four_horizon()
    if run_all or "e" in only:
        draw_error_cdf()
    print("WAF figures done.")


if __name__ == "__main__":
    main()
