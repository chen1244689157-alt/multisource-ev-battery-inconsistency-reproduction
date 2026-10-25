"""Render multidimensional evidence and identifiability for voltage candidates.

The figure displays voltage, temperature, equivalent-R0 and relative-SOC
evidence derived from the released analysis records.
"""
from __future__ import annotations

from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import export_settings
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Patch

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'/'fig_06'
OUT=ROOT/'outputs'/'fig_06'
OUT.mkdir(parents=True,exist_ok=True)

BLUE = "#397CB3"; LIGHT_BLUE = "#79B7DE"; TEAL = "#268F81"
CORAL = "#D9675D"; PURPLE = "#79609C"; ORANGE = "#D0903D"
GRAY = "#6E7A83"; LIGHT_GRAY = "#D9DEE2"; DARK = "#243844"
RISK = {"normal": "#5797CE", "medium": "#329D8D", "high": "#DF756A"}
CASES=[('A-TR-23','A-TR-23',2,'Normal'),('A-TR-02','A-TR-02',26,'Medium'),('A-TR-01','A-TR-01',25,'High')]


def style():
    mpl.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans", "DejaVu Sans"],
        "font.size": 7, "axes.titlesize": 8, "axes.labelsize": 7,
        "xtick.labelsize": 6.2, "ytick.labelsize": 6.2, "legend.fontsize": 6.2,
        "axes.linewidth": .65, "pdf.fonttype": 42, "svg.fonttype": "none",
        "legend.frameon": False,
    })


def finish(ax):
    for s in ax.spines.values():
        s.set_visible(True); s.set_color("#626870"); s.set_linewidth(.65)
    ax.tick_params(direction="out", length=2.5, width=.6, top=False, right=False)


def label(ax, s, x=-.14, y=1.07):
    ax.text(x, y, s, transform=ax.transAxes, fontsize=10, fontweight="bold",
            va="bottom", color="#111111")


def save(fig, stem):
    fig.savefig(stem.with_suffix(".pdf"), facecolor="white")
    fig.savefig(stem.with_suffix(".svg"), facecolor="white")
    fig.savefig(stem.with_suffix(".png"), dpi=600, facecolor="white")
    fig.savefig(stem.with_suffix(".tiff"), dpi=600, facecolor="white",
                pil_kwargs={"compression": "tiff_lzw"})
    plt.close(fig)


def percentile(x):
    return (pd.Series(x, dtype=float).rank(method="average", pct=True) * 100).to_numpy(float)


