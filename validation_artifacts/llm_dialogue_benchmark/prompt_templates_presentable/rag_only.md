# RAG-Only Mode

Answer using the retrieved context below. Ensure your output is structured professionally.

Case: `{{case_title}}`

Dialogue:

```text
{{dialogue_context}}
```

Retrieved context:

```text
{{evidence}}
```

Format your output strictly as follows:

## Assessment
(Briefly evaluate the retrieved evidence against the user's request)

## Response
(Your answer derived purely from the retrieved context)

Do not use CAP telemetry or release policy.
