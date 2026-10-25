"""Extend the layered-risk figure with retrospective label agreement metrics.

The binary evaluation rule is fixed by the study definition:
  - true positive class: inconsistency or thermal-runaway label;
  - predicted positive class: medium or high risk.

The figure keeps the existing risk/disposition panels and adds a label-to-grade
matrix plus threshold-based performance metrics. Labels are read from the
released 98-vehicle workbook.
"""
from pathlib import Path
from math import sqrt

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import export_settings
from matplotlib.patches import Patch, Rectangle
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "fig_11"
OUT.mkdir(parents=True, exist_ok=True)

COLORS = {
    "low": "#5797CE",
    "medium": "#329D8D",
    "high": "#DF756A",
}
EDGE = "#40535F"
TEXT = "#173344"
GROUP_ORDER = ["A_train", "B_train", "A_test", "B_test", "C_independent"]
GROUP_DISPLAY = {
    "A_train": "A train",
    "B_train": "B train",
    "A_test": "A test",
    "B_test": "B test",
    "C_independent": "C",
}
STATUS_ORDER = [
    ("normal", "low", ""),
    ("medium", "medium", ""),
    ("medium_colocated", "medium", "//"),
    ("medium_distributed", "medium", ".."),
    ("high", "high", ""),
    ("high_supported", "high", "xx"),
]
TRUE_ORDER = ["normal", "inconsistency", "thermal_runaway"]
TRUE_DISPLAY = ["Normal", "Inconsistency", "Thermal runaway"]
RISK_ORDER = ["low", "medium", "high"]
RISK_DISPLAY = ["Low", "Medium", "High"]


def safe_div(num, den):
    return float(num / den) if den else np.nan


def wilson_interval(successes, total, z=1.959963984540054):
    """Wilson score interval for a binomial proportion."""
    if total == 0:
        return np.nan, np.nan
    p = successes / total
    den = 1 + z * z / total
    center = (p + z * z / (2 * total)) / den
    half = z * sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / den
    return center - half, center + half


def panel_label(ax, letter):
    ax.text(-0.11, 1.08, letter, transform=ax.transAxes, fontsize=10,
            fontweight="bold", va="bottom")


def style_axes(ax):
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color("#626870")
        spine.set_linewidth(0.65)
    ax.tick_params(direction="out", length=2.5, width=0.6,
                   top=False, right=False, labeltop=False, labelright=False)