def build_fig44():
    heat=pd.read_csv(DATA/'cell_evidence.csv')
    summary=pd.read_csv(DATA/'candidate_summary.csv')
    avail=pd.read_csv(DATA/'identifiability.csv')
    relation=pd.read_csv(DATA/'support_relation.csv')

    cmap = LinearSegmentedColormap.from_list("evidence", ["#F5F7F8", "#B8D9E8", "#5AA6BC", "#285C8E"])
    cmap.set_bad("#E3E6E8")
    fig = plt.figure(figsize=(7.20, 5.01))
    gs = fig.add_gridspec(2, 3, left=.120, right=.985, bottom=.092, top=.850,
                          height_ratios=[1.08, 1.00], hspace=.50, wspace=.40)
    heat_rows = []
    im = None
    for j, (short, vid, candidate, risk) in enumerate(CASES):
        q=heat[heat.vehicle_alias.eq(vid)]
        dims=['voltage_low_tail_mV','r0_robust_z','module_deltaT_C','relative_SOC_low_pp']
        pivot=q.pivot(index='cell_index',columns='dimension',values='raw_value').sort_index()
        cells=pivot.index.to_numpy(int)
        v,r0,temp,rsoc=[pivot[x].to_numpy(float) for x in dims]
        M=q.pivot(index='cell_index',columns='dimension',values='within_vehicle_percentile').reindex(index=cells,columns=dims).to_numpy(float).T
        ax = fig.add_subplot(gs[0, j])
        im = ax.imshow(np.ma.masked_invalid(M), aspect="auto", cmap=cmap, vmin=0, vmax=100,
                       interpolation="nearest", extent=[cells.min()-.5, cells.max()+.5, 3.5, -.5],
                       rasterized=True)
        ax.axvline(candidate, color=CORAL, lw=1.0)
        ax.scatter([candidate], [-.38], marker="v", s=18, color=CORAL, edgecolor="white", lw=.35,
                   clip_on=False, zorder=4)
        ax.set_xticks([1, 24, 48, 72, int(cells.max())]); ax.set_xlabel("Cell index")
        ax.set_yticks(range(4), ["ΔV low tail", "R0", "Module ΔT", "Relative SOC"] if j == 0 else ["", "", "", ""])
        if not np.isfinite(rsoc).any():
            # Place the marker away from the candidate-cell reference line.
            x_ni = cells.min() + 0.78 * (cells.max() - cells.min())
            ax.text(x_ni, 3, "NI", ha="center", va="center", fontsize=5.6, color=GRAY)
        label(ax, chr(ord("a")+j), x=-.22 if j == 0 else -.16)
        finish(ax)
        for dim, raw, pct in zip(["voltage_low_tail_mV", "r0_robust_z", "module_deltaT_C", "relative_SOC_low_pp"],
                                 [v, r0, temp, rsoc], M):
            for c, rv, pv in zip(cells, raw, pct):
                heat_rows.append([vid, int(c), dim, rv, pv, int(c == candidate)])

    cax = fig.add_axes([.470, .923, .200, .014])
    cb = fig.colorbar(im, cax=cax, orientation="horizontal"); cb.set_ticks([0, 50, 100])
    cb.ax.tick_params(labelsize=5.2, length=2)
    fig.text(.460,.930,"Evidence\npercentile",ha="right",va="center",fontsize=5.6,color=DARK)
    fig.text(.570,.982,"Cell index",ha="center",va="center",fontsize=7,color=DARK)

    # Integrated evidence matrix: each row retains its native unit and uses an
    # independent normalization. A common blue scale keeps the panel visually
    # consistent with the single-cell evidence maps above.
    labels_x = ["A-TR-23", "A-TR-02", "A-TR-01"]
    rel=summary.candidate_relative_soc_median_pp.to_numpy(float)
    raw = np.vstack([
        summary.voltage_p05_mV.to_numpy(float),
        summary.r0_max_step_robust_z.to_numpy(float),
        summary.module_temp_excess_p95_C.to_numpy(float),
        np.asarray(rel, dtype=float),
    ])
    row_names = ["Low-side ΔV\n(mV)", "R0", "Module ΔT\n(°C)", "Relative SOC\n(pp)"]
    summary_cmap = LinearSegmentedColormap.from_list("summary_blue", ["#F1F6F8", "#8FC4D8", "#2D6E9A"])
    row_cmaps = [summary_cmap] * 4
    row_norms = [Normalize(0, 11), Normalize(0, 3), Normalize(0, 3), Normalize(0, 2.6)]
    strength = np.vstack([-raw[0], raw[1], raw[2], -raw[3]])
    ax = fig.add_subplot(gs[1, 0])
    ax.set_xlim(-.5, 2.5); ax.set_ylim(3.5, -.5)
    ax.set_xticks(range(3), labels_x); ax.set_yticks(range(4), row_names)
    for rr in range(4):
        for cc in range(3):
            value = raw[rr, cc]
            if np.isfinite(value):
                face = row_cmaps[rr](row_norms[rr](max(strength[rr, cc], 0)))
                if rr == 0: txt = f"{value:.1f}"
                elif rr == 1: txt = f"{value:.2f}"
                elif rr == 2: txt = f"{value:.1f}"
                else: txt = f"{value:.2f}"
            else:
                face, txt = LIGHT_GRAY, "NI"
            ax.add_patch(plt.Rectangle((cc-.5, rr-.5), 1, 1, facecolor=face,
                                       edgecolor="white", lw=1.0))
            level = row_norms[rr](max(strength[rr, cc], 0)) if np.isfinite(value) else 0
            ax.text(cc, rr, txt, ha="center", va="center", fontsize=6.5,
                    color="white" if level >= .68 else DARK,
                    fontweight="bold" if rr == 0 else "normal")
    ax.tick_params(axis="y", labelsize=5.6)
    label(ax, "d", x=-.20); finish(ax)

    ax = fig.add_subplot(gs[1, 1])
    rel_order = ["No repeated support", "Distributed", "Candidate / module"]
    rel_colors = {"No repeated support": GRAY, "Distributed": BLUE, "Candidate / module": CORAL}
    risk_order = ["Medium", "High"]; y = np.arange(2); left = np.zeros(2)
    rr = relation.set_index("risk_level"); totals = rr.loc[risk_order, rel_order].sum(axis=1).to_numpy(float)
    for name in rel_order:
        counts = rr.loc[risk_order, name].to_numpy(float); pct = 100*counts/totals
        ax.barh(y, pct, left=left, height=.82, color=rel_colors[name], edgecolor="white", lw=.4)
        for yy, n, width, start in zip(y, counts.astype(int), pct, left):
            if n:
                shown = {"No repeated support":"None","Distributed":"Distributed","Candidate / module":"Co-located"}[name]
                txt = f"{shown}\n{n}" if yy == 0 else str(n)
                ax.text(start+width/2, yy, txt, ha="center", va="center", fontsize=5.4, color="white")
        left += pct
    ax.set_yticks(y, ["Medium", "High"]); ax.set_ylim(1.42,-.42); ax.set_xlim(0,100)
    ax.tick_params(axis="y", pad=4, labelsize=5.5, length=0)
    ax.set_xlabel("Share within voltage grade (%)")
    label(ax, "e", x=-.15); finish(ax)

    ax = fig.add_subplot(gs[1, 2])
    cols = ["Voltage", "Temperature", "R0", "Relative_SOC"]
    M = avail[cols].to_numpy(float)
    cov = LinearSegmentedColormap.from_list("coverage", ["#EEF4F7", "#A9D3CC", TEAL]); cov.set_bad(LIGHT_GRAY)
    ax.imshow(np.ma.masked_invalid(M), aspect="auto", vmin=0, vmax=100, cmap=cov, interpolation="nearest", rasterized=True)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i,j]; txt = "NA" if np.isnan(v) else f"{v:.0f}%"
            ax.text(j,i,txt,ha="center",va="center",fontsize=5.8,
                    color="white" if np.isfinite(v) and v>=70 else DARK,fontweight="bold")
    ax.set_xticks(range(4), ["Voltage","Temp.","R0","Rel. SOC"])
    short_groups = ["A-Tr", "B-Tr", "A-Te", "B-Te", "C"]
    ax.set_yticks(range(len(avail)), short_groups)
    ax.tick_params(axis="y", pad=2, labelsize=5.2)
    label(ax,"f",x=-.13); finish(ax)

    stem = OUT / "fig_06"
    save(fig, stem)

if __name__=='__main__':
    style()
    build_fig44()
