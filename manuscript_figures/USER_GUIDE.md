# User guide

## Quick start

Use Python 3.12. Install the pinned dependencies with `python -m pip install -r requirements.txt`, then run `python run_all.py`. To regenerate selected figures, use `python run_all.py --figures 6 11 13`.

Inputs and outputs are resolved relative to the package location. Figure outputs are stored in `outputs/fig_XX/`. See `DATA_INDEX.md` for figure captions, input files, columns and executable entry points.

## Reproduction scope

Figures 2–13 are regenerated from numerical plotting data. Figure 1 exports the final schematic artwork. The workflow starts from derived numerical inputs, including fitted curves and model outputs, as detailed in the main manuscript and the source-data index.

## Data conventions

Vehicle aliases identify anonymized study cases. Cell and module indices refer to monitored positions. Calendar timestamps and original identifier mappings are excluded. Missing auxiliary entries indicate unavailable observations; numeric zeros retain their measured or calculated meaning. Units and statistical quantities are given in column names, captions and axis labels.

For `data/fig_11/metrics.csv`, `metric` is the metric name, `value` is the dimensionless result, `percentage` is the result multiplied by 100 where reported, and `numerator` and `denominator` are the counts used for proportion metrics. `wilson_95_ci_lower` and `wilson_95_ci_upper` are dimensionless Wilson confidence limits. Empty count or interval fields mean that the corresponding quantity was not reported for that metric.

## Data representation

Anonymous vehicle aliases, relative elapsed times, cell/module indices and derived numerical variables support direct regeneration of the figures. Dataset D attribution is retained in `THIRD_PARTY_DATA_NOTICE.md`.

All explanatory text, filenames, data headers and code comments use English. Mathematical symbols and scientific units are retained.
