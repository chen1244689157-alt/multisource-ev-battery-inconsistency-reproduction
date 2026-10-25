from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import export_settings
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "fig_08"
OUT = ROOT / "outputs" / "fig_08"
OUT.mkdir(parents=True, exist_ok=True)

BLUE = "#4F8FC4"
TEAL = "#2F9988"
CORAL = "#D87063"
PURPLE = "#7661A2"
ORANGE = "#D18F3F"
GRAY = "#78838B"
LIGHT_GRAY = "#DCE2E6"
DARK = "#1F2C34"


def style():
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "DejaVu Sans", "DejaVu Sans"],
        "font.size": 7.2,
        "axes.titlesize": 8.2,
        "axes.labelsize": 7.2,
        "xtick.labelsize": 6.4,
        "ytick.labelsize": 6.4,
        "legend.fontsize": 6.0,
        "axes.linewidth": .70,
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
    })


def finish(ax):
    for s in ax.spines.values():
        s.set_visible(True)
        s.set_linewidth(.70)
        s.set_color("#59636B")
    ax.tick_params(direction="out", length=2.6, width=.65, top=False, right=False,
                   colors="#222222")


def label(ax, text, x=-.140, y=1.080):
    ax.text(x, y, text, transform=ax.transAxes, fontsize=10.5,
            fontweight="bold", va="bottom", color="#111111")


def save(fig, stem):
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight", facecolor="white")
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight", facecolor="white")
    fig.savefig(stem.with_suffix(".png"), dpi=600, bbox_inches="tight", facecolor="white")
    fig.savefig(stem.with_suffix(".tiff"), dpi=600, bbox_inches="tight", facecolor="white",
                pil_kwargs={"compression": "tiff_lzw"})


style()
pa = pd.read_csv(DATA / "ocv_panel_a_source.csv")
rest = pd.read_csv(DATA / "ocv_panel_b_source.csv")
anchors = pa[pa.series.eq("qualified_rest_anchor")].reset_index(drop=True)
assert len(anchors) == len(rest)
assert np.allclose(rest.soc, anchors.soc_pct)
rest["pack_median_voltage_V"] = anchors.voltage_V
ref = pa[pa.series.eq("soc_bin_median")].rename(columns={"soc_pct":"soc_bin","voltage_V":"pack_voltage_V"})
fit = pa[pa.series.eq("monotonic_fit")]
grid = fit.soc_pct.to_numpy(float)
curve = fit.voltage_V.to_numpy(float)
slope_valid = fit.slope_valid.astype(str).str.lower().eq("true").to_numpy()
temp_local = pd.read_csv(DATA / "temperature_panel_c_source.csv")
temp_distributed = pd.read_csv(DATA / "temperature_panel_d_source.csv")

fig = plt.figure(figsize=(7.20, 4.70))
gs = fig.add_gridspec(2, 2, left=.090, right=.985, bottom=.105, top=.900,
                      hspace=.46, wspace=.28)

# a: vehicle-specific monotonic OCV-SOC reference.
ax = fig.add_subplot(gs[0, 0])
ax.scatter(rest.soc, rest.pack_median_voltage_V, s=18, color=BLUE, alpha=.62,
           edgecolor="white", linewidth=.35, label="Qualified rest anchor", zorder=2)
ax.scatter(ref.soc_bin, ref.pack_voltage_V, s=28, color=TEAL, edgecolor="white",
           linewidth=.45, label="SOC-bin median", zorder=3)
ax.plot(grid, curve, color=CORAL, lw=1.55, label="Monotonic OCV–SOC fit", zorder=4)
invalid = np.where(slope_valid, np.nan, curve)
ax.plot(grid, invalid, color=LIGHT_GRAY, lw=2.0,
        label="Slope below inversion threshold", zorder=5)
ax.set_xlabel("Pack SOC (%)")
ax.set_ylabel("Rest-state pack median voltage (V)")
ax.set_title("Vehicle-specific OCV–SOC reference: A-TR-01", pad=5)
ax.legend(loc="upper left", frameon=False, ncol=1)
label(ax, "a")
finish(ax)

# b: candidate-cell rest-voltage offsets around the fitted pack reference.
ax = fig.add_subplot(gs[0, 1])
ax.axhline(0, color=GRAY, lw=.85, ls=(0, (3, 2)), zorder=0)
ax.scatter(rest.soc, rest.pack_ocv_residual_mV, s=12, color=GRAY, alpha=.55,
           edgecolor="white", linewidth=.25, zorder=1)
