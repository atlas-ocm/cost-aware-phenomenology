#!/usr/bin/env python3
"""Deterministic integrity check for the AICE 6xx taxonomy (draft v0.12).

Placed under reference/python/scripts/ to match this repository's convention
(Python validators live here; scripts/ holds only the PowerShell orchestrator).
Runnable standalone and wired into check_repo.ps1.

The v0.12 code set is CLOSED and, with AICE-621 now assigned, contiguous:
AICE-601..AICE-621. AICE-600 is RESERVED for Ontological Lockdown -- undefined,
and NOT available to another class; AICE-622 is neither defined nor reserved,
i.e. genuinely available. Membership is checked by exact set comparison, never
derived from a numeric min/max range, so no reserved/unreserved code (AICE-600,
AICE-622) is silently admitted by treating the set as an open range.

Checks:
- all AICE JSON files parse;
- the registry defined-code set is exactly {AICE-601..AICE-621}, unique;
- the registry declares the unassigned set {AICE-600};
- the registry reserves {AICE-600: Ontological Lockdown} as RESERVED_UNDEFINED,
  with no registry entry, code document or schema enum slot;
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
- protected canonical prose still agrees with the registry (see below);
- relative Markdown links across the AICE surface resolve to existing files.

Structured-list parity is not narrative-claim parity. A registry can be perfectly
well-formed while the human-readable prose beside it asserts something the
registry contradicts, and a machine-valid registry with false canonical prose is
not a valid publication. Prose whose truth depends on registry state is therefore
wrapped in explicit markers and carries bounded, machine-checkable claims. This is
deliberately not unrestricted natural-language reasoning: only declared claims are
evaluated inside marked spans, plus two bounded token rules outside them — prose
outside any span may name only defined or unassigned code identities, and may not
name a near-successor by bare number, so an unreserved successor cannot be
promised in an unmarked paragraph either. Scanned text is normalized first
(HTML entities, NFKC, hyphen variants; rendering-invisible characters stripped
by Unicode category; digits folded to ASCII), so encoded spellings of a token
or number are the same token or number. A paraphrase naming no identity and no
successor number is beyond deterministic checking by design; that residue is a
review obligation, not a machine guarantee.

Out of scope by construction: the quarantined draft-proposal surface under
spec/aice/, historical evidence, quoted obsolete text labelled historical,
non-exhaustive examples, and prose marked as frozen projection metadata.

Exit status is non-zero if any check fails. No check is reported as passing
unless it was actually executed here.
"""
from __future__ import annotations

import html
import json
import re
import sys
import unicodedata
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[4]
AICE_SPEC = ROOT / "spec" / "aice"
REGISTRY_PATH = AICE_SPEC / "registry.json"
SCHEMA_PATH = AICE_SPEC / "incident.schema.json"
CODES_DIR = AICE_SPEC / "codes"
EXAMPLES_DIR = ROOT / "examples" / "aice"

# Closed and contiguous (AICE-621 now assigned): an explicit set, still compared
# by exact membership and never derived from a numeric min/max range, so the
# unassigned AICE-600 and the unreserved AICE-622 stay out of the defined set.
# Extending the range does not reserve its successor.
EXPECTED_CODES = [f"AICE-{n}" for n in range(601, 622)]
EXPECTED_UNASSIGNED = ["AICE-600"]
# A number has exactly one of three states, and the middle one is not "available":
#
#   DEFINED             in canonical_defined_set, with an entry, a document and a schema enum slot
#   RESERVED_UNDEFINED  held by explicit operator ruling: no entry, no document, no enum slot,
#                       and NOT assignable to any other incident class
#   AVAILABLE           absent from every set above (what the `unreserved` claim asserts)
#
# AICE-600 is RESERVED_UNDEFINED. It is unassigned (nothing is defined under it) but it is
# emphatically not available, so "unassigned" alone must never be published as if it meant free.
EXPECTED_RESERVED = {"AICE-600": "Ontological Lockdown"}
EXPECTED_VERSION = "0.12.0"
EXPECTED_SCHEMA_ID = "urn:cap:schema:aice-incident:v0.12"

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

