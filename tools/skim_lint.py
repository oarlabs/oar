#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
tools/skim_lint.py - the skim lint. Does the front door hand the reader the
checkable artifacts before the reader stops reading?

    python tools/skim_lint.py                  # lint this kit's front door
    python tools/skim_lint.py --root <path>    # lint another tree
    python tools/skim_lint.py --door <name>    # a front door other than README.md
    python tools/skim_lint.py --selftest       # incl. the negative controls
    python tools/skim_lint.py --list           # print every mention seen, in
                                               # the window and outside it

    exit 0  every required artifact is reachable from inside the window. The
            summary line says CLEAN or PARTIAL and prints the denominator -
            see THE STATE WORD below
    exit 1  at least one required artifact is not reachable from inside the
            window, and the line names which
    exit 2  abort (no root, no front door, nothing to read). A run that could
            not read the door NEVER shares an exit code with a run that read
            it and found nothing wrong.

==========================================================================
WHY THIS EXISTS
==========================================================================
Round 29 (R29-3): the first person outside this program to read the kit
skimmed the front door, stopped, and never reached the escape table - the one
artifact on the repository that answers the question he had asked. The three
practitioner-legible artifacts (the escape table, the claims audit, the
published walk prompts) were each reachable only from inside a paragraph of
long-form prose, and two of them only from paragraphs several screens down.
Round 30's three cold evaluation reads reported the same routing failure, and
round 30 then restructured the front door - which is the point at which a
placement regression becomes cheap to introduce and expensive to notice.

The instrument that would have caught it was declined in round 29 and the
declination's reasoning is worth restating, because this tool is the narrow
half of it and NOT the whole thing:

    "the check would have to model a reader, and no instrument in this kit
     reads a document the way a reader does."

That is still true. What is checkable is PLACEMENT: whether the three
artifacts are named where a reader who stops early has already been. This
tool asks that question and nothing larger. It cannot tell you whether the
block is read; it can tell you whether the block is there.

Round 29 raised two objections to building even the narrow half. Both are
answered here rather than left standing:

  1. "a check whose expectation is a list this round wrote, which is the
     self-referential shape `expectation_lint` flags." The list of three
     artifacts is `REQUIRED` below, a hand-written literal - the
     SPECIFICATION, not a reading of the subject. It is registered
     `expectation_from: "inline"` for the same reason every selftest literal
     in this kit is: a literal does not move when the document moves, which
     is the entire property being bought. What WOULD be the flagged shape is
     a check that read the list of artifacts out of `README.md` and then
     asserted `README.md` names them; that check is vacuous and is not this
     one.
  2. "it would go green on a block nobody reads." Correct, and stated in
     OUT OF SCOPE below rather than argued with. Readership is measured by
     a reader, and the persona skim walk that would measure it is held as
     candidate acceptance evidence at the owner's gate.

==========================================================================
N, AND WHY IT IS NOT TUNED
==========================================================================
`WINDOW_LINES = 50`. The number models FIRST CONTACT: what a reader has in
front of them before the first scroll. Its derivation is printed on every run
so it can be argued with, and it is stated here in the order it was actually
performed, because a number chosen after measuring the document it judges is
a number tuned to pass:

  1. A viewport ESTIMATE, labelled as one, with its basis named: a
     1080-pixel-tall desktop browser window, of which roughly the top 200
     pixels are the forge's own chrome and file header, rendering body text
     at roughly 24 pixels a line. (1080 - 200) / 24 = 36 rendered lines of
     text before the first scroll. This is an estimate of a viewport, not a
     measurement of a reader, and this kit's own rule about unlabelled
     estimates is why that sentence is here.
  2. A SOURCE-LINE CONVERSION, because this tool counts source lines and a
     source line is not a rendered line. This repository's markdown is
     hard-wrapped near 78 columns with a blank line between blocks, so a
     window of source lines carries fewer lines of text than it holds: the
     measured blank-line share over the front door's opening was 22% when
     this tool was built. 36 / (1 - 0.22) = 46 source lines.
  3. ROUNDED UP to the nearest 5: 50. Up rather than down on purpose. A
     window that is too tight manufactures findings against a front door
     that is fine, which is the failure mode every lint in this kit spends
     its controls preventing; a window slightly too generous merely fails to
     catch a marginal case.

