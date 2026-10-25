# Figure and source-data index

All filenames are relative to this package. CSV column names specify plotted quantities; units follow the accompanying caption and plot axes. Missing auxiliary evidence remains missing rather than being replaced with zero.

## Fig. 1

Entry point: `code/export_fig_01.py`

Voltage-led battery inconsistency screening and multidimensional explainable localization. a, Multisource cell-voltage records from datasets A-C undergo time ordering, session reconstruction and quality control to generate native-resolution records and 10-min snapshots. b, Physical evidence comprises module-relative temperature, equivalent-resistance step responses and conditionally identifiable relative SOC. c, Relative-voltage stage changes and terminal deviations determine risk grades, while condition-matched historical references characterize cross-session recurrence. d, VM-GMEFNet integrates voltage priors with availability-masked auxiliary evidence for candidate ranking and evidence verification. e, Hierarchical outputs include voltage risk, candidate locations, evidence support and retrospective timing. f, The independent dataset-D path uses DOC-MLP to model brand-specific normal charging responses and aggregates the highest-scoring 5% of sessions for pack-level screening.


## Fig. 2

Entry point: `code/plot_fig_02.py`

Cohort scale, operating coverage and quality control. a, Vehicle numbers and observation resolution; the horizontal axis is logarithmic. A and B contain separate training and test cohorts, C is an independent source domain, and D provides pack-level charging records. b, Contours enclosing approximately 75% of the observation distribution in SOC–absolute-current space for each domain. c, Principal component analysis (PCA) of vehicle-level operating profiles; each point represents one vehicle from A training, B training, C or D. Profiles comprise the median and interquartile range of SOC, absolute current, upper-temperature statistics and voltage spread. The first two principal components (PC1 and PC2) explain 46.8% and 18.9% of the variance, respectively. d, Retention after quality control, with analysis counts shown as records for A-C and sessions for D. The dashed line indicates complete retention.

- `data/fig_02/cohorts.csv` — 6 rows; columns: `cohort`, `vehicles`, `role`, `resolution`.
- `data/fig_02/coverage_A.npy` — 60 × 60 numeric SOC–current bin counts; loaded with pickle disabled.
- `data/fig_02/coverage_B.npy` — 60 × 60 numeric SOC–current bin counts; loaded with pickle disabled.
- `data/fig_02/coverage_C.npy` — 60 × 60 numeric SOC–current bin counts; loaded with pickle disabled.
- `data/fig_02/coverage_D.npy` — 60 × 60 numeric SOC–current bin counts; loaded with pickle disabled.
- `data/fig_02/profiles.csv` — 395 rows; columns: `domain`, `soc_med`, `soc_iqr`, `abs_current_med`, `abs_current_iqr`, `t_upper_med`, `t_upper_iqr`, `spread_mv_med`, `spread_mv_iqr`, `PC1`, `PC2`.
- `data/fig_02/retention.csv` — 6 rows; columns: `cohort`, `input_units`, `retained_units`, `retention_pct`, `unit`.

## Fig. 3

Entry point: `code/plot_fig_03.py`

Voltage-derived risk distributions across full-cell cohorts. a-e, Ascending vehicle voltage scores for A training (n = 25), B training (n = 13), A test (n = 30), B test (n = 20) and C (n = 10), respectively. Each point represents one vehicle; blue, green and coral indicate low (labelled Normal in the legend), medium and high risk. Dashed and dotted lines mark the 75th- and 90th-percentile reference boundaries. The test cohorts of platforms A and B use boundaries frozen from their respective training cohorts; C uses its own reference distribution. The score is the product of a voltage change and a dimensionless terminal-deviation fraction and thus retains millivolt units. f, Cohort-wise vehicle counts in each grade across all 98 vehicles.

- `data/fig_03/thresholds.csv` — 5 rows; columns: `cohort`, `q75_mV`, `q90_mV`.
- `data/fig_03/vehicle_scores.csv` — 98 rows; columns: `vehicle_alias`, `cohort`, `risk_score_mV`, `top_cell`, `rank`, `risk_grade`.

## Fig. 4

Entry point: `code/plot_fig_04.py`

Cell-voltage behaviour and operating conditions of representative risk grades. Columns show A-TR-23, A-TR-02 and A-TR-01, representing low (labelled Normal), medium and high risk. a-c, Relative voltage of the score-leading cell (red) against the contemporaneous 10th-90th percentile range of the remaining cells (blue). The horizontal dashed line marks -3 mV. Shaded time regions identify the first and last 20% of valid snapshots used for stage comparison. d-f, Median relative-voltage profiles across cell indices in the early (green) and late (purple) stages; highlighted markers identify the score-leading cell. The reported changes refer to that cell. g-i, State of charge (SOC; left axis) and pack current (right axis) over the same observation period. Vehicle codes combine the domain, training (TR) or test (TE) split, and an anonymized within-group index. The three cases link risk grades to cell behaviour and its operating context.