# Protected canonical prose.
#
#   <!-- aice-prose-parity: defined-range 601 621; unassigned AICE-600 -->
#   ...prose...
#   <!-- /aice-prose-parity -->
#
# registry.json has no comment syntax, so its `set_note` is claimed by the sibling
# `set_note_claims` array using the same grammar.
#
# Claim grammar (the whole of it — anything else is an error, never a pass):
#   defined-range LO HI   the defined set is exactly the contiguous range LO..HI
#   defined-count N       exactly N codes are defined
#   enumerates-all        the span is an exhaustive list: every defined code appears
#                         in it (this is what catches an omitted identity)
#   defined AICE-NNN      AICE-NNN is in the defined set
#   unassigned AICE-NNN   AICE-NNN is declared unassigned (nothing is DEFINED under
#                         it — this alone says nothing about availability)
#   reserved AICE-NNN     AICE-NNN is held in reserved_codes as RESERVED_UNDEFINED:
#                         not defined, and not available to any other class
#   unreserved AICE-NNN   AICE-NNN is absent from the defined set, the unassigned
#                         set, reserved_codes, the registry entries, and the schema
#                         enum — i.e. genuinely AVAILABLE
#
# Outside spans two bounded rules apply: a code token that is neither defined nor
# unassigned may not appear at all — it must be moved inside a span whose claims
# cover it — and the bare successor numbers (max defined + 1 .. + 9) may not be
# named either, so "code number 622 is reserved" fails like "AICE-622" does.
# No other prose is interpreted: a paraphrase that names no code identity and no
# successor number is beyond deterministic token checking BY DESIGN and remains a
# review obligation, not a machine guarantee.
#
# All scanned text is normalized first: HTML entities unescaped, NFKC, Unicode
# hyphen variants folded to "-", rendering-invisible characters (categories Cf
# and Mn) stripped, and all decimal digits folded to ASCII — so an encoded,
# exotic-hyphen, invisible-split, or other-script-digit spelling of a token or
# number is the same token or number.
PROSE_OPEN_RE = re.compile(r"<!--\s*aice-prose-parity:\s*(.*?)\s*-->", re.S)
PROSE_CLOSE = "<!-- /aice-prose-parity -->"
PROSE_MARKER_LITERAL = "aice-prose-parity"
CODE_TOKEN_RE = re.compile(r"AICE-(\d{3})(?!\d)")
# Deleting the markers must not silently disarm the guard: these files must each
# carry at least one protected span, and the registry must carry its claims.
REQUIRED_PROSE_FILES = ["AICE.md", "README.md", "spec/aice/README.md"]
# Hyphen family: U+2010..U+2015, minus sign, small/fullwidth hyphen-minus.
_HYPHEN_VARIANTS = dict.fromkeys(
    map(ord, "‐‑‒–—―−﹣－"), "-"
)


def _normalize_scan_text(text: str) -> str:
    """Deterministic normalization so representation tricks cannot hide a token.

    HTML entities are unescaped, NFKC applied, hyphen variants folded to "-".
    Rendering-invisible characters are then removed BY UNICODE CATEGORY — Cf
    (format: zero-width, joiners, invisible separators, soft hyphen, BOM) and Mn
    (combining marks, which are invisible when orphaned inside a digit run) — not
    by enumeration, so a novel invisible character is stripped without a checker
    change. Every decimal digit (category Nd) is folded to its ASCII value, so an
    Arabic-Indic or other-script spelling of a number is the same number.
    """
    text = html.unescape(text)
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(_HYPHEN_VARIANTS)
    out: list[str] = []
    for ch in text:
        cat = unicodedata.category(ch)
        if cat in ("Cf", "Mn"):
            continue
        if cat == "Nd":
            out.append(str(unicodedata.digit(ch)))
        else:
            out.append(ch)
    return "".join(out)


