# Presentable Template Walkthrough

Status: presentation/demo lane, not a frozen benchmark lane.

These templates are intended to produce readable Markdown demonstrations from
capable chat models. The first intended local targets are Qwen and Mistral; the
same lane can later be reused for Gemini or another external model. The
templates add visible sections such as `## Assessment`, `## CAP Release
Decision`, and `## Final Response`, so they intentionally change the task
surface. Do not compare their scores against runs produced with
`prompt_templates/` or `prompt_templates_hardened_v2/`.

## Files

- `prompt_only.md` - clean direct-answer baseline.
- `rag_only.md` - retrieved evidence plus answer.
- `validator_only.md` - validation check plus final answer.
- `prompt_level_cap.md` - visible CAP context audit.
- `proxy_level_cap.md` - visible external CAP release-policy decision.

## First Check: Dry Run

From the `CAP/` directory, render prompts without calling an LLM:

```powershell
python reference\python\scripts\generate_llm_dialogue_outputs.py `
  --dry-run `
  --template-dir validation_artifacts\llm_dialogue_benchmark\prompt_templates_presentable `
  --case-dir validation_artifacts\llm_dialogue_benchmark\hard_holdout\cases `
  --output-json $env:TEMP\cap_presentable_prompt_manifest.json
```

This confirms that all placeholders resolve and that the template directory is
compatible with the existing runner.

## Local Qwen Demo Run

This command calls the local OpenAI-compatible LM Studio endpoint. Load the
model before running the command and keep the output separate from baseline
score artifacts.

```powershell
python reference\python\scripts\generate_llm_dialogue_outputs.py `
  --base-url http://127.0.0.1:1234/v1 `
  --models atlas/qwen3.5-9b-no-thinking `
  --template-dir validation_artifacts\llm_dialogue_benchmark\prompt_templates_presentable `
  --case-dir validation_artifacts\llm_dialogue_benchmark\hard_holdout\cases `
  --output-json validation_artifacts\llm_dialogue_benchmark\hard_holdout\model_outputs\qwen35_9b_presentable_demo_outputs.json `
  --temperature 0 `
  --max-tokens 32768 `
  --write-partial `
  --resume
```

## Local Mistral Demo Run

Run Mistral in a separate command so LM Studio does not need to switch models
back and forth inside a single process.

```powershell
python reference\python\scripts\generate_llm_dialogue_outputs.py `
  --base-url http://127.0.0.1:1234/v1 `
  --models mistral-nemo-instruct-2407 `
  --template-dir validation_artifacts\llm_dialogue_benchmark\prompt_templates_presentable `
  --case-dir validation_artifacts\llm_dialogue_benchmark\hard_holdout\cases `
  --output-json validation_artifacts\llm_dialogue_benchmark\hard_holdout\model_outputs\mistral_nemo_presentable_demo_outputs.json `
  --temperature 0 `
  --max-tokens 8192 `
  --write-partial `
  --resume
```

## External Provider Demo Run

For Gemini or another OpenAI-compatible external endpoint, verify the model id
via the provider's `/models` surface first, then set the API key in the
configured environment variable.

```powershell
$env:CAP_LLM_API_KEY = "<provider-api-key>"

python reference\python\scripts\generate_llm_dialogue_outputs.py `
  --base-url "<openai-compatible-base-url>" `
  --models "<available-model-id>" `
  --template-dir validation_artifacts\llm_dialogue_benchmark\prompt_templates_presentable `
  --case-dir validation_artifacts\llm_dialogue_benchmark\hard_holdout\cases `
  --output-json validation_artifacts\llm_dialogue_benchmark\hard_holdout\model_outputs\<provider>_presentable_demo_outputs.json `
  --temperature 0 `
  --max-tokens 8192 `
  --write-partial `
  --resume
```

If the provider is rate-limited, add a delay/retry policy:

```powershell
  --delay-seconds 13 `
  --retries 4 `
  --retry-delay-seconds 30
```

## Reporting Rule

Report outputs from this folder as:

```text
presentable demo outputs
```

Do not report them as:

```text
baseline benchmark outputs
frozen scorer results
release-gate validation results
```

The visible Markdown sections are useful for presentation, but they can also
trigger stricter shape checks in release-gate evaluations. Keep this lane
separate from benchmark and adjudication artifacts.