def main():
    d=pd.read_csv(ROOT / "data" / "fig_11" / "grade_evidence_labels.csv")
    d=d.rename(columns={'group':'cohort','row_index':'row_index','risk':'risk_grade','label':'reference_label','final_risk_label':'evidence_state'})
    required = {
        "cohort", "row_index", "risk_grade", "evidence_state", "reference_label"
    }
    missing = required - set(d.columns)
    if missing:
        raise ValueError(f"Missing workbook columns: {sorted(missing)}")
    if len(d) != 98 or not d["row_index"].is_unique:
        raise ValueError("The complete-cell sheet must contain 98 unique vehicles")
    if d["reference_label"].isna().any():
        raise ValueError("All 98 vehicles must have a true label")
    if not set(d["reference_label"]).issubset(set(TRUE_ORDER)):
        raise ValueError(f"Unexpected true labels: {sorted(set(d['reference_label']) - set(TRUE_ORDER))}")
    if not set(d["risk_grade"]).issubset(set(RISK_ORDER)):
        raise ValueError("Unexpected risk grade")

    # Fixed evaluation definition requested by the author.
    d["reference_positive"] = d["reference_label"].isin(["inconsistency", "thermal_runaway"])
    d["predicted_positive"] = d["risk_grade"].isin(["medium", "high"])
    tp = int((d["reference_positive"] & d["predicted_positive"]).sum())
    tn = int((~d["reference_positive"] & ~d["predicted_positive"]).sum())
    fp = int((~d["reference_positive"] & d["predicted_positive"]).sum())
    fn = int((d["reference_positive"] & ~d["predicted_positive"]).sum())

    accuracy = safe_div(tp + tn, len(d))
    precision = safe_div(tp, tp + fp)
    sensitivity = safe_div(tp, tp + fn)
    specificity = safe_div(tn, tn + fp)
    f1 = safe_div(2 * tp, 2 * tp + fp + fn)
    balanced_accuracy = np.nanmean([sensitivity, specificity])
    npv = safe_div(tn, tn + fn)
    mcc_den = sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = safe_div(tp * tn - fp * fn, mcc_den)

    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "DejaVu Sans"],
        "font.size": 7,
        "axes.titlesize": 8,
        "axes.labelsize": 7,
        "xtick.labelsize": 6.5,
        "ytick.labelsize": 6.5,
        "axes.linewidth": 0.65,
        "legend.fontsize": 6.5,
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
        "hatch.linewidth": 0.5,
    })

    fig = plt.figure(figsize=(7.20, 4.88))
    gs = fig.add_gridspec(
        2, 2, left=0.145, right=0.985, bottom=0.105, top=0.83,
        hspace=0.40, wspace=0.33, width_ratios=[1.55, 1.0],
        height_ratios=[1.0, 1.05]
    )

    # a: risk and evidence-disposition counts by data group.
    ax = fig.add_subplot(gs[0, 0])
    y = np.arange(len(GROUP_ORDER))
    left = np.zeros(len(GROUP_ORDER), dtype=float)
    count_rows = []
    for status, risk, hatch in STATUS_ORDER:
        vals = np.array([
            int(((d["cohort"] == group) &
                 (d["evidence_state"] == status)).sum())
            for group in GROUP_ORDER
        ])
        bars = ax.barh(
            y, vals, left=left, height=0.62, color=COLORS[risk],
            edgecolor=EDGE if hatch else "white", linewidth=0.4,
            hatch=hatch, rasterized=bool(hatch)
        )
        for group, v in zip(GROUP_ORDER, vals):
            count_rows.append({"cohort": group, "evidence_state": status, "vehicle_count": int(v)})
        for yy, v, lft in zip(y, vals, left):
            if v >= 1:
                ax.text(lft + v / 2, yy, str(int(v)), ha="center", va="center",
                        fontsize=6.2, color=TEXT,
                        fontweight="bold" if hatch else "normal")
        left += vals
    ax.set_yticks(y, [GROUP_DISPLAY[g] for g in GROUP_ORDER])
    ax.invert_yaxis()
    ax.set_xlim(0, 32)
    ax.set_xlabel("Number of vehicles")
    panel_label(ax, "a")
    style_axes(ax)

    # b: evidence refinement within medium/high voltage risk grades.
    ax = fig.add_subplot(gs[0, 1])
    base_rows = [
        ("Medium", int((d["risk_grade"]=="medium").sum()), [
            ("medium", int((d["evidence_state"]=="medium").sum()), "medium", ""),
            ("medium_colocated", int((d["evidence_state"]=="medium_colocated").sum()), "medium", "//"),
            ("medium_distributed", int((d["evidence_state"]=="medium_distributed").sum()), "medium", ".."),
        ]),
        ("High", int((d["risk_grade"]=="high").sum()), [
            ("high", int((d["evidence_state"]=="high").sum()), "high", ""),
            ("high_supported", int((d["evidence_state"]=="high_supported").sum()), "high", "xx"),
        ]),
    ]
    yb = np.arange(2)
    left_b = np.zeros(2)
    for part_idx in range(3):
        for yy, (_, total, parts) in enumerate(base_rows):
            if part_idx >= len(parts):
                continue
            status, expected, risk, hatch = parts[part_idx]
            observed = int((d["evidence_state"] == status).sum())
            if observed != expected:
                raise ValueError(f"Unexpected count for {status}: {observed} != {expected}")
            if observed == 0:
                continue
            width = 100 * observed / total
            ax.barh(
                yy, width, left=left_b[yy], height=0.55, color=COLORS[risk],
                edgecolor=EDGE if hatch else "white", linewidth=0.4,
                hatch=hatch, rasterized=bool(hatch)
            )
            label = str(observed) if width < 8 else f"{observed}\n({width:.0f}%)"
            ax.text(left_b[yy] + width / 2, yy, label, ha="center", va="center",
                    fontsize=6.2, color=TEXT,
                    fontweight="bold" if hatch else "normal")
            left_b[yy] += width
    ax.set_yticks(yb, [f"Medium (n = {base_rows[0][1]})", f"High (n = {base_rows[1][1]})"])
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share within voltage base grade (%)")
    panel_label(ax, "b")
    style_axes(ax)

    # c: full three-label versus three-grade association matrix.
    ax = fig.add_subplot(gs[1, 0])
    table = pd.crosstab(d["reference_label"], d["risk_grade"]).reindex(
        index=TRUE_ORDER, columns=RISK_ORDER, fill_value=0
    )
    row_pct = table.div(table.sum(axis=1), axis=0) * 100
    ax.set_xlim(0, 3)
    ax.set_ylim(3, 0)
    for i, true_label in enumerate(TRUE_ORDER):
        for j, risk in enumerate(RISK_ORDER):
            n = int(table.loc[true_label, risk])
            pct = float(row_pct.loc[true_label, risk])
            alpha = 0.08 if n == 0 else 0.24 + 0.70 * pct / 100
            rect = Rectangle((j, i), 1, 1, facecolor=COLORS[risk], alpha=alpha,
                             edgecolor="white", linewidth=1.1)
            ax.add_patch(rect)
            ax.text(j + 0.5, i + 0.5, f"{n}\n({pct:.1f}%)",
                    ha="center", va="center", fontsize=7,
                    color=TEXT, fontweight="bold" if pct >= 50 else "normal")
    ax.set_xticks(np.arange(3) + 0.5, RISK_DISPLAY)
    ax.set_yticks(np.arange(3) + 0.5, TRUE_DISPLAY)
    ax.set_xlabel("Predicted risk grade")
    panel_label(ax, "c")
    style_axes(ax)

    # d: binary metrics for medium-or-higher as the positive prediction.
    # Horizontal position carries the value; equal bubble areas avoid visually
    # exaggerating the small differences among the four metrics.
    ax = fig.add_subplot(gs[1, 1])
    false_positive_rate = safe_div(fp, fp + tn)
    metric_names = ["Accuracy", "Precision", "Recall", "F1 score", "False-positive rate"]
    metric_values = np.array([accuracy, precision, sensitivity, f1, false_positive_rate]) * 100
    metric_colors = ["#5B8FB9", "#DF756A", "#DF756A", "#8A6FA8", "#6F7C85"]
    yd = np.arange(len(metric_names))
    ax.hlines(yd, 0, np.maximum(metric_values - 0.8, 0), color="#C9D3DA",
              linewidth=2.0, zorder=1)
    ax.scatter(metric_values, yd, s=120, color=metric_colors,
               edgecolor="none", linewidth=0, zorder=3)
    for yy, value in zip(yd, metric_values):
        high_value = value >= 85
        x = value - 2.0 if high_value else value + 2.0
        ax.text(x, yy - 0.36, f"{value:.1f}%", ha="right" if high_value else "left", va="center",
                fontsize=6.2, color=TEXT, fontweight="bold")
    ax.set_yticks(yd, metric_names)
    ax.invert_yaxis()
    ax.set_xlim(0, 108)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Metric value (%)")
    panel_label(ax, "d")
    style_axes(ax)

    # Shared keys. Pattern overlays remain text-only for Adobe compatibility.
    legend = [
        Patch(facecolor=COLORS["low"], edgecolor="none", label="Low"),
        Patch(facecolor=COLORS["medium"], edgecolor="none", label="Medium"),
        Patch(facecolor=COLORS["high"], edgecolor="none", label="High"),
    ]
    fig.legend(handles=legend, loc="upper center", bbox_to_anchor=(0.5, 0.985),
               ncol=3, frameon=False, columnspacing=1.25, handlelength=1.6)
    fig.text(
        0.5, 0.916,
        "Pattern overlays:  //  Co-located recurrent support     ··  Distributed multidimensional support     ××  Cross-session auxiliary support",
        ha="center", va="center", fontsize=6.2, color=EDGE
    )

    stem = OUT / "fig_11"
    fig.savefig(str(stem) + ".png", dpi=600)
    fig.savefig(str(stem) + ".pdf")
    fig.savefig(str(stem) + ".svg")
    fig.savefig(str(stem) + ".tiff", dpi=600, pil_kwargs={"compression": "tiff_lzw"})
    plt.close(fig)


if __name__ == "__main__":
    main()
