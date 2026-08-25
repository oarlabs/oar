#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/citation_lint.py - the attribution lint. Does the quotation exist?

    python tools/citation_lint.py                 # lint the kit's own documents
    python tools/citation_lint.py --root <path>   # lint another tree
    python tools/citation_lint.py --selftest      # incl. the negative controls
    python tools/citation_lint.py --list          # print every attribution seen

    exit 0  clean - every quoted string attributed to a named kit document was
            found in that document
    exit 1  at least one quotation is not in the document it names, or is
            not at the lines its locator names (the round-27 window class)
    exit 2  abort (no root, nothing to read)

==========================================================================
WHY THIS EXISTS
==========================================================================
Twice now, a build has written a quotation from memory, attributed it to a
shipped document, and shipped it.

  round 19  the relabel build - three MAJORs with one root cause, "attribution
            written from memory rather than from the source, including one
            invented quotation". Recorded as an ORACLE CANDIDATE. Not built.
  round 22  the ONBOARD build - a quotation attributed to `DECISION-BRIEF.md`
            limitation 2. The words were real; the section named was not the
            section holding them.

One sighting is an anecdote. Two is a pattern, and this kit's own promotion
rule says a prose rule that keeps failing gets promoted to a mechanical layer.
This is that layer, and it is deliberately the NARROW version of it.

The class is bigger than this tool: *a claim in a document should be
verifiable against the source it names* - quoted strings, cited steps, stated
counts. This tool takes the first of those three, because it is the one that
can be decided mechanically with no judgment: the string is in the file or it
is not.

==========================================================================
THE ROUND-22 IMPLEMENTATION LESSON, WHICH IS THE WHOLE DESIGN
==========================================================================
The round-22 finding was reported as a FABRICATED quotation, on the evidence
of a tree-wide grep that returned no hit. The quotation was real. It sits in
`DECISION-BRIEF.md`, and it WRAPS ACROSS A LINE BREAK:

    ... in the tree. It produced no usable
    human time estimate - it measures an agent executing tool calls ...

A line-oriented grep cannot see it. So a check built the obvious way would not
merely miss defects - it would MANUFACTURE them, reporting real quotations as
invented, in a kit whose whole argument is that a green means something.

Therefore: **both sides are whitespace-normalised before comparison.** Runs of
any whitespace collapse to one space, in the needle and in the haystack alike.
`CITE(wrapped-quote)` is the negative control that holds this, and it is the
most important control in the file.

==========================================================================
WHAT IT CAN SEE, AND WHAT IT CANNOT
==========================================================================
IN SCOPE - two attribution shapes, both requiring a BACKTICKED kit filename:

  Shape B (leading)   `FILE.md`:40-41 ... says "the quoted words"
                      `FILE.md` Step 4 ... says "the quoted words"
                      The locator is optional. The quote must follow within
                      200 GLUE UNITS - a unit is one plain character or one
                      complete inline code span - so glue that holds code
                      spans can reach past 200 raw characters (the longest
                      live shape-B glue in the kit today is 238). No
                      intervening backticked .md reference and no table-cell
                      boundary between them. Inline code spans in between
                      are ordinary prose and do NOT break the attribution -
                      see THE ROUND-27 RECALL LESSON below.

  Shape A (trailing)  "the quoted words" (`FILE.md`:14)
                      The parenthesised reference must follow the closing
                      quote within 60 characters.

A quotation is only considered prose if it carries at least MIN_WORDS words.
Shorter quoted strings are output lines, flags and verdict words - `"0
skipped"`, `"VERIFY: PASS"` - which a document names rather than quotes, and
which appear in tools rather than in prose.

==========================================================================
THE ROUND-27 RECALL LESSON: A CHECK'S REACH IS PART OF ITS CLAIM
==========================================================================
Round 26's evaluation read (finding m4) found a real ten-word attribution this
tool could not see - `ONBOARD.md`:227-228, quoting `QUICKSTART.md` named two
lines earlier. The cause was shape B's GLUE. The glue forbade a backtick
between the reference and the quotation, as a cheap way to enforce the real
rule: another document named in between takes the attribution instead. But a
backtick is not only a document reference. It is also `PROJECT_NAME`,
`GATE_COMMAND` and every other inline code span, and the kit's prose is full of
them, so the cheap rule silently dropped attributions that mention a config key
on the way to their quotation.

The real rule was already enforced separately and correctly, by the MD_REF
post-filter in `attributions()`. So the glue now admits COMPLETE inline code
spans and the post-filter decides. Two further mechanics make that safe:

  - The glue admits a complete `...` span, never a lone backtick, so an
    unpaired backtick cannot be crossed. (Permitting bare backticks pairs one
    phrase's quote mark with the next phrase's, the same mis-pairing
    `CITE(quote-cell-boundary)` records.)
  - The glue and the quotation are matched inside a LOOKAHEAD, so a match
    consumes only the reference itself. Without that, `finditer` swallows the
    span up to the quotation and the NEXT reference in it never gets its own
    attempt - which would silently repeal `CITE(intervening-ref)`, the rule
    that decides which of two named documents owns a quotation.

Measured: recall over the shipped kit rose from 40 attributions to 44, with
none lost. Section E now asserts NAMED attributions are found, not merely that
some number is non-zero: a presence count is satisfied by a pattern that has
quietly stopped seeing half the tree.

