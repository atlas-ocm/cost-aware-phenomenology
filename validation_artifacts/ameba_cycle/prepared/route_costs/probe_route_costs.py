"""Oracle and probe for the whole-route costs step (driver-written, deterministic, no model calls).

usage: python probe_route_costs.py <repo_root> [--expect-closed]

Uses two committed records and their verbatim router receipts as they are in the tree: run 008 (one
attempt) and run 006 (a set-aside cheap attempt and a closing fallback attempt). Builds in memory
schema-version-0.2 copies of those records with a `costs.route` block derived from the receipts, plus
mutated copies whose route costs contradict the receipts, and validates each against the repository with
revisions resolved. Every case carries an expectation: ACCEPT (no problem at all) or REFUSE with a named
anchor that at least one problem string must contain. Observation mode (default) exits 0. With
--expect-closed the script exits 0 only when every expectation holds; on the code before the step the
0.2 positives are refused by the schema (schema_version is the const "0.1") and the cost contradictions
are accepted, so it is red on the baseline for the named reason.

What a green run means: the costs written in a record are the costs the router receipt recorded, for
every attempt of the route and for its total wall time; the closing attempt's figures never stand in
for the route. Nothing about money, driver time or relay tokens is bound by this.
"""
import copy
import json
import pathlib
import sys

repo = pathlib.Path(sys.argv[1]).resolve()
expect_closed = "--expect-closed" in sys.argv
sys.path.insert(0, str(repo / "reference" / "python"))
from cap.execution_record import validate_execution_record  # noqa: E402

RUN_008 = "validation_artifacts/ameba_cycle/run_008_record_binding"
RUN_006 = "validation_artifacts/ameba_cycle/run_006_com_log_link"


def load(rel):
    return json.loads((repo / rel).read_text(encoding="utf-8-sig"))


rec8, rcp8 = load(f"{RUN_008}/transition_execution_record.json"), load(f"{RUN_008}/nomcp_coding_receipt.json")
rec6, rcp6 = load(f"{RUN_006}/transition_execution_record.json"), load(f"{RUN_006}/nomcp_coding_receipt.json")


def route_from(receipt):
    """The route block exactly as the receipt records it: every attempt in order, then the totals."""
    attempts = [("cheap_coder", receipt["first_attempt"])]
    if receipt.get("fallback_used"):
        attempts.append(("fallback_coder", receipt["fallback_attempt"]))
    listed = [{"role": role, "model_served": a["model_served"], "turns": a["turns"],
               "output_tokens": a["output_tokens"], "wall_s": a["wall_s"]} for role, a in attempts]
    return {"attempts": listed,
            "turns_total": sum(a["turns"] for a in listed),
            "output_tokens_total": sum(a["output_tokens"] for a in listed),
            "router_wall_s": receipt["total_wall_s"]}


def upgraded(record, receipt):
    r = copy.deepcopy(record)
    r["schema_version"] = "0.2"
    r["costs"]["route"] = route_from(receipt)
    return r


ACCEPT = "ACCEPT"
cases = []


def case(label, record, expectation):
    cases.append((label, record, expectation))


case("positive_run_008_record_v0_1_unchanged", copy.deepcopy(rec8), ACCEPT)
case("positive_run_008_v0_2_route_from_receipt", upgraded(rec8, rcp8), ACCEPT)
case("positive_run_006_v0_2_two_attempts_from_receipt", upgraded(rec6, rcp6), ACCEPT)

r = copy.deepcopy(rec8)
r["schema_version"] = "0.2"
case("gap1_v0_2_record_without_route", r, ("REFUSE", "route"))

r = upgraded(rec8, rcp8)
r["costs"]["route"]["turns_total"] += 1
case("gap2_turns_total_off_by_one", r, ("REFUSE", "costs.route.turns_total"))

r = upgraded(rec8, rcp8)
r["costs"]["route"]["attempts"][0]["output_tokens"] -= 1
case("gap3_attempt_output_tokens_differ_from_receipt", r, ("REFUSE", "costs.route.attempts[0].output_tokens"))

r = upgraded(rec8, rcp8)
r["costs"]["route"]["router_wall_s"] = r["costs"]["route"]["attempts"][0]["wall_s"]  # the closing attempt standing in for the route
case("gap4_router_wall_replaced_by_closing_attempt", r, ("REFUSE", "costs.route.router_wall_s"))

r = upgraded(rec6, rcp6)
r["costs"]["route"]["attempts"] = r["costs"]["route"]["attempts"][1:]  # the set-aside cheap attempt dropped
r["costs"]["route"]["turns_total"] = r["costs"]["route"]["attempts"][0]["turns"]
r["costs"]["route"]["output_tokens_total"] = r["costs"]["route"]["attempts"][0]["output_tokens"]
case("gap5_set_aside_attempt_dropped_from_route", r, ("REFUSE", "costs.route.attempts"))

r = copy.deepcopy(rec8)
r["costs"]["measured"]["worker_turns"] += 1  # a v0.1 record whose closing-attempt figures are not the receipt's
case("gap6_measured_worker_turns_not_the_receipt_closing_attempt", r, ("REFUSE", "costs.measured.worker_turns"))

all_hold = True
for label, record, expectation in cases:
    problems = validate_execution_record(record, repo, repo)
    observed = "REFUSED" if problems else "OK"
    if expectation == ACCEPT:
        holds = not problems
        expected = "ACCEPT"
    else:
        anchor = expectation[1]
        holds = any(anchor in problem for problem in problems)
        expected = f"REFUSE[{anchor}]"
    all_hold = all_hold and holds
    print(f"case={label} observed={observed} expected={expected} holds={holds} problems={json.dumps(problems, ensure_ascii=True)}")

if expect_closed:
    print("probe_route_costs: " + ("every expectation holds" if all_hold else "at least one expectation fails"))
    sys.exit(0 if all_hold else 1)
print("probe_route_costs: observation mode, exit 0")
