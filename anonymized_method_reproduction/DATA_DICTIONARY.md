# Data dictionary

## Analysis snapshots

`snapshot_index` is the within-vehicle row order. `elapsed_seconds` is measured from the first released snapshot. `interval_seconds` retains temporal gaps. `session_index` increments when the gap exceeds 7,200 s or the operating-state code changes. `pack_current_A`, `pack_SOC_percent`, `temperature_min_C` and `temperature_max_C` describe operating conditions. `RV_i_mV` is cell i voltage minus the simultaneous pack cell-voltage median, in millivolts. `relative_mileage_km` is mileage after subtraction of the first valid value and is present only where the source provided mileage.

## Auxiliary evidence

Temperature files contain module-level thermal excess and persistence quantities. Equivalent-R0 files contain current-step counts and relative R0 statistics in milliohms. Event-voltage files contain event-level relative-voltage summaries. Event identifiers are replaced by within-vehicle indices and event dates by elapsed days.

## Relative SOC

Relative SOC is reported in percentage points for observations satisfying the OCV-SOC slope and repeated stationary-event identifiability criteria. Missing values indicate that no relative-SOC estimate is assigned.
