from __future__ import annotations

from pathlib import Path
import math
import re
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import export_settings
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "fig_07"
OUT = ROOT / "outputs" / "fig_07"
OUT.mkdir(parents=True, exist_ok=True)

BLUE = "#4F8FC4"
TEAL = "#2F9988"
CORAL = "#D87063"
PURPLE = "#7661A2"
ORANGE = "#D18F3F"
GRAY = "#7B858D"
LIGHT_GRAY = "#DCE2E6"
DARK = "#1F2C34"
RISK_COLORS = {"medium": TEAL, "high": CORAL}


def style():
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "DejaVu Sans", "DejaVu Sans"],
        "font.size": 7.2,
        "axes.titlesize": 8.2,
        "axes.labelsize": 7.2,
        "xtick.labelsize": 6.4,
        "ytick.labelsize": 6.4,
        "legend.fontsize": 6.2,
        "axes.linewidth": 0.70,
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
        "savefig.facecolor": "white",
    })


def finish(ax):
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.70)
        spine.set_color("#59636B")
    ax.tick_params(direction="out", length=2.6, width=0.65,
                   colors="#222222", top=False, right=False)
    ax.xaxis.label.set_color("#111111")
    ax.yaxis.label.set_color("#111111")
    ax.title.set_color("#111111")


def panel_label(ax, s, x=-0.16, y=1.05):
    ax.text(x, y, s, transform=ax.transAxes, fontsize=10.5,
            fontweight="bold", va="bottom", ha="left", color="#111111")


def dot_box(ax, df, ycol, ylabel, title, panel, ylim=None, hline=None, symlog=False):
    order = ["medium", "high"]
    for i, risk in enumerate(order):
        series = pd.to_numeric(df.loc[df.risk_level.eq(risk), ycol], errors="coerce")
        vals = series[series.notna()].to_numpy(float)
        if len(vals):
            bp = ax.boxplot([vals], positions=[i], widths=.46, patch_artist=True,
                            showfliers=False, whis=(5, 95), zorder=1,
                            boxprops=dict(facecolor=RISK_COLORS[risk], alpha=.16,
                                          edgecolor=RISK_COLORS[risk], linewidth=1.0),
                            medianprops=dict(color=RISK_COLORS[risk], linewidth=1.3),
                            whiskerprops=dict(color=RISK_COLORS[risk], linewidth=.8),
                            capprops=dict(color=RISK_COLORS[risk], linewidth=.8))
            # Deterministic offsets preserve every observation without adding simulated data.
            jitter = np.linspace(-.095, .095, len(vals)) if len(vals) > 1 else np.array([0.0])
            ax.scatter(i + jitter, vals, s=18, color=RISK_COLORS[risk], alpha=.88,
                       edgecolor="white", linewidth=.35, zorder=3)
    ns = [pd.to_numeric(df.loc[df.risk_level.eq(r), ycol], errors="coerce").notna().sum() for r in order]
    ax.set_xticks([0, 1], [f"Medium\n(n = {ns[0]})", f"High\n(n = {ns[1]})"])
    ax.set_ylabel(ylabel)
    ax.set_title(title, pad=5)
    if ylim is not None:
        ax.set_ylim(*ylim)
    if hline is not None:
        ax.axhline(hline, color=GRAY, ls=(0, (3, 2)), lw=.85, zorder=0)
    if symlog:
        ax.set_yscale("symlog", linthresh=.001, linscale=.7)
        ax.set_yticks([0, .001, .01, .1])
        ax.set_yticklabels(["0", "0.001", "0.01", "0.1"])
    panel_label(ax, panel)
    finish(ax)


def parse_cells(value):
    return [int(x) for x in re.findall(r"\d+", str(value))]


def save(fig, stem):
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".png"), dpi=600, bbox_inches="tight")
    fig.savefig(stem.with_suffix(".tiff"), dpi=600, bbox_inches="tight",
                pil_kwargs={"compression": "tiff_lzw"})


style()
pop = pd.read_csv(DATA / "population_source.csv")
temp_vehicle = pop[pop.panel.eq("a_temperature")].copy()
r0_vehicle = pop[pop.panel.eq("b_r0")].copy()
soc_vehicle = pop[pop.panel.eq("c_relative_soc")].copy()

fig = plt.figure(figsize=(7.20, 4.75))
gs = fig.add_gridspec(2, 3, left=.085, right=.985, bottom=.105, top=.890,
                      hspace=.48, wspace=.34)

# Population-level distributions among frozen medium/high-risk vehicles.
ax = fig.add_subplot(gs[0, 0])
dot_box(ax, temp_vehicle, "candidate_module_support_pct",
        "Repeated thermal support (%)", "Candidate-associated module temperature", "a",
        ylim=(-.7, 15.0), hline=0)

ax = fig.add_subplot(gs[0, 1])
dot_box(ax, r0_vehicle, "candidate_r0_p95_mohm",
        "Relative R0 response (mΩ)", "Candidate-cell equivalent R0", "b",
        symlog=True)

ax = fig.add_subplot(gs[0, 2])
dot_box(ax, soc_vehicle, "candidate_relative_soc_pp",
        "Relative SOC offset (percentage points)", "Identifiable candidate-cell relative SOC", "c",
        ylim=(-3.0, 1.0), hline=0)