- `data/fig_04/A-TR-01_early_late_cells.csv` — 95 rows; columns: `vehicle_alias`, `cell_index`, `early_median_mV`, `late_median_mV`, `change_mV`, `tail_low_fraction`, `tail_score`.
- `data/fig_04/A-TR-01_relative_voltage.csv` — 7982 rows; columns: `vehicle_alias`, `elapsed_days`, `candidate_relative_mV`, `other_P10_mV`, `other_P90_mV`, `SOC_percent`, `current_A`.
- `data/fig_04/A-TR-02_early_late_cells.csv` — 95 rows; columns: `vehicle_alias`, `cell_index`, `early_median_mV`, `late_median_mV`, `change_mV`, `tail_low_fraction`, `tail_score`.
- `data/fig_04/A-TR-02_relative_voltage.csv` — 1670 rows; columns: `vehicle_alias`, `elapsed_days`, `candidate_relative_mV`, `other_P10_mV`, `other_P90_mV`, `SOC_percent`, `current_A`.
- `data/fig_04/A-TR-23_early_late_cells.csv` — 95 rows; columns: `vehicle_alias`, `cell_index`, `early_median_mV`, `late_median_mV`, `change_mV`, `tail_low_fraction`, `tail_score`.
- `data/fig_04/A-TR-23_relative_voltage.csv` — 6935 rows; columns: `vehicle_alias`, `elapsed_days`, `candidate_relative_mV`, `other_P10_mV`, `other_P90_mV`, `SOC_percent`, `current_A`.

## Fig. 5

Entry point: `code/plot_fig_05.py`

Condition-matched historical reference and cross-session recurrence. Columns compare low-risk A-TR-23 (labelled Normal; Cell 2), medium-risk A-TR-02 (Cell 26) and high-risk A-TR-01 (Cell 25). a-c, Session-level conditional-residual maps across cell indices and chronologically ordered eligible sessions; colour indicates the median voltage departure of each cell in each session. d-f, Relative-voltage profiles summarized in SOC bins for condition-matched early references (blue circles) and supported late observations (red diamonds). Blue shading shows the interquartile range of the matched historical references. Early and late sets contain the first and last 20% of valid snapshots. g-i, Candidate-cell session residuals (left axis) and negative-session fractions over the latest 3, 6 and 12 eligible sessions (right axis). A negative session has at least three valid residuals, with at least half below -3 mV.

- `data/fig_05/A-TR-01_matched_late_observations.csv` — 1596 rows; columns: `vehicle_alias`, `late_elapsed_days`, `soc_percent`, `current_A`, `mean_temperature_C`, `candidate_relative_voltage_mV`, `matched_reference_mV`, `reference_P25_mV`, `reference_P75_mV`, `reference_count`, `conditional_residual_mV`, `reference_supported`.
- `data/fig_05/A-TR-01_soc_condition_curve.csv` — 9 rows; columns: `vehicle_alias`, `SOC`, `reference`, `ref_low`, `ref_high`, `late`, `late_low`, `late_high`, `n_late`.
- `data/fig_05/A-TR-02_matched_late_observations.csv` — 334 rows; columns: `vehicle_alias`, `late_elapsed_days`, `soc_percent`, `current_A`, `mean_temperature_C`, `candidate_relative_voltage_mV`, `matched_reference_mV`, `reference_P25_mV`, `reference_P75_mV`, `reference_count`, `conditional_residual_mV`, `reference_supported`.
- `data/fig_05/A-TR-02_soc_condition_curve.csv` — 9 rows; columns: `vehicle_alias`, `SOC`, `reference`, `ref_low`, `ref_high`, `late`, `late_low`, `late_high`, `n_late`.
- `data/fig_05/A-TR-23_matched_late_observations.csv` — 1387 rows; columns: `vehicle_alias`, `late_elapsed_days`, `soc_percent`, `current_A`, `mean_temperature_C`, `candidate_relative_voltage_mV`, `matched_reference_mV`, `reference_P25_mV`, `reference_P75_mV`, `reference_count`, `conditional_residual_mV`, `reference_supported`.
- `data/fig_05/A-TR-23_soc_condition_curve.csv` — 9 rows; columns: `vehicle_alias`, `SOC`, `reference`, `ref_low`, `ref_high`, `late`, `late_low`, `late_high`, `n_late`.

