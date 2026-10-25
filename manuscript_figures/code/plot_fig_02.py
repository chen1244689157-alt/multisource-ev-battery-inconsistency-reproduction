from __future__ import annotations

from pathlib import Path
import json

import matplotlib as mpl
import matplotlib.pyplot as plt
import export_settings
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.patches import Patch, Rectangle
from scipy.ndimage import gaussian_filter


ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'/'fig_02'
OUT=ROOT/'outputs'/'fig_02'
OUT.mkdir(parents=True,exist_ok=True)
COLORS = {
    "A": "#4C8FC1",
    "B": "#2A9D8F",
    "C": "#D97A6A",
    "D": "#76558F",
    "train": "#4C8FC1",
    "test": "#2A9D8F",
    "independent": "#D97A6A",
    "aggregate": "#76558F",
    "gray": "#6E7B83",
    "lightgray": "#E8ECEF",
}

mpl.rcParams.update(
    {
        "font.family": "Arial",
        "font.size": 7.5,
        "axes.titlesize": 8.5,
        "axes.labelsize": 7.5,
        "xtick.labelsize": 7.5,
        "ytick.labelsize": 7.5,
        "legend.fontsize": 8.0,
        "axes.linewidth": 0.8,
        "xtick.major.width": 0.7,
        "ytick.major.width": 0.7,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "savefig.facecolor": "white",
    }
)


def contour_mass_level(h: np.ndarray, mass: float = 0.75) -> float:
    vals = np.asarray(h, dtype=float).ravel()
    vals = vals[np.isfinite(vals) & (vals > 0)]
    if vals.size == 0:
        return np.nan
    vals = np.sort(vals)[::-1]
    cs = np.cumsum(vals)
    idx = int(np.searchsorted(cs, mass * cs[-1], side="left"))
    return float(vals[min(idx, len(vals) - 1)])


def style_axes(ax: mpl.axes.Axes) -> None:
    for side in ["left", "right", "top", "bottom"]:
        ax.spines[side].set_visible(True)
        ax.spines[side].set_color("#6F7780")
        ax.spines[side].set_linewidth(0.8)
    ax.tick_params(top=False, right=False, length=3, pad=2)
    ax.grid(False)


def panel_label(ax: mpl.axes.Axes, letter: str) -> None:
    ax.text(-0.14, 1.06, letter, transform=ax.transAxes, fontsize=11, fontweight="bold", va="top")


