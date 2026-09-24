# Run 007 — what the execution-record validator binds, and what it does not

Status: `evidence-only run / research-only` (no transition; like run 003). Initial
state: published tip `26535dc`, clean, full suite `1004 passed, 2 skipped` at
`ebe0ba0`. Input: the review of `26535dc` received on 2026-09-24, which reported
that a record passes `validate_execution_record.py` while its stored results
contradict it, and asked that the next bounded step bind the record to the
call, the checked revision, the criterion, the actual exit and the stored result.

## 1. What was probed and how

`probe_record_binding.py` (driver-written, outside the code tree, no model
calls) copies every file the shipped example record references into a scratch
base, then validates five mutated copies of the example against that base with
revisions resolved in this repository. Each gap case keeps the record
schema-valid and self-consistent while the stored result contradicts it.
Output at `26535dc`: `probe_output_26535dc.txt`.

| case | mutation | validator at `26535dc` |
|---|---|---|
| control | `checks[0].result_ref` names a missing file | REFUSED (`reference not found`) |
| gap 1 | stored result says `exit=1` / `1 failed`; record says `pass`, `exit_code 0` | **OK** |
| gap 2 | `checks[0].revision_checked` = `e65b9af4` (exists; not the re-observed revision) | **OK** |
| gap 3 | `checks[0].command` differs from the criterion's `check_command` | **OK** |
| gap 4 | `receipt_ref` names a stray text file; `provenance_established: true` | **OK** |

Cause, from the validator's source (`reference/python/cap/execution_record.py`
at `8d23161`): it resolves references, re-derives input hashes, resolves
revisions and checks criterion coverage; it never opens a stored result and
never compares a claim of the record with the content of a stored file. The
review's table is reproduced exactly.

With `--expect-closed` the same script is the oracle of the binding step: it
exits 1 today (four gap cases accepted) and will exit 0 only when every case
is refused. It is red on the baseline for the named reason.

## 2. Readiness of the existing records for the prepared rules

`probe_existing_records.py` → `readiness_26535dc.txt`. Every check in the
records of runs 002, 004, 005a, 005b and 006 already has `command` equal to its
criterion's `check_command`, `revision_checked` equal to the re-observed
revision, and a stored result with one `exit=` line equal to `exit_code`; every
receipt is JSON that mentions the decision and the served model. Two findings:

- **run 005a, `execution.inputs[0]`** hashes the stored `coding_packet.json`
  (LF, 8,271 bytes, `9b0f0bd6...`); the router hashed the packet it was given,
  `tasks5a.json` with CRLF line endings (8,296 bytes, `08111685...`, the
  receipt's `inputs.packet.sha256`). Same text, different bytes. The stored copy
  was normalised on copy and would be normalised by `.gitattributes`
  (`* text=auto eol=lf`) on staging anyway. The record is internally consistent
  and is not bound to the bytes the executor consumed; rule 4 below refuses it,
  which is the intended behaviour. Recorded as correction_003 in that run's
  README; the record is left as written.
- the shipped example's stand-in result file has no `exit=` line and its
  stand-in receipt does not mention the hashed input; both are updated by the
  binding step (the packet says exactly how).

## 3. Corrections made alongside (records only, no code)

- `execution.tool` in the records of runs 005a, 005b and 006 said "one native
  Workflow with one nomcp-haiku relay per stage" (the template of runs 002 and
  004, where it was true). Those three coding routes ran detached through the
  shim after the relay ceiling of run 005a; only their verdict stage was
  relayed. Corrected in place; originals in `1db22cf` (005a, 005b) and
  `9942901` (006).
- `costs.measured` in every record holds the closing attempt only. The whole
  route (every attempt, the router's baseline and checks, the verifier) is the
  figure to compare transitions on; `../route_costs_correction_001.json`
  (from `route_costs_from_receipts.py`, verbatim receipts) lists it per run.
  Run 006: 40 turns, 20,703 output tokens, 117.17 s of router wall, verifier
  37.4 s, against the recorded 31 / 16,842 / 92.72. The record schema has no
  place for route totals; adding one is a separate bounded step.

## 4. What this run does not say

Nothing about whether Adjustment chooses a cheaper transition. It says that
"the record passed the validator" meant, until now, "its references, hashes,
revisions and coverage resolve", not "its stored results support it". The
binding step is prepared under `../prepared/record_binding/` (packet, oracle =
this run's probe with `--expect-closed`, declared checks) and not executed.

## 5. Costs of this run

Driver only: two probe scripts, one route-cost script, corrections; no model
calls; about 25 minutes of wall time. Money: none.
