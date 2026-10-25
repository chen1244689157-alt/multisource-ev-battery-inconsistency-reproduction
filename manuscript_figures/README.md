# Figure reproduction package

This package follows the manuscript figure numbering **Fig. 1–13**. The figure captions and corresponding entry points are listed in `figure_manifest.json`.

## Reproduce

Tested with Python 3.12. Install the dependencies in a clean environment and run

```bash
python -m pip install -r requirements.txt
python run_all.py
```

To regenerate selected figures, use `python run_all.py --figures 4 6 13`. Scripts locate all inputs relative to the package, independently of the current working directory. All plotting inputs are supplied within the package. Typography uses Arial with DejaVu Sans as the fallback font.

## Contents and scope

- `data/fig_XX/` contains the minimum derived plotting data and the manuscript caption.
- `code/` contains the figure-specific Python entry points.
- `outputs/fig_XX/` contains regenerated PNG, PDF, SVG and compressed TIFF files. Fig. 1 has no SVG export.
- `DATA_INDEX.md` lists each source table, its dimensions and columns.

**Figures 2–13 are regenerated from derived numerical data. Figure 1 exports the final schematic artwork.** Principal-component coordinates, fitted reference curves and model outputs are supplied as analysis inputs for the corresponding panels. The plotting workflow starts from these inputs; upstream feature extraction and model training are described in the main manuscript. The source tables preserve the numerical values used for plotting.

## Data representation

The package provides de-identified analysis derivatives with anonymous vehicle aliases, relative elapsed times and cell/module indices. Dataset D attribution and reuse information are provided in `THIRD_PARTY_DATA_NOTICE.md`.
