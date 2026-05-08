# LLM Dialogue Proxy Policy Validation

This folder contains deterministic, dependency-free policy cases for the CAP
LLM dialogue proxy.

The cases do not run an LLM. They check the proxy rule surface:

```text
telemetry tag
-> parsed telemetry
-> response policy
-> expected decision
```

Run:

```bash
python reference/python/scripts/run_proxy_policy_pack.py --print-md
```

Expected result:

```text
Passed: 8
Failed: 0
```

This is not an external benchmark. It is a deterministic release-policy
regression pack for self-justification, claim/evidence mismatch, validator
rewrite state, high entropy, counter-source handling, false user framing,
weak-RAG overclaiming, and stale cross-turn anchors.