## Fig. 6

Entry point: `code/plot_fig_06.py`

Multidimensional evidence and parameter identifiability for voltage candidates. a-c, Cell-wise evidence maps for A-TR-23, A-TR-02 and A-TR-01, respectively. Colours show evidence percentiles calculated separately within each vehicle and dimension, and red triangles and vertical lines mark the voltage-score-leading cell. Module temperatures are mapped to their associated cell indices. Grey regions indicate non-identifiable (NI) relative SOC. d, Candidate-associated values in the same vehicle order: low-side voltage offset in mV, dimensionless equivalent-resistance robust z score, module-relative temperature in °C and relative-SOC offset in percentage points (pp). e, Spatial relation of repeated auxiliary evidence to voltage candidates among 16 medium- and 13 high-risk vehicles. Labels give vehicle counts; bar widths give within-grade proportions. Co-located evidence overlaps the candidate cell or its module, whereas distributed evidence occurs elsewhere. f, Percentages of vehicles meeting each dimension’s identifiability criteria by cohort. Tr and Te denote training and test cohorts.

- `data/fig_06/candidate_summary.csv` — 3 rows; columns: `vehicle_alias`, `voltage_p05_mV`, `r0_max_step_robust_z`, `module_temp_excess_p95_C`, `candidate_relative_soc_median_pp`.
- `data/fig_06/cell_evidence.csv` — 1140 rows; columns: `cell_index`, `dimension`, `raw_value`, `within_vehicle_percentile`, `is_voltage_candidate`, `vehicle_alias`.
- `data/fig_06/identifiability.csv` — 5 rows; columns: `group`, `n`, `Voltage`, `Temperature`, `R0`, `Relative_SOC`.
- `data/fig_06/support_relation.csv` — 2 rows; columns: `risk_level`, `No repeated support`, `Distributed`, `Candidate / module`.

## Fig. 7

Entry point: `code/plot_fig_07.py`

Auxiliary-evidence distributions and representative physical responses. a-c, Candidate-associated thermal support, relative equivalent-resistance response and relative SOC offset among identifiable medium- and high-risk vehicles. Each point is one vehicle; sample counts are given beneath each group. Boxes span the 25th-75th percentiles, central lines show medians and whiskers extend to the 5th–95th percentile limits; all vehicle observations are overlaid. The resistance axis uses a symmetric logarithmic scale to retain zero-valued responses. d, Fractions of eligible sessions supporting elevated module temperature in A-TR-06; red triangles mark voltage-candidate modules. e, Cell-wise fractions of supporting equivalent-resistance sessions in A-TR-01, with candidate cells marked. f, Its cell-wise relative-SOC offsets, highlighting Cell 23, Cell 25 and Cell 47. Dashed zero lines provide the no-offset or no-support reference. Dimension-specific identifiability requirements yield different sample sizes across dimensions.

- `data/fig_07/panel_d_source.csv` — 17 rows; columns: `module_id`, `qualified_events`, `thermal_support_events`, `candidate_module`.
- `data/fig_07/panel_e_source.csv` — 95 rows; columns: `cell_index`, `support_events`, `events`, `voltage_candidate`.
- `data/fig_07/panel_f_source.csv` — 95 rows; columns: `cell_index`, `relative_soc_median_pp`, `voltage_candidate`.
- `data/fig_07/population_source.csv` — 69 rows; columns: `risk_level`, `cell_index`, `module_id`, `candidate_module_support_pct`, `panel`, `candidate_r0_p95_mohm`, `candidate_relative_soc_pp`.

## Fig. 8

Entry point: `code/plot_fig_08.py`

Vehicle-adaptive OCV-SOC reference and module-temperature evolution. a, Stationary anchors (blue), SOC-bin medians (green) and the monotonic OCV-SOC reference (red) for A-TR-01. The fit uses 22 qualified anchors spanning 47 SOC percentage points; grey reference segments identify slopes below the inversion threshold of 0.8 mV per SOC percentage point. b, Stationary voltage departures from the fitted reference for candidate Cell 23, Cell 25 and Cell 47, with the pack-median departure shown in grey. c,d, Session-level 95th-percentile module-relative temperatures over elapsed time in A-TR-06 and A-TR-01, respectively. Module labels identify candidate, neighbouring or supporting locations; M denotes module index. The two cases contrast a localized thermal region near the candidates with evidence distributed across other modules. Temperature provides module-level context, while the stationary-voltage reference supports relative-SOC interpretation at cell level.