THE FIRST OBSERVATION IS BOUND TO ITS SOURCE. Step 2's 22% is an input to the
derivation, so `--selftest` re-measures it against the live front door and
requires it to still sit inside `BLANK_SHARE_BAND`. If the document's shape
moves - a README written one-line-per-paragraph, or one padded with blank
lines - the derivation's input has moved and the selftest goes red naming
both numbers. The same binding shape `kit_doctor.py`'s digest ceiling and
`escape_rate.py`'s ceiling cross-check use, and for the same reason: a
constant derived once from a measurement drifts silently otherwise.

THE COMMAND LINE CANNOT WIDEN THE WINDOW. `scan()` takes N as a parameter so
that its boundary can be tested at N and at N+1; `main()` never exposes one.
A window a runner can widen is a window that will be widened on the day it
first goes red, and this check's whole value is that the document moves
instead of the number. If N is wrong, it is wrong in the source, in a
reviewed commit, with this section rewritten to match.

WHAT TO DO WHEN IT GOES RED, stated in the red itself: put a link where the
skimming reader already is. Do not raise N.

==========================================================================
WHAT COUNTS AS REACHABLE
==========================================================================
A required artifact is REACHABLE when the window holds a mention of its path,
outside any fenced code block. Two kinds, and the difference is the state
word rather than the exit code:

  LINK  a markdown inline link whose target is the artifact:
        `[the escape table](KNOWN-ISSUES.md)`. A leading `./` and a trailing
        `#anchor` are normalised away. For a DIRECTORY artifact
        (`docs/walks/`) a target INSIDE it counts - `docs/walks/README.md`
        routes the reader into the directory - as does the slashless form.

  NAME  the path written as text, linked or not: `` `KNOWN-ISSUES.md` ``.
        The finding this tool exists for was about routing, and a named path
        in a door list routes a reader who can type. It is weaker than a
        link, and the state word is where that shows.

BOUNDARIES. A mention must not be part of a longer path: `docs/KNOWN-ISSUES.md`
and `KNOWN-ISSUES.md.bak` are different artifacts and satisfy nothing, which is
the control that stops this tool passing on a near-miss.

A MENTION INSIDE A FENCED CODE BLOCK IS NOT ROUTING. The front door's
Quickstart block contains `--ledger KNOWN-ISSUES.md`; it is a command
argument, not a door, and a reader cannot follow it. Fenced mentions are
excluded from the verdict and COUNTED ON EVERY RUN, because an exclusion
nobody sees is not an exclusion - the same convention the sibling lints apply
to their skips and waivers.

==========================================================================
THE STATE WORD, AND THE DENOMINATOR
==========================================================================
Round 30 retired the bare word `clean` from this kit's lints, because "the
check did not run" and "the check passed" must never render alike. The rule
applies to a check built after it as much as to the two it was written about.
The shipped door's own line, quoted from the run that produced it:

    SKIM LINT: CLEAN - 3 of 3 required artifact(s) reachable within the
    first 50 of 246 line(s) of README.md, 3 by link, 0 by name only - exit 0

  CLEAN    every required artifact is reachable BY LINK.
  PARTIAL  every required artifact is reachable, but at least one only by
           name. The reader was told what to look for and not handed it.

THE EXIT CODE DOES NOT MOVE BETWEEN THOSE TWO, and that is a decision rather
than an oversight, taken for the reason `count_lint` states about its own
coverage figure: a named path satisfies the check this tool was chartered to
build, so making it red would be this tool deciding a question the charter
did not ask. The degradation is on the summary line where the exit code is
read.

==========================================================================
OUT OF SCOPE - stated plainly, because a check whose limits are not published
gets read as covering more than it does
==========================================================================
  - **Whether anybody reads the window.** The declination's second objection,
    unanswered by construction. This tool asserts placement. The instrument
    for readership is a reader.
  - **Whether the artifact is any good.** A link to an empty escape table
    passes. Its content is `escape_rate.py`'s question and this tool has no
    opinion.
  - **Whether the target exists.** A link to a deleted file passes here. That
    is a link-integrity check, a different decidable question, and this kit's
    convention is one question per tool with its own selftest and its own
    summary line. Named as an uncovered neighbour rather than silently
    implied.
  - **Mentions a renderer hides that are not fences.** A path inside an HTML
    comment (`<!-- KNOWN-ISSUES.md -->`) or a four-space indented code block
    counts as routing here, though a reader never sees either. Only fenced
    blocks are excluded; these neighbours are stated rather than covered,
    for the same reason as the reference-style residual below. The front
    door uses neither form.
  - **Reference-style links.** `[the table][ki]` with `[ki]: KNOWN-ISSUES.md`
    defined at the foot of the document is not resolved: the label carries no
    path, so the reference is invisible unless the path itself also appears in
    the window. The front door does not use that form; the residual is stated
    rather than covered, and a control pins the current behaviour so a later
    change to it is visible.
  - **Rendered lines.** This tool counts SOURCE lines, and the conversion
    between the two is an estimate in step 2 of the derivation above. A table
    row, a heading and a horizontal rule do not render at body-text height,
    and no line count in a markdown file is a promise about pixels.
  - **Front doors that are not this one.** `REQUIRED` names three artifacts of
    THIS kit. `--door` and `--root` let the tool run elsewhere, but the
    required list is this repository's; an adopting project that wants the
    check wants its own list, and there is no honest way to guess it.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