def main():
    cohort=pd.read_csv(DATA/'cohorts.csv')
    quality=pd.read_csv(DATA/'retention.csv')
    profiles=pd.read_csv(DATA/'profiles.csv')
    fig = plt.figure(figsize=(7.2, 5.8), constrained_layout=False)
    gs = fig.add_gridspec(2, 2, left=0.085, right=0.985, bottom=0.10, top=0.94, wspace=0.27, hspace=0.34)
    axa = fig.add_subplot(gs[0, 0])
    axb = fig.add_subplot(gs[0, 1])
    axc = fig.add_subplot(gs[1, 0])
    axd = fig.add_subplot(gs[1, 1])

    # a: cohort composition
    y = np.arange(len(cohort))[::-1]
    role_colors = {"Training": COLORS["train"], "Testing": COLORS["test"], "Independent": COLORS["independent"], "Aggregate": COLORS["aggregate"]}
    bars = axa.barh(y, cohort["vehicles"], color=[role_colors[r] for r in cohort["role"]], height=0.62, edgecolor="white", linewidth=0.5)
    axa.set_xscale("log")
    axa.set_xlim(7, 520)
    axa.set_yticks(y, cohort["cohort"])
    axa.set_xlabel("Number of vehicles (log scale)")
    for bar, (_, row) in zip(bars, cohort.iterrows()):
        if row["cohort"] == "D":
            axa.text(row["vehicles"] * 0.94, bar.get_y() + bar.get_height() / 2, f"{row['vehicles']}  |  {row['resolution']}", va="center", ha="right", fontsize=7.4, color="white", fontweight="bold")
        else:
            axa.text(row["vehicles"] * 1.08, bar.get_y() + bar.get_height() / 2, f"{row['vehicles']}  |  {row['resolution']}", va="center", fontsize=7.4, color="#30363B")
    style_axes(axa)
    panel_label(axa, "a")

    # b: 75% mass contours in SOC-current space, computed from all valid observations
    xedges = np.linspace(0, 100, 61)
    yedges = np.linspace(0, 300, 61)
    for dom in ["A", "B", "C", "D"]:
        h=np.load(DATA/f'coverage_{dom}.npy',allow_pickle=False)
        xe=xedges;ye=yedges
        h = gaussian_filter(h, sigma=1.1)
        level = contour_mass_level(h, 0.75)
        xc = (xe[:-1] + xe[1:]) / 2
        yc = (ye[:-1] + ye[1:]) / 2
        axb.contour(xc, yc, h.T, levels=[level], colors=[COLORS[dom]], linewidths=1.5)
    axb.set_xlim(0, 100)
    axb.set_ylim(0, 300)
    axb.set_xlabel("SOC (%)")
    axb.set_ylabel("Absolute current (A)")
    axb.legend(
        handles=[mpl.lines.Line2D([0], [0], color=COLORS[d], lw=1.7, label=d) for d in ["A", "B", "C", "D"]],
        frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.0), columnspacing=0.8, handlelength=1.5,
    )
    style_axes(axb)
    panel_label(axb, "b")

    # c: vehicle-level PCA; one point per vehicle, no row subsampling
    markers = {"A": "o", "B": "s", "C": "^", "D": "D"}
    for dom in ["A", "B", "C", "D"]:
        g = profiles[profiles["domain"] == dom]
        display = {"A": "A train", "B": "B train", "C": "C", "D": "D"}[dom]
        axc.scatter(g["PC1"], g["PC2"], s=17 if dom != "D" else 11, marker=markers[dom], c=COLORS[dom], alpha=0.78, edgecolors="white", linewidths=0.25, label=f"{display} (n={len(g)})", rasterized=True)
    axc.axhline(0, color="#CFD5D9", lw=0.6, zorder=0)
    axc.axvline(0, color="#CFD5D9", lw=0.6, zorder=0)
    axc.set_xlabel(f"PC1 ({46.8:.1f}%)")
    axc.set_ylabel(f"PC2 ({18.9:.1f}%)")
    axc.legend(frameon=False, ncol=2, loc="upper right", columnspacing=0.8, handletextpad=0.3)
    style_axes(axc)
    panel_label(axc, "c")

    # d: preprocessing retention; dots avoid exaggerating small differences.
    role_lookup = dict(zip(cohort["cohort"], cohort["role"]))
    yd = np.arange(len(quality))[::-1]
    for yi, (_, row) in zip(yd, quality.iterrows()):
        color = role_colors[role_lookup[row["cohort"]]]
        axd.hlines(yi, 98.75, row["retention_pct"], color="#D5DADF", lw=1.2, zorder=1)
        axd.scatter(row["retention_pct"], yi, s=42, color=color, edgecolor="white", linewidth=0.6, zorder=3)
        unit_text = "records" if row["unit"] == "Record" else "sessions"
        axd.text(row["retention_pct"] - 0.025, yi + 0.20, f"{row['retention_pct']:.2f}%", ha="right", va="bottom", fontsize=7.4, color="#30363B")
        axd.text(98.77, yi - 0.22, f"n={int(row['input_units']):,} {unit_text}", ha="left", va="top", fontsize=7.4, color="#667078")
    axd.axvline(100, color="#6E7B83", lw=0.8, ls="--", zorder=0)
    axd.set_xlim(98.72, 100.08)
    axd.set_ylim(-0.55, len(quality) - 0.45)
    axd.set_yticks(yd, quality["cohort"])
    axd.set_xlabel("Retained after quality control (%)")
    style_axes(axd)
    panel_label(axd, "d")

    fig.savefig(OUT / "fig_02.png", dpi=600)
    fig.savefig(OUT / "fig_02.tiff", dpi=600, pil_kwargs={"compression": "tiff_lzw"})
    fig.savefig(OUT / "fig_02.pdf")
    fig.savefig(OUT / "fig_02.svg")
    plt.close(fig)


if __name__=='__main__':
    main()