- `data/fig_08/ocv_panel_a_source.csv` — 229 rows; columns: `soc_pct`, `voltage_V`, `series`, `rest_count`, `slope_mV_per_pp`, `slope_valid`.
- `data/fig_08/ocv_panel_b_source.csv` — 22 rows; columns: `soc`, `pack_ocv_residual_mV`, `U_23_residual_mV`, `U_25_residual_mV`, `U_47_residual_mV`.
- `data/fig_08/temperature_panel_c_source.csv` — 304 rows; columns: `module_id`, `excess_median_C`, `excess_p95_C`, `elapsed_days`, `rolling_p95_C`.
- `data/fig_08/temperature_panel_d_source.csv` — 530 rows; columns: `module_id`, `excess_median_C`, `excess_p95_C`, `elapsed_days`, `rolling_p95_C`.

## Fig. 9

Entry point: `code/plot_fig_09.py`

VM-GMEFNet evidence fusion and candidate-cell ranking. a, Voltage-attention and mean auxiliary-evidence scores for the 38 training vehicles from platforms A and B, coloured by voltage base grade, with Normal denoting low risk. Both coordinates are dimensionless. b, Number of shared cells between the voltage-prior and network top-three candidate sets in five vehicles with identifiable relative SOC. Grey and green markers represent three-dimensional and four-dimensional evidence configurations, respectively; connecting lines pair the same vehicle. c, Learned auxiliary gate weights for those vehicles. The dimensionless gate weights quantify the network weighting of available auxiliary features. d, Voltage and network ranks for Cell 23, Cell 25 and Cell 47 in A-TR-01, followed by their voltage, equivalent resistance, module-temperature and relative-SOC values. Rank 1 denotes the highest rank. Dashed and dotted reference lines indicate −3 mV and zero relative-SOC offset, respectively.

- `data/fig_09/candidate_profile.csv` — 3 rows; columns: `cell_index`, `voltage_rank`, `network_rank`, `delta_v_mV`, `relative_r0_milliohm`, `module_deltaT_C`, `relative_SOC_pp`.
- `data/fig_09/concordance.csv` — 11 rows; columns: `vehicle_alias`, `no_soc_overlap`, `four_dim_overlap`, `relative_soc_available`.
- `data/fig_09/network_outputs.csv` — 38 rows; columns: `vehicle_alias`, `rule_level`, `voltage_attention_score`, `mean_auxiliary_score`, `gate_temperature`, `gate_r0`, `gate_relative_soc`.

## Fig. 10

Entry point: `code/plot_fig_10.py`

VM-GMEFNet structural sensitivity and voltage-dominant stability. a, Mean rank correlation between network and voltage-prior ordering across 36 combinations of the auxiliary cap and voltage and auxiliary coefficients. b, Percentage of vehicles retaining the same leading candidate as the default configuration. Rows specify the auxiliary and voltage coefficients; columns specify the auxiliary cap. c, Mean auxiliary contribution versus the cap, with the range across coefficient combinations indicated by the error bars. The highlighted marker and vertical dashed line identify the default cap of 0.30. All panels use the same 38 training vehicles from platforms A and B. Candidate-rank agreement summarizes ranking stability, and auxiliary contribution quantifies the magnitude of the gated adjustment.

- `data/fig_10/candidate_stability.csv` — 38 rows; columns: `unique_top1_across_36`.
- `data/fig_10/default_top1_stability.csv` — 36 rows; columns: `beta_v`, `beta_a`, `alpha_max`, `top1_same_as_default_pct`.
- `data/fig_10/parameter_grid_summary.csv` — 36 rows; columns: `beta_v`, `beta_a`, `alpha_max`, `vehicles`, `voltage_top1_retention_pct`, `mean_top3_overlap`, `top3_set_retention_pct`, `exact_top3_order_pct`, `ranking_changed_pct`, `mean_rank_correlation`, `voltage_grade_agreement_pct`, `mean_auxiliary_contribution`.
- `data/fig_10/tie_adjusted_summary.csv` — 36 rows; columns: `beta_v`, `beta_a`, `alpha_max`, `vehicles`, `strict_top1_retention_pct`, `top1_in_voltage_max_tie_pct`, `top1_within_001_pct`, `top1_within_005_pct`, `median_voltage_max_tie_count`, `mean_voltage_gap`, `mean_rank_correlation`, `voltage_grade_agreement_pct`.

## Fig. 11