==========================================================================
THE LINE WINDOW: IS THE QUOTATION WHERE THE LOCATOR SAYS IT IS?
==========================================================================
v1 asked only "is the string in the file". Round 22's actual defect was a real
quotation under a wrong locator, and round 26 found six live locator defects in
one document. So when an attribution carries a LINE locator - `FILE.md`:40 or
`FILE.md`:40-41 - this tool now also asks whether the quotation is at those
lines.

TOLERANCE = 0 lines, and the comparison is OVERLAP, not containment. The
quotation passes if the lines it occupies intersect the named window at all.
Overlap is what makes a zero tolerance defensible, because it already absorbs
the two honest ways a correct locator disagrees with a quotation's extent:

  - a quotation that WRAPS beyond a single-line locator - `:208` naming a
    quotation running from 208 to 209 - overlaps and passes;
  - a locator naming a WIDER range than the quotation occupies - `:202-209`
    for a quotation at 208-209 - contains it, so it overlaps and passes.

What overlap does not absorb is a window that misses the quotation entirely,
which is exactly the defect class. A tolerance above zero buys nothing here and
costs real recall: of the six round-26 defects, the tightest sits ONE line
outside its cited range (`:203-207` for a quotation at 208-209), so a tolerance
of even one line makes the check blind to it. A locator is a mechanical fact
about a file, not an estimate, and it is cheap to correct.

Line numbers are recovered by `flatten_with_lines()`, which produces the SAME
normalised string as `flatten()` alongside a source line number for each
character. One normalisation, asserted equal in the selftest against every
shipped document: a window layer that normalised differently from the presence
layer could report a quotation as both present and absent.

OUT OF SCOPE - stated plainly, because a check whose limits are not published
gets read as covering more than it does:

  - **Paraphrase.** No quotation marks, nothing to match. The larger half of
    the class, and this tool sees none of it.
  - **A right quotation under a wrong SECTION.** Narrowed, not closed. A LINE
    locator is now checked (above). `FILE.md` limitation 2 and `FILE.md` Step 4
    name no line, so a quotation moved to the wrong section of the right
    document still passes. Closing that needs a section resolver and remains
    the v2 question.
  - **A stale locator carrying no quotation of its own.** The window check
    needs a needle. Measured against the six round-26 locator defects it
    reaches THREE; the other three are unreachable by construction and are
    named here rather than left to be assumed covered:
      - a BARE trailing locator - `` Step 3 is headed "..." (:366) `` - names
        a line but no file, and the shape's own locator is a section name. The
        bare `DOC.md`:N form is the shared gap recorded below.
      - a locator with NO quotation anywhere near it - `` `:806-811`, the two
        failure signatures `` - offers nothing to look for.
      - a quotation separated from its reference by more than the glue allows
        - here, 150 characters and an intervening parenthesis. Widening the
        glue to reach it would trade a known miss for unknown false findings,
        which is the wrong trade for a tool whose green is the product.
  - **Anything not attributed to a kit .md file** - external sources, tools,
    a person, or nothing at all.
  - **Attributions whose file cannot be resolved** in the tree being linted.
    Skipped rather than failed - `docs/ORACLE-<gate>.md` names a file only an
    adopter has - but the skip count is PRINTED on every run, because a skip
    nobody sees is not a skip.
  - **Single-quoted and typographic-quoted strings.** Straight double quotes
    only in v1.
  - **A citation with no quotation at all.** `` `LEVEL-1.md`:320's rule ``
    names a file and a line and quotes nothing, so there is no needle and
    this tool sees the reference not at all - it is not skipped and does not
    enter the skip count, because nothing here recognises it as a citation in
    the first place. `tools/count_lint.py` is blind to the same shape from
    the other side: its `SECTION_REF` excludes the bare line form by design,
    since a line range names no enumerable section. So NEITHER LINT READS A
    BARE `DOC.md`:N REFERENCE, and neither one's green is evidence that the
    number is still right. Round 24 shipped two stale ones inside a clause
    written that same round, and its review found them by hand (m1). Named as
    a shared gap rather than covered; the check that would cover it is an
    ORACLE-DECLINED row of round 24.
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

# A quotation shorter than this is a literal the document NAMES (an output
# line, a flag, a verdict word), not prose it QUOTES from somewhere else.
MIN_WORDS = 4
# How far a quote may sit from the reference that attributes it.
GLUE_B = 200
GLUE_A = 60
# How far a quotation may sit from the LINE WINDOW its locator names, in lines.
# Zero, deliberately, and the comparison is overlap - see the module docstring
# under THE LINE WINDOW. A locator is a mechanical fact, not an estimate.
LINE_TOLERANCE = 0

_NAME = r'[A-Za-z0-9][A-Za-z0-9._/<>-]*\.md'
MD_REF = re.compile(r'`(' + _NAME + r')`')

# An optional citation locator between the filename and the quote: `:40-41`,
# ` Step 4`, ` limitation 2`, ` row 3`, ` §2`. Up to three of them.
_LOC = (r'(?:\s*:\s*\d+(?:\s*[-–]\s*\d+)?'
        r'|\s+(?:Step|step|section|Section|row|line|lines|limitation|entry'
        r'|item|Round|round|walk|phase|§)\s*[#A-Za-z0-9.]+){0,3}')

