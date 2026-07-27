"""Bounded, read-only validator for the AICE candidate quarantine surface.

NON-CANONICAL. This script is intentionally separate from check_aice.py and is
never imported or invoked by it: the candidate surface must not gain any
influence over the canonical registry, schema, defined-code count, or example
count (see spec/aice/candidates/README.md, "Authority status"). It only checks
internal consistency of spec/aice/candidates/ itself:

  - every full-status dossier carries the required identity fields and
    required sections (see the candidates README's "Required candidate
    fields");
  - HYPOTHESIS_HELD entries are held to the reduced set the README exempts
    them to;
  - every status value in use is one the candidates README documents;
  - README "## Contents" lists exactly the files that exist on disk;
  - a candidate whose machine_name (or previous_machine_name) matches a
    canonical registry entry is marked PROMOTED, so a promotion can never go
    stale the way AICE-619/620's dossiers did before this script existed;
  - a WITHDRAWN_TRIGGER_FALSIFIED dossier states its retraction reason;
  - no two non-withdrawn candidates claim the same machine_name;
  - an operator-indicated future number is never asserted as this file's own
    canonical_code.

A finding here is a documentation defect in the quarantine surface, not an
AICE incident and not a canonical-registry defect.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CAND_DIR = ROOT / "spec" / "aice" / "candidates"
FIXTURES_DIR = CAND_DIR / "fixtures"
README = CAND_DIR / "README.md"
REGISTRY = ROOT / "spec" / "aice" / "registry.json"

HELD_MULTI_FILE = "held-hypotheses.md"

# Required sections for a full-status dossier, matched as case-insensitive
# substrings against the whole document. House style varies wording slightly
# across dossiers written at different times, so each entry MAY list more
# than one accepted alias; only one alias needs to be present.
FULL_REQUIRED_SECTIONS = [
    ("source and provenance limits",),
    ("core definition",),
    ("trigger predicates", "canonical trigger"),
    ("forbidden",),
    ("required terminal",),
    ("comparison with",),
    ("false-positive boundary",),
    ("portable",),
    ("promotion gate",),
    ("verification status",),
]
NEGATIVE_CONTROL_MARKER = "negative control"

IDENTITY_FIELD_PATTERNS = {
    "working_title": re.compile(r"working[ _]title", re.I),
    "machine_name": re.compile(r"machine[ _]name", re.I),
    "status": re.compile(r"\bstatus\b", re.I),
    "canonical_code": re.compile(r"canonical[ _]code", re.I),
    "number_reserved": re.compile(r"(canonical[_ ]number[_ ]reserved|number reserved)", re.I),
}

ALWAYS_KNOWN_LIFECYCLES = {"PROMOTED"}


def get_identity_block(text):
    m = re.search(r"## Identity\b(.*?)\n##[ \t]", text, re.S)
    return m.group(1) if m else text[:1500]


def extract_value(scope_text, pattern, window=200):
    m = pattern.search(scope_text)
    if not m:
        return None
    snippet = scope_text[m.end(): m.end() + window]
    m2 = re.search(r"[|:]?\s*`?([A-Z][A-Z0-9_\-]*)`?", snippet)
    return m2.group(1) if m2 else None


def is_promoted(text):
    return bool(re.search(r"promotion_status\s*[|:]?\s*`?PROMOTED`?", text))


def load_readme_lifecycles(text):
    m = re.search(r"## Candidate lifecycle(.*?)\n## ", text, re.S)
    body = m.group(1) if m else text
    return set(re.findall(r"^### ([A-Z_]+)", body, re.M)) | ALWAYS_KNOWN_LIFECYCLES


def load_readme_contents(text):
    m = re.search(r"## Contents(.*)\Z", text, re.S)
    body = m.group(1) if m else ""
    return set(re.findall(r"\]\(\./((?:fixtures/)?[a-zA-Z0-9_\-]+\.md)\)", body))


def load_registry():
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    defined = set(data.get("canonical_defined_set", []))
    machine_names = {c["machine_name"]: c["code"] for c in data.get("codes", []) if c.get("machine_name")}
    reserved = {r["code"]: r.get("reserved_title", "")
                for r in data.get("reserved_codes", []) if isinstance(r, dict) and r.get("code")}
    return defined, machine_names, reserved


def _norm_identity(value):
    return re.sub(r"[^A-Z0-9]+", "_", (value or "").upper()).strip("_")


def _is_the_reserved_class(block, title):
    """True only if the dossier's OWN identity fields name the reserved class.

    Occurrence of the reserved title anywhere in the block is NOT proof: a
    different candidate could mention 'Ontological Lockdown' in a comparison
    row, a differential, or a negated sentence and thereby inherit the right to
    the reserved number. Ownership has to be read off the identity fields the
    dossier claims for itself.
    """
    want = _norm_identity(title)
    for field in ("working[ _]title", "machine[ _]name"):
        for m in re.finditer(field + r"\s*[|:]\s*`?([^|`\n]+)`?", block, re.I):
            if _norm_identity(m.group(1)) == want:
                return True
    return False


def check_reserved_numbers(name, block, reserved, errors):
    """A reserved number is not a parking space for the next good idea.

    AICE-600 is held for Ontological Lockdown by explicit operator ruling. A
    candidate may neither indicate it as a future publication identity nor claim
    it as its own canonical_code — the second is barred even for the reserved
    class itself, because promotion is a separate ratification episode.
    """
    for code, title in reserved.items():
        indicated = re.search(
            r"(?:operator_indicated_number|operator-selected code)\s*[|:]?\s*`?"
            + re.escape(code) + r"`?", block, re.I)
        if indicated and not _is_the_reserved_class(block, title):
            fail(errors, f"{name}: indicates reserved number {code}, which is held for "
                          f"'{title}' and is not available to another incident class")
        claims = re.search(r"canonical_code\s*[|:]?\s*`?" + re.escape(code) + r"`?", block, re.I)
        if claims:
            fail(errors, f"{name}: claims canonical_code {code}; that number is RESERVED and "
                          f"undefined — assigning it requires a formal promotion episode")


def check_dossier(path, text, registry_defined, registry_machine_names, registry_reserved,
                  readme_lifecycles, errors):
    name = path.name
    block = get_identity_block(text)

    check_reserved_numbers(name, block, registry_reserved, errors)

    status = extract_value(block, IDENTITY_FIELD_PATTERNS["status"])
    if status is None:
        fail(errors, f"{name}: no readable status value in the Identity block")
        status = ""

    promoted = is_promoted(text)
    effective_lifecycle = "PROMOTED" if promoted else status
    if effective_lifecycle and effective_lifecycle not in readme_lifecycles:
        fail(errors, f"{name}: lifecycle '{effective_lifecycle}' is not documented under "
                      f"README '## Candidate lifecycle'")

    is_withdrawn = status == "WITHDRAWN_TRIGGER_FALSIFIED"
    is_held = status == "HYPOTHESIS_HELD" and not promoted

    if is_withdrawn and not re.search(r"retract|withdrawal reason", text, re.I):
        fail(errors, f"{name}: withdrawn candidate has no retraction/withdrawal-reason section")

    if is_held:
        for field in ("working_title", "machine_name", "status"):
            if not IDENTITY_FIELD_PATTERNS[field].search(block):
                fail(errors, f"{name}: held hypothesis missing '{field}' in the Identity block")
        if not re.search(r"promotion gate|why (this is )?held|blocking_question", text, re.I):
            fail(errors, f"{name}: held hypothesis does not state what would resolve it")
    else:
        for field, pattern in IDENTITY_FIELD_PATTERNS.items():
            if not pattern.search(block):
                fail(errors, f"{name}: missing required field '{field}' in the Identity block")
        for aliases in FULL_REQUIRED_SECTIONS:
            if not any(alias in text.lower() for alias in aliases):
                fail(errors, f"{name}: missing required section matching {aliases!r}")
        if NEGATIVE_CONTROL_MARKER not in text.lower():
            fail(errors, f"{name}: no negative control present")

    if not promoted and not is_withdrawn:
        cc = extract_value(block, IDENTITY_FIELD_PATTERNS["canonical_code"])
        if cc and cc != "UNASSIGNED":
            fail(errors, f"{name}: canonical_code is '{cc}', not UNASSIGNED, and the file "
                          f"is not marked PROMOTED")

    # Registry cross-reference: a candidate whose OWN indicated number or
    # machine_name is now canonical must say so, so a promotion can never
    # silently go stale. Scoped to the specific identity fields, not to any
    # AICE-NNN mention in the block, since legitimate prose there (e.g.
    # "the registry's own claim -- AICE-601...AICE-621 defined") cites real
    # canonical codes purely as context.
    if not promoted and not is_withdrawn:
        own_number = re.search(
            r"(?:operator_indicated_number|operator-selected code)\s*[|:]?\s*`?(AICE-\d{3})`?",
            block, re.I,
        )
        if own_number and own_number.group(1) in registry_defined:
            fail(errors, f"{name}: its own indicated number {own_number.group(1)} IS now "
                          f"canonical, but the file carries no promotion_status: PROMOTED marker")
        for field in ("machine_name", "previous_machine_name"):
            # Both spellings are read here so a promotion can never hide behind
            # punctuation; which spelling a file is ALLOWED to use is enforced
            # separately below.
            field_re = field.replace("_", "[ _]")
            pat = re.compile(field_re + r"\s*[|:]?\s*`?([A-Z][A-Z0-9_]+)`?", re.I)
            m = pat.search(block)
            if m and m.group(1) in registry_machine_names:
                fail(errors, f"{name}: {field}={m.group(1)} matches canonical "
                              f"{registry_machine_names[m.group(1)]}, but the file carries no "
                              f"promotion_status: PROMOTED marker")

    # Legacy spelling is grandfathered, not permitted. Dossiers already promoted
    # predate the underscored house style and are retained verbatim as promotion
    # provenance; every active or new candidate must use `machine_name`, so the
    # old grammar cannot keep spreading through new files.
    if not promoted and re.search(r"machine name", block, re.I) \
            and not re.search(r"machine_name", block):
        fail(errors, f"{name}: active candidate spells the field 'machine name'; new and "
                      f"active dossiers must use 'machine_name' (the spaced form is "
                      f"grandfathered for already-PROMOTED dossiers only)")

    lifecycle_for_dedup = "WITHDRAWN_TRIGGER_FALSIFIED" if is_withdrawn else effective_lifecycle
    machine_name = extract_value(block, IDENTITY_FIELD_PATTERNS["machine_name"])
    return lifecycle_for_dedup, machine_name


def check_held_hypotheses_file(path, text, errors):
    entries = re.findall(r"^## \d+\. .+$", text, re.M)
    if not entries:
        fail(errors, f"{path.name}: no numbered hypothesis entries found")
    # Anchored at line start so `previous_machine_name` is not counted as a
    # second identity for the same entry.
    machine_names = re.findall(r"^machine_name\s+([A-Z0-9_]+)", text, re.M)
    if len(machine_names) != len(entries):
        fail(errors, f"{path.name}: {len(entries)} hypothesis entries but "
                      f"{len(machine_names)} machine_name values")
    if len(machine_names) != len(set(machine_names)):
        fail(errors, f"{path.name}: duplicate machine_name within the held-hypotheses file")
    if "HYPOTHESIS_HELD" not in text:
        fail(errors, f"{path.name}: no entry declares status HYPOTHESIS_HELD")
    return machine_names


def fail(errors, msg):
    errors.append(msg)


def main():
    errors = []
    readme_text = README.read_text(encoding="utf-8")
    readme_lifecycles = load_readme_lifecycles(readme_text)
    contents_files = load_readme_contents(readme_text)
    registry_defined, registry_machine_names, registry_reserved = load_registry()

    actual_files = {p.name for p in CAND_DIR.glob("*.md") if p.name != "README.md"}
    if FIXTURES_DIR.exists():
        actual_files |= {f"fixtures/{p.name}" for p in FIXTURES_DIR.glob("*.md")}

    for f in sorted(actual_files - contents_files):
        fail(errors, f"README Contents: {f} exists on disk but is not listed")
    for f in sorted(contents_files - actual_files):
        fail(errors, f"README Contents: {f} is listed but does not exist on disk")

    all_machine_names = {}
    for path in sorted(CAND_DIR.glob("*.md")):
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        if path.name == HELD_MULTI_FILE:
            for mn in check_held_hypotheses_file(path, text, errors):
                all_machine_names.setdefault(mn, []).append(path.name)
            continue
        lifecycle, mn = check_dossier(
            path, text, registry_defined, registry_machine_names, registry_reserved,
            readme_lifecycles, errors
        )
        if mn and lifecycle != "WITHDRAWN_TRIGGER_FALSIFIED":
            all_machine_names.setdefault(mn, []).append(path.name)

    for mn, files in all_machine_names.items():
        if len(files) > 1:
            fail(errors, f"machine_name '{mn}' claimed by more than one candidate: {files}")

    if errors:
        print(f"CANDIDATE SURFACE CHECK — {len(errors)} finding(s):")
        for e in errors:
            print(" -", e)
        return 1
    print(f"CANDIDATE SURFACE CHECK OK — {len(actual_files)} files, bounded validator, "
          f"non-canonical, does not affect the AICE registry.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