def _iter_prose_spans(text: str):
    """Yield (raw_claims, span_text, line_no, start, end) for each protected span."""
    pos = 0
    while True:
        opened = PROSE_OPEN_RE.search(text, pos)
        if not opened:
            return
        line_no = text.count("\n", 0, opened.start()) + 1
        closed = text.find(PROSE_CLOSE, opened.end())
        if closed == -1:
            yield opened.group(1), None, line_no, opened.start(), len(text)
            return
        end = closed + len(PROSE_CLOSE)
        yield opened.group(1), text[opened.end():closed], line_no, opened.start(), end
        pos = end


def _check_prose_claims(raw: str, span: str, where: str, ctx: dict, issues: list[str]) -> None:
    """Evaluate one span's declared claims, then require the span to be covered."""
    claims = [c.strip() for c in raw.split(";") if c.strip()]
    if not claims:
        issues.append(f"{where}: protected prose span declares no claims")
        return

    span_tokens = {f"AICE-{m}" for m in CODE_TOKEN_RE.findall(span)}
    covered: set[str] = set()
    for claim in claims:
        parts = claim.split()
        kind = parts[0] if parts else ""
        named: set[str] = set()

        if kind == "defined-range" and len(parts) == 3 and all(p.isdigit() for p in parts[1:]):
            lo, hi = int(parts[1]), int(parts[2])
            expected = [f"AICE-{n}" for n in range(lo, hi + 1)]
            if sorted(ctx["defined"]) != sorted(expected):
                issues.append(
                    f"{where}: claim '{claim}' is false; the defined set is "
                    f"{sorted(ctx['defined'])}"
                )
            covered.update(expected)
            named = {f"AICE-{lo}", f"AICE-{hi}"}
        elif kind == "defined-count" and len(parts) == 2 and parts[1].isdigit():
            if len(ctx["defined"]) != int(parts[1]):
                issues.append(
                    f"{where}: claim '{claim}' is false; {len(ctx['defined'])} codes are defined"
                )
        elif kind == "enumerates-all" and len(parts) == 1:
            missing = sorted(c for c in ctx["defined"] if c not in span_tokens)
            if missing:
                issues.append(
                    f"{where}: claim 'enumerates-all' is false; the list omits {missing}"
                )
            covered.update(ctx["defined"])
        elif kind == "defined" and len(parts) == 2:
            if parts[1] not in ctx["defined"]:
                issues.append(f"{where}: claim '{claim}' is false; {parts[1]} is not defined")
            covered.add(parts[1])
            named = {parts[1]}
        elif kind == "unassigned" and len(parts) == 2:
            if parts[1] not in ctx["unassigned"]:
                issues.append(
                    f"{where}: claim '{claim}' is false; unassigned_codes is "
                    f"{sorted(ctx['unassigned'])}"
                )
            covered.add(parts[1])
            named = {parts[1]}
        elif kind == "reserved" and len(parts) == 2:
            # Asserts the middle state: held by ruling, not defined, not available.
            if parts[1] not in ctx["reserved"]:
                issues.append(
                    f"{where}: claim '{claim}' is false; reserved_codes is "
                    f"{sorted(ctx['reserved'])}"
                )
            covered.add(parts[1])
            named = {parts[1]}
        elif kind == "unreserved" and len(parts) == 2:
            code = parts[1]
            where_found = [
                name
                for name, pool in (
                    ("canonical_defined_set", ctx["defined"]),
                    ("unassigned_codes", ctx["unassigned"]),
                    ("reserved_codes", ctx["reserved"]),
                    ("registry entries", ctx["entries"]),
                    ("schema enum", ctx["enum"]),
                )
                if code in pool
            ]
            if where_found:
                issues.append(
                    f"{where}: claim '{claim}' is false; {code} is present in "
                    f"{', '.join(where_found)}"
                )
            covered.add(code)
            named = {code}
        else:
            issues.append(f"{where}: unrecognised prose claim '{claim}'")
            continue

        # A claim must be grounded in the prose it annotates, not a detached decoration.
        for token in sorted(named):
            if token not in span_tokens:
                issues.append(
                    f"{where}: claim '{claim}' names {token}, which the prose does not mention"
                )

    # Coverage: every code identity the prose names must be answered by a claim.
    # This is what stops a future edit from promising an unreserved successor in words.
    for token in sorted(span_tokens):
        if token not in covered:
            issues.append(
                f"{where}: protected prose mentions {token} but no claim covers it"
            )