# Shape B. The glue may not contain a `|` (a markdown table-cell boundary - the
# reference is then in a different cell, and cells are different sentences). It
# MAY contain complete inline code spans, which are ordinary prose; an
# intervening .md REFERENCE is rejected afterwards by the MD_REF post-filter in
# `attributions()`, which is where that rule actually lives. A lone backtick is
# still refused, so an unpaired one cannot be crossed.
#
# The glue and the quotation sit inside a LOOKAHEAD so that a match consumes
# only the reference. See THE ROUND-27 RECALL LESSON: without it, `finditer`
# eats the span up to the quotation and the nearer reference inside it never
# gets its own attempt, repealing `CITE(intervening-ref)` silently.
_GLUE_B_BODY = r'(?:[^"`|]|`[^"`|\n]{0,120}`){0,' + str(GLUE_B) + r'}?'
SHAPE_B = re.compile(
    r'`(?P<f>' + _NAME + r')`(?P<loc>' + _LOC + r')'
    r'(?=(?P<glue>' + _GLUE_B_BODY + r')'
    r'[*_]{0,2}"(?P<q>[^"|]{1,400})")')

# Shape A. Same cell-boundary rule. The locator follows the filename inside the
# parentheses - `(`FILE.md`:14)` - so it is captured on this side of the name.
SHAPE_A = re.compile(
    r'"(?P<q>[^"|]{1,400})"[*_]{0,2}'
    r'(?P<glue>[^"(|]{0,' + str(GLUE_A) + r'}?)'
    r'\(\s*`(?P<f>' + _NAME + r')`(?P<loc>' + _LOC + r')')

# A blank line between the reference and the quotation. An attribution and the
# words it attributes live in the SAME paragraph; across a paragraph break the
# reference is describing something else, and treating it as an attribution is
# how a proximity heuristic invents findings.
PARA_BREAK = re.compile(r'\n[ \t]*\n')

# REGISTER DOCUMENTS. A findings register quotes text AS IT WAS when the finding
# was raised, and the disposition beside it is usually "FIXED" - so the quoted
# words are absent from the current tree BY CONSTRUCTION, and checking them
# against it asks the wrong question. Exempted as a document class rather than
# one waiver per row, because the alternative grows by several rows every round.
# The count is PRINTED on every run, the same way `kit_doctor.py`'s shipped-value
# scan prints how many lines each of its exemptions removed.
#
# RESIDUAL, STATED: a genuine miscitation written INTO the register is exempt
# too. The register is the one document in this kit where an attribution is not
# checked, and this comment is the disclosure.
REGISTER_DOCS = frozenset({"KNOWN-ISSUES.md"})

# THE RECALL FLOOR. Named attributions that the shipped kit really contains and
# this tool must really find. Held as data, the same way `expectation_lint.py`
# holds its FAMILIES, so that section E asserts a SPECIFICATION rather than a
# count - "the lint sees some attributions" was the whole of section E until
# round 27, and it was satisfied by a pattern that had silently stopped seeing
# a document's worth of them (finding m4). Each row is
# (document, attributed-to, the quotation's first words), and every row is
# asserted twice: the attribution is EXTRACTED from the document, and its
# quotation is PRESENT in the source it names.
#
# A row that goes red because the kit's prose legitimately changed is corrected
# here, deliberately and visibly. That is the point: the floor should be
# expensive enough to notice.
RECALL_FLOOR = (
    # THE ROUND-26 m4 CASE. Two inline code spans sit between the reference and
    # the quotation; before round 27 the glue refused to cross them and this
    # attribution was invisible. It is first in the list on purpose.
    ("ONBOARD.md", "QUICKSTART.md", "Four keys come back later"),
    # The round-22 defect's own sentence, now correct - shape B with a line
    # locator. Asserted extracted and present, like every floor row; the
    # window layer is NOT exercised here - its controls live in section F.
    ("ONBOARD.md", "DECISION-BRIEF.md", "produced no usable human time"),
    # A section locator rather than a line locator: presence is checked, the
    # window is not applicable, and the row proves that path stays alive.
    ("ONBOARD.md", "QUICKSTART.md", "an afternoon of thinking"),
    # A second document, so the floor is not one page's shape.
    ("DEFAULTS.md", "DEFAULT-CONTRACT.md", "Two consequences that follow"),
)

# WAIVERS. Same convention as `tools/expectation_lint.py`: a case the pattern
# cannot decide is named out loud with its reason and PRINTED ON EVERY RUN,
# never suppressed silently. Keyed by (document name, the first words of the
# quotation). A waiver with no reason is treated as the silent case.
WAIVERS = {
    ("SEED-INTERVIEW.md", "Default 1 (recommendation-first) is"):
        "NOT AN ATTRIBUTION - an EXEMPLAR. The document names "
        "`DEFAULT-CONTRACT.md` as the thing an answer may contradict, then "
        "shows the adopter a sentence to WRITE in their own profile. The "
        "quoted words are a template for the reader's prose, not a quotation "
        "from the named file, and no shape in v1 tells 'cites' apart from "
        "'shows you what to write'. Left as a waiver rather than narrowed, "
        "because a rule keyed on the colon-then-imperative shape would start "
        "dropping real attributions.",
}


# ==========================================================================
# THE PURE LAYER
# ==========================================================================
def flatten(text: str) -> str:
    """Collapse every run of whitespace to one space.

    THE LOAD-BEARING FUNCTION. A quotation in one document wraps at that
    document's margin; the same words in the source wrap at the source's. Any
    comparison that does not do this reports true quotations as invented - see
    the module docstring."""
    return re.sub(r"\s+", " ", text).strip()