Entry point: `code/plot_fig_11.py`

Voltage-derived base risk and multidimensional evidence support. a, Voltage base grades across the five complete-cell cohorts (98 vehicles). Colours encode low, medium and high risk; pattern overlays distinguish co-located recurrent support, distributed multidimensional support and cross-session auxiliary support. b, Evidence-state proportions within the 16 medium- and 13 high-risk vehicles. Unpatterned portions indicate vehicles lacking the specified repeated auxiliary support. c, Cross-tabulation against the reference labels normal, inconsistency and thermal runaway. Entries give vehicle counts and percentages within each reference-label row. d, Pooled vehicle-level label agreement when medium or high risk is a positive screen and inconsistency or thermal runaway is a positive reference label. The F1 score is the harmonic mean of precision and recall. Metrics pool all 98 vehicles from the reference and test cohorts.

- `data/fig_11/confusion_matrix.csv` — 1 rows; columns: `TP`, `TN`, `FP`, `FN`.
- `data/fig_11/grade_evidence_labels.csv` — 98 rows; columns: `row_index`, `group`, `risk`, `label`, `final_risk_label`.
- `data/fig_11/metrics.csv` — 8 rows; columns: `metric`, `value`, `percentage`, `numerator`, `denominator`, `wilson_95_ci_lower`, `wilson_95_ci_upper`.

## Fig. 12

Entry point: `code/plot_fig_12.py`

Temporal evolution of inconsistency risk. a–c, Voltage scores recomputed from successive observation prefixes for A-TR-23, A-TR-02 and A-TR-01, respectively; panel titles state the final risk grade. Point colours show the grade at each evaluated prefix, and dashed and dotted lines indicate the domain-specific 75th- and 90th-percentile boundaries. d, Corresponding risk states for all 98 vehicles, grouped by cohort. Each row represents a vehicle and horizontal position is normalized to its own observation period. Grey denotes unavailable assessment or absent observations. Scores and grades are recalculated at each observation prefix. This retrospective reconstruction traces the emergence and evolution of risk evidence over the recorded observation period.

- `data/fig_12/prefix_replay.csv.gz` — 19600 rows; columns: `vehicle_alias`, `cohort`, `final_risk`, `final_score`, `bin`, `progress_pct`, `elapsed_days`, `prefix_count`, `new_snapshots`, `score_mV`, `top_cell`, `state`, `display_state`, `q75_mV`, `q90_mV`.

## Fig. 13

Entry point: `code/plot_fig_13.py`

Brand-wise conditional-response modelling and pack-level screening of aggregated charging segments. a, Vehicle scores divided by their brand-specific calibrated thresholds and ranked within each brand (n = 198, 49 and 100). The dashed line at one is the screening boundary. b, Accuracy, specificity and false-positive rate against the source-provided vehicle-level normal and abnormal labels across all 347 vehicles from five-fold vehicle-isolated cross-validation (CV); displayed values are rounded to whole percentages. c,d, Observed session voltage-spread 95th percentiles against median SOC for vehicle 100 (431 sessions) and vehicle 107 (42 sessions). Each point represents a session, coloured by charging current. e,f, Corresponding session 5th-percentile minimum-cell voltage and 95th-percentile temperature spread, with blue circles and coral diamonds distinguishing the two vehicles. These measured session summaries characterize the voltage and thermal responses associated with the vehicle screening scores.

- `data/fig_13/high_score_sessions.csv` — 42 rows; columns: `soc_median_pct`, `cell_spread_p95_mV`, `current_median_A`, `min_cell_p05_V`, `temp_spread_p95_C`.
- `data/fig_13/method_metrics.csv` — 1 rows; columns: `method`, `n`, `accuracy`, `specificity`, `false_positive_rate`.
- `data/fig_13/non_alarm_sessions.csv` — 431 rows; columns: `soc_median_pct`, `cell_spread_p95_mV`, `current_median_A`, `min_cell_p05_V`, `temp_spread_p95_C`.
- `data/fig_13/overall_metrics.csv` — 1 rows; columns: `n`, `TP`, `FP`, `TN`, `FN`, `accuracy`, `sensitivity`, `specificity`, `precision`, `false_positive_rate`, `false_negative_rate`, `method`.
- `data/fig_13/score_distribution.csv` — 347 rows; columns: `brand`, `threshold_ratio`.
- `data/fig_13/vehicle_scores.csv` — 347 rows; columns: `vehicle_alias`, `brand_domain`, `threshold_ratio`, `predicted_alarm`, `reference_label`.
