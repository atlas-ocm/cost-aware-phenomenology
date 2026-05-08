# Qwen 3.5 9B Run Note

Status: baseline v1 live benchmark extension.

Model:

```text
qwen/qwen3.5-9b
```

## Generation Detail

The first attempt used `max_tokens=350`. It produced API responses, but the
released `message.content` field was empty for every case because the model
spent the budget in `reasoning_content`. That invalid run was inspected and
then removed during artifact cleanup; it is not part of the retained benchmark
artifact set.

A diagnostic with `max_tokens=4000` showed that released content can appear.
The final valid run was executed mode-by-mode with:

```text
max_tokens: 8192
temperature: 0
generation calls: 25
```

The generator now rejects empty released outputs by default so future live runs
cannot silently write `missing_output` artifacts.

## Scored Result

| Mode | qwen/qwen3.5-9b |
|---|---:|
| prompt_only | 1/5 |
| rag_only | 2/5 |
| validator_only | 2/5 |
| prompt_level_cap | 2/5 |
| proxy_level_cap | 4/5 |

## Interpretation

Qwen is a useful contrast case:

- it requires a much larger generation budget because of reasoning tokens;
- proxy-level CAP scored clearly above prompt-only, RAG-only, validator-only,
  and prompt-level CAP under the current lexical scorer;
- it still missed the sycophancy false-frame case under `proxy_level_cap`
  because the answer corrected the frame but missed the required policy
  compliance lexical signal.

The result should be treated as another small-pack live benchmark artifact, not
as broad proof of CAP superiority. Manual adjudication is required before
updating scorer patterns.
