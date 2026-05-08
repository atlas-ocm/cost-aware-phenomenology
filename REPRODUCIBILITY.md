# Reproducibility

This document explains how to reproduce the validation results presented in this repository.

## Install

```bash
cd reference/python
pip install -r requirements.txt
```

## One-command check on Windows

From the `CAP/` directory:

```powershell
.\scripts\check_repo.ps1 -Install
.\scripts\check_repo.ps1
```

The script checks dependency imports, compiles the reference Python package,
runs unit tests, validates artifact integrity, runs the deterministic LLM proxy
policy pack, prints the proxy policy demo, and runs the LLM dialogue benchmark
scaffold. It also runs the CAP Lite middleware demo, a hard-holdout rewrite
shaper smoke pass, and renders the optional model-graded auditor prompt pack.
None of these steps call an LLM unless you explicitly run the live output
generator.

## Run unit tests

The test suite verifies the validator, schemas, operator alphabet, CAP Lite
middleware, benchmark scorer, adjudication tooling, model-graded auditor
scaffold, deterministic proxy release gate, and deterministic rewrite shaper:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q -p no:cacheprovider reference/python/tests
```

Expected output: all tests pass (currently 47 tests across 12 test files).

## Run CAP Lite middleware demo

This demo does not call an LLM and does not require LM Studio:

```bash
python reference/python/cap_lite.py
```

It builds a policy instruction from messages, optional retrieval context, and
optional prior telemetry.

## Run LLM proxy policy demo

This demo does not call an LLM and does not require LM Studio:

```bash
python reference/python/scripts/demo_llm_proxy_policy.py --counter-source
```

It parses telemetry such as:

```text
@R[N:R:RF:TC4.1:RCL:E0.7:CSH:VA]
```

and produces a response policy that deprecates the prior node, forbids
defending the previous claim, and requires recheck / downgrade / validator
review.

## Run LLM proxy policy pack

```bash
python reference/python/scripts/run_proxy_policy_pack.py --print-md
```

Expected output: `Passed: 8`, `Failed: 0`.

## Run LLM dialogue benchmark scaffold

This benchmark runner does not call an LLM. It scores already-produced outputs.
The default input is a synthetic smoke fixture used to verify the scorer and
report shape:

```bash
python reference/python/scripts/run_llm_dialogue_benchmark.py --print-md
```

Expected report properties:

```text
Status: synthetic_fixture_smoke_test
Cases: 5
Modes: prompt_only, rag_only, validator_only, prompt_level_cap, proxy_level_cap
```

To score real LLM outputs later, pass another outputs file:

```bash
python reference/python/scripts/run_llm_dialogue_benchmark.py --outputs-json path/to/model_outputs.json
```

## Generate live LLM benchmark outputs

This command calls an OpenAI-compatible LLM endpoint. For LM Studio, make sure
the target model is already loaded:

```bash
python reference/python/scripts/generate_llm_dialogue_outputs.py \
  --base-url http://127.0.0.1:1234/v1 \
  --models comet_12b_v.7-i1 \
  --output-json validation_artifacts/llm_dialogue_benchmark/model_outputs/comet_outputs.json
```

Dry-run without LLM calls:

```bash
python reference/python/scripts/generate_llm_dialogue_outputs.py --dry-run
```

The live generator loops by model first, then prompt mode, then case.

## Prepare blinded adjudication pack

This command does not call an LLM. It builds a blinded review package from
already-produced outputs:

```bash
python reference/python/scripts/prepare_llm_dialogue_adjudication.py \
  --outputs-json validation_artifacts/llm_dialogue_benchmark/model_outputs/comet_silicon_outputs.json \
  --output-dir validation_artifacts/llm_dialogue_benchmark/adjudication \
  --seed 20260505
```

## Prepare optional model-graded auditor prompts

This command does not call an LLM. It builds prompt records that can later be
sent to a separate judge model or reviewed manually:

```bash
python reference/python/scripts/prepare_model_graded_auditor.py \
  --outputs-json validation_artifacts/llm_dialogue_benchmark/model_outputs/comet_silicon_outputs.json \
  --output-dir validation_artifacts/llm_dialogue_benchmark/model_graded_auditor