def _check_doc_prose(text: str, rel: str, ctx: dict, issues: list[str]) -> bool:
    """Check one document's spans, marker integrity, and out-of-span tokens.

    Returns True if the document carries at least one protected span.
    """
    text = _normalize_scan_text(text)
    spans = list(_iter_prose_spans(text))

    # Marker integrity: a typo'd open marker, an orphan close, or a nested open
    # must be an error, never a silent disarm of the guard.
    opens = len(PROSE_OPEN_RE.findall(text))
    closes = text.count(PROSE_CLOSE)
    mentions = text.count(PROSE_MARKER_LITERAL)
    if opens != closes or mentions != opens + closes or len(spans) != opens:
        issues.append(
            f"{rel}: malformed aice-prose-parity markers ({opens} open, {closes} "
            f"close, {mentions} literal mention(s), {len(spans)} span(s) parsed)"
        )

    for raw, span, line_no, _, _ in spans:
        if span is None:
            issues.append(f"{rel}:{line_no}: protected prose span is never closed")
            continue
        _check_prose_claims(raw, span, f"{rel}:{line_no}", ctx, issues)

    # Outside protected spans, a canonical document may name only defined or
    # unassigned code identities. An unreserved successor named in an unmarked
    # paragraph is exactly the promise-in-prose hole; it must move inside a span
    # whose claims cover it. No other out-of-span prose is interpreted.
    residual = text
    for _, _, _, start, end in reversed(spans):
        residual = residual[:start] + residual[end:]
    allowed = ctx["defined"] | ctx["unassigned"]
    for token in sorted({f"AICE-{m}" for m in CODE_TOKEN_RE.findall(residual)}):
        if token not in allowed:
            issues.append(
                f"{rel}: prose outside any protected span names {token}, which is "
                "neither defined nor unassigned; wrap the mention in an "
                "aice-prose-parity span with a covering claim"
            )

    # The successor may not be promised by bare number either ("code number 621
    # is reserved"). Bounded to the next nine numbers past the defined maximum.
    # Full AICE-NNN tokens are stripped first so each mention is judged by
    # exactly one rule.
    residual_numbers = CODE_TOKEN_RE.sub("", residual)
    if ctx["defined"]:
        highest = max(int(c.split("-")[1]) for c in ctx["defined"])
        for n in range(highest + 1, highest + 10):
            if re.search(rf"(?<!\d){n}(?!\d)", residual_numbers):
                issues.append(
                    f"{rel}: prose outside any protected span names the successor "
                    f"number {n}; an unreserved successor may not be referenced "
                    "outside a covered aice-prose-parity span"
                )

    return bool(spans)


