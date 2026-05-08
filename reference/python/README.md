# CAP Reference Python Implementation

Minimal Python reference for validating CAP outputs. This is **not** a production engine — it is a reference validator that verifies a COM-Log document conforms to the published schemas.

## Install

```bash
pip install -r requirements.txt
```

## Quick start

Validate a single COM-Log file:

```bash
python scripts/validate_com_log.py path/to/com_log.json
```

Run a folder of cases:

```bash
python scripts/run_case_pack.py path/to/cases/
```

Run the LLM proxy policy demo:

```bash
python scripts/demo_llm_proxy_policy.py --counter-source
python scripts/demo_llm_proxy_policy.py --false-user-frame
python scripts/demo_llm_proxy_policy.py --stale-anchor
```

Run the copyable CAP Lite middleware demo:

```bash
python cap_lite.py
```

Run the deterministic LLM proxy policy pack:

```bash
python scripts/run_proxy_policy_pack.py --print-md
```

Run the LLM dialogue benchmark scaffold:

```bash
python scripts/run_llm_dialogue_benchmark.py --print-md
```

Run the hard-holdout scaffold:

```bash
python scripts/run_llm_dialogue_benchmark.py \
  --case-dir ../../validation_artifacts/llm_dialogue_benchmark/hard_holdout/cases \
  --outputs-json ../../validation_artifacts/llm_dialogue_benchmark/hard_holdout/fixture_outputs/smoke_outputs.json \
  --print-md
```

Run the deterministic proxy release gate over already-produced outputs:

```bash
python scripts/run_proxy_release_gate.py \
  --case-dir ../../validation_artifacts/llm_dialogue_benchmark/hard_holdout/cases \
  --outputs-json ../../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/qwen35_9b_no_thinking_hard_holdout_outputs.json \
  --print-md
```

Run the preregistered v0.2 gate explicitly:

```bash
python scripts/run_proxy_release_gate.py \
  --gate-version v0.2 \
  --case-dir ../../validation_artifacts/llm_dialogue_benchmark/hard_holdout/cases \
  --outputs-json ../../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/qwen35_9b_no_thinking_hard_holdout_outputs.json \
  --print-md
```

Compare v0.1 and v0.2 gate JSON reports:

```bash
python scripts/compare_proxy_release_gate_reports.py \
  --pair ../../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/qwen35_9b_no_thinking_proxy_release_gate.json ../../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/qwen35_9b_no_thinking_proxy_release_gate_v02.json \
  --print-md
```

Run the deterministic post-gate rewrite shaper over already-produced outputs:

```bash
python scripts/run_proxy_rewrite_shaper.py \
  --case-dir ../../validation_artifacts/llm_dialogue_benchmark/hard_holdout/cases \
  --outputs-json ../../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/qwen35_9b_no_thinking_hard_holdout_outputs.json \
  --output-json ../../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/qwen35_9b_no_thinking_shaped_v02_outputs.json \
  --summary-md ../../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/qwen35_9b_no_thinking_shaped_v02_summary.md
```

Render live-benchmark prompts without calling an LLM:

```bash
python scripts/generate_llm_dialogue_outputs.py --dry-run
```

Prepare a blinded adjudication pack:

```bash
python scripts/prepare_llm_dialogue_adjudication.py
```

Export manual labels to a spreadsheet-friendly TSV:

```bash
python scripts/adjudication_labels_tsv.py export
```

Import filled TSV labels back to JSON:

```bash
python scripts/adjudication_labels_tsv.py import
```

Prepare optional model-graded auditor prompts without calling an LLM:

```bash
python scripts/prepare_model_graded_auditor.py --print-summary
```

Analyze lexical/manual adjudication disagreements after manual labels are
filled:

```bash
python scripts/analyze_adjudication_disagreements.py --print-md
python scripts/analyze_adjudication_disagreements.py --labels-tsv ../../validation_artifacts/llm_dialogue_benchmark/adjudication_four_model/manual_labels_template.tsv --print-md
```

Prepare a compact blinded adjudication pack for proxy release-gate boundary
actions (`release` and `block`):

```bash
python scripts/prepare_release_gate_adjudication.py \
  --outputs-json ../../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/qwen35_9b_no_thinking_hard_holdout_outputs.json \
  --outputs-json ../../validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/mistral_nemo_hard_holdout_outputs.json \
  --output-dir ../../validation_artifacts/llm_dialogue_benchmark/hard_holdout/release_gate_adjudication_boundary
```

Analyze proxy release-gate/manual action disagreements after manual actions are
filled:

