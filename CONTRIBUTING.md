# Contributing to CAP

Thank you for your interest in CAP — Cost-Aware Phenomenology. This is a research framework, and contributions are welcome on cases, validation, and applications.

## What we accept

- New validation cases (deterministic + LLM-checkable)
- Worked examples from real domains (with anonymization where appropriate)
- Boundary clarifications and counterexamples
- Application proposals (LLM/RAG, decision support, repair planning, etc.)
- Bug reports against the schemas, the COM-Log format, or the operator alphabet
- Documentation improvements (clarity, English polish, cross-references)

## What we do not accept

- Unverified empirical claims about lived experience presented as proven
- Coaching, motivational, or therapeutic content
- Outputs from LLMs presented as evidence of CAP's ontology (LLM is scaffold, not evidence)
- Recommendations that bypass the budget / telemetry discipline

## Issue templates

Open an issue using one of the following intents:

### Case pack proposal
- Describe the boundary you want to test.
- Provide a minimum of one deterministic input and an expected verdict.
- Note which subsystem(s) the case exercises.

### Validation result
- Identify the model surface (model id, runtime, identity verification method).
- Attach the raw JSON output and the comparison verdict.
- Flag any discrepancies against the deterministic baseline.

### Boundary clarification
- Quote the passage that was unclear.
- Describe the interpretation that broke and the interpretation that you think works.
- Propose specific edited wording where possible.

## Pull request style

- Clean English. Short sentences. Active voice.
- Cite sources for any external claim.
- Make outputs machine-checkable wherever possible: structured JSON, explicit verdicts, deterministic baselines.
- Keep the IS / IS NOT contract intact. New material must not introduce coaching, divination, or unbudgeted recommendations.
- One logical change per PR.

## How to add a new validation case

1. Create a JSON file in the appropriate `validation_artifacts/<subsystem>/cases/` folder.
2. Include: `case_id`, `description`, `input`, `expected_verdict`, `expected_primary_reading`, and any boundary annotations.
3. Add the case to the corresponding `case_pack.md` summary.
4. If you have run the case against a model, attach the raw model output as a separate file and a comparison report.
5. Update the deterministic baseline summary if the new case extends coverage.

## How to add a new worked example

1. Place the example in `examples/<short_descriptive_name>.md`.
2. Structure: Setup -> Input -> COM-Log output -> Diagnosis -> Recommended operators -> Why this is or is not admissible under the current budget and telemetry.
3. Anonymize personal details. Examples should illustrate boundaries, not expose third parties.
4. Cross-reference the relevant subsystem documents.
5. Add a link to the example from the `README.md` or the relevant subsystem document.

## Code of conduct

This project follows the spirit of the Contributor Covenant. Be respectful, on-topic, and precise. Disagreement on framework boundaries is welcome; ad hominem is not. See https://www.contributor-covenant.org/ for the standard text.

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0, the same license as the rest of the project.
