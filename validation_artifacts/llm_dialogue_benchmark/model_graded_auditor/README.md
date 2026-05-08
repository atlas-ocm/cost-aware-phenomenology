# Model-Graded Auditor Prompt Pack

Status: optional auxiliary audit artifact.

This folder contains prompts that can be given to a separate judge model or human reviewer.
The judge is not treated as ground truth and does not replace blinded manual adjudication.

Source outputs:

```text
validation_artifacts\llm_dialogue_benchmark\model_outputs\comet_silicon_outputs.json
```

Records: `50`

Files:

- `judge_prompt_pack.json` - machine-readable prompt pack
- `judge_prompt_pack.md` - readable prompt pack
- `judge_response_template.json` - response template keyed by `record_id`

Recommended use:

1. Freeze the lexical scorer and case pack.
2. Run a judge model over `judge_prompt_pack.json` or review manually.
3. Store responses in the template shape.
4. Compare judge labels with lexical scores and manual adjudication.

Do not cite the judge score as a benchmark result without reporting the judge model, prompt, disagreements, and manual review status.