```

The judge layer is auxiliary. It should be reported alongside the judge model,
prompt, disagreements, and manual adjudication status.

## Analyze adjudication disagreements

After filling a manual labels file, compare it against the lexical scorer:

```bash
python reference/python/scripts/analyze_adjudication_disagreements.py \
  --adjudication-dir validation_artifacts/llm_dialogue_benchmark/adjudication_four_model \
  --output-md validation_artifacts/llm_dialogue_benchmark/adjudication_four_model/disagreement_summary.md \
  --output-json validation_artifacts/llm_dialogue_benchmark/adjudication_four_model/disagreement_summary.json
```

With the unfilled template, the expected status is `pending_manual_labels`.

## Run deterministic post-gate rewrite shaper

This command does not call an LLM. It rewrites already-produced hard-holdout
outputs that are not release-ready into deterministic case-contract release
candidates:

```bash
python reference/python/scripts/run_proxy_rewrite_shaper.py \
  --case-dir validation_artifacts/llm_dialogue_benchmark/hard_holdout/cases \
  --outputs-json validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/qwen35_9b_no_thinking_hard_holdout_outputs.json \
  --output-json validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/qwen35_9b_no_thinking_shaped_v02_outputs.json \
  --summary-md validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/qwen35_9b_no_thinking_shaped_v02_summary.md \
  --summary-json validation_artifacts/llm_dialogue_benchmark/hard_holdout/model_outputs/qwen35_9b_no_thinking_shaped_v02_summary.json
```

The shaped outputs should then be checked with `run_proxy_release_gate.py
--gate-version v0.2`. These shaped outputs are pipeline-boundary artifacts, not
raw model outputs or benchmark wins.

## Validate one COM-Log document

```bash
python reference/python/scripts/validate_com_log.py path/to/com_log.json
```

Returns 0 if valid; nonzero with errors if not.

## Validate validation_artifacts integrity

```bash
python reference/python/scripts/validate_artifacts.py
```

Checks that:
- Every case in `validation_artifacts/*/cases/` has a corresponding model_run for each of the 3 expected models (`comet_12b_v.7-i1`, `silicon-maid-7b-imatrix`, `fimbulvetr-11b-v2`).
- Every model_run contains a valid `llm_reading` block with `overall_verdict` and `primary_reading`.
- All case IDs match between case files and model_run files.

Expected output: `Total issues: 0`

## Inspect model_run outputs

Each model_run JSON in `validation_artifacts/*/model_runs*/` contains:

- `case_payload`: the exact case presented to the model
- `llm_reading`: the model's structured JSON response (parsed and normalized)
- `raw_response`: the model's raw response text
- `model_identity`: requested and verified model ID

You can inspect any file directly to see what each model said for each case.

## Check comparison reports

Pre-computed comparison reports are in each `validation_artifacts/` subfolder:

- `validation_artifacts/com_grammar/comparison_report.md` / `.json`
- `validation_artifacts/adjustment_layer/comparison_report_main.md` / `.json`
- `validation_artifacts/adjustment_layer/comparison_report_holdout.md` / `.json`
- `validation_artifacts/llm_dialogue_proxy/comparison_report.md` / `.json`
- `validation_artifacts/llm_dialogue_benchmark/scaffold_report.md` / `.json`

These are generated from the actual model_run files in this repository, not from an external source.

## Reproduce LLM validation runs

To re-run validation from scratch, you would need:

1. An OpenAI-compatible API server (e.g. LM Studio) with the three models loaded.
2. The validation runner scripts (planned for v0.3 release).
3. Identity-verification that confirms the response `model` field matches the requested model ID.

The case prompts are embedded in each `case_payload` field in the model_run JSONs, so the inputs are fully inspectable.

## Known limitations

- The Python reference validator only validates COM-Log *document structure*. It does not run an LLM or produce a COM-Log from raw input text — that requires the parser layer (planned for v0.3).
- Validation is **structured-output consistency validation**, not empirical proof of real-world outcomes.
- The three models are local LM Studio models; results may not transfer to other providers without re-running.
- `validate_artifacts.py` checks structural integrity, not semantic correctness of individual responses.
- Deterministic shaped outputs are not raw model outputs and must not be
  reported as model scores.
