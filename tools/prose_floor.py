#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/prose_floor.py - the prose floor. Reader-facing docs stay terse;
rationale lives in records, not inline.

    python tools/prose_floor.py                  # lint this tree
    python tools/prose_floor.py --root <path>    # lint another tree
    python tools/prose_floor.py --public-root <path>  # also fail if a
                                                 # records dir shipped there
    python tools/prose_floor.py --selftest       # incl. forced-red controls

    exit 0  PROSE_FLOOR: CLEAN, with denominators
    exit 1  PROSE_FLOOR: FAIL, naming each file and finding
    exit 2  abort (no root, no manifest) - never shared with a real verdict

Expectation source: prose-budgets.json (registered in checks-registry.json).
Scope: *.md at the root and in docs/ (not docs/walks/, not modules/).
Checks per budgeted file: word budget; long-sentence share; banned stock
phrases; em-dash density; jargon terms used without a GLOSSARY.md link.
An in-scope file absent from the manifest is a FAIL: new docs declare a
budget or an exemption in the change that adds them.
[record: owner ruling 2026-08-26, prose-floor quest; the program records run log]
"""
import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

REQUIRED_LINE = "PROSE_FLOOR"


def strip_non_prose(text: str) -> str:
    """Remove fenced code, tables, headings, and link-reference lines."""
    out, in_fence = [], False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or s.startswith("|") or s.startswith("#"):
            continue
        if re.match(r"^\[[^\]]+\]:\s", s):
            continue
        out.append(line)
    return "\n".join(out)


def sentences(prose: str):
    parts = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", prose))
    return [p for p in parts if len(p.split()) >= 3]


def lint_file(root: Path, rel: str, budget: int, cfg: dict):
    """Return a list of finding strings for one budgeted file."""
    p = root / rel
    findings = []
    if not p.exists():
        return [f"listed in manifest but absent: {rel}"]
    raw = p.read_text(encoding="utf-8", errors="replace")
    prose = strip_non_prose(raw)
    words = len(prose.split())
    lim = cfg["limits"]
    if words > budget:
        findings.append(f"over budget: {words} words > {budget}")
    sents = sentences(prose)
    long_max = lim["long_sentence_words"]
    longs = [s for s in sents if len(s.split()) > long_max]
    if len(sents) >= lim["min_sentences_for_share"]:
        share = len(longs) / len(sents)
        if share > lim["long_sentence_share_max"]:
            findings.append(
                f"long sentences: {len(longs)}/{len(sents)} "
                f"({share:.0%}) exceed {long_max} words "
                f"(max share {lim['long_sentence_share_max']:.0%}); "
                f"first: \"{longs[0][:80]}...\"")
    low = prose.lower()
    for phrase in cfg["banned_phrases"]:
        if phrase in low:
            findings.append(f"banned phrase: \"{phrase}\"")
    if words:
        dashes = prose.count("—")
        density = dashes * 100.0 / words
        if density > lim["emdash_per_100_words_max"]:
            findings.append(
                f"em-dash density: {dashes} in {words} words "
                f"({density:.1f}/100 > {lim['emdash_per_100_words_max']})")
    if rel != "GLOSSARY.md":
        used = [t for t in cfg["jargon_requires_glossary"]
                if re.search(r"\b" + re.escape(t.replace('_', '_')) + r"\b",
                             low)]
        if used and "glossary.md" not in raw.lower():
            findings.append(
                "jargon without a GLOSSARY.md link: " + ", ".join(used))
    return findings


def check_ratchet(old_budgets: dict, new_budgets: dict):
    """Budgets only ratchet down: any budget higher than its committed
    (HEAD) value is a finding. New keys are allowed."""
    out = []
    for k, old in old_budgets.items():
        new = new_budgets.get(k)
        if new is not None and new > old:
            out.append((k, f"budget raised {old} -> {new}: budgets only "
                           f"ratchet down (raising one takes an owner "
                           f"ruling recorded in the same change)"))
    return out


def head_budgets(root: Path):
    """The budgets in the committed prose-budgets.json at HEAD, or None
    when there is no git, no HEAD, or no committed manifest yet."""
    import subprocess
    try:
        r = subprocess.run(["git", "-C", str(root), "show",
                            "HEAD:prose-budgets.json"],
                           capture_output=True, text=True, timeout=30)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout).get("budgets", {})
    except Exception:
        return None


def scan(root: Path, public_root=None):
    """Return (findings_by_file, counts). Raises FileNotFoundError on a
    missing manifest."""
    cfg = json.loads((root / "prose-budgets.json").read_text(
        encoding="utf-8"))
    in_scope = sorted(
        [p.name for p in root.glob("*.md")] +
        ["docs/" + p.name for p in (root / "docs").glob("*.md")]
        if (root / "docs").exists() else [p.name for p in root.glob("*.md")])
    findings = {}
    budgeted = exempt = 0
    for rel in in_scope:
        if rel in cfg["budgets"]:
            budgeted += 1
            f = lint_file(root, rel, cfg["budgets"][rel], cfg)
            if f:
                findings[rel] = f
        elif rel in cfg["exempt"]:
            exempt += 1
        else:
            findings[rel] = ["not in prose-budgets.json: declare a budget "
                             "or an exemption in the change that adds it"]
    if public_root is not None:
        rec = Path(public_root) / "docs" / "records"
        if rec.exists():
            findings["docs/records/"] = [
                "records directory present in the public tree; records "
                "never ship to the public mirror"]
    old = head_budgets(root)
    if old is not None:
        for k, why in check_ratchet(old, cfg["budgets"]):
            findings.setdefault(k, []).append(why)
    return findings, budgeted, exempt


def selftest() -> int:
    cases = {
        "over-budget.md": ("word " * 200, ["over budget"]),
        "long-sentences.md": (
            " ".join(["this planted control sentence deliberately runs on "
                      "and on and on with far too many words in one single "
                      "unbroken span so that it sails well past the long "
                      "sentence ceiling the prose floor enforces today "
                      "okay."] * 12),
            ["long sentences"]),
        "banned.md": ("Short doc. This check has earned its keep. Done.",
                      ["banned phrase"]),
        "jargon.md": ("Short doc. The escape rate fell again this round.",
                      ["jargon without a GLOSSARY.md link"]),
        "clean.md": ("Short doc. It passes. See GLOSSARY.md for terms.", []),
    }
    failures = []
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "docs").mkdir()
        manifest = {
            "limits": {"long_sentence_words": 30,
                       "long_sentence_share_max": 0.10,
                       "min_sentences_for_share": 10,
                       "emdash_per_100_words_max": 1.2},
            "budgets": {k: 100 for k in cases},
            "exempt": {},
            "banned_phrases": ["earned its keep"],
            "jargon_requires_glossary": ["escape rate"],
        }
        (root / "prose-budgets.json").write_text(json.dumps(manifest),
                                                 encoding="utf-8")
        for name, (body, _) in cases.items():
            (root / name).write_text(body, encoding="utf-8")
        (root / "docs" / "unregistered.md").write_text("Surprise.",
                                                       encoding="utf-8")
        found, _, _ = scan(root)
        for name, (_, expected) in cases.items():
            got = found.get(name, [])
            for marker in expected:
                if not any(marker in g for g in got):
                    failures.append(f"{name}: expected a '{marker}' red")
            if not expected and got:
                failures.append(f"{name}: expected clean, got {got}")
        if "docs/unregistered.md" not in found:
            failures.append("unregistered doc: expected a red")
        pub = root / "pub" / "docs" / "records"
        pub.mkdir(parents=True)
        found2, _, _ = scan(root, public_root=root / "pub")
        if "docs/records/" not in found2:
            failures.append("public records dir: expected a red")
    if not check_ratchet({"a.md": 100}, {"a.md": 150}):
        failures.append("ratchet: raised budget expected a red")
    if check_ratchet({"a.md": 100}, {"a.md": 90, "new.md": 500}):
        failures.append("ratchet: lowered budget + new key must pass")
    n = len(cases) + 4
    if failures:
        print(f"{REQUIRED_LINE} SELFTEST: FAIL - " + "; ".join(failures))
        return 1
    print(f"{REQUIRED_LINE} SELFTEST: PASS - {n} controls "
          f"(forced-red cases and the clean case all behaved)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent
                                          .parent))
    ap.add_argument("--public-root", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    root = Path(a.root)
    if not root.exists():
        print(f"{REQUIRED_LINE}: ABORT - root not found: {root}")
        return 2
    try:
        findings, budgeted, exempt = scan(root, a.public_root)
    except FileNotFoundError:
        print(f"{REQUIRED_LINE}: ABORT - no prose-budgets.json at {root}")
        return 2
    for rel in sorted(findings):
        for f in findings[rel]:
            print(f"  {rel}: {f}")
    if findings:
        total = sum(len(v) for v in findings.values())
        print(f"{REQUIRED_LINE}: FAIL - {total} finding(s) across "
              f"{len(findings)} file(s); {budgeted} budgeted, "
              f"{exempt} exempt")
        return 1
    print(f"{REQUIRED_LINE}: CLEAN - {budgeted} docs within budget, "
          f"{exempt} exempt by name")
    return 0


if __name__ == "__main__":
    sys.exit(main())
