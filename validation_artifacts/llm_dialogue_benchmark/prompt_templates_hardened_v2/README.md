# Hardened Prompt Templates v2

Status: post-hoc prompt hardening lane.

These templates were created after the `mistral-nemo-instruct-2407` transfer
probe exposed weak instruction transfer in the original prompt templates.

They are not a replacement for the original v1 templates in
[`../prompt_templates/`](../prompt_templates/). The v1 templates remain the
baseline used by the first live reports.

The purpose of v2 is narrower:

- make every mode request a final assistant answer, not a meta-label;
- prevent one-word outputs such as `Rejected`;
- make proxy-level CAP policy operational rather than decorative;
- test whether the Mistral failures are prompt-transfer failures or deeper
  policy-following failures.

Because v2 was created after inspecting failures, v2 results should be reported
as a prompt-hardening experiment, not as a frozen benchmark result.

Placeholders:

```text
{{case_title}}
{{dialogue_context}}
{{evidence}}
{{telemetry_tag}}
{{cap_policy}}
```