def attributions(doc_text: str, self_name: str = ""):
    """Every (filename, quotation, shape, locator) this tool claims to see.

    Returns them in document order. A quotation attributed to the document it
    is written in is dropped: a page quoting itself is not an attribution. The
    locator is the raw text as written (`:40-41`, ` Step 4`, or empty);
    `line_span()` turns the line forms into a window and returns None for the
    rest."""
    found = []
    for m in SHAPE_B.finditer(doc_text):
        if MD_REF.search(m.group("glue")):
            # Another document was named between the reference and the quote,
            # so the reference no longer attributes it.
            continue
        if PARA_BREAK.search(m.group("glue")):
            continue
        found.append((m.start("q"), m.group("f"), m.group("q"), "B",
                      m.group("loc") or ""))
    for m in SHAPE_A.finditer(doc_text):
        if PARA_BREAK.search(m.group("glue")):
            continue
        found.append((m.start("q"), m.group("f"), m.group("q"), "A",
                      m.group("loc") or ""))

    out, seen = [], set()
    for pos, ref, quote, shape, loc in sorted(found):
        # A quotation may WRAP - that is the whole point of this tool - so
        # newlines inside it are ordinary. A BLANK line is not: an unmatched
        # quote mark would otherwise swallow paragraphs until the next one.
        if "\n\n" in quote or "\r\n\r\n" in quote:
            continue
        if len(quote.split()) < MIN_WORDS:
            continue
        if self_name and Path(ref).name == self_name:
            continue
        if (pos, ref) in seen:
            continue
        seen.add((pos, ref))
        out.append((ref, quote, shape, loc))
    return out


def quote_is_in(quote: str, source_text: str) -> bool:
    """Is the quotation present in the source, ignoring how either one wraps?"""
    return flatten(quote) in flatten(source_text)


# --------------------------------------------------------------------------
# THE LINE WINDOW
# --------------------------------------------------------------------------
_LINE_LOC = re.compile(r':\s*(\d+)(?:\s*[-–]\s*(\d+))?')


def line_span(loc: str):
    """The (first, last) line window a locator names, or None.

    Only the LINE forms produce a window. ` Step 4` and ` limitation 2` name a
    section, which this tool cannot resolve, so they return None and the
    attribution is checked for presence only."""
    m = _LINE_LOC.search(loc or "")
    if not m:
        return None
    lo = int(m.group(1))
    hi = int(m.group(2)) if m.group(2) else lo
    return (lo, hi) if lo <= hi else (hi, lo)


def flatten_with_lines(text: str):
    """`flatten(text)`, plus the source line number of every character in it.

    THE INVARIANT, asserted in the selftest against every shipped document:
    `flatten_with_lines(t)[0] == flatten(t)`. The window layer and the presence
    layer must normalise identically, or a quotation could be reported present
    by one and absent by the other."""
    chars, lines = [], []
    line, pending, started = 1, False, False
    for ch in text:
        if ch.isspace():
            if ch == "\n":
                line += 1
            if started:
                pending = True
            continue
        if pending:
            chars.append(" ")
            lines.append(line)
            pending = False
        chars.append(ch)
        lines.append(line)
        started = True
    return "".join(chars), lines


def quote_line_spans(quote: str, source_text: str):
    """Every (first line, last line) at which the quotation occurs in source.

    A quotation may legitimately appear more than once; each occurrence gets a
    span, and the window check accepts if ANY of them lands in the window."""
    needle = flatten(quote)
    if not needle:
        return []
    flat, lines = flatten_with_lines(source_text)
    out, i = [], flat.find(needle)
    while i != -1:
        out.append((lines[i], lines[i + len(needle) - 1]))
        i = flat.find(needle, i + 1)
    return out


def quote_in_window(quote: str, source_text: str, lo: int, hi: int,
                    tol: int = LINE_TOLERANCE) -> bool:
    """Does the quotation OVERLAP the named window, widened by `tol` lines?

    Overlap, not containment - a single-line locator on a quotation that wraps,
    and a range wider than the quotation, are both correct citations."""
    for first, last in quote_line_spans(quote, source_text):
        if first <= hi + tol and last >= lo - tol:
            return True
    return False


def waiver_for(doc_name: str, quote: str):
    """The waiver covering this quotation, or None. An empty reason is not a
    waiver - it is the silent case this tool exists to prevent."""
    flat_q = flatten(quote)
    for (name, prefix), reason in WAIVERS.items():
        if name == doc_name and flat_q.startswith(flatten(prefix)):
            return reason if reason and reason.strip() else None
    return None


# ==========================================================================
# THE RUNNING LAYER  (impure below this line)
# ==========================================================================
def kit_documents(root: Path):
    seen = {}
    for pat in ("*.md", "modules/*/*.md", "docs/**/*.md", "modules/**/*.md"):
        for p in root.glob(pat):
            if p.is_file():
                seen[p.resolve()] = p
    return sorted(seen.values(), key=lambda p: p.as_posix())


def resolve(root: Path, ref: str, index: dict):
    p = (root / ref)
    if p.is_file():
        return p
    return index.get(Path(ref).name)


