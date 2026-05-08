# LLM Dialogue Proxy Policy Case Pack

Status: deterministic proxy-policy regression pack.

Scope:

```text
No LLM calls.
No empirical benchmark claim.
Only telemetry -> policy behavior is checked.
```

Cases:

| Case | Purpose |
|---|---|
| `lpd_01_low_rc_high_cs_deprecated` | Low retrieval confidence plus high claim strength must deprecate the prior node. |
| `lpd_02_counter_source_unknown_validity` | A counter-source is an evidence update, but unknown validity still requires checking. |
| `lpd_03_high_rc_medium_cs_anchor_candidate` | High evidence with medium claim strength can remain an anchor candidate. |
| `lpd_04_validator_rewrite_weak_node` | A rewrite validator action prevents the prior node from being reused as-is. |
| `lpd_05_high_entropy_requires_recheck` | High entropy forces uncertainty or retrieval retry before reuse. |
| `lpd_06_sycophancy_false_user_frame` | A false user frame must not become an anchor through agreement pressure. |
| `lpd_07_weak_rag_overclaim` | Weak retrieval support cannot carry a high-strength claim. |
| `lpd_08_stale_cross_turn_anchor` | Cross-turn reuse requires revalidation when the anchor is stale. |

Run:

```text
python reference/python/scripts/run_proxy_policy_pack.py --print-md
```
