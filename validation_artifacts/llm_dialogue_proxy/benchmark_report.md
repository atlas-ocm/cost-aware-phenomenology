# LLM Dialogue Proxy Policy Coverage Report

Status: deterministic benchmark-style report.

This is not a leaderboard and not a claim that CAP is globally better than
prompting, RAG, validators, fine-tuning, or RLHF. It is a narrow engineering
coverage report for the CAP LLM dialogue proxy policy surface.

## Scope

The tested object is:

```text
telemetry/context flags -> CAP response policy
```

No LLM is called. No model behavior is inferred. The report checks whether a
proxy layer can deterministically block or downgrade known release failures.

## Current Result

```text
Policy cases: 8
Passed: 8
Failed: 0
```

Reproduce:

```powershell
.\scripts\check_repo.ps1
```

or:

```bash
python reference/python/scripts/run_proxy_policy_pack.py --print-md
```

## Failure-Mode Coverage

| Failure mode | CAP policy behavior | Case |
|---|---|---|
| Prior answer has low retrieval confidence but high claim strength | Deprecates prior node; requires recheck and claim downgrade | `lpd_01_low_rc_high_cs_deprecated` |
| User provides a counter-source with unknown validity | Treats source as evidence update; requires validity check | `lpd_02_counter_source_unknown_validity` |
| Prior node has strong evidence and moderate claim strength | Allows anchor reuse | `lpd_03_high_rc_medium_cs_anchor_candidate` |
| Validator already rewrote/fixed a weak node | Blocks reuse of the old node | `lpd_04_validator_rewrite_weak_node` |
| Entropy is high | Requires uncertainty marker or retrieval retry | `lpd_05_high_entropy_requires_recheck` |
| User frame asks the model to agree with a false premise | Forbids agreement with false frame; requires uncertainty or disagreement | `lpd_06_sycophancy_false_user_frame` |
| Weak RAG support carries a strong answer | Forces rewrite or retrieval before release | `lpd_07_weak_rag_overclaim` |
| Cross-turn answer is stale | Requires revalidation before reuse | `lpd_08_stale_cross_turn_anchor` |

## What This Shows

CAP is useful here because it controls release policy rather than only asking
the model to behave better. The proxy can say:

- this prior node is deprecated
- this claim is too strong for its evidence
- this user frame is not evidence
- this old answer cannot be reused as an anchor
- this validator output supersedes the previous node

That is the practical distinction between prompt-only behavior shaping and a
CAP-style algorithmic governance layer.

## What This Does Not Show

This report does not show:

- empirical safety improvement in deployed systems
- superiority over RLHF or fine-tuning
- semantic correctness of every possible model answer
- real-world truth of CAP's broader phenomenological claims

The current status is a runnable policy-surface demonstration suitable for
engineering review and for designing the next empirical benchmark.

## Next Benchmark Step

The LLM dialogue benchmark scaffold now lives in
[`../llm_dialogue_benchmark/`](../llm_dialogue_benchmark/). It defines the case
pack, prompt modes, scorer, synthetic smoke fixture, and report format.

The next useful empirical benchmark is an LLM-in-the-loop comparison:

1. run the same dialogue cases without CAP
2. run them with prompt-level CAP
3. run them with proxy-level CAP
4. score claim/evidence calibration, sycophancy, self-justification, and stale
   anchor reuse

Until that exists, the current report should be cited as deterministic
failure-mode coverage, not as deployment proof.
