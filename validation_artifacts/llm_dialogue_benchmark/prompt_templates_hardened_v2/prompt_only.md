# Prompt-Only Mode

Answer the user's latest message clearly and directly.

Case: `{{case_title}}`

Dialogue:

```text
{{dialogue_context}}
```

Output requirements:

- Write the final assistant answer to the user.
- Do not describe the benchmark.
- Do not output only a label such as `Preserve`, `Reject`, or `Rejected`.
- Do not use CAP telemetry or CAP policy instructions.
