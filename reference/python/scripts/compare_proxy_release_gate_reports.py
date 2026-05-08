#!/usr/bin/env python3
"""Compare deterministic CAP proxy release-gate report JSON files."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

ROOT = Path(__file__).resolve().parents[3]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compare_report_pair(before_path: Path, after_path: Path) -> dict[str, Any]:
    before = load_json(before_path)
    after = load_json(after_path)
    before_modes = {_mode_key(mode): mode for mode in before.get("modes", [])}
    after_modes = {_mode_key(mode): mode for mode in after.get("modes", [])}
    mode_keys = sorted(set(before_modes) | set(after_modes))

    mode_comparisons = []
    for key in mode_keys:
        before_mode = before_modes.get(key)
        after_mode = after_modes.get(key)
        if before_mode is None or after_mode is None:
            mode_comparisons.append({
                "mode": key,
                "status": "missing_mode",
                "before_counts": _empty_counts(),
                "after_counts": _empty_counts(),
                "changed_cases": [],
            })
            continue

        changed_cases = _compare_case_actions(before_mode, after_mode)
        mode_comparisons.append({
            "mode": before_mode["mode"],
            "model": before_mode.get("model"),
            "prompt_mode": before_mode.get("prompt_mode"),
            "status": "compared",
            "before_counts": before_mode["action_counts"],
            "after_counts": after_mode["action_counts"],
            "changed_cases": changed_cases,
        })

    return {
        "before_json": _relative(before_path),
        "after_json": _relative(after_path),
        "before_gate_version": before.get("gate_version", "v0.1"),
        "after_gate_version": after.get("gate_version", "unknown"),
        "mode_comparisons": mode_comparisons,
        "changed_case_count": sum(
            len(mode["changed_cases"])
            for mode in mode_comparisons
        ),
    }


def compare_report_pairs(pairs: list[tuple[Path, Path]]) -> dict[str, Any]:
    comparisons = [
        compare_report_pair(before_path.resolve(), after_path.resolve())
        for before_path, after_path in pairs
    ]
    return {
        "kind": "cap_proxy_release_gate_report_comparison",
        "status": "compared",
        "comparisons": comparisons,
        "changed_case_count": sum(
            comparison["changed_case_count"]
            for comparison in comparisons
        ),
    }


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Proxy Release Gate v0.1 / v0.2 Comparison",
        "",
        f"Status: `{summary['status']}`",
        "",
        "This report compares already-produced deterministic release-gate JSON",
        "files. It does not call an LLM and does not overwrite v0.1 reports.",
        "",
        f"Changed case actions: `{summary['changed_case_count']}`",
        "",
    ]

    for comparison in summary["comparisons"]:
        lines.extend([
            f"## {comparison['before_json']} -> {comparison['after_json']}",
            "",
            f"Before gate version: `{comparison['before_gate_version']}`",
            f"After gate version: `{comparison['after_gate_version']}`",
            "",
            "| Mode | v0.1 release | v0.1 rewrite | v0.1 block | v0.2 release | v0.2 rewrite | v0.2 block | Changed cases |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ])

        for mode in comparison["mode_comparisons"]:
            before = mode["before_counts"]
            after = mode["after_counts"]
            lines.append(
                f"| `{mode['mode']}` | "
                f"{before.get('release', 0)} | {before.get('rewrite_required', 0)} | {before.get('block', 0)} | "
                f"{after.get('release', 0)} | {after.get('rewrite_required', 0)} | {after.get('block', 0)} | "
                f"{len(mode['changed_cases'])} |"
            )

        changed_modes = [
            mode
            for mode in comparison["mode_comparisons"]
            if mode["changed_cases"]
        ]
        if changed_modes:
            lines.extend(["", "### Changed Case Actions", ""])
            for mode in changed_modes:
                lines.extend([
                    f"#### {mode['mode']}",
                    "",
                    "| Case | v0.1 action | v0.2 action | v0.2 reasons |",
                    "|---|---|---|---|",
                ])
                for case in mode["changed_cases"]:
                    lines.append(
                        f"| `{case['case_id']}` | `{case['before_action']}` | "
                        f"`{case['after_action']}` | {', '.join(case['after_reasons']) or 'none'} |"
                    )
                lines.append("")
        else:
            lines.extend(["", "No case-level action changes.", ""])

    return "\n".join(lines).rstrip() + "\n"


def _compare_case_actions(
    before_mode: dict[str, Any],
    after_mode: dict[str, Any],
) -> list[dict[str, Any]]:
    before_cases = {
        result["case_id"]: result
        for result in before_mode.get("case_results", [])
    }
    after_cases = {
        result["case_id"]: result
        for result in after_mode.get("case_results", [])
    }
    changed_cases = []
    for case_id in sorted(set(before_cases) | set(after_cases)):
        before_result = before_cases.get(case_id, {})
        after_result = after_cases.get(case_id, {})
        before_action = before_result.get("release_action", "missing")
        after_action = after_result.get("release_action", "missing")
        if before_action != after_action:
            changed_cases.append({
                "case_id": case_id,
                "before_action": before_action,
                "after_action": after_action,
                "after_reasons": after_result.get("reasons", []),
            })
    return changed_cases


def _mode_key(mode: dict[str, Any]) -> str:
    model = mode.get("model")
    prompt_mode = mode.get("prompt_mode")
    if model and prompt_mode:
        return f"{model} / {prompt_mode}"
    return mode["mode"]


def _empty_counts() -> dict[str, int]:
    return {"release": 0, "rewrite_required": 0, "block": 0}


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare CAP proxy release-gate reports.")
    parser.add_argument(
        "--pair",
        action="append",
        nargs=2,
        metavar=("BEFORE_JSON", "AFTER_JSON"),
        required=True,
        help="A v0.1/v0.2 JSON report pair. Can be repeated.",
    )
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    parser.add_argument("--print-md", action="store_true")
    args = parser.parse_args()

    pairs = [(Path(before), Path(after)) for before, after in args.pair]
    summary = compare_report_pairs(pairs)

    if args.output_json:
        output = Path(args.output_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.output_md:
        output = Path(args.output_md)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_markdown(summary), encoding="utf-8")

    if args.print_md:
        print(render_markdown(summary))
    else:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