def run(root: Path, show_all: bool) -> int:
    docs = kit_documents(root)
    if not docs:
        print(f"{RED}CITATION LINT: ABORT — no markdown documents under "
              f"{root}{RESET}")
        return 2

    index = {}
    for p in docs:
        index.setdefault(p.name, p)

    cache, checked, skipped, problems, waived = {}, 0, [], [], []
    register, windowed, stale = 0, 0, []
    for doc in docs:
        try:
            text = doc.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"{RED}CITATION LINT: ABORT — cannot read {doc}: {exc}{RESET}")
            return 2
        if doc.name in REGISTER_DOCS:
            register += len(attributions(text, doc.name))
            continue
        for ref, quote, shape, loc in attributions(text, doc.name):
            src = resolve(root, ref, index)
            if src is None or src.resolve() == doc.resolve():
                skipped.append((doc, ref, quote))
                continue
            if src not in cache:
                cache[src] = src.read_text(encoding="utf-8")
            checked += 1
            ok = quote_is_in(quote, cache[src])
            if show_all:
                mark = f"{GREEN}found{RESET}" if ok else f"{RED}MISSING{RESET}"
                print(f"  [{shape}] {mark}  {doc.name} -> {ref}{loc}\n"
                      f"        \"{quote[:100]}\"")
            if not ok:
                reason = waiver_for(doc.name, quote)
                if reason:
                    waived.append((doc, ref, quote, reason))
                else:
                    problems.append((doc, ref, quote, shape))
                continue
            # The quotation is in the document. If it named LINES, is it at
            # them? A missing quotation is the stronger finding and has already
            # been raised, so this only runs on the ones that were found.
            span = line_span(loc)
            if span is None:
                continue
            windowed += 1
            if not quote_in_window(quote, cache[src], *span):
                at = quote_line_spans(quote, cache[src])
                reason = waiver_for(doc.name, quote)
                if reason:
                    # A waived window finding prints with its reason like
                    # every other waiver - suppressing it silently is the
                    # exact case the WAIVERS convention forbids.
                    waived.append((doc, ref, quote, reason))
                else:
                    stale.append((doc, ref, quote, shape, span, at))

    print()
    print(f"root      : {root}")
    print(f"documents : {len(docs)} scanned")
    print(f"checked   : {checked} attributed quotation(s)")
    print(f"windows   : {windowed} of those named a LINE and were checked "
          f"against it (overlap, tolerance ±{LINE_TOLERANCE} lines)")
    # A skip nobody sees is not a skip - the same rule the expectation lint
    # applies to its waivers.
    print(f"skipped   : {len(skipped)} attribution(s) whose document is not in "
          f"this tree (printed with --list)")
    print(f"register  : {register} attribution(s) NOT checked, in "
          f"{', '.join(sorted(REGISTER_DOCS))} — a findings register quotes "
          f"text as it was, which a fixed tree no longer contains")
    # A waiver nobody sees is not a waiver - every run prints every one.
    print(f"waivers   : {len(waived)} (each printed below, every run)")
    for doc, ref, quote, reason in waived:
        print(f"{YELLOW}  WAIVED {doc.name} -> {ref}: "
              f"\"{flatten(quote)[:60]}...\"\n    {reason}{RESET}")
    if show_all:
        for doc, ref, quote in skipped:
            print(f"  {YELLOW}skip{RESET}  {doc.name} -> {ref}: "
                  f"\"{quote[:70]}\"")

    if stale:
        print()
        for doc, ref, quote, shape, (lo, hi), at in stale:
            where = ", ".join(f"{a}-{b}" if a != b else str(a) for a, b in at)
            print(f"{RED}NOT AT THE LINES IT NAMES{RESET}  "
                  f"[shape {shape}]  {doc.as_posix()}")
            print(f"  attributed to : {ref}:{lo}" + (f"-{hi}" if hi != lo else ""))
            print(f"  quotation     : \"{flatten(quote)[:90]}\"")
            print(f"  actually at   : {ref}:{where}")
            print(f"  {BOLD}The words are right and the locator is stale. Point "
                  f"it at {where}, or re-quote from the lines you meant.{RESET}")

    if problems:
        print()
        for doc, ref, quote, shape in problems:
            print(f"{RED}NOT IN THE DOCUMENT IT NAMES{RESET}  "
                  f"[shape {shape}]  {doc.as_posix()}")
            print(f"  attributed to : {ref}")
            print(f"  quotation     : \"{quote}\"")
            print(f"  {BOLD}Either the words are wrong or the document is. Open "
                  f"{ref}, find what it actually says, and quote that - or drop "
                  f"the quotation marks and cite the section for the idea.{RESET}")
        print()
        print(f"{RED}CITATION LINT: {len(problems)} quotation(s) not found in "
              f"the document named"
              + (f", {len(stale)} not at the lines named" if stale else "")
              + f" — exit 1{RESET}")
        return 1

    if stale:
        print()
        print(f"{RED}CITATION LINT: {len(stale)} quotation(s) not at the lines "
              f"named — exit 1{RESET}")
        return 1

    # THE STATE WORD (round 30), the same treatment count_lint's summary took
    # for the same reason: `clean` over a run that could not reach part of its
    # subject reads as a verdict about the subject rather than about the part
    # that was checked. Here the measurable skip is an attribution whose named
    # document is not in this tree.
    #
    # THE HALF THAT IS NOT IN THIS DENOMINATOR, stated on the line below it
    # rather than left to the docstring: an attribution whose SHAPE this tool
    # does not recognise is not skipped and not counted - it is invisible, and
    # round 26's evaluation read found a real ten-word one. RECALL_FLOOR is
    # the answer to that half and it is a floor, not a denominator. So this
    # percentage is the share of SEEN attributions that were checked, and it
    # is not a coverage figure for the class.
    state = "CLEAN" if not skipped else "PARTIAL"
    seen = checked + len(skipped)
    pct = (100.0 * checked / seen) if seen else 100.0
    print(f"{GREEN if state == 'CLEAN' else YELLOW}CITATION LINT: {state} - "
          f"{checked} of {seen} attribution(s) seen were checked ({pct:.1f}%), "
          f"0 unfound - exit 0{RESET}")
    print("            recall is a separate question: an attribution whose "
          "shape this tool does not recognise is invisible here, and "
          "RECALL_FLOOR is what holds that half.")
    return 0


