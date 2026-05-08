#!/usr/bin/env python3
"""Run one CAP LLM proxy policy demonstration."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cap.proxy_policy import build_policy, parse_compact_telemetry


DEFAULT_TELEMETRY = "@R[N:R:RF:TC4.1:RCL:E0.7:CSH:VA]"


def render_markdown(payload: dict) -> str:
    telemetry = payload["telemetry"]
    policy = payload["policy"]
    lines = [
        "# CAP LLM Proxy Policy Demo",
        "",
        "Input telemetry:",
        "",
        "```text",
        telemetry["raw"],
        "```",
        "",
        "Parsed telemetry:",
        "",
        "```text",
        f"RC = {telemetry['retrieval_confidence']}",
        f"E  = {telemetry['entropy']}",
        f"CS = {telemetry['claim_strength']}",
        f"TC = {telemetry['transition_cost']}",
        f"V  = {telemetry['validator_action']}",
        "```",
        "",
        "Policy:",
        "",
        "```text",
        f"node_status = {policy['node_status']}",
        f"allowed_as_anchor = {policy['allowed_as_anchor']}",
        f"release_action = {policy['release_action']}",
        f"forbid = {', '.join(policy['forbid']) or 'none'}",
        f"require = {', '.join(policy['require']) or 'none'}",
        "```",
        "",
        "Reasons:",
        "",
    ]
    for reason in policy["reasons"]:
        lines.append(f"- {reason}")
    if not policy["reasons"]:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Demonstrate CAP telemetry -> response policy for LLM dialogue."
    )
    parser.add_argument("--telemetry", default=DEFAULT_TELEMETRY)
    parser.add_argument("--counter-source", action="store_true")
    parser.add_argument("--source-validity", default="unknown")
    parser.add_argument("--false-user-frame", action="store_true")
    parser.add_argument("--stale-anchor", action="store_true")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of markdown.")
    args = parser.parse_args()

    telemetry = parse_compact_telemetry(args.telemetry)
    policy = build_policy(
        telemetry,
        user_counter_source=args.counter_source,
        source_validity=args.source_validity,
        false_user_frame=args.false_user_frame,
        stale_anchor=args.stale_anchor,
    )
    payload = {
        "telemetry": telemetry.__dict__,
        "user_counter_source": args.counter_source,
        "source_validity": args.source_validity,
        "false_user_frame": args.false_user_frame,
        "stale_anchor": args.stale_anchor,
        "policy": policy.to_dict(),
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