GREEN, RED, YELLOW, BOLD, RESET = (
    "\033[32m", "\033[31m", "\033[33m", "\033[1m", "\033[0m")
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ==========================================================================
# THE SPECIFICATION. Hand-written literals, deliberately: see WHY THIS EXISTS,
# objection 1. A list read out of the document being judged would make this
# check vacuous.
# ==========================================================================
DEFAULT_DOOR = "README.md"

# See N, AND WHY IT IS NOT TUNED. Changing this number is a reviewed commit
# and the docstring section above changes with it.
WINDOW_LINES = 50

# The derivation, printed on every run so the number can be argued with
# rather than merely obeyed. Held as data so the run and the selftest read
# the same words.
DERIVATION = (
    "(1080px viewport - 200px chrome) / 24px per line = 36 rendered line(s); "
    "/ (1 - 0.22 measured blank-line share) = 46 source line(s); "
    "rounded UP to the nearest 5 = 50"
)
# Step 2's input, bound to its source by --selftest section D. A band rather
# than a literal because the share moves by a line or two whenever the door is
# edited, and a check that reds on ordinary editing is a check people disable.
MEASURED_BLANK_SHARE = 0.22
BLANK_SHARE_BAND = (0.15, 0.30)

# The three artifacts R29-3 named. Each is (path, what a reader gets there).
REQUIRED = (
    ("KNOWN-ISSUES.md", "the escape table"),
    ("COMPARISON.md", "the claims audit"),
    ("docs/walks/", "the published walk prompts"),
    # Added at the prose-floor review (2026-08-26): the front door named
    # every evaluation artifact but no full-adoption entry point, and no
    # instrument could see the gap. The reviewer found README routed a
    # reader to LEVEL-1.md and never to QUICKSTART.md - a live escape,
    # pre-existing at HEAD.
    ("QUICKSTART.md", "the full-adoption entry point"),
)

# A character that can be part of a path. Used only in lookaround, so that a
# mention which is part of a LONGER path satisfies nothing.
PATH_CHAR = r"[A-Za-z0-9._/-]"

# A markdown inline link. The link text may hold backticks and emphasis; the
# target is the first run of non-space characters inside the parentheses, with
# an optional angle-bracket form and an optional title after it.
MD_LINK = re.compile(r'\[[^\]\n]*\]\(\s*<?([^)\s>]+)>?[^)\n]{0,80}?\)')


# ==========================================================================
# THE PURE LAYER - it decides a string, so every rule below is testable
# without a tree.
# ==========================================================================
def line_starts(text: str):
    """The character offset at which each line begins."""
    out, pos = [], 0
    for ln in text.splitlines(keepends=True):
        out.append(pos)
        pos += len(ln)
    return out


def line_of(starts, pos: int) -> int:
    """The 0-based line index holding character offset `pos`."""
    lo, hi = 0, len(starts) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if starts[mid] <= pos:
            lo = mid
        else:
            hi = mid - 1
    return max(lo, 0)


def fence_line_set(lines: list):
    """Every line index inside a fenced code block, fence markers included.

    Both fence forms are recognised (``` and ~~~), and a block closes only
    on its own marker - a ~~~ line inside a ``` block is content, which is
    how a renderer treats it. An unclosed fence swallows the rest of the
    document, which is what a renderer does with one."""
    inside, open_at, marker = set(), None, None
    for i, ln in enumerate(lines):
        stripped = ln.lstrip()
        if stripped.startswith("```"):
            m = "```"
        elif stripped.startswith("~~~"):
            m = "~~~"
        else:
            continue
        if open_at is None:
            open_at, marker = i, m
        elif m == marker:
            inside.update(range(open_at, i + 1))
            open_at, marker = None, None
    if open_at is not None:
        inside.update(range(open_at, len(lines)))
    return inside


