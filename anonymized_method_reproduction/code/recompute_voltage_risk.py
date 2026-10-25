from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
META = pd.read_csv(ROOT / "metadata/vehicle_metadata.csv")

def score_vehicle(path):
    d = pd.read_parquet(path)
    cols = sorted([c for c in d.columns if c.startswith("RV_")], key=lambda x: int(x.split("_")[1]))
    rel = d[cols].to_numpy(float)
    n = len(rel); early = max(1, int(0.2*n)); tail = max(early+1, int(0.8*n))
    change = np.nanmedian(rel[tail:], axis=0) - np.nanmedian(rel[:early], axis=0)
    repeat = np.mean(rel[tail:] < -3, axis=0)
    scores = np.maximum(-change, 0) * repeat
    value = float(np.nanmax(scores))
    top = 0 if value == 0 else int(np.nanargmax(scores)) + 1
    return value, top

rows = []
for r in META.itertuples(index=False):
    path = ROOT / "data/analysis_snapshots" / r.cohort / f"{r.vehicle_alias}.parquet"
    score, top = score_vehicle(path)
    rows.append({"vehicle_alias": r.vehicle_alias, "cohort": r.cohort, "score_mV": score, "top_cell": top})
scores = pd.DataFrame(rows)

thresholds = {}
for platform in ["A", "B"]:
    g = scores[scores.cohort.eq(f"{platform}_train")]
    thresholds[f"{platform}_train"] = tuple(g.score_mV.quantile([0.75, 0.90]))
    thresholds[f"{platform}_test"] = thresholds[f"{platform}_train"]
g = scores[scores.cohort.eq("C_independent")]
thresholds["C_independent"] = tuple(g.score_mV.quantile([0.75, 0.90]))

def grade(row):
    q75, q90 = thresholds[row.cohort]
    return "high" if row.score_mV + 1e-12 >= q90 else "medium" if row.score_mV + 1e-12 >= q75 else "low"
scores["risk_grade"] = scores.apply(grade, axis=1)
check = scores.merge(META[["vehicle_alias", "voltage_risk_score_mV", "voltage_leading_cell_index", "final_risk_grade"]], on="vehicle_alias", validate="one_to_one")
check["score_match"] = np.isclose(check.score_mV, check.voltage_risk_score_mV, rtol=0, atol=1e-9)
check["top_match"] = check.top_cell.eq(check.voltage_leading_cell_index)
check["grade_match"] = check.risk_grade.eq(check.final_risk_grade)
result = {
    "vehicles": len(check),
    "risk_counts": scores.risk_grade.value_counts().sort_index().to_dict(),
    "score_matches": int(check.score_match.sum()),
    "top_cell_matches": int(check.top_match.sum()),
    "grade_matches": int(check.grade_match.sum()),
    "max_score_difference_mV": float((check.score_mV-check.voltage_risk_score_mV).abs().max()),
    "thresholds_mV": {k: [float(x) for x in v] for k, v in thresholds.items()},
}
print(json.dumps(result, indent=2))
if result["score_matches"] != 98 or result["grade_matches"] != 98:
    raise SystemExit(1)
