# De-identified analysis data and method reproduction

This package provides the analysis inputs required to reproduce voltage-led inconsistency scores, cohort thresholds, risk grades, candidate cells, session structure and multidimensional evidence for 98 complete-cell vehicles.

## Contents

- `data/analysis_snapshots/`: 98 vehicle-level Parquet files. Each row is an eligible ten-minute terminal snapshot. Cell voltages are released as pack-median-relative values (`RV_*_mV`) rather than absolute cell voltages.
- `data/auxiliary_events/`: de-identified temperature-module, equivalent-R0 and event-voltage evidence for vehicles entering multidimensional interpretation.
- `data/relative_soc/`: conditionally identifiable relative-SOC event and cell summaries.
- `metadata/`: anonymized vehicle labels, cohort thresholds, row counts, cell counts, session counts and observation spans.
- `code/recompute_voltage_risk.py`: recomputes all 98 voltage scores, leading cells and grades from the released snapshots.

## De-identification

Vehicle aliases, relative elapsed time, relative mileage and pack-median-relative cell voltage provide the analytical representation used by the method. This representation preserves score calculation, temporal gaps, session segmentation and operating-condition matching.

## Reproduce the principal result

```bash
python code/recompute_voltage_risk.py
python code/validate_package.py
```

The expected output contains 98 matching scores and grades, with 69 low-, 16 medium- and 13 high-risk vehicles.