def normalise_target(target: str) -> str:
    """A link target reduced to the path it names.

    A leading `./`, a `#fragment` and a `?query` say nothing about WHICH file
    is being pointed at, and a front door that links to `KNOWN-ISSUES.md#the-
    kits-own-numbers` has routed the reader to the escape table more precisely
    than one that links to the file."""
    t = (target or "").strip().split("#", 1)[0].split("?", 1)[0].strip()
    while t.startswith("./"):
        t = t[2:]
    return t


def target_matches(target: str, artifact: str) -> bool:
    """Does a link target name this artifact?

    A directory artifact is satisfied by the directory, by its slashless form,
    and by any path inside it - all three route the reader into it."""
    t = normalise_target(target)
    if not t:
        return False
    if artifact.endswith("/"):
        return t == artifact or t == artifact[:-1] or t.startswith(artifact)
    return t == artifact


def name_pattern(artifact: str):
    """The path written as text, with both path boundaries enforced.

    The lookbehind is what stops `docs/KNOWN-ISSUES.md` satisfying
    `KNOWN-ISSUES.md`, and the lookahead is what stops `KNOWN-ISSUES.md.bak`
    doing it. A near-miss that passes is worse than a miss, because it is
    green."""
    if artifact.endswith("/"):
        body = re.escape(artifact) + PATH_CHAR + r"*"
        return re.compile(r'(?<!' + PATH_CHAR + r')(?:\./)?' + body)
    return re.compile(r'(?<!' + PATH_CHAR + r')(?:\./)?' + re.escape(artifact)
                      + r'(?!' + PATH_CHAR + r')')


def mentions(text: str, artifact: str):
    """Every mention of `artifact` in `text`, as dicts.

    Each carries a 1-based `line`, a `kind` (`link` or `name`), the matched
    `text`, and whether it sits `in_fence`. Matching is done over the whole
    document rather than line by line, so a link whose target wraps onto the
    next line is still seen - the sibling of the citation lint's most
    important rule, learned there the expensive way."""
    lines = text.splitlines()
    starts = line_starts(text)
    fenced = fence_line_set(lines)
    out, seen_pos = [], set()

    for m in MD_LINK.finditer(text):
        if not target_matches(m.group(1), artifact):
            continue
        idx = line_of(starts, m.start())
        seen_pos.add(m.start(1))
        out.append(dict(line=idx + 1, kind="link", in_fence=idx in fenced,
                        text=re.sub(r"\s+", " ", m.group(0))[:90]))

    for m in name_pattern(artifact).finditer(text):
        if m.start() in seen_pos:
            continue          # already counted as this link's own target
        idx = line_of(starts, m.start())
        out.append(dict(line=idx + 1, kind="name", in_fence=idx in fenced,
                        text=m.group(0)[:90]))

    out.sort(key=lambda d: (d["line"], 0 if d["kind"] == "link" else 1))
    return out


def scan(text: str, n: int = WINDOW_LINES, required=None):
    """Decide one front door.

    Returns (found, absent, fenced, outside):
      found    [(path, label, kind, line)] reachable inside the window
      absent   [(path, label)] not reachable inside it
      fenced   [(path, line)] inside the window but inside a fenced block
      outside  [(path, kind, line, in_fence)] mentioned only after the window

    `n` is a parameter so the boundary can be tested at n and at n + 1. The
    command line does not expose one - see the module docstring.
    `required=None` resolves the module REQUIRED at call time, so the
    selftest can pin its mechanics controls to the original three-artifact
    spec while the adoption-door controls run against the real one."""
    if required is None:
        required = REQUIRED
    found, absent, fenced, outside = [], [], [], []
    for path, label in required:
        got = mentions(text, path)
        window = [d for d in got
                  if d["line"] <= n and not d["in_fence"]]
        fenced.extend((path, d["line"]) for d in got
                      if d["line"] <= n and d["in_fence"])
        if window:
            # A link anywhere in the window beats a name anywhere in it: the
            # state word asks whether the reader CAN be handed the artifact,
            # not which mention comes first.
            link = next((d for d in window if d["kind"] == "link"), None)
            best = link or window[0]
            found.append((path, label, best["kind"], best["line"]))
        else:
            absent.append((path, label))
            # The fence flag travels with the location, because "it is already
            # in the Quickstart block" is the wrong fix and a reader of the red
            # should not have to open the file to learn that.
            outside.extend((path, d["kind"], d["line"], d["in_fence"])
                           for d in got if d["line"] > n)
    return found, absent, fenced, outside


def coverage_state(found):
    """(state word, links, names) for a run in which nothing is absent.

    CLEAN only when every required artifact is reachable BY LINK; PARTIAL when
    one is reachable by name alone. One function, so the summary line and its
    control read the same rule."""
    links = sum(1 for _p, _l, kind, _n in found if kind == "link")
    names = len(found) - links
    return ("CLEAN" if names == 0 else "PARTIAL"), links, names


