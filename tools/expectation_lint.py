#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/expectation_lint.py - the self-reference lint.

    python tools/expectation_lint.py                # lint the kit's registry
    python tools/expectation_lint.py --registry <f> # lint another one
    python tools/expectation_lint.py --selftest     # incl. both negative controls
    python tools/expectation_lint.py --list         # print the registry, waivers first

    exit 0  clean - every check reads its expectation from something other
            than its own subject, or says out loud why it cannot
    exit 1  at least one unwaived self-reference, or a waiver with no reason
    exit 2  abort (no registry, unreadable, bad schema)

==========================================================================
WHY THIS EXISTS - and why it is a LINT rather than another paragraph
==========================================================================
Six LLM-persona adoption walks found eight defects, and after the fourth it
was obvious they were one defect wearing different hats:

  1. the judges gate read only git's stdout, so "no repository" read as clean
  2. the runner resolved its root from its own location, so it judged the
     wrong tree and said the tree was fine
  3. --selftest named the example gates the documentation says to delete
  4. kit.config was not in the judge surface, so the config that parameterises
     the judges could change without invalidating them
  5. fixture j built its payload from the very key it was guarding
  6. the armed check trusted the settings file to prove the settings file
  7. NONE was read as a value, so a placeholder configured a rule that
     guarded nothing
  8. the statusLine value broke the JSON it was substituted into

THE CLASS: **a check whose expectation comes from the same artifact it is
asserting about cannot see a change to that artifact.** Fixture and defect
move together. The check stays green, and its greenness means nothing.