cell_colors = {23: CORAL, 25: PURPLE, 47: TEAL}
for cell in [23, 25, 47]:
    col = f"U_{cell}_residual_mV"
    q = rest[["soc", col]].sort_values("soc")
    ax.plot(q.soc, q[col], lw=.80, color=cell_colors[cell], alpha=.70, zorder=2)
    ax.scatter(q.soc, q[col], s=15, color=cell_colors[cell], edgecolor="white",
               linewidth=.30, zorder=3)
last_soc = float(rest.soc.max())
direct = [
    ("Pack median", GRAY, float(rest.loc[rest.soc.idxmax(), "pack_ocv_residual_mV"]), 5.2),
    ("Cell 47", TEAL, float(rest.loc[rest.soc.idxmax(), "U_47_residual_mV"]), -5.3),
    ("Cell 25", PURPLE, float(rest.loc[rest.soc.idxmax(), "U_25_residual_mV"]), -8.1),
    ("Cell 23", CORAL, float(rest.loc[rest.soc.idxmax(), "U_23_residual_mV"]), -16.0),
]
for name, color, y_end, y_text in direct:
    if name == "Pack median":
        ax.text(25.2, y_text, "●  Pack median", ha="left", va="center",
                fontsize=6.2, color=color)
    else:
        ax.annotate(name, xy=(last_soc, y_end), xytext=(76.0, y_text),
                    textcoords="data", ha="left", va="center", fontsize=6.2,
                    color=color, arrowprops=dict(arrowstyle="-", color=color, lw=.65))
ax.set_xlabel("Pack SOC (%)")
ax.set_ylabel("Voltage offset from fitted reference (mV)")
ax.set_title("Rest-voltage offsets of frozen candidates", pad=5)
ax.set_xlim(rest.soc.min()-2, 82)
label(ax, "b")
finish(ax)

# c: co-located/local module thermal response.
ax = fig.add_subplot(gs[1, 0])
colors_c = {7: ORANGE, 8: TEAL, 9: CORAL, 13: PURPLE}
labels_c = {7: "M7 (candidate)", 8: "M8 (adjacent)",
            9: "M9 (candidate)", 13: "M13 (candidate)"}
for module in [7, 8, 9, 13]:
    q = temp_local[temp_local.module_id.eq(module)]
    ax.scatter(q.elapsed_days, q.excess_p95_C, s=8, color=colors_c[module], alpha=.20,
               edgecolor="none", rasterized=True)
    ax.plot(q.elapsed_days, q.rolling_p95_C, lw=1.15, color=colors_c[module],
            label=labels_c[module])
ax.axhline(0, color=GRAY, lw=.75, ls=(0, (3, 2)))
ax.set_xlabel("Elapsed time (days)")
ax.set_ylabel("Module–pack ΔT, P95 (°C)")
ax.set_title("Localized module thermal response: A-TR-06", pad=5)
ax.set_ylim(-1.8, 5.0)
ax.legend(loc="upper center", ncol=2, frameon=False)
label(ax, "c")
finish(ax)

# d: distributed thermal support, separated from candidate-associated modules.
ax = fig.add_subplot(gs[1, 1])
colors_d = {5: CORAL, 9: BLUE, 10: TEAL, 15: PURPLE, 17: ORANGE}
labels_d = {5: "M5 (candidate)", 9: "M9 (candidate)", 10: "M10 (support)",
            15: "M15 (support)", 17: "M17 (support)"}
for module in [5, 9, 10, 15, 17]:
    q = temp_distributed[temp_distributed.module_id.eq(module)]
    ls = (0, (3, 2)) if module in [5, 9] else "-"
    alpha = .80 if module in [5, 9] else 1.0
    ax.scatter(q.elapsed_days, q.excess_p95_C, s=7, color=colors_d[module], alpha=.16,
               edgecolor="none", rasterized=True)
    ax.plot(q.elapsed_days, q.rolling_p95_C, lw=1.05, color=colors_d[module],
            ls=ls, alpha=alpha, label=labels_d[module])
ax.axhline(0, color=GRAY, lw=.75, ls=(0, (3, 2)))
ax.set_xlabel("Elapsed time (days)")
ax.set_ylabel("Module–pack ΔT, P95 (°C)")
ax.set_title("Distributed module thermal response: A-TR-01", pad=5)
ax.set_ylim(-1.2, 4.8)
ax.legend(loc="upper left", ncol=2, frameon=False)
label(ax, "d")
finish(ax)

stem = OUT / "fig_08"
save(fig, stem)
plt.close(fig)