def blank_share(text: str, n: int = WINDOW_LINES) -> float:
    """The blank-line share of the first `n` source lines.

    Step 2 of the derivation. Measured here so `--selftest` can bind the
    constant to the live document rather than to a number in a comment."""
    lines = text.splitlines()[:n]
    if not lines:
        return 0.0
    return sum(1 for ln in lines if not ln.strip()) / len(lines)


# ==========================================================================
# THE RUNNING LAYER  (impure below this line)
# ==========================================================================
def run(root: Path, door_name: str, show_all: bool) -> int:
    door = root / door_name
    if not door.is_file():
        print(f"{RED}SKIM LINT: ABORT — no {door_name} under {root}. "
              f"This run checked nothing.{RESET}")
        return 2
    try:
        text = door.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"{RED}SKIM LINT: ABORT — cannot read {door}: {exc}. "
              f"This run checked nothing.{RESET}")
        return 2
    if not text.strip():
        print(f"{RED}SKIM LINT: ABORT — {door_name} is empty. This run "
              f"checked nothing.{RESET}")
        return 2

    total = len(text.splitlines())
    found, absent, fenced, outside = scan(text, WINDOW_LINES)
    share = blank_share(text, WINDOW_LINES)

    print()
    print(f"root      : {root}")
    print(f"front door: {door_name} ({total} line(s))")
    print(f"window    : the first {WINDOW_LINES} line(s), "
          f"{share * 100:.1f}% of them blank")
    # The number is printed with its arithmetic on every run, green included -
    # the same disclosure kit_doctor.py makes about its digest ceiling. A
    # constant nobody can see the derivation of is a constant nobody argues
    # with.
    print(f"derivation: {DERIVATION}")
    print(f"required  : {len(REQUIRED)} artifact(s), named in this tool as the "
          f"specification (never read from the door)")
    for path, label, kind, line in found:
        mark = GREEN if kind == "link" else YELLOW
        print(f"  {mark}[{kind}]{RESET} {path} ({label}) — line {line}")
    # An exclusion nobody sees is not an exclusion.
    print(f"fenced    : {len(fenced)} mention(s) inside a fenced code block, "
          f"which route nobody and do not count")
    if show_all:
        for path, line in fenced:
            print(f"  {YELLOW}fenced{RESET} {path} — line {line}")
        for path, _label in REQUIRED:
            for d in mentions(text, path):
                where = "in window" if d["line"] <= WINDOW_LINES else "outside"
                print(f"  seen  {path} — line {d['line']} [{d['kind']}] "
                      f"({where}) {d['text']}")

    if absent:
        print()
        for path, label in absent:
            elsewhere = [(k, ln, fen) for p, k, ln, fen in outside
                         if p == path]
            print(f"{RED}NOT REACHABLE FROM THE FIRST SCREEN{RESET}  "
                  f"{door.as_posix()}")
            print(f"  artifact : {path} ({label})")
            print(f"  window   : the first {WINDOW_LINES} line(s)")
            if elsewhere:
                spots = ", ".join(
                    f"line {ln} ({k}{', in a fenced block' if fen else ''})"
                    for k, ln, fen in elsewhere[:3])
                print(f"  found at : {spots} — outside the window")
            else:
                print(f"  found at : nowhere in this document")
            print(f"  {BOLD}Put a link where the skimming reader already is, "
                  f"inside the first {WINDOW_LINES} lines. Do NOT widen the "
                  f"window: the number models a reader's screen, not this "
                  f"document's layout.{RESET}")
        print()
        names = ", ".join(p for p, _l in absent)
        print(f"{RED}SKIM LINT: {len(absent)} of {len(REQUIRED)} required "
              f"artifact(s) NOT reachable within the first {WINDOW_LINES} of "
              f"{total} line(s) of {door_name} — {names} — exit 1{RESET}")
        return 1

    state, links, names = coverage_state(found)
    colour = GREEN if state == "CLEAN" else YELLOW
    print()
    print(f"{colour}SKIM LINT: {state} - {len(found)} of {len(REQUIRED)} "
          f"required artifact(s) reachable within the first {WINDOW_LINES} of "
          f"{total} line(s) of {door_name}, {links} by link, {names} by name "
          f"only - exit 0{RESET}")
    print("            placement is what this asserts: whether anybody reads "
          "the window is a question for a reader, not for this tool.")
    return 0


