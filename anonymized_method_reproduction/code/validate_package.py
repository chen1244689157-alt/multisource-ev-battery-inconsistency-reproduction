from pathlib import Path
import hashlib, json, re
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
meta = pd.read_csv(ROOT / "metadata/vehicle_metadata.csv")
issues = []
files = list((ROOT / "data/analysis_snapshots").rglob("*.parquet"))
if len(files) != 98: issues.append(f"expected 98 snapshot files, found {len(files)}")
for p in files:
    schema = pq.ParquetFile(p).schema_arrow.names
    forbidden = {"vehicle_id", "epoch_s", "timestamp", "snapshot_time", "time_beijing_1", "mileage_num", "source_row"}.intersection(schema)
    if forbidden: issues.append(f"{p.name}: forbidden columns {sorted(forbidden)}")
    if not any(c.startswith("RV_") for c in schema): issues.append(f"{p.name}: no relative-voltage columns")
patterns = [re.compile("J"+"BGS"+r"\d+"), re.compile("L"+"B_"+r"\d+"), re.compile(r"\b20\d{2}-\d{2}-\d{2}\b"), re.compile(r"\b[A-Za-z]:\\")]
for p in ROOT.rglob("*"):
    if not p.is_file() or p.name == "validate_package.py": continue
    if p.suffix.lower() in {".csv", ".md", ".json", ".txt", ".py"}:
        text = p.read_text(encoding="utf-8", errors="ignore")
        if any(pat.search(text) for pat in patterns): issues.append(f"identifier/date/path pattern in {p.relative_to(ROOT)}")
result = {"status": "PASS" if not issues else "FAIL", "snapshot_files": len(files), "unique_aliases": int(meta.vehicle_alias.nunique()), "issues": issues}
print(json.dumps(result, indent=2, ensure_ascii=False))
raise SystemExit(0 if not issues else 1)
