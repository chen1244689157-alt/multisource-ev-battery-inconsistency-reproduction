from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import export_settings
from matplotlib.colors import LinearSegmentedColormap, Normalize
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1] / "data" / "fig_10"
OUT = Path(__file__).resolve().parents[1] / "outputs" / "fig_10"
OUT.mkdir(parents=True, exist_ok=True)

mpl.rcParams.update({
    "font.family": "Arial",
    "font.size": 7.0,
    "axes.titlesize": 8.2,
    "axes.labelsize": 7.2,
    "xtick.labelsize": 6.5,
    "ytick.labelsize": 6.5,
    "legend.fontsize": 6.5,
    "axes.linewidth": 0.75,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
})

BLUE = "#4F86B5"
TEAL = "#2F8F83"
CORAL = "#D36F61"
DARK = "#253642"
GRID = "#D7DEE3"
SPINE = "#65717A"

cmap_blue = LinearSegmentedColormap.from_list(
    "paper_blue", ["#E7EEF4", "#AAC7DC", "#4F86B5", "#244F78"]
)
cmap_teal = LinearSegmentedColormap.from_list(
    "paper_teal", ["#E4F0ED", "#9BC8BE", "#2F8F83", "#176056"]
)


def style_axis(ax):
    for side in ("left", "bottom", "right", "top"):
        ax.spines[side].set_visible(True)
        ax.spines[side].set_color(SPINE)
        ax.spines[side].set_linewidth(0.75)
    ax.tick_params(top=False, right=False, direction="out", length=2.5, width=0.65, color=SPINE)


def add_panel_label(ax, letter):
    ax.text(-0.19, 1.08, letter, transform=ax.transAxes, ha="left", va="bottom",
            fontsize=10.2, fontweight="bold", color="black", clip_on=False)