# ==========================================================================
def selftest() -> int:
    """The negative controls. Each is labelled SKIM(<id>) so the expectation
    lint can recover it from this source and report an unregistered one.

    The mechanics controls below run against the ORIGINAL three-artifact
    REQUIRED (their fixtures and expected lists are written to it); the
    2026-08-26 adoption-door row gets its own two controls at the end,
    against the real REQUIRED."""
    global REQUIRED
    real_required = REQUIRED
    REQUIRED = tuple(r for r in REQUIRED
                     if r[0] in ("KNOWN-ISSUES.md", "COMPARISON.md",
                                 "docs/walks/"))
    ok_all, n = True, 0

    def check(label, got, want):
        nonlocal ok_all, n
        n += 1
        good = got == want
        ok_all = ok_all and good
        print(f"  [{GREEN + 'PASS' + RESET if good else RED + 'FAIL' + RESET}] "
              f"{label}")
        if not good:
            print(f"        got  {got!r}\n        want {want!r}")

    def door(*routing, pad_before=0, pad_after=0):
        """A miniature front door: `pad_before` filler lines, the routing
        lines, then `pad_after` more."""
        return "\n".join(["filler"] * pad_before + list(routing)
                         + ["filler"] * pad_after) + "\n"

    print(f"{BOLD}=== A. the forced-red half: R29-3's own shape ==={RESET}")

    # R29-3 REPLANTED. The escape table and the walks directory reachable only
    # from prose several screens down - which is exactly what the front door
    # looked like when the first outside reader stopped before reaching them.
    R29_3 = door("# OAR", "", "- **[`COMPARISON.md`](COMPARISON.md)** — the audit",
                 pad_after=60) + (
        "- **`KNOWN-ISSUES.md`** — the escape table\n"
        "- **`docs/walks/`** — the prompts\n")
    found, absent, _f, outside = scan(R29_3, 10)
    check("SKIM(outside-window): an artifact named only past the window is a "
          "finding, and the finding names which",
          ([p for p, _l in absent], [p for p, _l, _k, _n in found]),
          (["KNOWN-ISSUES.md", "docs/walks/"], ["COMPARISON.md"]))
    check("SKIM(outside-window): ...and the red says where it IS, so the fix "
          "is a move rather than a hunt",
          [(p, k, fen) for p, k, _ln, fen in outside],
          [("KNOWN-ISSUES.md", "name", False),
           ("docs/walks/", "name", False)])

    gone = door("# OAR", "- **`COMPARISON.md`** — the audit",
                "- **`KNOWN-ISSUES.md`** — the escape table")
    _f2, absent, _f3, outside = scan(gone, 10)
    check("SKIM(absent): an artifact named NOWHERE is a finding too, and the "
          "run says it is nowhere rather than pointing at a line",
          ([p for p, _l in absent], outside), (["docs/walks/"], []))

    print()
    print(f"{BOLD}=== B. the controls that keep it from manufacturing "
          f"findings ==={RESET}")

    # THE MOST IMPORTANT CONTROL IN THE FILE, and the sibling of
    # COUNT(true-count). A checker that has only ever been red would turn
    # every correct front door into a finding.
    good_door = door(
        "# OAR", "",
        "- **[`KNOWN-ISSUES.md`](KNOWN-ISSUES.md)** — the escape table",
        "- **[`COMPARISON.md`](COMPARISON.md)** — the claims audit",
        "- **[`docs/walks/`](docs/walks/)** — the prompts", pad_after=80)
    found, absent, _f, _o = scan(good_door, WINDOW_LINES)
    check("SKIM(true-front-door): a door that DOES route the reader passes, "
          "and every artifact is reached by link",
          ([p for p, _l, _k, _n in found], [k for _p, _l, k, _n in found],
           absent),
          (["KNOWN-ISSUES.md", "COMPARISON.md", "docs/walks/"],
           ["link", "link", "link"], []))

    # THE BOUNDARY, HELD IN BOTH DIRECTIONS. A window is a number and a number
    # has an edge; an edge nobody tested is an edge that is off by one.
    at_n = door("filler", "- `KNOWN-ISSUES.md`", pad_before=8)   # line 10
    check("SKIM(boundary): a mention ON line N is inside the window",
          [ln for _p, _l, _k, ln in scan(at_n, 10)[0]], [10])
    check("SKIM(boundary): ...and the same mention with the window one line "
          "shorter is outside it",
          ([p for p, _l in scan(at_n, 9)[1]],
           [ln for _p, _k, ln, _f in scan(at_n, 9)[3]]),
          (["KNOWN-ISSUES.md", "COMPARISON.md", "docs/walks/"], [10]))

    fenced_door = door("# OAR", "", "```bash",
                       "python escape_rate.py --ledger KNOWN-ISSUES.md",
                       "```")
    found, absent, fenced, _o = scan(fenced_door, 10)
    check("SKIM(fenced-mention): a path inside a fenced code block is a "
          "command argument, not a door - it satisfies nothing...",
          [p for p, _l in absent],
          ["KNOWN-ISSUES.md", "COMPARISON.md", "docs/walks/"])
    check("SKIM(fenced-mention): ...and it is COUNTED, because an exclusion "
          "nobody sees is not an exclusion",
          fenced, [("KNOWN-ISSUES.md", 4)])

    tilde_door = door("# OAR", "", "~~~",
                      "python escape_rate.py --ledger KNOWN-ISSUES.md",
                      "~~~")
    check("SKIM(fenced-mention): the ~~~ fence form excludes exactly like "
          "the backtick form - a variant fence must not be a false green",
          [p for p, _l in scan(tilde_door, 10)[1]],
          ["KNOWN-ISSUES.md", "COMPARISON.md", "docs/walks/"])
    mixed_door = door("# OAR", "", "```", "~~~",
                      "python escape_rate.py --ledger KNOWN-ISSUES.md",
                      "```", "- see `KNOWN-ISSUES.md`")
    check("SKIM(fenced-mention): a fence closes only on its own marker - a "
          "~~~ inside a ``` block is content, and the mention after the "
          "close is real",
          [t[0] for t in scan(mixed_door, 10)[0] if t[0] == "KNOWN-ISSUES.md"],
          ["KNOWN-ISSUES.md"])

    near = door("- `docs/KNOWN-ISSUES.md`", "- `KNOWN-ISSUES.md.bak`",
                "- `docs/walkthroughs/`")
    check("SKIM(path-boundary): a longer path CONTAINING the artifact's name "
          "satisfies nothing - a near miss that passes is worse than a miss",
          [p for p, _l in scan(near, 10)[1]],
          ["KNOWN-ISSUES.md", "COMPARISON.md", "docs/walks/"])
    check("SKIM(path-boundary): ...and the honest forms still pass, including "
          "the `./` prefix and an anchored link",
          [(p, k) for p, _l, k, _n in scan(
              door("- [x](./KNOWN-ISSUES.md#the-kits-own-numbers)",
                   "- `COMPARISON.md`", "- `docs/walks/`"), 10)[0]],
          [("KNOWN-ISSUES.md", "link"), ("COMPARISON.md", "name"),
           ("docs/walks/", "name")])

    inside_dir = door("- [the prompts](docs/walks/README.md)",
                      "- `KNOWN-ISSUES.md`", "- `COMPARISON.md`")
    check("SKIM(directory-artifact): a link INTO a directory artifact routes "
          "the reader into it and counts",
          [(p, k) for p, _l, k, _n in scan(inside_dir, 10)[0] if "walks" in p],
          [("docs/walks/", "link")])
    check("SKIM(directory-artifact): ...and so does the slashless form",
          [p for p, _l, _k, _n in scan(
              door("- [x](docs/walks)", "- `KNOWN-ISSUES.md`",
                   "- `COMPARISON.md`"), 10)[0] if "walks" in p],
          ["docs/walks/"])

    # THE DISCLOSED LIMIT, HELD AS A CONTROL rather than left in prose. The
    # label carries no path, so the reference is invisible; pinning it here
    # means a later change to the behaviour is visible rather than silent.
    ref_style = door("- [the escape table][ki]", "- `COMPARISON.md`",
                     "- `docs/walks/`", pad_after=4) + "[ki]: KNOWN-ISSUES.md\n"
    check("SKIM(reference-style): a reference-style link whose definition sits "
          "outside the window is NOT resolved - the residual, pinned",
          [p for p, _l in scan(ref_style, 5)[1]], ["KNOWN-ISSUES.md"])

    # A wrapped link. The citation lint learned this the expensive way: a
    # line-oriented matcher reports real text as absent.
    wrapped = door("- [the escape table](", "  KNOWN-ISSUES.md)",
                   "- `COMPARISON.md`", "- `docs/walks/`")
    check("SKIM(wrapped-link): a link whose target wraps onto the next line is "
          "still seen - matching is over the document, not line by line",
          [(p, k) for p, _l, k, _n in scan(wrapped, 10)[0] if "KNOWN" in p],
          [("KNOWN-ISSUES.md", "link")])

    print()
    print(f"{BOLD}=== C. the state word and its denominator ==={RESET}")

    check("SKIM(state-word): every artifact reachable BY LINK is CLEAN",
          coverage_state(scan(good_door, WINDOW_LINES)[0]), ("CLEAN", 3, 0))
    named_door = door("- `KNOWN-ISSUES.md`", "- `COMPARISON.md`",
                      "- [the prompts](docs/walks/)")
    check("SKIM(state-word): ...and a door that NAMES two of them without "
          "linking them is PARTIAL, with both halves of the denominator "
          "printed rather than the word `clean`",
          coverage_state(scan(named_door, 10)[0]), ("PARTIAL", 1, 2))
    check("SKIM(state-word): the state word decides nothing about the exit "
          "code - a named path satisfies the check, and the degradation is "
          "disclosed on the summary line instead",
          [k for _p, _l, k, _n in scan(named_door, 10)[0]],
          ["name", "name", "link"])

    print()
    print(f"{BOLD}=== D. this tool against the door it ships beside ==={RESET}")
    root = Path(__file__).resolve().parent.parent
    live = root / DEFAULT_DOOR
    if not live.is_file():
        check("SKIM(window-derivation): the live front door is reachable "
              "(this tool copied out of a kit checkout reports UNAVAILABLE "
              "rather than passing in silence)", "UNAVAILABLE", "reachable")
    else:
        text = live.read_text(encoding="utf-8")
        # THE FIRST OBSERVATION, BOUND TO ITS SOURCE. Step 2 of the derivation
        # used a measured 22% blank-line share. If the door's shape moves, the
        # derivation's input has moved and this goes red naming both numbers -
        # the same binding shape kit_doctor's digest ceiling carries.
        share = blank_share(text, WINDOW_LINES)
        lo, hi = BLANK_SHARE_BAND
        check(f"SKIM(window-derivation): the blank-line share the window was "
              f"derived from still holds — measured {share * 100:.1f}%, "
              f"derived from {MEASURED_BLANK_SHARE * 100:.0f}%, band "
              f"{lo * 100:.0f}–{hi * 100:.0f}%",
              lo <= share <= hi, True)
        check("SKIM(window-derivation): ...and the shipped window is the "
              "number the derivation produces, not one edited to make a run "
              "green", WINDOW_LINES, 50)
        found, absent, _f, _o = scan(text, WINDOW_LINES)
        check("SKIM(live-door): the shipped front door routes the reader to "
              "all three artifacts from inside the window",
              [p for p, _l in absent], [])
        check("SKIM(live-door): ...and the tool really located them, rather "
              "than passing over a document it could not read",
              len(found), len(REQUIRED))

    # The 2026-08-26 adoption-door row, against the REAL required list.
    REQUIRED = real_required
    check("SKIM(adoption-door): the real REQUIRED names the full-adoption "
          "entry point — the reviewer's live escape stays closed",
          any(p == "QUICKSTART.md" for p, _l in REQUIRED), True)
    three_only = door(
        "# OAR", "",
        "- **[`KNOWN-ISSUES.md`](KNOWN-ISSUES.md)** — the escape table",
        "- **[`COMPARISON.md`](COMPARISON.md)** — the claims audit",
        "- **[`docs/walks/`](docs/walks/)** — the prompts", pad_after=80)
    check("SKIM(adoption-door): a door naming every evaluation artifact but "
          "no adoption entry point is a finding under the real spec",
          [p for p, _l in scan(three_only, WINDOW_LINES)[1]],
          ["QUICKSTART.md"])

    print()
    print((GREEN if ok_all else RED)
          + f"SKIM-LINT SELFTEST: {'PASS' if ok_all else 'FAIL'} "
            f"— {n} checks" + RESET)
    return 0 if ok_all else 1


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Does the front door hand the reader the checkable "
                    "artifacts before the reader stops reading?",
        epilog="exit 0 reachable · 1 not reachable · 2 abort. There is no "
               "flag for the window: see the module docstring.")
    ap.add_argument("--root", default="", help="the tree to lint")
    ap.add_argument("--door", default=DEFAULT_DOOR,
                    help=f"the front door to read (default {DEFAULT_DOOR})")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--list", action="store_true",
                    help="print every mention seen, in the window and outside")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    root = Path(a.root).resolve() if a.root \
        else Path(__file__).resolve().parent.parent
    if not root.is_dir():
        print(f"{RED}SKIM LINT: ABORT — no such directory: {root}. This run "
              f"checked nothing.{RESET}")
        return 2
    return run(root, a.door, a.list)


if __name__ == "__main__":
    sys.exit(main())
