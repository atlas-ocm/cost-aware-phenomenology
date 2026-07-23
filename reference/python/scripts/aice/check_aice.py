#!/usr/bin/env python3
"""Deterministic integrity check for the AICE 6xx taxonomy (draft v0.8).

Placed under reference/python/scripts/ to match this repository's convention
(Python validators live here; scripts/ holds only the PowerShell orchestrator).
Runnable standalone and wired into check_repo.ps1.

The v0.8 code set is a CLOSED but SPARSE set: AICE-602, AICE-604..AICE-616, and
AICE-618. AICE-600, AICE-601, AICE-603, and AICE-617 are unassigned. Membership
is checked by exact set comparison, never derived from a numeric min/max range,
so the sparse set is not silently treated as the contiguous range
AICE-602..AICE-618.

Checks:
- all AICE JSON files parse;
- the registry defined-code set is exactly {AICE-602, AICE-604..AICE-616, AICE-618}, unique;
- the registry declares the unassigned set {AICE-600, AICE-601, AICE-603, AICE-617};
- no registry entry or code document exists for an unassigned code;
- the registry carries no contiguity-promising `canonical_code_range` field;
- registry entries that declare a machine_name have it present in their code doc;
- registry machine_name values are unique (no two codes share a machine name);
- the registry spec_version matches the expected value;
- the schema $id and spec_version const match the expected values;
- every defined registry code has a corresponding codes/AICE-XXX.md document;
- every code document contains the required normative headings and version marker;
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

# Closed but sparse: an explicit set, never a numeric min/max range.
# AICE-617 is unassigned, so the set skips it between AICE-616 and AICE-618.
EXPECTED_CODES = ["AICE-602"] + [f"AICE-{n}" for n in range(604, 617)] + ["AICE-618"]
EXPECTED_UNASSIGNED = ["AICE-600", "AICE-601", "AICE-603", "AICE-617"]
EXPECTED_VERSION = "0.8.0"
EXPECTED_SCHEMA_ID = "urn:cap:schema:aice-incident:v0.8"

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

        if schema.get("$id") != EXPECTED_SCHEMA_ID:
            issues.append(
                f"schema $id is {schema.get('$id')!r}; expected {EXPECTED_SCHEMA_ID!r}"
            )
        schema_const = (
            schema.get("properties", {}).get("spec_version", {}).get("const")
        )
        if schema_const != EXPECTED_VERSION:
            issues.append(
                f"schema spec_version const is {schema_const!r}; "
                f"expected {EXPECTED_VERSION!r}"
            )

    registry_titles: dict[str, str] = {}
    if registry is not None:
        entries = registry.get("codes", [])
        codes = [e.get("code") for e in entries]
        registry_titles = {e.get("code"): e.get("title") for e in entries}

        if len(codes) != len(set(codes)):
            issues.append("registry contains duplicate codes")
        # Exact sparse-set membership — NOT derived from a numeric min/max range.
        if sorted(c for c in codes if c) != sorted(EXPECTED_CODES):
            issues.append(
                f"registry defined-code set is not exactly {sorted(EXPECTED_CODES)}; "
                f"got {sorted(codes)}"
            )

        declared_set = registry.get("canonical_defined_set")
        if declared_set is None:
            issues.append("registry is missing 'canonical_defined_set'")
        elif sorted(declared_set) != sorted(EXPECTED_CODES):
            issues.append(
                f"registry canonical_defined_set is {sorted(declared_set)}; "
                f"expected {sorted(EXPECTED_CODES)}"
            )

        declared_unassigned = registry.get("unassigned_codes")
        if declared_unassigned is None:
            issues.append("registry is missing 'unassigned_codes'")
        elif sorted(declared_unassigned) != sorted(EXPECTED_UNASSIGNED):
            issues.append(
                f"registry unassigned_codes is {sorted(declared_unassigned)}; "
                f"expected {sorted(EXPECTED_UNASSIGNED)}"
            )

        # The set is sparse and closed: a contiguity-promising range field is a false claim.
        if "canonical_code_range" in registry:
            issues.append(
                "registry declares 'canonical_code_range' (a contiguity claim); "
                "the defined set is sparse and must use 'canonical_defined_set'"
            )

        # No defined code may also be listed as unassigned, and no unassigned code
        # may have a registry entry or a code document.
        defined_codes = {c for c in codes if c}
        for code in EXPECTED_UNASSIGNED:
            if code in defined_codes:
                issues.append(f"unassigned code {code} has a registry entry")
            if (CODES_DIR / f"{code}.md").exists():
                issues.append(f"unassigned code {code} has a placeholder document")

        # Machine-name parity: an entry declaring a machine_name must have it in its doc.
        machine_names: list[str] = []
        for entry in entries:
            machine_name = entry.get("machine_name")
            code = entry.get("code")
            if machine_name and code:
                machine_names.append(machine_name)
                code_doc = CODES_DIR / f"{code}.md"
                if code_doc.exists() and machine_name not in code_doc.read_text(
                    encoding="utf-8"
                ):
                    issues.append(
                        f"{code}.md does not contain registry machine_name {machine_name!r}"
                    )
        # Machine names must be unique across the registry.
        if len(machine_names) != len(set(machine_names)):
            dupes = sorted({m for m in machine_names if machine_names.count(m) > 1})
            issues.append(f"registry contains duplicate machine_name(s): {dupes}")

        if registry.get("spec_version") != EXPECTED_VERSION:
            issues.append(
                f"registry spec_version is {registry.get('spec_version')!r}; "
                f"expected {EXPECTED_VERSION!r}"
            )

        version_marker = f"AICE v{EXPECTED_VERSION}"
        for code in EXPECTED_CODES:
            code_doc = CODES_DIR / f"{code}.md"
            if not code_doc.exists():
                issues.append(f"missing code document: {code_doc.relative_to(ROOT)}")
                continue
            doc_text = code_doc.read_text(encoding="utf-8")
            for heading in REQUIRED_HEADINGS:
                if heading not in doc_text:
                    issues.append(f"{code}.md missing heading: '{heading}'")
            if version_marker not in doc_text:
                issues.append(f"{code}.md missing version marker '{version_marker}'")

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