# Module-level temperature profile with co-located support.
q = pd.read_csv(DATA / "panel_d_source.csv").sort_values("module_id")
q["support_pct"] = 100 * q.thermal_support_events / q.qualified_events.replace(0, np.nan)
cand_modules = q.loc[q.candidate_module, "module_id"].tolist()
ax = fig.add_subplot(gs[1, 0])
supporting = q.support_pct.gt(0)
ax.vlines(q.loc[supporting, "module_id"], 0, q.loc[supporting, "support_pct"],
          color=TEAL, linewidth=1.8, alpha=.92, zorder=1)
ax.scatter(q.loc[~supporting, "module_id"], q.loc[~supporting, "support_pct"],
           s=18, color=LIGHT_GRAY, edgecolor="white", linewidth=.35, zorder=2)
ax.scatter(q.loc[supporting, "module_id"], q.loc[supporting, "support_pct"],
           s=38, color=TEAL, edgecolor="white", linewidth=.55, zorder=3)
for m in cand_modules:
    y = float(q.loc[q.module_id.eq(m), "support_pct"].iloc[0]) if q.module_id.eq(m).any() else 0
    ax.scatter(m, y + .45, marker="v", s=27, color=CORAL, edgecolor="white", linewidth=.4,
               zorder=4, clip_on=False)
ax.set_xticks([1, 4, 7, 10, 13, 17])
ax.set_xlabel("Module index")
ax.set_ylabel("Repeated thermal support (%)")
ax.set_title("Module thermal profile: A-TR-06", pad=5)
ax.set_ylim(0, max(15, np.nanmax(q.support_pct) + 2))
panel_label(ax, "d")
finish(ax)

# R0 recurrence profile: the candidates remain explicitly visible even when repeated R0 support is absent.
q = pd.read_csv(DATA / "panel_e_source.csv").sort_values("cell_index")
q["support_pct"] = 100 * q.support_events / q.events.replace(0, np.nan)
cands_r0 = q.loc[q.voltage_candidate, "cell_index"].tolist()
ax = fig.add_subplot(gs[1, 1])
ax.vlines(q.cell_index, 0, q.support_pct.fillna(0), color=BLUE, linewidth=.65, alpha=.72, zorder=1)
ax.scatter(q.cell_index, q.support_pct.fillna(0), s=8, color=BLUE, alpha=.85, zorder=2)
for c in cands_r0:
    row = q[q.cell_index.eq(c)]
    y = float(row.support_pct.iloc[0]) if len(row) and np.isfinite(row.support_pct.iloc[0]) else 0
    ax.scatter(c, y, marker="v", s=32, color=CORAL, edgecolor="white", linewidth=.45, zorder=4)
ax.set_xlim(0, 96)
ax.set_ylim(-.03, max(1.25, np.nanmax(q.support_pct.fillna(0)) + .18))
ax.set_xticks([1, 24, 48, 72, 95])
ax.set_xlabel("Cell index")
ax.set_ylabel("R0-support events (%)")
ax.set_title("Cross-session R0 support: A-TR-01", pad=5)
panel_label(ax, "e")
finish(ax)

# Relative-SOC cell profile for the same high-risk vehicle.
q = pd.read_csv(DATA / "panel_f_source.csv").sort_values("cell_index")
ax = fig.add_subplot(gs[1, 2])
ax.axhline(0, color=GRAY, lw=.85, ls=(0, (3, 2)), zorder=0)
ax.plot(q.cell_index, q.relative_soc_median_pp, color=PURPLE, lw=.8, alpha=.68, zorder=1)
ax.scatter(q.cell_index, q.relative_soc_median_pp, s=10, color=PURPLE,
           edgecolor="white", linewidth=.25, zorder=2)
for c in cands_r0:
    row = q[q.cell_index.eq(c)]
    if len(row):
        y = float(row.relative_soc_median_pp.iloc[0])
        ax.scatter(c, y, marker="v", s=36, color=CORAL, edgecolor="white", linewidth=.45, zorder=4)
        xoff = -8 if c == 23 else (8 if c == 25 else 0)
        ax.annotate(str(c), (c, y), xytext=(xoff, -10), textcoords="offset points",
                    ha="center", va="top", fontsize=5.7, color=CORAL)
ax.set_xlim(0, 96)
ax.set_xticks([1, 24, 48, 72, 95])
ax.set_xlabel("Cell index")
ax.set_ylabel("Relative SOC offset (percentage points)")
ax.set_title("Cell-level relative SOC: A-TR-01", pad=5)
panel_label(ax, "f")
finish(ax)

legend = [
    Line2D([0], [0], marker="o", color="none", markerfacecolor=TEAL,
           markeredgecolor="none", markersize=5.5, label="Medium risk"),
    Line2D([0], [0], marker="o", color="none", markerfacecolor=CORAL,
           markeredgecolor="none", markersize=5.5, label="High risk"),
    Line2D([0], [0], marker="v", color="none", markerfacecolor=CORAL,
           markeredgecolor="white", markersize=6.2, label="Frozen voltage candidate"),
    Line2D([0], [0], marker="o", color=TEAL, markerfacecolor=TEAL,
           markeredgecolor="white", linewidth=1.6, markersize=5.5,
           label="Repeated thermal support"),
]
fig.legend(handles=legend, loc="upper center", bbox_to_anchor=(.54, .988), ncol=4,
           frameon=False, handlelength=1.5, columnspacing=1.5)

stem = OUT / "fig_07"
save(fig, stem)
plt.close(fig)

