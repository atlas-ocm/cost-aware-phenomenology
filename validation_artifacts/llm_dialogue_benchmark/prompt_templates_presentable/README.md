# Presentable Prompt Templates

**Note:** These are presentation/demo templates, not frozen benchmark templates. 

These templates extend the baseline CAP benchmark prompts with explicit,
professional Markdown formatting instructions (e.g., `## Assessment`,
`## CAP Release Decision`, `## Final Response`). They are designed to elicit
clean, structured, and sponsor-ready demonstrations from capable LLMs, including
local Qwen and Mistral runs as well as external Gemini-style controls.

Because they introduce structural requirements, they alter the benchmark task surface. Do not use these templates for strict baseline comparatives or `release_gate v0.2` evaluations where internal-jargon leakage and formatting strictness are measured against the minimalist prompts in `prompt_templates/` or `prompt_templates_hardened_v2/`.

See [`walkthrough.md`](./walkthrough.md) for the dry-run command, live demo
command shape, and reporting rules.