# ==========================================================================
def selftest() -> int:
    """The negative controls. Each is labelled CITE(<id>) so the expectation
    lint can recover it from this source and report an unregistered one."""
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

    print(f"{BOLD}=== A. the forced-red half: a fabrication must be caught "
          f"==={RESET}")

    # THE ROUND-22 DEFECT, REPLANTED. The exact sentence that shipped, with
    # the exact string that is not in the source.
    fabricated = (
        "the kit already holds that line in two places - "
        "`EXISTING-PROJECT.md`'s provenance section keeps the timings off the "
        "page, and `DECISION-BRIEF.md` limitation 2 records that the walk "
        '"produced no usable invented time estimate". Use the same words.')
    src = ("2. **The walks were LLM personas, not humans.** Seven personas.\n"
           "   No human has run the walk.\n")
    seen = attributions(fabricated)
    check("CITE(fabricated-quote): the round-22 sentence shape is recognised, "
          "and the reference it lands on is the NEAREST one",
          [(f, s) for f, _, s, _l in seen], [("DECISION-BRIEF.md", "B")])
    # An empty extraction FAILS the check rather than crashing the run - a
    # selftest that aborts on IndexError reports nothing for every section
    # after it (the class round 20 recorded: crash instead of fail).
    check("CITE(fabricated-quote): ...and the quotation is NOT in the source",
          quote_is_in(seen[0][1], src) if seen else "NO ATTRIBUTION EXTRACTED",
          False)

    tp = attributions('He wrote "a line nobody ever wrote here" '
                      '(`README.md`:14).')
    check("CITE(trailing-paren): shape A, a fabrication in a parenthesised "
          "attribution, is caught too",
          quote_is_in(tp[0][1], "# README\nrails, not a runtime\n")
          if tp else "NO ATTRIBUTION EXTRACTED",
          False)

    print()
    print(f"{BOLD}=== B. the control that keeps it from manufacturing "
          f"findings ==={RESET}")

    # THE MOST IMPORTANT CONTROL IN THE FILE. This is the round-22 review's
    # own error, encoded: its grep was line-oriented, the source wrapped, and
    # a real quotation was reported as invented.
    wrapped_src = ("estimate is from the kit's streamlining report. One\n"
                   "LLM-persona walk has since adopted the kit. It produced "
                   "no usable\nhuman time estimate - it measures an agent "
                   "executing tool calls - but it\nproduced sixteen "
                   "findings.\n")
    needle = "produced no usable human time estimate - it measures an agent"
    check("CITE(wrapped-quote): a LINE-ORIENTED search misses a quotation "
          "that wraps in its source (the round-22 review's own error)",
          any(needle in line for line in wrapped_src.splitlines()), False)
    check("CITE(wrapped-quote): ...and this tool finds it, because both sides "
          "are whitespace-normalised",
          quote_is_in(needle, wrapped_src), True)
    check("CITE(wrapped-quote): ...and it holds when the QUOTATION is the "
          "side that wraps",
          quote_is_in("produced no usable human time\nestimate", wrapped_src),
          True)
    # FOUND BY THE FORCED-RED RUN, NOT BY DESIGN. The first build of this
    # tool excluded newlines from the quoted string itself, so a quotation
    # wrapped at the linting document's own margin - which is most of the
    # long ones in this kit - was never even SEEN, and the tool reported
    # clean over a planted fabrication. A checker with the same blind spot as
    # the defect is worse than no checker.
    check("CITE(wrapped-attribution): a quotation that wraps in the document "
          "being linted is still SEEN as an attribution",
          [f for f, _, _, _ in attributions(
              '`DECISION-BRIEF.md` limitation 2 records that the walk '
              '"yielded no human\nfactors measurement of any kind".')],
          ["DECISION-BRIEF.md"])
    check("CITE(wrapped-attribution): ...but a BLANK line ends it, so an "
          "unpaired quote mark cannot swallow whole paragraphs",
          attributions('`README.md` says "the words start here\n\nand a new '
                       'paragraph begins".'),
          [])

    print()
    print(f"{BOLD}=== C. what is NOT an attribution (the false-positive "
          f"floor) ==={RESET}")

    check("CITE(cell-boundary): a reference in a previous table cell does not "
          "attribute a quotation in this one",
          attributions("| Both are in `EXISTING-PROJECT.md`. | Step 4's "
                       '*"must print: VERIFY: PASS now"* is unreachable. |'),
          [])
    # Two documents named before one quotation. The quotation belongs to the
    # NEAREST, and the farther one must not also be made to answer for it -
    # that is how a proximity heuristic invents findings against innocent
    # documents. The rule that produces this is the no-backtick glue: the
    # LEVEL-1 match has `QUICKSTART.md` in its glue and is discarded.
    check("CITE(intervening-ref): with two documents named, the quotation is "
          "attributed to the NEAREST one and to that one only",
          attributions('`LEVEL-1.md` says, and so does `QUICKSTART.md`, that '
                       '"the words in question here" apply.'),
          [("QUICKSTART.md", "the words in question here", "B", "")])
    # ALSO FOUND BY THE FIRST LIVE RUN. Three of its five findings were one
    # class: a reference in an earlier PARAGRAPH, describing something else,
    # pulled onto a quotation that had nothing to do with it - a blockquoted
    # interview question, a persona prompt quoted from further down the same
    # page. Same principle as the cell rule, one level up.
    check("CITE(paragraph-break): a reference in an earlier paragraph does "
          "not attribute a quotation in a later one",
          attributions('Write the answers into `PROFILE-TEMPLATE.md`, '
                       'verbatim.\n\n## 1. Decision style\n\n'
                       '> **"When I have analysed something, do you want my '
                       'recommendation or the options?"**'),
          [])
    check("CITE(paragraph-break): ...and the same rule applies to shape A",
          attributions('"a quotation standing on its own here"\n\n'
                       'Some later paragraph (`README.md`:14).'),
          [])
    check("CITE(short-literal): a short quoted literal is a named output "
          "line, not a quotation",
          attributions('`QUICKSTART.md` Step 6 prints "0 skipped".'), [])
    check("CITE(short-literal): ...and the floor is the word count, so a long "
          "literal IS checked",
          [f for f, _, _, _ in attributions(
              '`QUICKSTART.md` Step 6 checkpoint prints "armed: for every '
              'block and no CONFIG WARNING".')],
          ["QUICKSTART.md"])
    check("CITE(self-quote): a document quoting itself is not an attribution",
          attributions('`ONBOARD.md` says "the shipped documents are the '
                       'authority here".', self_name="ONBOARD.md"), [])

    print()
    print(f"{BOLD}=== D. the clean half: a real quotation passes ==={RESET}")

    real_src = ("The kit remains rails, not a runtime, and every command it\n"
                "names is one of the documents' own.\n")
    rq = attributions('`README.md`:14 calls it "rails, not a runtime, '
                      'and every command it names".')
    check("CITE(real-quote): a quotation that IS in the source is clean",
          quote_is_in(rq[0][1], real_src)
          if rq else "NO ATTRIBUTION EXTRACTED",
          True)
    check("CITE(real-quote): ...and the shape is recognised with no locator "
          "at all",
          [f for f, _, s, _l in attributions(
              '`README.md` calls it "rails, not a runtime, and every '
              'command".')],
          ["README.md"])

    # ALSO FOUND BY A LIVE RUN - this time against the register row written to
    # record this very tool. An odd number of quote marks inside one table cell
    # made the pattern pair the CLOSING quote of one phrase with the OPENING
    # quote of the next, capturing a 300-character span of prose as a
    # "quotation". A quotation does not cross a cell boundary either.
    check("CITE(quote-cell-boundary): a quoted span that crosses a table-cell "
          "boundary is mis-paired quote marks, not a quotation",
          attributions('`QUICKSTART.md` says "the pointer was wrong. | '
                       '**FIXED** - cited as the two failure signatures".'),
          [])
    check("CITE(register): a findings register's attributions are not checked "
          "against the fixed tree - it quotes text as it was",
          "KNOWN-ISSUES.md" in REGISTER_DOCS, True)
    check("CITE(register): ...and the exemption is by document, so an ordinary "
          "page gets no such pass",
          "ONBOARD.md" in REGISTER_DOCS, False)

    check("CITE(waiver): a waiver covers a named case...",
          waiver_for("SEED-INTERVIEW.md",
                     "Default 1 (recommendation-first) is\n overridden")
          is not None, True)
    check("CITE(waiver): ...and does not cover anything else",
          waiver_for("ONBOARD.md", "Default 1 (recommendation-first) is"), None)
    check("CITE(waiver): ...and every shipped waiver carries a reason (an "
          "empty one is the silent case)",
          [k for k, v in WAIVERS.items() if not (v or "").strip()], [])

    print()
    print(f"{BOLD}=== E. the RECALL FLOOR: named attributions in the shipped "
          f"kit ==={RESET}")
    root = Path(__file__).resolve().parent.parent
    docs = kit_documents(root)
    index = {}
    for p in docs:
        index.setdefault(p.name, p)
    check("the kit's own documents are found", len(docs) > 10, True)
    total = 0
    for d in docs:
        total += len(attributions(d.read_text(encoding="utf-8"), d.name))
    check("...and the lint sees attributions in them (a pattern that matches "
          "nothing is a check that proves nothing)", total > 0, True)

    # ROUND 27, finding m4. A presence count is not recall. Until this block
    # existed, a pattern that had quietly stopped seeing a whole shape of
    # attribution still passed section E, because the OTHER shapes kept the
    # total above zero. Each named row is asserted twice.
    for doc_name, ref_name, opening in RECALL_FLOOR:
        src_doc = index.get(doc_name)
        if src_doc is None:
            check(f"CITE(recall-floor): {doc_name} -> {ref_name}: the document is "
                  f"in the tree", False, True)
            continue
        found = [(r, q) for r, q, _s, _l in
                 attributions(src_doc.read_text(encoding="utf-8"), doc_name)
                 if r == ref_name
                 and flatten(q).startswith(flatten(opening))]
        # Found, not counted. A document may legitimately make the same
        # attribution twice - `ONBOARD.md` does - and pinning an occurrence
        # count would make the floor red on an edit that changed no recall.
        check(f"CITE(recall-floor): {doc_name} -> {ref_name}: \"{opening}...\" is "
              f"EXTRACTED as an attribution", bool(found), True)
        if not found:
            continue
        target = resolve(root, ref_name, index)
        check(f"CITE(recall-floor): {doc_name} -> {ref_name}: ...and its "
              f"quotation is in the document it names",
              target is not None
              and quote_is_in(found[0][1],
                              target.read_text(encoding="utf-8")),
              True)

    print()
    print(f"{BOLD}=== F. the LINE WINDOW: is the quotation where the locator "
          f"says ==={RESET}")

    # THE NORMALISATION INVARIANT. The window layer recovers line numbers with
    # its own walk over the text; if that walk ever diverges from flatten(), a
    # quotation could be present to one layer and absent to the other. Asserted
    # against every shipped document rather than a fixture, because the
    # divergence would be in some real document's whitespace, not in a literal
    # written here.
    diverged = [d.name for d in docs
                if flatten_with_lines(d.read_text(encoding="utf-8"))[0]
                != flatten(d.read_text(encoding="utf-8"))]
    check("CITE(window-normalisation): flatten_with_lines() produces exactly "
          "flatten()'s string, over every shipped document", diverged, [])

    win_src = ("line one\n"
               "line two\n"
               "the quotation begins here and\n"
               "finishes on this line\n"
               "line five\n")
    q_win = "the quotation begins here and finishes on this line"
    check("CITE(window-lines): a wrapped quotation reports the span it really "
          "occupies", quote_line_spans(q_win, win_src), [(3, 4)])
    check("CITE(window-lines): ...and a locator naming only its FIRST line "
          "still overlaps, so a wrap is not a finding",
          quote_in_window(q_win, win_src, 3, 3), True)
    check("CITE(window-lines): ...and a WIDER range containing it passes too",
          quote_in_window(q_win, win_src, 1, 5), True)

    # THE FORCED-RED HALF. The round-22 defect's real shape: right words, wrong
    # lines. Tolerance is 0 and the tightest round-26 defect was ONE line out,
    # so the off-by-one case is the one that must be red.
    check("CITE(window-stale): a locator ONE line past the quotation is a "
          "finding (tolerance is 0 by design)",
          quote_in_window(q_win, win_src, 5, 6), False)
    check("CITE(window-stale): ...and one entirely elsewhere in the file",
          quote_in_window(q_win, win_src, 1, 2), False)
    check("CITE(window-stale): ...while the presence check alone still says "
          "the words ARE in the document - that is the gap this closes",
          quote_is_in(q_win, win_src), True)
    check("CITE(window-stale): ...and a tolerance wide enough to reach it "
          "would pass it, which is why the shipped tolerance is 0",
          quote_in_window(q_win, win_src, 5, 6, tol=1), True)

    check("CITE(window-locator): a LINE locator yields a window",
          line_span(":40-41"), (40, 41))
    check("CITE(window-locator): ...a single line is a one-line window",
          line_span(":208"), (208, 208))
    check("CITE(window-locator): ...a SECTION locator yields none, so the "
          "attribution is checked for presence only", line_span(" Step 4"), None)
    check("CITE(window-locator): ...and an absent locator yields none",
          line_span(""), None)
    check("CITE(window-locator): the extractor carries the locator through",
          [(f, l) for f, _q, _s, l in attributions(
              '`README.md`:14-15 calls it "rails, not a runtime, and every '
              'command it names".')],
          [("README.md", ":14-15")])

    # A quotation may appear more than once; any occurrence in the window is a
    # correct citation. Without this the check would invent findings against
    # documents that repeat a phrase - the same failure mode the wrapped-quote
    # control exists to prevent, one layer up.
    twice = "alpha\nthe repeated words\nbeta\ngamma\nthe repeated words\ndelta\n"
    check("CITE(window-repeat): a phrase occurring twice reports both spans",
          quote_line_spans("the repeated words", twice), [(2, 2), (5, 5)])
    check("CITE(window-repeat): ...and a locator naming EITHER one passes",
          [quote_in_window("the repeated words", twice, 2, 2),
           quote_in_window("the repeated words", twice, 5, 5)], [True, True])
    check("CITE(window-repeat): ...but a locator naming neither is still a "
          "finding", quote_in_window("the repeated words", twice, 3, 4), False)

    print()
    print((GREEN if ok_all else RED)
          + f"CITATION-LINT SELFTEST: {'PASS' if ok_all else 'FAIL'} "
            f"— {n} checks" + RESET)
    return 0 if ok_all else 1


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Does the quotation exist? Checks quoted strings "
                    "attributed to a named kit document against that document.",
        epilog="exit 0 clean · 1 a quotation is not there · 2 abort")
    ap.add_argument("--root", default="", help="the tree to lint")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--list", action="store_true",
                    help="print every attribution seen, found or missing")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    root = Path(a.root).resolve() if a.root else Path(__file__).resolve().parent.parent
    if not root.is_dir():
        print(f"{RED}CITATION LINT: ABORT — no such directory: {root}{RESET}")
        return 2
    return run(root, a.list)


if __name__ == "__main__":
    sys.exit(main())