def heatmap_panel(ax, df, value, title, cmap, fmt, cbar_label, vmin=None, vmax=None):
    beta_as = [0.10, 0.25, 0.50]
    beta_vs = [2.0, 4.0, 6.0]
    alphas = [0.10, 0.20, 0.30, 0.40]
    rows = [(ba, bv) for ba in beta_as for bv in beta_vs]
    matrix = np.full((len(rows), len(alphas)), np.nan)
    for r, (ba, bv) in enumerate(rows):
        for c, am in enumerate(alphas):
            hit = df[(np.isclose(df.beta_a, ba)) & (np.isclose(df.beta_v, bv)) &
                     (np.isclose(df.alpha_max, am))]
            matrix[r, c] = hit.iloc[0][value]

    if vmin is None:
        vmin = float(np.nanmin(matrix))
    if vmax is None:
        vmax = float(np.nanmax(matrix))
    im = ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax,
                   interpolation="nearest")
    ax.set_title(title, pad=6, color=DARK)
    ax.set_xlabel("Auxiliary cap, αmax", labelpad=4)
    ax.set_ylabel("Auxiliary / voltage coefficient, βA / βV", labelpad=4)
    ax.set_xticks(range(4), [f"{a:.2f}" for a in alphas])
    ax.set_yticks(range(9), [f"{ba:.2f} / {bv:.0f}" for ba, bv in rows])
    ax.set_xticks(np.arange(-.5, 4, 1), minor=True)
    ax.set_yticks(np.arange(-.5, 9, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.05)
    ax.tick_params(which="minor", bottom=False, left=False)
    style_axis(ax)

    threshold = vmin + 0.60 * (vmax - vmin)
    for r in range(matrix.shape[0]):
        for c in range(matrix.shape[1]):
            val = matrix[r, c]
            ax.text(c, r, format(val, fmt), ha="center", va="center",
                    fontsize=5.75, color="white" if val >= threshold else DARK)

    cb = plt.colorbar(im, ax=ax, orientation="horizontal", fraction=0.055, pad=0.16,
                      aspect=25)
    cb.set_label(cbar_label, labelpad=2.5)
    ticks = np.linspace(vmin, vmax, 4)
    cb.set_ticks(ticks)
    if vmax <= 1.0:
        cb.set_ticklabels([f"{x:.4f}" for x in ticks])
    else:
        cb.set_ticklabels([f"{x:.0f}" for x in ticks])
    cb.outline.set_linewidth(0.55)
    cb.outline.set_edgecolor(SPINE)
    cb.ax.tick_params(length=2, width=0.55, labelsize=6.0)
    return matrix


def main():
    grid = pd.read_csv(ROOT / "parameter_grid_summary.csv")
    stability = pd.read_csv(ROOT / "default_top1_stability.csv")
    tie = pd.read_csv(ROOT / "tie_adjusted_summary.csv")
    vehicles = pd.read_csv(ROOT / "candidate_stability.csv")
    df = grid.merge(stability, on=["beta_v", "beta_a", "alpha_max"], how="left")
    df.to_csv(OUT / "Figure_source_data.csv", index=False, encoding="utf-8-sig")

    fig = plt.figure(figsize=(7.35, 3.12), facecolor="white")
    gs = fig.add_gridspec(1, 3, width_ratios=[1.18, 1.18, 1.00],
                          left=0.075, right=0.985, bottom=0.21, top=0.87, wspace=0.42)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[0, 2])

    heatmap_panel(
        ax_a, df, "mean_rank_correlation", "Ranking agreement", cmap_blue,
        ".4f", "Mean rank correlation",
        vmin=float(df.mean_rank_correlation.min()),
        vmax=float(df.mean_rank_correlation.max()),
    )
    heatmap_panel(
        ax_b, df, "top1_same_as_default_pct", "Top-1 candidate stability", cmap_teal,
        ".0f", "Same as default (%)", vmin=88, vmax=100,
    )

    grouped = df.groupby("alpha_max")["mean_auxiliary_contribution"]
    alpha = np.array(sorted(df.alpha_max.unique()))
    mean = grouped.mean().reindex(alpha).to_numpy()
    low = grouped.min().reindex(alpha).to_numpy()
    high = grouped.max().reindex(alpha).to_numpy()
    ax_c.fill_between(alpha, low, high, color=TEAL, alpha=0.18, linewidth=0)
    ax_c.plot(alpha, mean, color=TEAL, linewidth=1.8, marker="o", markersize=4.2,
              markerfacecolor="white", markeredgewidth=1.2, label="Mean ± range")
    current_y = float(mean[np.where(np.isclose(alpha, 0.30))[0][0]])
    ax_c.scatter([0.30], [current_y], s=34, color=CORAL, edgecolor="white", linewidth=0.8,
                 zorder=4, label="Current setting")
    ax_c.axvline(0.30, color=CORAL, linewidth=0.9, linestyle=(0, (3, 2)), alpha=0.8)
    ax_c.set_title("Bounded auxiliary contribution", pad=6, color=DARK)
    ax_c.set_xlabel("Auxiliary cap, αmax", labelpad=4)
    ax_c.set_ylabel("Mean auxiliary contribution", labelpad=4)
    ax_c.set_xticks(alpha, [f"{x:.2f}" for x in alpha])
    ax_c.set_xlim(0.085, 0.415)
    ax_c.set_ylim(0, max(high) * 1.28)
    ax_c.grid(axis="y", color=GRID, linewidth=0.65, alpha=0.75)
    style_axis(ax_c)
    ax_c.legend(frameon=False, loc="upper left", handlelength=1.6, borderaxespad=0.25)

    stable_n = int((vehicles.unique_top1_across_36 == 1).sum())
    total_n = len(vehicles)
    tied_switch_n = total_n - stable_n
    tie_retention = float(tie.top1_in_voltage_max_tie_pct.min())
    callout = (f"{stable_n}/{total_n} vehicles retained one Top-1 candidate\n"
               f"{tied_switch_n}/{total_n} switched only within voltage ties\n"
               f"Tie-set retention: {tie_retention:.0f}%")
    ax_c.text(0.50, -0.27, callout, transform=ax_c.transAxes, ha="center", va="top",
              fontsize=6.15, color=DARK, linespacing=1.25, clip_on=False)

    add_panel_label(ax_a, "a")
    add_panel_label(ax_b, "b")
    add_panel_label(ax_c, "c")

    base = OUT / "fig_10"
    fig.savefig(base.with_suffix(".pdf"), dpi=600, bbox_inches="tight", facecolor="white")
    fig.savefig(base.with_suffix(".svg"), dpi=600, bbox_inches="tight", facecolor="white")
    fig.savefig(base.with_suffix(".png"), dpi=600, bbox_inches="tight", facecolor="white")
    fig.savefig(base.with_suffix(".tiff"), dpi=600, bbox_inches="tight", facecolor="white",
                pil_kwargs={"compression": "tiff_lzw"})
    plt.close(fig)


if __name__ == "__main__":
    main()
