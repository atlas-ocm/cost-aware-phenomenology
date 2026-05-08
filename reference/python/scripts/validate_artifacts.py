#!/usr/bin/env python3
"""Validate the integrity of validation_artifacts/.

Checks:
- Every case file has a corresponding model_run for each of the 3 expected models.
- Each model_run has llm_reading with overall_verdict and primary_reading.
- Each model_run case_id matches the case file case_id.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = ROOT / "validation_artifacts"
EXPECTED_MODELS = [
    "comet_12b_v.7-i1",
    "silicon-maid-7b-imatrix",
    "fimbulvetr-11b-v2",
]


def check_track(name: str, cases_dir: Path, model_runs_root: Path) -> dict:
    if not cases_dir.exists():
        return {"track": name, "case_count": 0, "issues": [f"cases dir missing: {cases_dir}"]}

    case_files = sorted(cases_dir.glob("*.json"))
    case_ids = [json.loads(f.read_text(encoding="utf-8"))["case_id"] for f in case_files]

    issues = []
    for model in EXPECTED_MODELS:
        model_dir = model_runs_root / model
        if not model_dir.exists():
            issues.append(f"missing model dir: {model_dir.name}")
            continue
        run_files = sorted(model_dir.glob("*.json"))
        run_data = {json.loads(f.read_text(encoding="utf-8")).get("case_id"): f for f in run_files}

        for cid in case_ids:
            if cid not in run_data:
                issues.append(f"{model}: missing run for {cid}")
                continue
            d = json.loads(run_data[cid].read_text(encoding="utf-8"))
            lr = d.get("llm_reading", {})
            if not lr.get("overall_verdict"):
                issues.append(f"{model}/{run_data[cid].name}: missing llm_reading.overall_verdict")
            if not lr.get("primary_reading"):
                issues.append(f"{model}/{run_data[cid].name}: missing llm_reading.primary_reading")

    return {"track": name, "case_count": len(case_files), "issues": issues}


def main() -> int:
    results = []

    com_grammar = ARTIFACTS / "com_grammar"
    if com_grammar.exists():
        results.append(check_track(
            "com_grammar",
            com_grammar / "cases",
            com_grammar / "model_runs",
        ))

    adjust = ARTIFACTS / "adjustment_layer"
    if adjust.exists():
        results.append(check_track(
            "adjustment_layer_main",
            adjust / "main_cases",
            adjust / "model_runs_main",
        ))
        results.append(check_track(
            "adjustment_layer_holdout",
            adjust / "holdout_cases",
            adjust / "model_runs_holdout",
        ))

    total_issues = 0
    for r in results:
        status = "OK" if not r["issues"] else f"ISSUES: {len(r['issues'])}"
        print(f"\n[{r['track']}] {r['case_count']} cases — {status}")
        for issue in r["issues"]:
            print(f"    - {issue}")
        total_issues += len(r["issues"])

    print(f"\nTotal issues: {total_issues}")
    return 0 if total_issues == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
