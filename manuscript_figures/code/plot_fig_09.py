"""Render VM-GMEFNet evidence fusion and candidate-cell ranking."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import export_settings
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'/'fig_09'
OUT=ROOT/'outputs'/'fig_09'
OUT.mkdir(parents=True,exist_ok=True)

BLUE = "#397CB3"
TEAL = "#268F81"
CORAL = "#D9675D"
GRAY = "#6E7A83"
DARK = "#243844"
RISK = {"normal": "#5797CE", "medium": "#329D8D", "high": "#DF756A"}


def style():
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Microsoft YaHei", "DejaVu Sans"],
        "font.size": 7,
        "axes.titlesize": 8,
        "axes.labelsize": 7,
        "xtick.labelsize": 6.2,
        "ytick.labelsize": 6.2,
        "legend.fontsize": 5.6,
        "axes.linewidth": .65,
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
        "legend.frameon": False,
    })


def finish(ax):
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color("#626870")
        spine.set_linewidth(.65)
    ax.tick_params(direction="out", length=2.5, width=.6, top=False, right=False)


def panel_label(ax, text, x=-.14, y=1.07):
    ax.text(x, y, text, transform=ax.transAxes, fontsize=10,
            fontweight="bold", va="bottom", color="#111111")


def parse_cells(value):
    return [int(x.replace("U_", "")) for x in str(value).split("|")]


def save(fig, stem):
    fig.savefig(stem.with_suffix(".pdf"), facecolor="white")
    fig.savefig(stem.with_suffix(".svg"), facecolor="white")
    fig.savefig(stem.with_suffix(".png"), dpi=600, facecolor="white")
    fig.savefig(stem.with_suffix(".tiff"), dpi=600, facecolor="white",
                pil_kwargs={"compression": "tiff_lzw"})
    plt.close(fig)


def build_figure():
    four_dim=pd.read_csv(DATA/'network_outputs.csv').rename(columns={'vehicle_alias':'vehicle_id'})
    matched=pd.read_csv(DATA/'concordance.csv').rename(columns={'vehicle_alias':'vehicle_id'})
    matched['vehicle']=matched.vehicle_id
    fig = plt.figure(figsize=(7.20, 4.88))
    grid = fig.add_gridspec(
        2, 3, left=.125, right=.975, bottom=.105, top=.865,
        height_ratios=[1.0, 1.08], hspace=.80, wspace=.58,
    )

    # a, vehicle-level network outputs stratified by voltage-derived risk.
    ax = fig.add_subplot(grid[0, 0])
    risk_handles = []
    for risk in ["normal", "medium", "high"]:
        subset = four_dim[four_dim.rule_level == risk]
        ax.scatter(subset.voltage_attention_score, subset.mean_auxiliary_score,
                   s=20, color=RISK[risk], alpha=.84, edgecolor="white", lw=.35)
        risk_handles.append(Line2D([], [], marker="o", linestyle="None", markersize=4.5,
                                   markerfacecolor=RISK[risk], markeredgecolor="white",
                                   markeredgewidth=.35,
                                   label=f"{risk.capitalize()} (n = {len(subset)})"))
    ax.set_xlabel("Voltage-attention score")
    ax.set_ylabel("Mean auxiliary score")
    
    ax.legend(handles=risk_handles, 
              title_fontsize=5.6, fontsize=5.1, ncol=3, loc="lower center",
              bbox_to_anchor=(.42, 1.12), handletextpad=.15, columnspacing=.30,
              borderaxespad=0)
    panel_label(ax, "a", x=-.20, y=1.04)
    finish(ax)

    # b, paired three-dimensional and four-dimensional candidate sets.
    ax = fig.add_subplot(grid[0, 1])
    identifiable = matched[matched.relative_soc_available == 1].copy()
    y = np.arange(len(identifiable))
    for yy, record in enumerate(identifiable.itertuples(index=False)):
        ax.plot([record.no_soc_overlap, record.four_dim_overlap], [yy, yy],
                color=GRAY, lw=1.0, zorder=1)
        ax.scatter(record.no_soc_overlap, yy, s=26, color=GRAY,
                   edgecolor="white", lw=.35, zorder=3)
        ax.scatter(record.four_dim_overlap, yy, s=28, color=TEAL,
                   edgecolor="white", lw=.35, zorder=3)
    ax.set_yticks(y, identifiable.vehicle)
    ax.set_xticks([0, 1, 2, 3])
    ax.set_xlim(-.15, 3.15)
    ax.invert_yaxis()
    ax.set_xlabel("Shared cells in voltage/network top 3")
    
    soc_handles = [
        Line2D([], [], marker="o", linestyle="None", markersize=4.5,
               markerfacecolor=GRAY, markeredgecolor="white", markeredgewidth=.35,
               label="Voltage + temperature + R0"),
        Line2D([], [], marker="o", linestyle="None", markersize=4.5,
               markerfacecolor=TEAL, markeredgecolor="white", markeredgewidth=.35,
               label="Voltage + temperature + R0 + relative SOC"),
        Line2D([], [], color=GRAY, lw=1.0, label="Matched vehicle"),
    ]
    ax.legend(handles=soc_handles, 
              title_fontsize=5.6, fontsize=5.0, ncol=2, loc="lower center",
              bbox_to_anchor=(.55, 1.12), handletextpad=.20, columnspacing=.55,
              borderaxespad=0)
    panel_label(ax, "b")
    finish(ax)

    # c, learned gates with an explicit quantitative colour key.
    ax = fig.add_subplot(grid[0, 2])
    gate_data = four_dim[four_dim.vehicle_id.isin(identifiable.vehicle_id)].copy()
    gate_data["vehicle"] = gate_data.vehicle_id
    gate_matrix = np.vstack([
        gate_data.gate_temperature.to_numpy(float),
        gate_data.gate_r0.to_numpy(float),
        gate_data.gate_relative_soc.to_numpy(float),
    ])
    gate_cmap = LinearSegmentedColormap.from_list(
        "gate_teal", ["#F1F6F6", "#91C8C0", TEAL])
    vmax = max(.15, float(np.nanmax(gate_matrix)))
    image = ax.imshow(gate_matrix, aspect="auto", vmin=0, vmax=vmax,
                      cmap=gate_cmap, interpolation="nearest", rasterized=True)
    for row in range(gate_matrix.shape[0]):
        for col in range(gate_matrix.shape[1]):
            value = gate_matrix[row, col]
            ax.text(col, row, f"{value:.02f}", ha="center", va="center",
                    fontsize=5.6, color="white" if value / vmax > .58 else DARK,
                    fontweight="bold")
    ax.set_xticks(range(len(gate_data)), gate_data.vehicle, rotation=28,
                  ha="right", rotation_mode="anchor")
    ax.set_yticks(range(3), ["Temperature", "R0", "Relative SOC"])
    ax.tick_params(axis="x", labelsize=5.2)
    ax.tick_params(axis="y", labelsize=5.5)
    
    color_axis = inset_axes(ax, width="78%", height="5%", loc="lower center",
                            bbox_to_anchor=(0, 1.04, 1, 1),
                            bbox_transform=ax.transAxes, borderpad=0)
    colorbar = fig.colorbar(image, cax=color_axis, orientation="horizontal")
    colorbar.set_ticks([0, vmax])
    colorbar.set_ticklabels(["0", f"{vmax:.2f}"])
    colorbar.ax.tick_params(labelsize=5.2, length=1.8, width=.5, pad=1)
    colorbar.outline.set_linewidth(.5)
    colorbar.set_label("Learned auxiliary gate weight", fontsize=5.8, labelpad=9)
    colorbar.ax.xaxis.set_label_position("top")
    colorbar.ax.xaxis.set_ticks_position("top")
    panel_label(ax, "c", x=-.16, y=1.08)
    finish(ax)

    # d, cell-level re-ranking and evidence profile for A-TR-01.
    profile=pd.read_csv(DATA/'candidate_profile.csv')
    order=profile.cell_index.to_list()
    network_rank_map=dict(zip(profile.cell_index,profile.network_rank))
    relative_soc=profile.relative_SOC_pp.to_numpy(float)
    lower_grid = grid[1, :].subgridspec(
        1, 5, width_ratios=[1.35, 1.15, 1.0, 1.0, 1.15], wspace=.58)
    cell_colors = [BLUE, TEAL, CORAL]
    voltage_rank = np.arange(1, 4, dtype=float)
    network_rank = np.array([network_rank_map[cell] for cell in order], dtype=float)

    ax = fig.add_subplot(lower_grid[0, 0])
    for cell, rank_v, rank_n, color in zip(order, voltage_rank, network_rank, cell_colors):
        ax.plot([0, 1], [rank_v, rank_n], color=color, lw=1.1,
                marker="o", ms=3.8)
        ax.text(1.23, rank_n + .22, f"Cell{cell}", ha="right", va="center",
                fontsize=5.4, color=color, fontweight="bold")
    ax.set_xlim(-.10, 1.36)
    ax.set_ylim(3.35, .65)
    ax.set_xticks([0, 1], ["Voltage", "Network"])
    ax.set_yticks([1, 2, 3])
    ax.set_ylabel("Rank (1 = highest)")
    ax.set_title("A-TR-01 candidate rank")
    panel_label(ax, "d", x=-.28, y=1.10)
    finish(ax)

    metrics = [
        ("ΔV (mV)", profile.delta_v_mV.to_numpy(float), (-15, 0), -3.0, "--", "{:+.0f}"),
        ("R0 (mΩ)", profile.relative_r0_milliohm.to_numpy(float), (0, .16), None, None, "{:.2f}"),
        ("ΔT (°C)", profile.module_deltaT_C.to_numpy(float), (0, 3.0), None, None, "{:.1f}"),
        ("Rel. SOC (pp)", relative_soc, (-3.0, .2), 0.0, ":", "{:+.2f}"),
    ]
    y_positions = np.arange(3)
    for metric_index, (title, values, xlim, reference, reference_style, value_format) in enumerate(metrics):
        ax = fig.add_subplot(lower_grid[0, metric_index + 1])
        if reference is not None:
            ax.axvline(reference, color=GRAY, ls=reference_style, lw=.8, zorder=0)
        for yy, value, color in zip(y_positions, values, cell_colors):
            ax.scatter(value, yy, s=28, color=color, edgecolor="white", lw=.4, zorder=3)
            place_left = value > xlim[0] + .65 * (xlim[1] - xlim[0])
            ax.annotate(value_format.format(value), (value, yy),
                        xytext=(-7 if place_left else 7, 0), textcoords="offset points",
                        ha="right" if place_left else "left", va="center",
                        fontsize=5.2, color=DARK)
        ax.set_xlim(*xlim)
        ax.set_ylim(2.5, -.5)
        ax.set_title(title)
        ax.set_yticks(y_positions, [f"Cell{cell}" for cell in order]
                      if metric_index == 0 else ["", "", ""])
        ax.tick_params(axis="y", labelsize=5.4)
        finish(ax)

    candidate_handles = [
        Line2D([], [], marker="o", color=color, lw=1.0, markersize=4,
               label=f"Cell{cell}")
        for cell, color in zip(order, cell_colors)
    ]
    boundary_handles = [
        Line2D([], [], color=GRAY, ls="--", lw=.8,
               label="ΔV descriptive boundary (−3 mV)"),
        Line2D([], [], color=GRAY, ls=":", lw=.9,
               label="Relative-SOC reference (0 pp)"),
    ]
    fig.legend(handles=candidate_handles + boundary_handles,
               
               title_fontsize=5.8, ncol=5, loc="center",
               bbox_to_anchor=(.57, .475), handlelength=1.6,
               handletextpad=.35, columnspacing=.9, borderaxespad=0)

    save(fig,OUT/'fig_09')

if __name__=='__main__':
    style();build_figure()
