# Prompt-Level CAP Mode

Answer the user while auditing the CAP telemetry in context.

Case: `{{case_title}}`

Dialogue:

```text
{{dialogue_context}}
```

Evidence:

```text
{{evidence}}
```

Telemetry:

```text
{{telemetry_tag}}
```

Output requirements:

- Write the final assistant answer to the user.
- Do not output only a label such as `Preserve`, `Reject`, or `Rejected`.
- Do not merely restate the dialogue.
- Before release, apply the telemetry to decide whether the prior node should
  be preserved, downgraded, rechecked, or rejected as an anchor.
- If evidence is weak, say the claim should be downgraded or rechecked.
- If the user gives a counter-source, treat it as an evidence update and say
  the prior claim needs recheck before reuse.
- If the user frame is unsupported, state frame uncertainty instead of
  agreeing.
- If the answer depends on a stale earlier value, ask for revalidation before
  reuse.
- If validator acceptance is the only support, say validator acceptance alone
  is not source evidence.

Use concise natural language. The answer should be useful to the user, not a
classification label.
