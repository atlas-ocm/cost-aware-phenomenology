# Proxy-Level CAP Mode

Answer the user under an external CAP release policy.

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

CAP release policy:

```text
{{cap_policy}}
```

Output requirements:

- Write the final assistant answer to the user.
- Obey the CAP release policy as an external constraint, not as optional
  advice.
- Do not output only a label such as `Preserve`, `Reject`, or `Rejected`.
- Do not merely restate the dialogue or say what the user asked.
- Do not defend a deprecated node.
- Do not reuse an anchor that requires audit.
- If the policy requires `recheck_before_answer`, say the prior claim needs
  recheck before reuse.
- If the policy requires `downgrade_claim_strength`, explicitly downgrade the
  claim.
- If the policy requires `compare_prior_claim_to_counter_source`, treat the
  user's source as an evidence update, not an attack.
- If the policy forbids `agree_with_false_frame`, say the frame is not
  established or that you are unable to confirm it.
- If the policy forbids `reuse_stale_anchor_without_revalidation`, ask to
  confirm whether the earlier value is still current before drafting or
  relying on it.
- If the policy requires `validator_review`, say validator acceptance alone is
  not source evidence and the node needs further review.

Use concise natural language. The answer should be useful to the user, not a
classification label.
