"""Readiness of the existing records for the binding rules prepared in run 007 (driver-run, deterministic).

usage: python probe_existing_records.py <repo_root>

For every recorded run's transition_execution_record.json and the shipped example, prints whether each
check's command equals its criterion's check_command, whether its revision_checked equals the re-observed
revision, whether its stored result carries one exit= line matching exit_code, and whether the receipt is
JSON whose text contains the decision, the served model and every hashed input. Observation only: exit 0.
"""
import json
import pathlib
import sys

repo = pathlib.Path(sys.argv[1]).resolve()
records = sorted((repo / "validation_artifacts" / "ameba_cycle").glob("run_00*/transition_execution_record.json"))
records.append(repo / "examples" / "transition_execution_record_example.json")
for path in records:
    record = json.loads(path.read_text(encoding="utf-8-sig"))
    criteria = {c["id"]: c["check_command"] for c in record["postcondition"]["criteria"]}
    observed = record["observation_after"]["revision_after"]
    print("==", path.relative_to(repo).as_posix())
    print("  object.revision_after == observation_after.revision_after:", record["object"]["revision_after"] == observed)
    for index, check in enumerate(record["checks"]):
        text = (repo / check["result_ref"]).read_text(encoding="utf-8", errors="replace")
        exits = [line for line in text.splitlines() if line.startswith("exit=")]
        print(f"  checks[{index}] {check['criterion_id']}: command==criterion:", check["command"] == criteria[check["criterion_id"]],
              "| revision_checked==observed:", check["revision_checked"] == observed,
              "| exit lines:", exits, "| exit_code:", check["exit_code"])
    receipt = (repo / record["execution"]["receipt_ref"]).read_text(encoding="utf-8-sig")
    try:
        json.loads(receipt)
        is_json = True
    except ValueError:
        is_json = False
    print("  receipt: json:", is_json, "| contains decision:", record["execution"]["decision"] in receipt,
          "| contains model_served:", record["execution"]["actor"]["model_served"] in receipt,
          "| contains each input sha256:", [entry["sha256"] in receipt for entry in record["execution"]["inputs"]])
