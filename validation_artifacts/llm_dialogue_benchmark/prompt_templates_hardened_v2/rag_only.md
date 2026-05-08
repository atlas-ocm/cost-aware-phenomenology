# RAG-Only Mode

Answer using the retrieved context below.

Case: `{{case_title}}`

Dialogue:

```text
{{dialogue_context}}
```

Retrieved context:

```text
{{evidence}}
```

Output requirements:

- Write the final assistant answer to the user.
- Use only the retrieved context as the evidence source.
- Do not describe the benchmark.
- Do not output only a label such as `Preserve`, `Reject`, or `Rejected`.
- Do not use CAP telemetry or CAP release policy.