This kit's own operating architecture has a standing rule for exactly this
situation - when a prose rule fails, promote it a layer or accept it with the
residual named. That rule has now fired eight times against the same class,
which makes promotion overdue. So the design question ("where does this
check's expectation come from?") becomes a **declaration every check must
make**, and a lint that fails when the answer is "from the thing it is
checking".

==========================================================================
WHAT IS AND IS NOT IN SCOPE
==========================================================================
IN scope: expectations derived from config files, settings files, or any
other artifact that is ALSO what the check asserts about.

OUT of scope: **inline literal expectations for pure functions.** A selftest
that says `assert judge_gate(spec, "0/0 passed")[0] is False` is not
self-referential in any interesting sense - the literal is the specification,
written by hand, and it does not move when the code does. Register those with
`expectation_from: "inline"`, which can never collide with a subject.

A WAIVER IS NOT A FAILURE. Some checks are legitimately self-referential and
the honest response is to say so, name what covers the gap instead, and print
it on every run. What is forbidden is the SILENT case - and a waiver with an
empty reason is treated as the silent case, because it is one.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = KIT / "checks-registry.json"

GREEN, RED, YELLOW, BOLD, RESET = (
    "\033[32m", "\033[31m", "\033[33m", "\033[1m", "\033[0m")
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REQUIRED = {"id", "subject", "expectation_from"}
INLINE = {"inline", "inline-literal", "none"}


# ==========================================================================
# THE PURE LAYER
# ==========================================================================
def artifact(spec: str) -> str:
    """The artifact half of a subject/source string.

    Entries may name a key inside a file - `kit.config:FORBIDDEN_SPAWN_TIER` -
    because that is the honest description of what a check is about. The
    comparison is on the ARTIFACT, since that is what moves: editing the file
    moves both the key and any expectation read from it."""
    return (spec or "").split(":", 1)[0].strip().replace("\\", "/").lower()


def lint_entry(e: dict):
    """(problem_or_None, waiver_note_or_None). Pure."""
    missing = REQUIRED - set(e)
    if missing:
        return (f"{e.get('id', '<no id>')}: missing required field(s) "
                f"{sorted(missing)}"), None
    eid = e["id"]
    subj, src = artifact(e["subject"]), artifact(e["expectation_from"])
    waived = bool(e.get("waived"))
    reason = (e.get("reason") or "").strip()

    if src in INLINE:
        if waived:
            return (f"{eid}: waived, but its expectation is inline - a waiver "
                    f"here hides nothing and only trains readers to skim "
                    f"waivers"), None
        return None, None

    if subj != src:
        return None, None

    # Self-referential from here down.
    if not waived:
        return (f"{eid}: SELF-REFERENTIAL - expectation is read from "
                f"{e['expectation_from']!r}, which is the same artifact as the "
                f"subject {e['subject']!r}. This check cannot see a change to "
                f"the thing it is checking. Fix it, or waive it with a reason."
                ), None
    if not reason:
        return (f"{eid}: waived with NO REASON. A waiver without a reason is "
                f"the silent case wearing a label."), None
    return None, f"{eid}: WAIVED - {reason}"


def lint(entries: list):
    """(problems, waivers). Pure."""
    problems, waivers, seen = [], [], set()
    for e in entries:
        if not isinstance(e, dict):
            problems.append(f"registry entry is not an object: {e!r}")
            continue
        eid = e.get("id")
        if eid in seen:
            problems.append(f"{eid}: duplicate id - one of these two is not "
                            f"being read by anybody")
        seen.add(eid)
        prob, waiver = lint_entry(e)
        if prob:
            problems.append(prob)
        if waiver:
            waivers.append(waiver)
    return problems, waivers


# The fixture table's ids. `{1,3}` rather than a single letter because the
# suite outgrew the alphabet when ten bypass fixtures landed; `("aa", ...)` is
# an ordinary id and an id the lint must still be able to recover.
FIXTURE_ID = re.compile(r'^\s*\("([a-z]{1,3})",\s', re.M)
# The doctor's check table. Same idea, different family: `("doctor:version",`.
DOCTOR_ID = re.compile(r'^\s*\("(doctor:[a-z0-9-]+)",\s', re.M)
# The escape-rate tool's NEGATIVE CONTROLS, a third family. Its ids are the
# `NC(vii)` labels its selftest prints. A new tool arriving with a set of
# unregistered checks grows this kit's own named blind spot by that many in
# one commit - the argument that made the doctor the second family. The
# controls are the part of that tool most at risk from a later tidy-up: they
# are the only reason its green means anything, and a suite that has never
# been red proves nothing. Registered as `escape:nc-vii`.
ESCAPE_ID = re.compile(r'\bNC\(([ivx]+)\)', re.M)
# A FOURTH family: the gate-line adapter's GOLDEN FIXTURES, whose ids are the
# `GOLDEN(all-pass)` labels its selftest prints - one per captured pytest run.
# Same argument as the escape controls, one degree stronger: these are the only
# expectations in that tool that did not come from its author. They are what
# pytest actually reported, so a case quietly dropped from the selftest takes a
# real captured outcome out of the net while the check count still looks
# healthy. Registered as `golden:all-pass`.
GOLDEN_ID = re.compile(r'\bGOLDEN\(([a-z0-9-]+)\)')
# A FIFTH family: the citation lint's NEGATIVE CONTROLS, whose ids are the
# `CITE(wrapped-quote)` labels its selftest prints. Same argument as the escape
# controls and the golden fixtures - a tool arriving in one commit with a set of
# unregistered checks grows this kit's named blind spot by that many at once.
# One degree stronger again: two of those controls are the only thing keeping
# that tool from MANUFACTURING findings (a quotation that wraps across a line
# must still be found), so a control quietly dropped there turns the checker
# into the defect it was built to catch. Registered as `citation:wrapped-quote`.
CITATION_ID = re.compile(r'\bCITE\(([a-z0-9-]+)\)')
# A SIXTH family: the count lint's NEGATIVE CONTROLS, whose ids are the
# `COUNT(stale-cross-doc)` labels its selftest prints. Same argument again, and
# the same one-degree-stronger clause the citation family carries: three of
# those controls are the only thing keeping that tool from MANUFACTURING
# findings against counts that are correct (a wrapped command counts once; a
# number inside a paragraph is not a count of the block below it). Registered
# as `count:wrapped-command`.
COUNT_ID = re.compile(r'\bCOUNT\(([a-z0-9-]+)\)')
# A SEVENTH family: the same tool's QUANTIFIER LAYER, added in round 30, whose
# ids are the `QUANT(f1-shape)` labels its selftest prints. It is its own
# family rather than more `count:` rows because an id recovered by one pattern
# and registered under another prefix is a cross-check that silently matches
# nothing - and because the layer answers a different question (is the
# universal claim true of every element) and shares only the target-location
# machinery. Its controls carry the same one-degree-stronger clause: five of
# them are the only thing keeping the layer from MANUFACTURING findings, and
# one of those five was written because the first live run did exactly that.
# Registered as `quant:f1-shape`.
QUANT_ID = re.compile(r'\bQUANT\(([a-z0-9-]+)\)')
# An EIGHTH family: the skim lint's NEGATIVE CONTROLS, added in round 31, whose
# ids are the `SKIM(boundary)` labels its selftest prints. Same argument as the
# seven families before it - a tool arriving in one commit with a set of
# unregistered checks grows this kit's named blind spot by that many at once -
# and it carries the one-degree-stronger clause too: that tool's window is a
# NUMBER, and a number's edge is the first thing a later edit moves. Six of its
# controls exist only to keep it from manufacturing findings against a front
# door that is fine, and two of them bind the window's derivation to the
# document it was derived from. Registered as `skim:boundary`.
SKIM_ID = re.compile(r'\bSKIM\(([a-z0-9-]+)\)')
# A NINTH family: the repeat lint's NEGATIVE CONTROLS, added in round 32, whose
# ids are the `REPEAT(relocation)` labels its selftest prints. Same argument as
# every family before it, and the same one-degree-stronger clause: that
# tool's threshold is a NUMBER derived from a measurement, and eight of its
# controls exist only to stop it going red on ordinary prose that two documents
# in a 63-document tree happen to share. Registered as `repeat:relocation`.
REPEAT_ID = re.compile(r'\bREPEAT\(([a-z0-9-]+)\)')
# A TENTH family: THIS TOOL'S OWN seen-red controls, added in round 32, whose
# ids are the `SEENRED(absent)` labels the selftest below prints. It is the
# first family recovered from this file rather than from another tool, and that
# is not the self-reference this lint exists to catch: the SUBJECT is the
# registry on disk and the EXPECTATION is a literal in this source, which are
# two artifacts, in the same way every `expectation_from: "inline"` row is.
# Registered as `seenred:absent`.
SEENRED_ID = re.compile(r'\bSEENRED\(([a-z0-9-]+)\)')


def coverage_gaps(fixtures_src: str, entries: list,
                  pattern=FIXTURE_ID, family: str = "fixture"):
    """Registered checks the source has, and source checks the registry lacks.

    THE LINT'S OWN BLIND SPOT, closed as far as it can be: a registry can only
    judge what is written in it, so the failure mode it cannot see is an entry
    that is simply absent. For a family whose ids are recoverable from the
    source, absence IS detectable, and this is that cross-check. The families
    it runs over are FAMILIES below (ten of them) - that tuple is the
    authority, and
    `--selftest` asserts the prose agrees with it rather than restating a count
    here that would go stale (it already had: this paragraph said "three" while
    the tuple held four). The doctor was the reason to generalise it - a
    diagnostic tool with ten unregistered checks would have grown the kit's
    named blind spot by ten in one commit - and the escape-rate tool, the
    gate-line adapter and the citation lint are the same argument again.

    Everything outside those families still relies on the author adding a row -
    stated in KNOWN-ISSUES as a residual rather than papered over."""
    in_src = set(pattern.findall(fixtures_src or ""))
    prefix = family + ":"
    registered = {e.get("id", "")[len(prefix):]
                  for e in entries
                  if isinstance(e, dict) and e.get("id", "").startswith(prefix)}
    if family == "doctor":
        # The doctor's ids already carry the family, so recovered id and
        # registry id are the same string.
        in_src = {i[len("doctor:"):] for i in in_src}
    if family == "escape":
        # The recovered id is a roman numeral from an `NC(vii)` label; the
        # registry spells it `escape:nc-vii`.
        in_src = {"nc-" + i for i in in_src}
    return sorted(in_src - registered), sorted(registered - in_src)


# The families the cross-check runs over, and the file each is recovered from.
# Held as data rather than as a loop body so that `--selftest` can assert the
# set is what the docstring and the waiver reason claim it is - a fifth family
# added to the loop and left out of the prose is the same silent narrowing this
# lint exists to catch.
FAMILIES = (
    ("modules/02-enforcement/hook_fixtures.py", FIXTURE_ID, "fixture"),
    ("tools/kit_doctor.py", DOCTOR_ID, "doctor"),
    ("modules/04-ledgers/escape_rate.py", ESCAPE_ID, "escape"),
    ("modules/03-verification/gate_line.py", GOLDEN_ID, "golden"),
    ("tools/citation_lint.py", CITATION_ID, "citation"),
    ("tools/count_lint.py", COUNT_ID, "count"),
    ("tools/count_lint.py", QUANT_ID, "quant"),
    ("tools/skim_lint.py", SKIM_ID, "skim"),
    ("tools/repeat_lint.py", REPEAT_ID, "repeat"),
    ("tools/expectation_lint.py", SEENRED_ID, "seenred"),
)


# ==========================================================================
# THE SEEN-RED FIELD (round 32). Three adversarial batteries in a row convicted
# the same sentence - "every check has been seen to fail on purpose" - and the
# conviction was always the same: no instrument in this kit could answer the
# question for any single check. The registry now carries `seen_red` on every
# row, and this is the layer that keeps it there.
#
# WHAT IS CHECKED, and it is deliberately narrow: PRESENCE and SHAPE.
#
#   - An ABSENT field is a PROBLEM. That is the whole point. This kit's state
#     word doctrine says "the check did not run" and "the check passed" must
#     never render alike, and a row with no seen_red renders exactly like a row
#     whose red was recorded yesterday.
#   - The value NEVER is NOT a problem. A check with no recorded red is an
#     honest state of the record and the register publishes how many there are.
#     Making NEVER red would buy a permanently red lint whose red means "the
#     backfill is unfinished", which is a red people learn to skip - the same
#     argument count_lint's own docstring makes about PARTIAL runs.
#   - Anything else must be an ISO YYYY-MM-DD date. A free-text value is a
#     problem, because a field that accepts prose stops being answerable.
#
# WHAT IS NOT CHECKED, stated so nobody reads more into a green than is there:
# whether the date is TRUE. Nothing in this kit observes a check going red and
# writes the date itself. seen_red is an author's claim, in the same class as
# expectation_from, and it is exactly as trustworthy. What the field buys is
# that the claim now has to be made per check rather than asserted once over
# all of them in a front-door sentence.
SEEN_RED_NEVER = "NEVER"
ISO_DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def seen_red_problems(entries: list):
    """(problems, dated, never) for the seen-red field over `entries`.

    Pure - it decides a list of dicts - so the controls below test the rule
    rather than the registry that happens to be on disk today."""
    problems, dated, never = [], 0, 0
    for e in entries:
        cid = e.get("id", "<no id>")
        if "seen_red" not in e:
            problems.append(f"{cid!r} carries no seen_red field - an absent "
                            f"field renders like a recorded red. Write a date "
                            f"or the literal {SEEN_RED_NEVER}")
            continue
        val = e.get("seen_red")
        if val == SEEN_RED_NEVER:
            never += 1
            continue
        if isinstance(val, str) and ISO_DATE.match(val):
            dated += 1
            continue
        problems.append(f"{cid!r} has seen_red {val!r}, which is neither "
                        f"{SEEN_RED_NEVER} nor an ISO YYYY-MM-DD date")
    return problems, dated, never


def load(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("checks"), list):
        return data["checks"]
    raise ValueError("registry must be a list, or an object with a 'checks' list")


def selftest() -> int:
    ok_all, n = True, 0

    def check(label, got, want):
        nonlocal ok_all, n
        n += 1
        good = got == want
        ok_all = ok_all and good
        print(f"  [{'PASS' if good else 'FAIL'}] {label}"
              + ("" if good else f"\n        got  {got!r}\n        want {want!r}"))

    print(f"{BOLD}=== A. the two NEGATIVE CONTROLS: the class, reconstructed ==={RESET}")
    # (i) the fixture-j pattern - the payload built from the guarded key.
    nc_j = {"id": "nc:fixture-j-pattern",
            "subject": "kit.config:FORBIDDEN_SPAWN_TIER",
            "expectation_from": "kit.config"}
    probs, _ = lint([nc_j])
    check("NC(i) the fixture-j pattern is FLAGGED un-waived", len(probs), 1)
    check("...and the message names the class",
          "SELF-REFERENTIAL" in probs[0], True)
    check("...and it names both artifacts",
          "kit.config" in probs[0] and "FORBIDDEN_SPAWN_TIER" in probs[0], True)

    # (ii) the SB-A pattern - the armed check trusting the file it validates.
    nc_a = {"id": "nc:armed-pattern",
            "subject": ".claude/settings.json",
            "expectation_from": ".claude/settings.json"}
    probs, _ = lint([nc_a])
    check("NC(ii) the armed-check pattern is FLAGGED un-waived", len(probs), 1)
    check("...and the message names the class",
          "SELF-REFERENTIAL" in probs[0], True)

    probs, _ = lint([nc_j, nc_a])
    check("both fire together, independently", len(probs), 2)

    print(f"\n{BOLD}=== B. waivers: visible, and only with a reason ==={RESET}")
    waived = dict(nc_j, waived=True, reason="covered structurally instead")
    probs, waivers = lint([waived])
    check("a waiver with a reason clears the lint", probs, [])
    check("...and is PRINTED, not swallowed", len(waivers), 1)
    check("...with the reason in the line",
          "covered structurally instead" in waivers[0], True)
    probs, _ = lint([dict(nc_j, waived=True)])
    check("a waiver with NO reason is a failure", len(probs), 1)
    check("...and says why", "silent case" in probs[0], True)
    probs, _ = lint([dict(nc_j, waived=True, reason="   ")])
    check("whitespace is not a reason", len(probs), 1)

    print(f"\n{BOLD}=== C. what is deliberately OUT of scope ==={RESET}")
    check("an inline literal expectation is fine",
          lint([{"id": "x", "subject": "verify.py", "expectation_from": "inline"}])[0],
          [])
    check("different artifacts are fine",
          lint([{"id": "x", "subject": "examples/suite.py",
                 "expectation_from": "verify.py"}])[0], [])
    check("a key-scoped subject still compares on the ARTIFACT",
          artifact("kit.config:LANE_TIER"), "kit.config")
    check("path separators do not defeat the comparison",
          artifact(".claude\\settings.json"), ".claude/settings.json")
    check("case does not defeat it", artifact("Kit.Config"), "kit.config")
    check("waiving an inline entry is itself flagged (it hides nothing)",
          len(lint([{"id": "x", "subject": "v.py", "expectation_from": "inline",
                     "waived": True, "reason": "r"}])[0]), 1)

    print(f"\n{BOLD}=== D. schema and bookkeeping ==={RESET}")
    check("a missing field is caught",
          "missing required field" in lint([{"id": "x"}])[0][0], True)
    check("a duplicate id is caught",
          any("duplicate id" in p for p in lint([
              {"id": "d", "subject": "a", "expectation_from": "inline"},
              {"id": "d", "subject": "b", "expectation_from": "inline"}])[0]),
          True)
    check("a non-object entry is caught",
          len(lint(["not an entry"])[0]), 1)

    print(f"\n{BOLD}=== E. the lint's own blind spot, narrowed ==={RESET}")
    src = '        ("z", "a brand-new fixture nobody registered", {"deny"},\n'
    missing, stale = coverage_gaps(src, [])
    check("a fixture in the source but not the registry is reported",
          missing, ["z"])
    missing, stale = coverage_gaps("", [{"id": "fixture:q", "subject": "s",
                                         "expectation_from": "inline"}])
    check("a registry entry with no fixture behind it is reported",
          stale, ["q"])
    check("a multi-letter fixture id is still recovered (the suite outgrew "
          "the alphabet)",
          coverage_gaps('        ("aa", "the eleventh bypass", {"deny"},\n',
                        [])[0], ["aa"])

    # The SECOND family. Ten unregistered doctor checks would have grown the
    # kit's own named blind spot by ten in a single commit, so the cross-check
    # runs over the doctor's table too.
    doc_src = '        ("doctor:vacuous-gate", "gates that cannot fail",\n'
    check("a doctor check in the source but not the registry is reported",
          coverage_gaps(doc_src, [], DOCTOR_ID, "doctor")[0],
          ["vacuous-gate"])
    check("...and a registered doctor check with no code behind it is too",
          coverage_gaps("", [{"id": "doctor:gone", "subject": "s",
                              "expectation_from": "inline"}],
                        DOCTOR_ID, "doctor")[1], ["gone"])
    check("...and a registered doctor check that IS in the source is clean",
          coverage_gaps(doc_src, [{"id": "doctor:vacuous-gate",
                                   "subject": "s",
                                   "expectation_from": "inline"}],
                        DOCTOR_ID, "doctor"), ([], []))

    # The THIRD family: the escape-rate tool's negative controls. They are the
    # only reason that tool's green means anything, and a later tidy-up that
    # deletes one is exactly the silent narrowing this lint exists to catch.
    esc_src = '        check("NC(vii) a HALF-declared uncountable row ABORTS",\n'
    check("an escape-rate negative control in the source but not the "
          "registry is reported",
          coverage_gaps(esc_src, [], ESCAPE_ID, "escape")[0], ["nc-vii"])
    check("...and a registered control with no code behind it is too",
          coverage_gaps("", [{"id": "escape:nc-xx", "subject": "s",
                              "expectation_from": "inline"}],
                        ESCAPE_ID, "escape")[1], ["nc-xx"])
    # The FOURTH family: the gate-line adapter's golden fixtures. Each one is
    # a real captured pytest outcome, so dropping a case from the selftest
    # removes an expectation nobody in this kit wrote.
    gold_src = ('        check(f"GOLDEN({cid}) the pure layer rebuilds the '
                'captured lines exactly",\n')
    check("a golden fixture case in the source but not the registry is "
          "reported",
          coverage_gaps('  check("GOLDEN(collapsed-collection) x",\n', [],
                        GOLDEN_ID, "golden")[0], ["collapsed-collection"])
    check("...and a registered golden case with no code behind it is too",
          coverage_gaps("", [{"id": "golden:gone", "subject": "s",
                              "expectation_from": "inline"}],
                        GOLDEN_ID, "golden")[1], ["gone"])
    check("...and an f-string label is still recovered (the selftest builds "
          "them from the case id)",
          coverage_gaps(gold_src.replace("{cid}", "subset"), [],
                        GOLDEN_ID, "golden")[0], ["subset"])
    check("CITE-family: an unregistered citation control is reported",
          coverage_gaps('    check("CITE(wrapped-quote): x",\n', [],
                        CITATION_ID, "citation")[0], ["wrapped-quote"])
    check("...and a registered citation control with no code behind it is too",
          coverage_gaps("", [{"id": "citation:gone", "subject": "s",
                              "expectation_from": "inline"}],
                        CITATION_ID, "citation")[1], ["gone"])
    # The SIXTH family: the count lint's negative controls. Three of them are
    # the only thing keeping that tool from manufacturing findings against
    # counts that are right, which is the same argument the citation family
    # made and the reason both are cross-checked rather than trusted.
    check("COUNT-family: an unregistered count control is reported",
          coverage_gaps('    check("COUNT(wrapped-command): x",\n', [],
                        COUNT_ID, "count")[0], ["wrapped-command"])
    check("...and a registered count control with no code behind it is too",
          coverage_gaps("", [{"id": "count:gone", "subject": "s",
                              "expectation_from": "inline"}],
                        COUNT_ID, "count")[1], ["gone"])
    # The EIGHTH family: the skim lint's negative controls. Same argument as
    # every family before it, and the same reason it is its own prefix rather
    # than more `count:` rows - an id recovered by one pattern and registered
    # under another is a cross-check that silently matches nothing.
    check("SKIM-family: an unregistered skim control is reported",
          coverage_gaps('    check("SKIM(boundary): x",\n', [],
                        SKIM_ID, "skim")[0], ["boundary"])
    check("...and a registered skim control with no code behind it is too",
          coverage_gaps("", [{"id": "skim:gone", "subject": "s",
                              "expectation_from": "inline"}],
                        SKIM_ID, "skim")[1], ["gone"])
    check("the cross-check runs over TEN families, and the list is the one "
          "the waiver reason names",
          [f for _, _, f in FAMILIES],
          ["fixture", "doctor", "escape", "golden", "citation", "count",
           "quant", "skim", "repeat", "seenred"])
    check("REPEAT-family: an unregistered repeat control is reported",
          coverage_gaps('    check("REPEAT(relocation): x",\n', [],
                        REPEAT_ID, "repeat")[0], ["relocation"])
    check("SEENRED-family: an unregistered seen-red control is reported",
          coverage_gaps('    check("SEENRED(absent): x",\n', [],
                        SEENRED_ID, "seenred")[0], ["absent"])
    check("...and the quantifier family recovers its own label shape, not the "
          "count family's",
          (coverage_gaps('    check("QUANT(f1-shape): x",\n', [],
                         QUANT_ID, "quant")[0],
           coverage_gaps('    check("COUNT(true-count): x",\n', [],
                         QUANT_ID, "quant")[0]),
          (["f1-shape"], []))

    check("...and a registered control that IS in the source is clean",
          coverage_gaps(esc_src, [{"id": "escape:nc-vii", "subject": "s",
                                   "expectation_from": "inline"}],
                        ESCAPE_ID, "escape"), ([], []))

    print()
    print(f"{BOLD}=== D. the SEEN-RED field: the forced-red half ==={RESET}")
    # THE FORCED RED. A row with no seen_red field must be a problem, because
    # an absent field renders exactly like a recorded red - which is the
    # three-battery conviction this field answers.
    probs, dated, never = seen_red_problems(
        [{"id": "x:no-field", "subject": "s", "expectation_from": "inline"}])
    check("SEENRED(absent): a row with NO seen_red field is a PROBLEM",
          (len(probs), dated, never), (1, 0, 0))
    check("...and the message names the field and both legal values",
          ("seen_red" in probs[0] and "NEVER" in probs[0]), True)
    probs, _, _ = seen_red_problems(
        [{"id": "x:prose", "subject": "s", "expectation_from": "inline",
          "seen_red": "yes, ages ago"}])
    check("SEENRED(free-text): a value that is neither NEVER nor an ISO date "
          "is a PROBLEM - a field that accepts prose stops being answerable",
          (len(probs), "neither NEVER nor an ISO" in probs[0]), (1, True))
    probs, _, _ = seen_red_problems(
        [{"id": "x:sloppy", "subject": "s", "expectation_from": "inline",
          "seen_red": "2026-8-5"}])
    check("SEENRED(loose-date): ...and so is a date that is not zero-padded "
          "ISO, because two spellings of a date are two fields",
          len(probs), 1)

    print()
    print(f"{BOLD}=== E. the SEEN-RED field: the controls that keep it from "
          f"manufacturing findings ==={RESET}")
    # THE MOST IMPORTANT CONTROL IN THIS SECTION. NEVER is the honest value for
    # an unbackfilled row and MUST stay green, or this lint goes permanently
    # red over an unfinished backfill and its red stops being read.
    probs, dated, never = seen_red_problems(
        [{"id": "x:never", "subject": "s", "expectation_from": "inline",
          "seen_red": "NEVER"}])
    check("SEENRED(never-is-clean): NEVER is an honest state of the RECORD and "
          "is NOT a problem - it is counted, not failed",
          (probs, dated, never), ([], 0, 1))
    probs, dated, never = seen_red_problems(
        [{"id": "x:dated", "subject": "s", "expectation_from": "inline",
          "seen_red": "2026-08-25"}])
    check("SEENRED(date-is-clean): an ISO date passes and is counted as "
          "backfilled",
          (probs, dated, never), ([], 1, 0))
    probs, dated, never = seen_red_problems([
        {"id": "a", "seen_red": "NEVER"},
        {"id": "b", "seen_red": "2026-08-25"},
        {"id": "c"},
    ])
    check("SEENRED(denominator): the two counts are the denominator the "
          "summary prints, and a row that failed is in NEITHER count",
          (len(probs), dated, never), (1, 1, 1))

    print()
    print(f"{BOLD}=== F. the SEEN-RED field against the registry it ships "
          f"with ==={RESET}")
    # A rule that matches nothing proves nothing - the same assertion every
    # other family in this file makes about itself.
    try:
        live = load(DEFAULT_REGISTRY)
    except Exception:
        live = []
    lp, ld, ln_ = seen_red_problems(live)
    check("every shipped registry row carries the field", lp, [])
    check("...and the shipped registry has BOTH kinds of row, so neither "
          "branch of the rule is untested by the tree it ships in",
          (ld > 0, ln_ > 0, ld + ln_ == len(live)), (True, True, True))

    print()
    print((GREEN if ok_all else RED)
          + f"EXPECTATION-LINT SELFTEST: {'PASS' if ok_all else 'FAIL'} "
            f"— {n} checks" + RESET)
    return 0 if ok_all else 1


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Fail when a check reads its expectation from its own subject.")
    ap.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    reg = Path(a.registry)
    try:
        entries = load(reg)
    except FileNotFoundError:
        print(f"{RED}ABORT: no registry at {reg}{RESET}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"{RED}ABORT: {reg} is not a usable registry: {e}{RESET}",
              file=sys.stderr)
        return 2

    problems, waivers = lint(entries)

    for rel, pattern, family in FAMILIES:
        src_path = KIT / rel
        if not src_path.is_file():
            continue
        try:
            missing, stale = coverage_gaps(
                src_path.read_text(encoding="utf-8"), entries, pattern, family)
        except OSError:
            missing, stale = [], []
        name = src_path.name
        for m in missing:
            problems.append(f"{family} {m!r} exists in {name} and is NOT in "
                            f"the registry - an unregistered check is "
                            f"invisible to this lint")
        for st in stale:
            problems.append(f"registry names {family} {st!r}, which no longer "
                            f"exists in {name}")

    sr_problems, sr_dated, sr_never = seen_red_problems(entries)
    problems.extend(sr_problems)

    print(f"registry  : {reg}")
    print(f"checks    : {len(entries)} registered")
    # THE BACKFILL DENOMINATOR, ON EVERY RUN. A count of dated rows with no
    # denominator beside it is the watermelon this kit exists to refuse.
    sr_seen = sr_dated + sr_never
    sr_pct = (100.0 * sr_dated / sr_seen) if sr_seen else 0.0
    print(f"seen-red  : {sr_dated} of {sr_seen} row(s) carry a recorded "
          f"forced-red date ({sr_pct:.1f}%); {sr_never} are honest "
          f"{SEEN_RED_NEVER}s. NEVER is a state of the RECORD, not a claim "
          f"about history, and the backfill is not finished")
    if a.list:
        for e in sorted(entries, key=lambda x: (not x.get("waived"),
                                                x.get("id", ""))):
            mark = "WAIVED " if e.get("waived") else "       "
            print(f"  {mark}{e.get('id',''):<34} {e.get('subject','')}"
                  f"  <-  {e.get('expectation_from','')}")
    for w in waivers:
        print(f"{YELLOW}  {w}{RESET}")
    print(f"waivers   : {len(waivers)} (each printed above, every run - a "
          f"waiver nobody sees is not a waiver)")

    if problems:
        print()
        for p in problems:
            print(f"{RED}  SELF-REFERENCE  {p}{RESET}")
        print()
        print(f"{RED}EXPECTATION LINT: {len(problems)} PROBLEM(S) - exit 1{RESET}")
        return 1
    print(f"{GREEN}EXPECTATION LINT: PASS - {len(entries)} registry "
          f"entrie(s) checked, 0 self-referential - exit 0{RESET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