def _check_protected_prose(ctx: dict, issues: list[str]) -> None:
    scanned: set[str] = set()
    docs = [ROOT / "AICE.md", ROOT / "README.md", AICE_SPEC / "README.md"]
    docs += sorted(CODES_DIR.glob("*.md"))
    for md in docs:
        if not md.exists():
            continue
        rel = md.relative_to(ROOT).as_posix()
        text = md.read_text(encoding="utf-8")
        if _check_doc_prose(text, rel, ctx, issues):
            scanned.add(rel)

    for required in REQUIRED_PROSE_FILES:
        if required not in scanned:
            issues.append(
                f"{required} carries no protected prose span; the narrative-parity "
                "guard must not be removable by deleting its markers"
            )

    note = ctx["registry"].get("set_note")
    note_claims = ctx["registry"].get("set_note_claims")
    if not isinstance(note, str) or not note.strip():
        issues.append("registry is missing 'set_note' canonical prose")
    if not note_claims:
        issues.append("registry is missing 'set_note_claims' for its set_note prose")
    elif not isinstance(note_claims, list) or not all(isinstance(c, str) for c in note_claims):
        issues.append("registry 'set_note_claims' must be a list of claim strings")
    elif isinstance(note, str):
        _check_prose_claims(
            "; ".join(note_claims),
            _normalize_scan_text(note),
            "spec/aice/registry.json:set_note",
            ctx,
            issues,
        )


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

        # Reserved-but-undefined numbers. The reservation is data, not prose, so a
        # future edit cannot quietly re-open the number by rewording a paragraph.
        declared_reserved = registry.get("reserved_codes")
        if declared_reserved is None:
            issues.append("registry is missing 'reserved_codes'")
        else:
            seen_reserved = {}
            for item in declared_reserved:
                if not isinstance(item, dict) or not item.get("code"):
                    issues.append(f"reserved_codes entry is malformed: {item!r}")
                    continue
                # Keyed accumulation silently collapses duplicates, and the
                # expected-key comparison below would then still pass — so the
                # duplicate has to be caught BEFORE the assignment.
                if item["code"] in seen_reserved:
                    issues.append(
                        f"reserved code {item['code']} is listed more than once in "
                        f"reserved_codes; a duplicated reservation can hide a second, "
                        f"differing row"
                    )
                seen_reserved[item["code"]] = item
                if item.get("status") != "RESERVED_UNDEFINED":
                    issues.append(
                        f"reserved code {item['code']} has status {item.get('status')!r}; "
                        f"expected 'RESERVED_UNDEFINED'"
                    )
                if not item.get("reserved_title"):
                    issues.append(
                        f"reserved code {item['code']} has no reserved_title; an untitled "
                        f"reservation cannot be distinguished from an available number"
                    )
            if sorted(seen_reserved) != sorted(EXPECTED_RESERVED):
                issues.append(
                    f"registry reserved_codes is {sorted(seen_reserved)}; "
                    f"expected {sorted(EXPECTED_RESERVED)}"
                )
            for code, title in EXPECTED_RESERVED.items():
                got = (seen_reserved.get(code) or {}).get("reserved_title")
                if code in seen_reserved and got != title:
                    issues.append(
                        f"reserved code {code} is titled {got!r}; expected {title!r}"
                    )
                # A reservation is not a definition: it must stay out of every
                # surface that would make it a published incident code.
                if code in {c for c in codes if c}:
                    issues.append(f"reserved code {code} has a registry entry")
                if (CODES_DIR / f"{code}.md").exists():
                    issues.append(f"reserved code {code} has a code document")
                enum = (schema or {}).get("properties", {}).get("code", {}).get("enum") or []
                if code in enum:
                    issues.append(f"reserved code {code} appears in the schema enum")

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

    # Narrative-claim parity. A machine-valid registry beside false canonical prose
    # is not a valid publication.
    if registry is not None and schema is not None:
        _check_protected_prose(
            {
                "registry": registry,
                "defined": set(registry.get("canonical_defined_set") or []),
                "unassigned": set(registry.get("unassigned_codes") or []),
                "reserved": {r.get("code") for r in (registry.get("reserved_codes") or [])
                             if isinstance(r, dict)},
                "entries": {e.get("code") for e in registry.get("codes", [])},
                "enum": set(schema.get("properties", {}).get("code", {}).get("enum") or []),
            },
            issues,
        )

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