```bash
python scripts/analyze_release_gate_adjudication.py \
  --adjudication-dir ../../validation_artifacts/llm_dialogue_benchmark/hard_holdout/release_gate_adjudication_boundary \
  --labels-tsv ../../validation_artifacts/llm_dialogue_benchmark/hard_holdout/release_gate_adjudication_boundary/manual_labels_template.tsv \
  --print-md
```

## Run tests

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q -p no:cacheprovider tests/
```

## What it does

- Loads JSON Schemas from `spec/` (com_log_schema.json, operator_alphabet.json)
- Validates the document against the schema (jsonschema)
- Performs CAP-specific consistency checks beyond JSON Schema:
  - Operator name must be in the 13-operator alphabet
  - `risk_weight_percent` should fall within the operator's typical range
  - `telemetry_state=Breach` requires `budget_gate=Recovery-Only`
- Demonstrates dependency-free LLM proxy policy checks:
  - low retrieval confidence + high claim strength deprecates the prior node
  - counter-sources trigger audit instead of self-defense
  - validator rewrite/fallback prevents reuse of the original node as an anchor
  - false user framing cannot force agreement
  - stale cross-turn anchors require revalidation
- Scores already-produced LLM dialogue benchmark outputs for:
  - self-justification
  - sycophancy
  - weak RAG overclaiming
  - stale anchor reuse
  - validator overtrust
- Prepares optional model-graded auditor prompt packs for already-produced
  benchmark outputs. The judge is auxiliary, not ground truth.
- Compares lexical scorer labels against manual adjudication labels once the
  labels template is filled.
- Prepares and analyzes blinded manual adjudication packs for deterministic
  proxy release-gate actions (`release`, `rewrite_required`, `block`).
- Runs explicit v0.1/v0.2 deterministic proxy release-gate variants and
  compares their action changes without overwriting prior reports.
- Runs a deterministic post-gate rewrite shaper for hard-holdout cases. The
  shaped outputs are release-candidate artifacts, not raw model outputs.
- Provides a copyable CAP Lite middleware:
  - builds a system policy from messages, retrieval context, and prior telemetry
  - flags self-justification, sycophancy, weak evidence, and overload risks
  - returns a telemetry stub for downstream logging

## What it does not do

- Does not run any LLM
- Does not produce a COM-Log from input text (parsing is a separate component)
- Does not assess whether the recommendation is "correct" — only whether it is well-formed

The validator answers a narrow question: *is this document a valid CAP output?* Whether the CAP analysis itself is correct is a separate empirical question (see [`03_validation/`](../../03_validation/)).

The LLM proxy demo answers a different narrow question: *what policy follows
from this telemetry tag?* It is deterministic and does not benchmark model
behavior.

The LLM dialogue benchmark runner answers another narrow question: *do these
already-produced outputs exhibit the target failure signals or required success
signals?* It does not call an LLM by itself.

`cap_lite.py` answers an integration question: *what lightweight policy should
be injected before the next LLM call?* It does not call an LLM.

`generate_llm_dialogue_outputs.py` is the live LLM-in-the-loop generator. It
targets an OpenAI-compatible API and writes model outputs that
`run_llm_dialogue_benchmark.py` can score. Use `--resume`,
`--delay-seconds`, `--retries`, and `--retry-delay-seconds` for rate-limited
or unstable API endpoints.

`prepare_llm_dialogue_adjudication.py` builds a blinded manual review pack from
already-produced outputs. It does not call an LLM.

`adjudication_labels_tsv.py` converts manual labels between JSON and a
spreadsheet-friendly TSV sheet. It does not unblind model or prompt-mode ids.

`prepare_model_graded_auditor.py` builds prompt packs for a separate judge model
or reviewer from already-produced outputs. It does not call an LLM and should
not be treated as replacing manual adjudication.

`analyze_adjudication_disagreements.py` compares lexical scores against manual
labels from JSON or TSV. If labels are still empty, it reports
`pending_manual_labels`.

`prepare_release_gate_adjudication.py` builds a blinded manual review pack for
the deterministic proxy release gate. It is useful for reviewing boundary
actions without relabeling every rewrite case.

`analyze_release_gate_adjudication.py` compares gate actions against manual
actions from JSON or TSV. If labels are still empty, it reports
`pending_manual_labels`.

`compare_proxy_release_gate_reports.py` compares already-produced gate report
JSON files. It does not call an LLM and is intended for v0.1/v0.2 release-gate
diffs.

`run_proxy_rewrite_shaper.py` rewrites hard-holdout outputs that fail the
release gate into deterministic case-contract release candidates, then records
whether the shaped text passes the gate. It does not call an LLM and should not
be reported as model performance.
