# Multisource EV battery inconsistency reproduction data and code

This repository provides the processed data, figure source tables and executable Python workflows supporting a voltage-led method for battery-cell inconsistency screening and multidimensional evidence localization.

## Repository contents

- `anonymized_method_reproduction/` contains de-identified analysis snapshots and auxiliary evidence for 98 complete-cell vehicles, together with code that reproduces voltage-risk scores, leading cells and risk grades.
- `manuscript_figures/` contains the source data, captions, plotting code and publication-ready exports for Figures 1–13.
- `THIRD_PARTY_DATA_NOTICE.md` gives the attribution and access route for Dataset D.

## Reproduce the analysis and figures

Follow the README files in `anonymized_method_reproduction/` and `manuscript_figures/`. Both workflows resolve inputs from repository-relative paths.

## Data availability

Datasets A–C are supplied as de-identified analysis-level records that preserve the variables, temporal structure and session information required for the reported calculations. Dataset D uses processed charging-snippet data released by Zhang *et al.* under a CC BY 4.0 licence at https://doi.org/10.6084/m9.figshare.23659323.v1.
