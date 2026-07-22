#!/usr/bin/env python3
"""Deterministic integrity check for the AICE 6xx taxonomy (draft v0.1).

Placed under reference/python/scripts/ to match this repository's convention
(Python validators live here; scripts/ holds only the PowerShell orchestrator).
Runnable standalone and wired into check_repo.ps1.

Checks:
- all AICE JSON files parse;
- the registry code set is exactly AICE-604..AICE-609 with unique codes;
- every registry code has a corresponding codes/AICE-XXX.md document;
- every code document contains the required normative headings;
- example payloads conform to spec/aice/incident.schema.json;
- example code/title agree with the registry;
- no example embeds a 64-hex-char digest value (no invented SHA-256);
- relative Markdown links across the AICE surface resolve to existing files.

Exit status is non-zero if any check fails. No check is reported as passing
unless it was actually executed here.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[4]
AICE_SPEC = ROOT / "spec" / "aice"
REGISTRY_PATH = AICE_SPEC / "registry.json"
SCHEMA_PATH = AICE_SPEC / "incident.schema.json"
CODES_DIR = AICE_SPEC / "codes"
EXAMPLES_DIR = ROOT / "examples" / "aice"

EXPECTED_CODES = [f"AICE-60{n}" for n in range(4, 10)]

REQUIRED_HEADINGS = [
    "## Canonical identifier",
    "## Human-readable alias",
    "## Intent",
    "## Trigger condition",
    "## Required observations",
    "## Missing-evidence condition",
    "## False-positive guards",
    "## Workflow semantics",
    "## Remediation",
    "## Example",
    "## Related codes",
]

# 64 hex chars on a token boundary — a bare SHA-256 value we must never fabricate.
SHA256_RE = re.compile(r"(?<![0-9a-fA-F])[0-9a-fA-F]{64}(?![0-9a-fA-F])")
# Markdown relative links (skip http(s):, mailto:, and pure #anchors).
LINK_RE = re.compile(r"\]\((?!https?:|mailto:|#)([^)]+)\)")


def _load_json(path: Path, issues: list[str]):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        issues.append(f"missing file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        issues.append(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
    return None


def _check_links(md_path: Path, issues: list[str]) -> None:
    text = md_path.read_text(encoding="utf-8")
    for target in LINK_RE.findall(text):
        rel = target.split("#", 1)[0]
        if not rel:
            continue
        resolved = (md_path.parent / rel).resolve()
        if not resolved.exists():
            issues.append(f"broken link in {md_path.relative_to(ROOT)}: {target}")


def main() -> int:
    issues: list[str] = []

    registry = _load_json(REGISTRY_PATH, issues)
    schema = _load_json(SCHEMA_PATH, issues)

    if schema is not None:
        try:
            jsonschema.Draft202012Validator.check_schema(schema)
        except jsonschema.exceptions.SchemaError as exc:
            issues.append(f"incident.schema.json is not valid Draft 2020-12: {exc}")

    registry_titles: dict[str, str] = {}
    if registry is not None:
        entries = registry.get("codes", [])
        codes = [e.get("code") for e in entries]
        registry_titles = {e.get("code"): e.get("title") for e in entries}

        if len(codes) != len(set(codes)):
            issues.append("registry contains duplicate codes")
        if sorted(c for c in codes if c) != EXPECTED_CODES:
            issues.append(
                f"registry code set is not exactly {EXPECTED_CODES}; got {sorted(codes)}"
            )

        for code in EXPECTED_CODES:
            code_doc = CODES_DIR / f"{code}.md"
            if not code_doc.exists():
                issues.append(f"missing code document: {code_doc.relative_to(ROOT)}")
                continue
            doc_text = code_doc.read_text(encoding="utf-8")
            for heading in REQUIRED_HEADINGS:
                if heading not in doc_text:
                    issues.append(f"{code}.md missing heading: '{heading}'")

    # Examples must conform to the schema and agree with the registry.
    if schema is not None:
        validator = jsonschema.Draft202012Validator(schema)
        example_files = sorted(EXAMPLES_DIR.glob("*.json"))
        if not example_files:
            issues.append(f"no example payloads found in {EXAMPLES_DIR.relative_to(ROOT)}")
        for ex_path in example_files:
            example = _load_json(ex_path, issues)
            if example is None:
                continue
            for err in sorted(validator.iter_errors(example), key=lambda e: list(e.path)):
                loc = "/".join(str(p) for p in err.path) or "<root>"
                issues.append(f"{ex_path.name} schema error at {loc}: {err.message}")

            code = example.get("code")
            title = example.get("title")
            if code in registry_titles and title != registry_titles[code]:
                issues.append(
                    f"{ex_path.name} title '{title}' does not match registry title "
                    f"'{registry_titles[code]}' for {code}"
                )

            raw = ex_path.read_text(encoding="utf-8")
            if SHA256_RE.search(raw):
                issues.append(f"{ex_path.name} contains a 64-hex-char string (possible fabricated SHA-256)")

    # Relative links across the AICE documentation surface must resolve.
    link_docs = [ROOT / "AICE.md", AICE_SPEC / "README.md"]
    link_docs += sorted(CODES_DIR.glob("*.md"))
    for md in link_docs:
        if md.exists():
            _check_links(md, issues)
        else:
            issues.append(f"missing doc: {md.relative_to(ROOT)}")

    if issues:
        print(f"AICE integrity check FAILED ({len(issues)} issue(s)):")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print(
        f"AICE integrity check OK — {len(EXPECTED_CODES)} codes, "
        f"{len(sorted(EXAMPLES_DIR.glob('*.json')))} examples, schema valid, links resolve."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
