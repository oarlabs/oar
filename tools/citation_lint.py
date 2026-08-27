#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/citation_lint.py - the attribution lint. Does the quotation exist?

    python tools/citation_lint.py                 # lint the kit's own documents
    python tools/citation_lint.py --root <path>   # lint another tree
    python tools/citation_lint.py --selftest      # incl. the negative controls
    python tools/citation_lint.py --list          # print every attribution seen
    python tools/citation_lint.py --fix           # rewrite stale locators that
                                                  # relocate to exactly one place

    exit 0  clean - every quoted string attributed to a named kit document was
            found in that document, and every section anchor names a heading
            that exists
    exit 1  at least one quotation is not in the document it names, is not at
            the lines its locator names (the round-27 window class), or names a
            section the target does not have
    exit 2  abort (no root, nothing to read)

==========================================================================
THE THREE CITATION FORMS THIS TOOL VERIFIES
==========================================================================
Write a citation in one of these three forms and the lint can check it.

  1. QUOTE + LINE LOCATOR    `FILE.md`:40-41 says "the quoted words"
     The words must be in the file, and at those lines. Brittle by
     construction: a line number is correct only until somebody edits above
     it. v2 repairs it instead of only reporting it - see THE RELOCATION
     PASS below.

  2. SECTION ANCHOR          `FILE.md` §6
     The target must carry a heading numbered 6. Survives edits above it.
     Measured on 2026-08-26, before this round's migration: 46 in the tree,
     zero breaks across a day of editing that broke three line locators.

  3. HEADING ANCHOR          `FILE.md`, "Also measured, at Level 1"
     The quoted string must appear in a HEADING of the target, not merely
     somewhere in its prose. The quotation must be ADJACENT to the
     reference - only whitespace, a comma, or a section locator between
     them - because that adjacency is what distinguishes "I am naming a
     section" from "I am quoting a sentence". Put any word between the
     reference and the quotation and it is an ordinary attribution again,
     checked for presence rather than for being a heading.

     RESIDUAL, STATED: comma adjacency is a heuristic for intent, not a proof
     of it, so a sentence that genuinely reads `FILE.md`, "the quoted words"
     and means the words rather than a heading is claimed by this form and
     asked to be a heading - zero instances in the shipped kit at round 34,
     where all 26 adjacent-quote references named headings, and the escape
     hatch is printed in the finding itself.

PREFER 2 AND 3 FOR A BARE REFERENCE - one carrying no quotation of its own,
which is the class this guidance is about; it does NOT extend to a line
locator that already sits beside its quotation, because there the ±0 window
re-decides the number on every run, the locator cannot rot silently, and
converting it would trade a stronger check for a weaker one (the kit keeps
its 11 quote-guarded line locators deliberately, at the round-34 review's
ruling). A line locator is a fact about a file's current formatting. A
heading is a fact about its content.

==========================================================================
THE RELOCATION PASS, AND --fix
==========================================================================
When a quotation is real but its line locator is stale, the tool searches
the target for the quotation:

  - exactly one match elsewhere - the finding names the exact replacement,
    and `--fix` rewrites the locator in place. Only the digits move. The
    quoted text is never touched.
  - zero matches - the quotation is not in the document at all, which is the
    stronger finding and is reported as such.
  - more than one match - the correct locator is ambiguous, so the tool
    refuses to choose. Red, with every candidate printed.

`--fix` rewrites, re-runs the analysis once, and reports on the repaired
tree. It edits only locator digits inside a citation. It never edits a
quotation, a heading, or any other number.

==========================================================================
THE BARE-LOCATOR DISCLOSURE
==========================================================================
A reference of the form `FILE.md`:40 with NO quotation next to it carries
no needle, so nothing here can decide whether 40 is still the right line.
Those references were previously invisible: not checked, not skipped, not
counted. v2 counts them and prints where they are, as a segment of the
summary line - "N bare locator(s) unguarded".

They are a DISCLOSURE, not a finding. Making them red would red the whole
tree at once over a class nobody has yet had a chance to migrate, and a red
that means "the migration is unfinished" is a red people learn to skip -
the same argument `tools/expectation_lint.py` makes for its NEVER value.
The way to clear one is to migrate it to form 2 or form 3 above.

Register documents (KNOWN-ISSUES.md) are exempt, as they are for
quotations: a register records a locator as it was when a finding was
raised.

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
  - **A right quotation under a wrong SECTION.** Narrowed again in v2, not
    closed. `FILE.md` §6 and `FILE.md`, "Heading text" are now resolved
    against the target's headings. `FILE.md` limitation 2 and `FILE.md` Step 4
    are not: they name a document's internal numbering rather than a heading,
    and no rule here maps one to the other. A quotation moved to the wrong
    Step of the right document still passes.
  - **A stale locator carrying no quotation of its own.** The window check
    needs a needle. v2 COUNTS these rather than checking them - see THE
    BARE-LOCATOR DISCLOSURE above. Two neighbouring shapes are not even
    counted, and are named here rather than left to be assumed covered:
      - a BARE trailing locator - `` Step 3 is headed "..." (:366) `` - names
        a line but no file, so there is nothing to resolve it against.
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
    only, still.
  - **Whether a bare locator's number is RIGHT.** `` `LEVEL-1.md`:320's rule ``
    names a file and a line and quotes nothing, so there is no needle. v2
    counts and prints it; nothing here decides it. `tools/count_lint.py` is
    blind to the same shape from the other side: its `SECTION_REF` excludes
    the bare line form by design, since a line range names no enumerable
    section. So NEITHER LINT DECIDES A BARE `DOC.md`:N REFERENCE, and neither
    one's green is evidence that the number is still right. Round 24 shipped
    two stale ones inside a clause written that same round, and its review
    found them by hand (m1). The disclosure makes the residual countable; the
    migration to a section anchor is what actually closes one.
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


def attributions_located(doc_text: str, self_name: str = ""):
    """`attributions()`, plus where the LOCATOR sits in the citing document.

    Rows are (filename, quotation, shape, locator, loc_start, loc_end). The two
    offsets are what makes `--fix` possible: a repair rewrites exactly the
    characters between them and nothing else. They also tell the bare-locator
    scan which line references are already guarded by a quotation."""
    found = []
    for m in SHAPE_B.finditer(doc_text):
        if MD_REF.search(m.group("glue")):
            # Another document was named between the reference and the quote,
            # so the reference no longer attributes it.
            continue
        if PARA_BREAK.search(m.group("glue")):
            continue
        found.append((m.start("q"), m.group("f"), m.group("q"), "B",
                      m.group("loc") or "", m.start("loc"), m.end("loc")))
    for m in SHAPE_A.finditer(doc_text):
        if PARA_BREAK.search(m.group("glue")):
            continue
        found.append((m.start("q"), m.group("f"), m.group("q"), "A",
                      m.group("loc") or "", m.start("loc"), m.end("loc")))

    out, seen = [], set()
    for pos, ref, quote, shape, loc, a, b in sorted(found):
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
        out.append((ref, quote, shape, loc, a, b))
    return out


def attributions(doc_text: str, self_name: str = ""):
    """Every (filename, quotation, shape, locator) this tool claims to see.

    Returns them in document order. A quotation attributed to the document it
    is written in is dropped: a page quoting itself is not an attribution. The
    locator is the raw text as written (`:40-41`, ` Step 4`, or empty);
    `line_span()` turns the line forms into a window and returns None for the
    rest."""
    return [(r, q, s, l)
            for r, q, s, l, _a, _b in attributions_located(doc_text, self_name)]


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


# --------------------------------------------------------------------------
# THE RELOCATION PASS
# --------------------------------------------------------------------------
def retarget(loc: str, lo: int, hi: int) -> str:
    """A locator with its LINE NUMBERS replaced, and nothing else changed.

    Pure, and deliberately narrow. It rewrites only the digits `_LINE_LOC`
    matched: a locator reading ` Step 4:12` keeps its ` Step 4`. Anything with
    no line form in it comes back unchanged, so a caller cannot use this to
    edit a section name."""
    m = _LINE_LOC.search(loc or "")
    if not m:
        return loc
    dash = "–" if "–" in m.group(0) else "-"
    new = f":{lo}" if lo == hi else f":{lo}{dash}{hi}"
    return loc[:m.start()] + new + loc[m.end():]


def relocation(quote: str, source_text: str, lo: int, hi: int,
               tol: int = LINE_TOLERANCE):
    """Where a stale locator SHOULD point, or None if that is not decidable.

    Returns the single (first, last) span the quotation occupies, when the
    quotation occurs exactly once and that once is outside the named window.
    Zero occurrences is the stronger 'not in this document' finding, and more
    than one is ambiguous - in both cases this returns None and the tool
    reports rather than repairs. A tool that guesses which of two candidates
    the author meant would write a wrong locator with a green beside it."""
    spans = quote_line_spans(quote, source_text)
    if len(spans) != 1:
        return None
    first, last = spans[0]
    if first <= hi + tol and last >= lo - tol:
        return None
    return spans[0]


def contested(claims) -> bool:
    """Must `--fix` refuse this locator? `claims` is one entry per claimant.

    THE ROUND-34 REVIEW'S MAJOR-2. One locator can be claimed by TWO
    attributions: shape A reads the quotation BEFORE the reference and shape B
    the quotation AFTER it, and a sentence shaped
    `"first quote" (`SRC.md`:18) says "second quote"` gives both of them the
    same `:18`. The two claimants want different line numbers, so repairing for
    one breaks the other. The reviewer measured the result: `:18` to `:5` to
    `:18` across five `--fix` runs, exit stuck at 1, never converging.

    A locator with one claimant is never contested. With more than one:

      ""     this claimant is SATISFIED - its quotation is at the locator now
      None   stale, and not relocatable (nowhere, or ambiguous)
      ":N"   stale, and relocatable to exactly this

    Refuse when writing anything would be wrong for somebody: a satisfied
    claimant would be broken by any rewrite, an unrepairable one cannot be
    served, and two different concrete replacements cannot both be written.
    Agreement is the only case that proceeds - and if every claimant is
    satisfied there is nothing to write in the first place."""
    if len(claims) < 2:
        return False
    wanted = {c for c in claims if c}
    if not wanted:
        return False
    if None in claims or "" in claims:
        return True
    return len(wanted) > 1


def splice(text: str, spans):
    """`text` with each (start, end, replacement) applied. Pure.

    APPLIED FROM THE LAST OFFSET BACKWARDS, which is the whole reason this is
    its own function. Forward order shifts every later offset by the length
    delta of every earlier edit, and the review's MINOR-3 found that nothing
    asserted the order: a forward-order mutant passed all 87 checks while
    destroying a citation line, because every control until then applied a
    single edit, and one edit is correct in either order."""
    for start, end, new in sorted(spans, reverse=True):
        text = text[:start] + new + text[end:]
    return text


# --------------------------------------------------------------------------
# SECTION ANCHORS: the citation form that survives an edit above it
# --------------------------------------------------------------------------
# An ATX heading. Setext headings (underlined with === or ---) are not read;
# the kit writes none, and the shipped documents are the tree this runs over.
HEADING = re.compile(r'^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$', re.M)


# --------------------------------------------------------------------------
# FENCED CODE, WHICH IS NOT PROSE ON EITHER SIDE
# --------------------------------------------------------------------------
# THE ROUND-34 REVIEW'S MAJOR-1. `# 9. copy the runner` inside a ```bash block
# is a shell comment. Read as markdown it is an ATX heading, and the first build
# of the section-anchor layer read it that way: 41 phantom headings across the
# shipped kit (QUICKSTART 22, the modules 13, ONBOARD 6). That is wrong in both
# directions at once.
#
#   TARGET SIDE   a phantom heading lets a section anchor resolve to something
#                 no reader can see, so the check passes a citation that is
#                 wrong. A false GREEN.
#   CITING SIDE   a `FILE.md` §9 written inside a fence is an EXAMPLE of the
#                 citation form, not a citation. Reading it as one reports a
#                 finding against a document that is fine. A false RED, and this
#                 kit's rule is that manufacturing findings is the worse half.
#
# So fences are masked on BOTH sides. The idiom is `fence_line_set()` in
# `tools/skim_lint.py`, reused rather than reinvented: both markers, a block
# closes only on its own marker, and an unclosed fence swallows the rest of the
# document - which is what a renderer does with one.
#
# MASKED, NOT DELETED. `--fix` splices by character offset and the bare scan
# reports line numbers, so the text this tool matches over has to stay the text
# on disk. Matches are dropped by LINE instead.
def fenced_lines(text: str):
    """Every 0-based line index inside a fenced code block, markers included."""
    inside, open_at, marker = set(), None, None
    lines = text.splitlines()
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


def line_index(text: str, pos: int) -> int:
    """The 0-based line index of a character offset."""
    return text.count("\n", 0, pos)


# `FILE.md` §6. The section number may be dotted - §4.5 - because the kit's own
# headings are. The dot must be FOLLOWED BY A DIGIT to be part of the number:
# `§4.7.` at the end of a sentence is section 4.7 and a full stop, and a first
# build that read it as "4.7." reported a section that does not exist.
SECTION_REF = re.compile(
    r'`(?P<f>' + _NAME + r')`\s*§\s*(?P<n>\d+(?:\.\d+)*)')

# `FILE.md`, "Also measured, at Level 1" - the HEADING ANCHOR. The quotation
# must be ADJACENT: whitespace, one comma, and an optional locator are all that
# may sit between the reference and the opening quote. That adjacency is the
# whole discriminator between naming a section and quoting a sentence, so it is
# kept tight on purpose. A heading anchor is checked against the target's
# HEADINGS; anything with a word in the glue stays an ordinary attribution and
# is checked for presence.
HEADING_REF = re.compile(
    r'`(?P<f>' + _NAME + r')`(?P<loc>' + _LOC + r')[ \t]*,?[ \t]*'
    r'[*_]{0,2}"(?P<h>[^"\n]{4,160})"')

# `FILE.md`:40, `FILE.md`:40-41, and the WORD form `FILE.md` line 40 /
# `FILE.md` lines 40-41. The bare-locator scan starts here and then removes the
# ones a quotation already guards. The word form is in `_LOC` already, so an
# attribution has always been able to carry it; the review's MINOR-6 was that
# the DISCLOSURE could not see it, which made the same reference countable in
# one spelling and invisible in the other.
LINE_REF = re.compile(
    r'`(?P<f>' + _NAME + r')`'
    r'(?P<loc>\s*:\s*\d+(?:\s*[-–]\s*\d+)?'
    r'|\s+lines?\s+\d+(?:\s*[-–]\s*\d+)?)')


def headings(text: str):
    """Every ATX heading's text, whitespace-normalised, in document order.

    FENCED LINES ARE NOT READ. `# 9. copy the runner` inside a ```bash block is
    a shell comment, and reading it as a heading resolves section anchors
    against something no reader can see - the review's MAJOR-1, measured at 41
    phantom headings in the shipped kit."""
    skip = fenced_lines(text)
    return [flatten(m.group(1)) for m in HEADING.finditer(text)
            if line_index(text, m.start()) not in skip]


def section_hit(number: str, source_text: str) -> bool:
    """Does the source carry a heading numbered `number`?

    The kit numbers headings `## 6. The wiring` and `### 4.5 Ignore rules`, so
    the test is that a heading STARTS with the number followed by a dot, a
    space, or the end of the heading. `§4` does not match `## 4.5 ...` unless
    that is the whole numbering, which is the correct strictness: §4 and §4.5
    are different sections."""
    pat = re.compile(re.escape(number) + r'(\.(?!\d)|\s|$)')
    return any(pat.match(h) for h in headings(source_text))


def heading_hit(title: str, source_text: str) -> bool:
    """Is the quoted title part of a HEADING in the source?

    Containment rather than equality, because the kit's headings carry leading
    numbering and trailing clauses that a citation reasonably drops: `### 4.5
    ONE MACHINE PER SETTINGS FILE` is cited as "ONE MACHINE PER SETTINGS FILE".
    Containment in a heading is still a much narrower claim than containment in
    the document, which is what the presence check already gives."""
    needle = flatten(title)
    return any(needle in h for h in headings(source_text))


def section_refs(text: str, self_name: str = ""):
    """Every (filename, section number) named with the `§N` form.

    Fenced lines are skipped: a `FILE.md` §9 inside a code block is an EXAMPLE
    of the citation form, not a citation, and reporting it is how a new check
    manufactures findings against a document that is fine."""
    skip = fenced_lines(text)
    return [(m.group("f"), m.group("n")) for m in SECTION_REF.finditer(text)
            if line_index(text, m.start()) not in skip
            and not (self_name and Path(m.group("f")).name == self_name)]


def heading_refs(text: str, self_name: str = ""):
    """Every (filename, quoted title) named with the adjacent-quote form.

    A reference carrying a LINE locator is NOT a heading anchor even when its
    quotation is adjacent: the author named lines, so the words are prose and
    the window check owns them. Excluding that case costs nothing measured (no
    heading anchor in the shipped kit carries a line locator) and removes the
    one shape where this form could steal an ordinary quotation.

    Fenced lines are skipped, for the same reason `section_refs()` skips them.

    RESIDUAL, STATED (the review's MINOR-8): comma adjacency is a heuristic,
    not a proof of intent. A sentence that legitimately reads `` `FILE.md`, "the
    quoted words" `` and means the words rather than a heading is claimed by
    this form and asked to be a heading. Zero instances in the shipped kit at
    round 34, where all 26 adjacent-quote references were heading names. The
    escape hatch is in the finding's own message: put a word between the
    reference and the quotation."""
    skip = fenced_lines(text)
    return [(m.group("f"), m.group("h")) for m in HEADING_REF.finditer(text)
            if line_span(m.group("loc")) is None
            and line_index(text, m.start()) not in skip
            and not (self_name and Path(m.group("f")).name == self_name)]


def bare_locators(text: str, guarded=()):
    """Every (filename, locator, line) line reference with no quotation on it.

    `guarded` is the (start, end) span of every locator that an attribution
    already owns, from `attributions_located()`. What is left is the invisible
    class: a line number with no needle beside it, which nothing in this tool
    can decide. They are counted and printed, never failed - see THE
    BARE-LOCATOR DISCLOSURE in the module docstring.

    Fenced lines are skipped (the review's MINOR-7). A locator inside a code
    block is an example of the form, and counting it inflates a number whose
    whole job is to say how much real migration is left."""
    skip = fenced_lines(text)
    out = []
    for m in LINE_REF.finditer(text):
        at = m.start("loc")
        if any(a <= at < b for a, b in guarded):
            continue
        if line_index(text, m.start()) in skip:
            continue
        out.append((m.group("f"), m.group("loc").strip(),
                    line_index(text, m.start()) + 1))
    return out


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


def apply_fixes(edits) -> int:
    """Rewrite stale locators in place. `edits` is (path, start, end, new).

    The ordering rule lives in `splice()`, which is pure and controlled.
    Returns how many locators were written."""
    by_doc = {}
    for path, start, end, new in edits:
        by_doc.setdefault(path, []).append((start, end, new))
    written = 0
    for path, spans in by_doc.items():
        path.write_text(splice(path.read_text(encoding="utf-8"), spans),
                        encoding="utf-8")
        written += len(spans)
    return written


def run(root: Path, show_all: bool, fix: bool = False,
        _repaired: int = 0) -> int:
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
    anchors, anchor_bad, register_anchors = 0, [], 0
    bare, register_bare = [], 0
    # Every claimant of every LINE locator, keyed by the locator's exact span in
    # its document. One span can have two claimants - see `contested()`.
    claims = {}
    for doc in docs:
        try:
            text = doc.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"{RED}CITATION LINT: ABORT — cannot read {doc}: {exc}{RESET}")
            return 2
        rows = attributions_located(text, doc.name)
        if doc.name in REGISTER_DOCS:
            register += len(rows)
            register_anchors += (len(section_refs(text, doc.name))
                                 + len(heading_refs(text, doc.name)))
            register_bare += len(bare_locators(
                text, [(a, b) for *_r, a, b in rows]))
            continue

        # ---- SECTION ANCHORS, checked before the quotations so that a heading
        # anchor naming a section that is not there is reported once, as the
        # section finding, rather than twice.
        anchor_reported = set()
        for ref, number in section_refs(text, doc.name):
            src = resolve(root, ref, index)
            if src is None or src.resolve() == doc.resolve():
                skipped.append((doc, ref, f"§{number}"))
                continue
            if src not in cache:
                cache[src] = src.read_text(encoding="utf-8")
            anchors += 1
            if not section_hit(number, cache[src]):
                anchor_bad.append((doc, ref, f"§{number}", "section number"))
        for ref, title in heading_refs(text, doc.name):
            src = resolve(root, ref, index)
            if src is None or src.resolve() == doc.resolve():
                skipped.append((doc, ref, title))
                continue
            if src not in cache:
                cache[src] = src.read_text(encoding="utf-8")
            anchors += 1
            if not heading_hit(title, cache[src]):
                anchor_bad.append((doc, ref, f'"{flatten(title)[:70]}"',
                                   "heading"))
                anchor_reported.add(flatten(title))

        # ---- THE BARE-LOCATOR DISCLOSURE. Everything LINE_REF sees that no
        # attribution owns, and whose file is in this tree.
        for ref, loc, line in bare_locators(
                text, [(a, b) for *_r, a, b in rows]):
            if resolve(root, ref, index) is None:
                continue
            bare.append((doc, ref, loc, line))

        for ref, quote, shape, loc, loc_start, loc_end in rows:
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
                elif flatten(quote) in anchor_reported:
                    # Already raised as a section anchor naming a heading that
                    # is not there. One citation, one finding.
                    pass
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
            key = (doc, loc_start, loc_end)
            if quote_in_window(quote, cache[src], *span):
                # A SATISFIED CLAIMANT. Recorded, because a locator that is
                # right for this quotation must not be rewritten for another
                # one that happens to share it - the review's MAJOR-2.
                claims.setdefault(key, []).append("")
                continue
            at = quote_line_spans(quote, cache[src])
            reason = waiver_for(doc.name, quote)
            if reason:
                # A waived window finding prints with its reason like every
                # other waiver - suppressing it silently is the exact case the
                # WAIVERS convention forbids.
                waived.append((doc, ref, quote, reason))
                continue
            # THE RELOCATION PASS. The words are somewhere; is there exactly
            # one somewhere?
            to = relocation(quote, cache[src], *span)
            new = retarget(loc, *to) if to else None
            claims.setdefault(key, []).append(new)
            stale.append((doc, ref, quote, shape, span, at, new, key))

    # ---- CONTESTED LOCATORS. A span more than one attribution claims, where
    # any rewrite would be wrong for one of them. `--fix` refuses these; the
    # finding still stands, so the exit code is unchanged.
    conflicted = {k for k, c in claims.items() if contested(c)}
    edits, seen_key = [], set()
    for _d, _r, _q, _s, _sp, _at, new, key in stale:
        if not new or key in conflicted or key in seen_key:
            continue
        seen_key.add(key)
        edits.append((key[0], key[1], key[2], new))

    # ---- THE REPAIR. Rewrite, then run the whole analysis again over the
    # repaired tree, so what gets reported is the state the tree is actually
    # in when the command exits - not the state it was in when it started.
    if fix and edits:
        n = apply_fixes(edits)
        print()
        for path, _s, _e, new in sorted(edits, key=lambda e: (str(e[0]), e[1])):
            print(f"{YELLOW}FIXED{RESET}  {path.as_posix()}  ->  {new}")
        print(f"{YELLOW}--fix rewrote {n} stale locator(s). Re-running over "
              f"the repaired tree.{RESET}")
        return run(root, show_all, fix=False, _repaired=n)

    print()
    print(f"root      : {root}")
    print(f"documents : {len(docs)} scanned")
    print(f"checked   : {checked} attributed quotation(s)")
    print(f"windows   : {windowed} of those named a LINE and were checked "
          f"against it (overlap, tolerance ±{LINE_TOLERANCE} lines)")
    print(f"anchors   : {anchors} section anchor(s) (`FILE.md` §N and "
          f"`FILE.md`, \"Heading\") resolved against the target's headings")
    # THE DISCLOSURE. Not a finding, and printed whether or not there are any,
    # so that a zero is a measurement rather than a silence.
    print(f"bare      : {len(bare)} line locator(s) with NO quotation beside "
          f"them — nothing here can decide these; migrate them to §N or to a "
          f"quoted heading")
    for doc, ref, loc, line in bare:
        print(f"{YELLOW}  unguarded{RESET}  {doc.as_posix()}:{line} -> "
              f"{ref}{loc}")
    # A skip nobody sees is not a skip - the same rule the expectation lint
    # applies to its waivers.
    print(f"skipped   : {len(skipped)} citation(s) whose document is not in "
          f"this tree (printed with --list)")
    print(f"register  : {register} attribution(s), {register_anchors} anchor(s) "
          f"and {register_bare} bare locator(s) NOT checked, in "
          f"{', '.join(sorted(REGISTER_DOCS))} — a findings register quotes "
          f"text as it was, which a fixed tree no longer contains")
    if _repaired:
        print(f"repaired  : {_repaired} stale locator(s) rewritten by --fix "
              f"before this run")
    # A waiver nobody sees is not a waiver - every run prints every one.
    print(f"waivers   : {len(waived)} (each printed below, every run)")
    for doc, ref, quote, reason in waived:
        print(f"{YELLOW}  WAIVED {doc.name} -> {ref}: "
              f"\"{flatten(quote)[:60]}...\"\n    {reason}{RESET}")
    if show_all:
        for doc, ref, quote in skipped:
            print(f"  {YELLOW}skip{RESET}  {doc.name} -> {ref}: "
                  f"\"{quote[:70]}\"")

    if anchor_bad:
        print()
        for doc, ref, named, kind in anchor_bad:
            print(f"{RED}NAMES A SECTION THAT IS NOT THERE{RESET}  "
                  f"{doc.as_posix()}")
            print(f"  cited as      : {ref} {named}")
            print(f"  {BOLD}No {kind} in {ref} answers to that. Open {ref}, "
                  f"read its headings, and cite one of those — or, if you meant "
                  f"to quote a sentence rather than name a section, put a word "
                  f"between the reference and the quotation.{RESET}")

    if stale:
        print()
        for doc, ref, quote, shape, (lo, hi), at, new, key in stale:
            where = ", ".join(f"{a}-{b}" if a != b else str(a) for a, b in at)
            print(f"{RED}NOT AT THE LINES IT NAMES{RESET}  "
                  f"[shape {shape}]  {doc.as_posix()}")
            print(f"  attributed to : {ref}:{lo}" + (f"-{hi}" if hi != lo else ""))
            print(f"  quotation     : \"{flatten(quote)[:90]}\"")
            print(f"  actually at   : {ref}:{where or 'NOWHERE IN THAT FILE'}")
            if key in conflicted:
                # CONTESTED. Two attributions share this one locator and want
                # different things from it, so any rewrite breaks one of them.
                print(f"  {BOLD}CONFLICT — this locator is claimed by "
                      f"{len(claims[key])} attributions that do not agree on "
                      f"it, so --fix leaves it alone. Give each quotation its "
                      f"own reference, or anchor one of them to a section."
                      f"{RESET}")
            elif new:
                # RELOCATABLE. One occurrence, so the replacement is a fact
                # rather than a guess, and the message says exactly what to
                # write. `--fix` writes it.
                print(f"  {BOLD}RELOCATABLE — replace the locator with "
                      f"`{new}` (run --fix to do it), or re-quote from the "
                      f"lines you meant.{RESET}")
            else:
                print(f"  {BOLD}AMBIGUOUS — the quotation occurs "
                      f"{len(at)} time(s), so there is no single correct "
                      f"replacement. Choose one of the locations above by "
                      f"hand; --fix will not guess.{RESET}")

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
              + (f", {len(anchor_bad)} section(s) not there" if anchor_bad
                 else "")
              + f" — exit 1{RESET}")
        return 1

    if stale or anchor_bad:
        print()
        parts = []
        if stale:
            fixable = sum(1 for s in stale if s[6] and s[7] not in conflicted)
            contest = sum(1 for s in stale if s[7] in conflicted)
            parts.append(f"{len(stale)} quotation(s) not at the lines named "
                         f"({fixable} relocatable with --fix"
                         + (f", {contest} CONTESTED and refused" if contest
                            else "") + ")")
        if anchor_bad:
            parts.append(f"{len(anchor_bad)} section anchor(s) naming a "
                         f"heading that is not there")
        print(f"{RED}CITATION LINT: " + ", ".join(parts) + f" — exit 1{RESET}")
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
    #
    # v2 ADDS A SECOND REASON TO SAY PARTIAL: a bare line locator. It is not a
    # finding and does not change the exit code, but a run that leaves a dozen
    # line numbers undecided must not print the same word as a run that leaves
    # none. The count rides the summary line so it is visible at the same
    # glance as the verdict.
    state = "CLEAN" if not skipped and not bare else "PARTIAL"
    seen = checked + len(skipped)
    pct = (100.0 * checked / seen) if seen else 100.0
    tail = (f", {len(bare)} bare locator(s) unguarded" if bare
            else ", 0 bare locator(s) unguarded")
    print(f"{GREEN if state == 'CLEAN' else YELLOW}CITATION LINT: {state} - "
          f"{checked} of {seen} attribution(s) seen were checked ({pct:.1f}%), "
          f"{anchors} section anchor(s) resolved, 0 unfound{tail} - exit 0"
          f"{RESET}")
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

    def _forward_splice(text, spans):
        """`splice()`'s MUTANT: the same edits applied front to back.

        It lives here rather than in the running layer because its only job is
        to prove the ordering control can tell the two apart. A control whose
        assertion is satisfied by both the right implementation and the wrong
        one is the case the review's MINOR-3 found."""
        for start, end, new in sorted(spans):
            text = text[:start] + new + text[end:]
        return text

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
    print(f"{BOLD}=== G. THE RELOCATION PASS: a stale locator that can be "
          f"repaired, and one that cannot ==={RESET}")

    # THE FORCED RED, AND THE REPAIR. Right words, wrong lines, and the words
    # occur exactly once - so the correct locator is a FACT about the file, not
    # a guess, and the tool may both report it and write it.
    moved = ("a new opening paragraph\n"
             "that pushed everything down\n"
             "alpha\n"
             "the words that moved down the page\n"
             "omega\n")
    q_moved = "the words that moved down the page"
    check("CITE(stale-relocatable): the locator is stale - the words are NOT "
          "at the lines it names",
          quote_in_window(q_moved, moved, 2, 2), False)
    check("CITE(stale-relocatable): ...and the words ARE in the document, so "
          "this is a locator defect and not a fabrication",
          quote_is_in(q_moved, moved), True)
    check("CITE(stale-relocatable): ...and the one place they occur is where "
          "the locator should point", relocation(q_moved, moved, 2, 2), (4, 4))
    check("CITE(stale-relocatable): ...so the exact replacement is computable",
          retarget(":2", *relocation(q_moved, moved, 2, 2)), ":4")
    # THE CONTROL THAT KEEPS THE REPAIR FROM MANUFACTURING ONE. A locator that
    # is already CORRECT must yield no relocation, or --fix would rewrite
    # right citations on every run.
    check("CITE(stale-relocatable): ...while a locator that is already right "
          "yields NO relocation, so --fix never touches a correct citation",
          relocation(q_moved, moved, 4, 4), None)
    check("CITE(stale-relocatable): ...and a quotation that is nowhere in the "
          "document yields none either - that is the stronger finding",
          relocation("words this file has never held", moved, 2, 2), None)

    # THE AMBIGUOUS HALF. Two occurrences, neither in the window. The tool must
    # stay RED and must NOT choose: writing one of two candidate locators would
    # put a wrong number under a green.
    check("CITE(stale-ambiguous): a quotation occurring TWICE, with the "
          "locator on neither, is still a finding",
          quote_in_window("the repeated words", twice, 3, 4), False)
    check("CITE(stale-ambiguous): ...but there is no single correct "
          "replacement, so the tool refuses to repair it",
          relocation("the repeated words", twice, 3, 4), None)
    check("CITE(stale-ambiguous): ...and both candidates are still reported, "
          "so a human can choose",
          quote_line_spans("the repeated words", twice), [(2, 2), (5, 5)])

    # THE REWRITE ITSELF. Pure, and narrow on purpose: only the digits move.
    check("CITE(fix-rewrite): a single-line locator is rewritten to a single "
          "line", retarget(":208", 311, 311), ":311")
    check("CITE(fix-rewrite): ...a range to a range", retarget(":40-41", 7, 9),
          ":7-9")
    check("CITE(fix-rewrite): ...an en-dash range keeps its en-dash, because "
          "a repair may not restyle the prose it edits",
          retarget(":40–41", 7, 9), ":7–9")
    check("CITE(fix-rewrite): ...a SECTION locator is returned untouched, so "
          "nothing here can rewrite a section name into a line number",
          retarget(" Step 4", 7, 9), " Step 4")
    check("CITE(fix-rewrite): ...and a locator carrying both keeps the "
          "section half", retarget(" Step 4:12", 7, 9), " Step 4:7-9")
    # THE OFFSETS THE REWRITE USES. A splice at the wrong offsets would edit
    # the quotation, which is the one thing this tool must never do.
    doc_fix = 'Prose here. `README.md`:14 says "the words in question here".'
    rows = attributions_located(doc_fix)
    _r, _q, _s, loc, a, b = rows[0]
    check("CITE(fix-rewrite): the extractor reports the locator's exact span "
          "in the citing document", (loc, doc_fix[a:b]), (":14", ":14"))
    check("CITE(fix-rewrite): ...so a splice at those offsets changes the "
          "locator and NOTHING else",
          doc_fix[:a] + retarget(loc, 22, 22) + doc_fix[b:],
          'Prose here. `README.md`:22 says "the words in question here".')

    # THE REVIEW'S MINOR-3. Every control above applies ONE edit, and one edit
    # is correct in either order - so nothing asserted the ordering, and a
    # forward-order mutant passed all 87 checks while destroying a citation
    # line. Two edits in one document, asserted as WHOLE-FILE content.
    two_src = ('First `A.md`:100-200 says "the first quotation here".\n'
               'Then `B.md`:7 says "the second quotation here".\n')
    a1 = two_src.index(":100-200")
    a2 = two_src.index(":7")
    check("CITE(fix-order): two edits in one document are applied from the "
          "LAST offset backwards, so the earlier one does not shift the later "
          "one - asserted as whole-file content, because a single edit is "
          "correct in either order and proves nothing",
          splice(two_src, [(a1, a1 + len(":100-200"), ":4"),
                           (a2, a2 + len(":7"), ":88-99")]),
          'First `A.md`:4 says "the first quotation here".\n'
          'Then `B.md`:88-99 says "the second quotation here".\n')
    check("CITE(fix-order): ...and the forward-order mutant this control "
          "exists to catch really does corrupt the file",
          _forward_splice(two_src, [(a1, a1 + len(":100-200"), ":4"),
                                    (a2, a2 + len(":7"), ":88-99")])
          == splice(two_src, [(a1, a1 + len(":100-200"), ":4"),
                              (a2, a2 + len(":7"), ":88-99")]),
          False)

    print()
    print(f"{BOLD}=== G2. CONTESTED LOCATORS: one locator, two claimants "
          f"(the review's MAJOR-2) ==={RESET}")

    # THE OSCILLATION, ENCODED. `"first" (`SRC.md`:18) says "second"` gives
    # shape A and shape B the same locator. Repairing for either breaks the
    # other, and the reviewer measured :18 -> :5 -> :18 across five --fix runs
    # with the exit code stuck at 1.
    two_claim = ('"quote one really lives on line five" (`SOURCE.md`:18) '
                 'says "quote two really lives on line eighteen".')
    rows2 = attributions_located(two_claim)
    check("CITE(contested): one reference really is claimed by TWO "
          "attributions, and both land on the same locator span",
          (len(rows2), len({(r[4], r[5]) for r in rows2}),
           sorted(r[2] for r in rows2)),
          (2, 1, ["A", "B"]))
    check("CITE(contested): a satisfied claimant beside a relocatable one is "
          "CONTESTED - any rewrite breaks the satisfied one",
          contested(["", ":5"]), True)
    check("CITE(contested): ...and so is a claimant that cannot be repaired "
          "at all", contested([":5", None]), True)
    check("CITE(contested): ...and two claimants wanting DIFFERENT lines",
          contested([":5", ":18"]), True)
    # THE CONTROLS THAT KEEP THE REFUSAL FROM SWALLOWING REAL REPAIRS.
    check("CITE(contested): ...but a single claimant is never contested, "
          "which is every ordinary citation in the kit",
          (contested([":5"]), contested([""]), contested([None])),
          (False, False, False))
    check("CITE(contested): ...and two claimants that AGREE are repaired, not "
          "refused", contested([":18", ":18"]), False)
    check("CITE(contested): ...and two claimants that are both already "
          "satisfied have nothing to write, so nothing to refuse",
          contested(["", ""]), False)

    print()
    print(f"{BOLD}=== H. THE BARE-LOCATOR DISCLOSURE: the invisible class, "
          f"counted ==={RESET}")

    # THE CLASS ITSELF. A line number with no quotation beside it. Before v2
    # this was not checked, not skipped and not counted - it did not appear in
    # any number the tool printed.
    check("CITE(bare-locator): a line reference with no quotation beside it "
          "is detected",
          bare_locators("The rule at `LEVEL-1.md`:320 stands unchanged."),
          [("LEVEL-1.md", ":320", 1)])
    check("CITE(bare-locator): ...and a RANGE is detected the same way",
          [r for _f, r, _l in bare_locators("See `QUICKSTART.md`:77-89 for it.")],
          [":77-89"])
    check("CITE(bare-locator): ...and the line it sits on is reported, "
          "because a count with no location is not actionable",
          [l for _f, _r, l in bare_locators(
              "line one\nline two\nThe rule at `LEVEL-1.md`:320 stands.")],
          [3])
    # THE CONTROL THAT KEEPS THE COUNT HONEST. A locator that a quotation
    # already guards is NOT bare - counting it would inflate the disclosure
    # with references the window check decides on every run.
    guarded_doc = '`README.md`:14 says "the words in question here".'
    check("CITE(bare-locator): ...but a locator a QUOTATION already guards is "
          "not bare, so the disclosure does not double-count the window check",
          bare_locators(guarded_doc,
                        [(a2, b2) for *_x, a2, b2
                         in attributions_located(guarded_doc)]),
          [])
    check("CITE(bare-locator): ...and with the guard list empty the same "
          "reference IS reported, so the exclusion is doing the work",
          [f for f, _r, _l in bare_locators(guarded_doc)], ["README.md"])
    check("CITE(bare-locator): a SECTION anchor is not a line locator and is "
          "never counted as one",
          bare_locators("Read `BLUEPRINT.md` §12 before you argue."), [])
    # THE REVIEW'S MINOR-6. `_LOC` has always known the word form, so an
    # ATTRIBUTION could carry it while the DISCLOSURE could not see it - the
    # same reference countable in one spelling and invisible in the other.
    check("CITE(bare-locator): the WORD form is a line locator too, in both "
          "its spellings",
          [(f, r) for f, r, _l in bare_locators(
              "See `LEVEL-1.md` line 320 and `QUICKSTART.md` lines 77-89.")],
          [("LEVEL-1.md", "line 320"), ("QUICKSTART.md", "lines 77-89")])
    # THE REVIEW'S MINOR-7. A locator inside a fence is an example of the form.
    check("CITE(bare-locator): ...but a locator inside a FENCE is an example "
          "of the form, not a citation, and inflates a number whose job is to "
          "say how much migration is left",
          bare_locators("Write it like this:\n\n```markdown\n"
                        "The rule at `LEVEL-1.md`:320 stands.\n```\n"), [])
    check("CITE(bare-locator): ...while the same line OUTSIDE the fence is "
          "still counted, so the exclusion is scoped and not a blanket",
          [f for f, _r, _l in bare_locators(
              "```markdown\nfenced `A.md`:1\n```\nreal `B.md`:2\n")],
          ["B.md"])

    print()
    print(f"{BOLD}=== I. SECTION ANCHORS: the citation form that survives an "
          f"edit above it ==={RESET}")

    sec_src = ("# A document\n"
               "\n"
               "## 1. The first section\n"
               "prose\n"
               "## 4.7 Run, commit, run again\n"
               "prose\n"
               "### Also measured, at Level 1 (5 min)\n"
               "prose that merely MENTIONS Run, commit, run again in a line\n")
    check("CITE(section-anchor): the headings of a document are recovered",
          headings(sec_src),
          ["A document", "1. The first section", "4.7 Run, commit, run again",
           "Also measured, at Level 1 (5 min)"])
    check("CITE(section-anchor): §1 resolves to the heading numbered 1",
          section_hit("1", sec_src), True)
    check("CITE(section-anchor): ...and a DOTTED section number resolves too",
          section_hit("4.7", sec_src), True)
    # THE FORCED RED. A section number the target does not carry.
    check("CITE(section-anchor): ...but §9 is a finding, because no heading "
          "answers to it", section_hit("9", sec_src), False)
    # THE CONTROL AGAINST A LOOSE PREFIX MATCH. §4 and §4.7 are different
    # sections, and a rule that matched on the leading digit would silently
    # accept the wrong one.
    check("CITE(section-anchor): ...and §4 does NOT resolve to a heading "
          "numbered 4.7 - they are different sections",
          section_hit("4", sec_src), False)
    check("CITE(section-anchor): the reference form is extracted with its "
          "number", section_refs("Read `BLUEPRINT.md` §12 first."),
          [("BLUEPRINT.md", "12")])
    # FOUND BY THE FIRST LIVE RUN OF THIS LAYER, NOT BY DESIGN. `§4.7.` at the
    # end of a sentence was read as section "4.7." and reported as missing - a
    # new check manufacturing a finding against a correct citation on its
    # first run, which is the failure mode section B exists to prevent.
    check("CITE(section-anchor): ...and a sentence-final full stop is NOT part "
          "of the section number",
          section_refs("See `QUICKSTART.md` §4.7."), [("QUICKSTART.md", "4.7")])
    check("CITE(section-anchor): ...and a document does not cite its own "
          "sections", section_refs("`ONBOARD.md` §4 says so.",
                                   self_name="ONBOARD.md"), [])

    check("CITE(heading-anchor): a quoted string adjacent to a reference names "
          "a HEADING, and containment allows the heading's own numbering and "
          "trailing clause to be dropped",
          heading_hit("Also measured, at Level 1", sec_src), True)
    # THE FORCED RED, AND THE POINT OF THE FORM. The words ARE in the document
    # - the last line of sec_src holds them - so the presence check alone
    # passes. Only the heading rule refuses.
    check("CITE(heading-anchor): ...while a string that is in the document's "
          "PROSE but in no heading is a finding - that is the whole gap this "
          "form closes",
          (quote_is_in("Run, commit, run again in a line", sec_src),
           heading_hit("Run, commit, run again in a line", sec_src)),
          (True, False))
    check("CITE(heading-anchor): the adjacent form is extracted",
          heading_refs('Cited in `LEVEL-1.md`, "scan before you publish", '
                       'as the rule.'),
          [("LEVEL-1.md", "scan before you publish")])
    check("CITE(heading-anchor): ...and a locator between the two does not "
          "break the adjacency",
          [t for _f, t in heading_refs(
              '`QUICKSTART.md` Step 4, "ONE MACHINE PER SETTINGS FILE" says '
              'so.')],
          ["ONE MACHINE PER SETTINGS FILE"])
    # THE CONTROL THAT KEEPS THIS FORM FROM STEALING ORDINARY QUOTATIONS. One
    # word of glue and it is an attribution again, checked for presence.
    check("CITE(heading-anchor): ...but any WORD between the reference and the "
          "quotation makes it an ordinary attribution, not a section name",
          heading_refs('`LEVEL-1.md` says "scan before you publish" here.'),
          [])
    check("CITE(heading-anchor): ...and a LINE locator does too, because the "
          "author named lines and the window check owns those",
          heading_refs('`LEVEL-1.md`:227, "scan before you publish".'), [])
    check("CITE(heading-anchor): ...and a document does not cite its own "
          "headings",
          heading_refs('`ONBOARD.md`, "The operator capability grant".',
                       self_name="ONBOARD.md"), [])

    # THE LIVE HALF. A rule that matches nothing proves nothing, so both forms
    # are asserted against the shipped kit as well as against literals.
    live_anchors = 0
    for d in docs:
        if d.name in REGISTER_DOCS:
            continue
        t = d.read_text(encoding="utf-8")
        live_anchors += (len(section_refs(t, d.name))
                         + len(heading_refs(t, d.name)))
    check("CITE(section-anchor): the shipped kit really uses this form, so "
          "neither scanner is a pattern that matches nothing",
          live_anchors > 20, True)

    print()
    print(f"{BOLD}=== J. FENCED CODE: not a heading, not a citation (the "
          f"review's MAJOR-1) ==={RESET}")

    # THE TARGET SIDE. A shell comment in a ```bash block is not a heading, and
    # reading it as one resolves an anchor against something no reader sees.
    fenced_src = ("# Real title\n"
                  "\n"
                  "## 1. A real section\n"
                  "\n"
                  "```bash\n"
                  "# 9. copy the runner and the enforcement files\n"
                  "cp tools/verify.py .\n"
                  "```\n"
                  "\n"
                  "## 2. Another real section\n")
    check("CITE(fenced-heading): the fenced lines of a document are found",
          sorted(fenced_lines(fenced_src)), [4, 5, 6, 7])
    check("CITE(fenced-heading): a shell comment inside a fence is NOT a "
          "heading",
          headings(fenced_src),
          ["Real title", "1. A real section", "2. Another real section"])
    # THE FORCED FALSE-GREEN, which is what the phantom bought before the fix.
    check("CITE(fenced-heading): ...so §9 does NOT resolve - the phantom "
          "heading was a false GREEN on a citation that is wrong",
          section_hit("9", fenced_src), False)
    check("CITE(fenced-heading): ...while the real sections still resolve, so "
          "the exclusion did not cost recall",
          (section_hit("1", fenced_src), section_hit("2", fenced_src)),
          (True, True))
    check("CITE(fenced-heading): ...and a heading anchor is refused the same "
          "way", heading_hit("copy the runner", fenced_src), False)
    check("CITE(fenced-heading): both fence markers are recognised, and a "
          "block closes only on its own",
          sorted(fenced_lines("a\n~~~\n# 1. not a heading\n~~~\nb\n")),
          [1, 2, 3])
    check("CITE(fenced-heading): ...and an UNCLOSED fence swallows the rest "
          "of the document, which is what a renderer does with one",
          sorted(fenced_lines("a\n```\n# 1. x\nmore\n")), [1, 2, 3])

    # THE CITING SIDE, and the half that matters more: a false RED. A §N inside
    # a fence is an EXAMPLE of the citation form.
    fenced_citer = ("Write a citation like this:\n"
                    "\n"
                    "```markdown\n"
                    "Read `SOURCE.md` §9 for the rule.\n"
                    "See `SOURCE.md`, \"a heading that does not exist\".\n"
                    "```\n")
    check("CITE(fenced-heading): a §N inside a fence is an EXAMPLE, not a "
          "citation, and reporting it manufactures a finding",
          section_refs(fenced_citer), [])
    check("CITE(fenced-heading): ...and so is a heading anchor inside one",
          heading_refs(fenced_citer), [])
    check("CITE(fenced-heading): ...while the same two lines OUTSIDE a fence "
          "ARE citations, so the exclusion is scoped and not a blanket",
          (section_refs("Read `SOURCE.md` §9 for the rule."),
           heading_refs('See `SOURCE.md`, "a heading that does not exist".')),
          ([("SOURCE.md", "9")],
           [("SOURCE.md", "a heading that does not exist")]))

    # THE LIVE HALF. The measurement that convicted the first build.
    phantom = 0
    for d in docs:
        t = d.read_text(encoding="utf-8")
        skip = fenced_lines(t)
        phantom += sum(1 for m in HEADING.finditer(t)
                       if line_index(t, m.start()) in skip)
    check("CITE(fenced-heading): the shipped kit really contains fenced lines "
          "that LOOK like headings, so this rule is not hypothetical",
          phantom > 20, True)
    check("CITE(fenced-heading): ...and none of them survives into headings()",
          [d.name for d in docs
           if set(headings(d.read_text(encoding="utf-8")))
           - {flatten(m.group(1)) for m in
              HEADING.finditer(d.read_text(encoding="utf-8"))}],
          [])

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
    ap.add_argument("--fix", action="store_true",
                    help="rewrite stale line locators that relocate to exactly "
                         "one place; never touches quoted text")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    root = Path(a.root).resolve() if a.root else Path(__file__).resolve().parent.parent
    if not root.is_dir():
        print(f"{RED}CITATION LINT: ABORT — no such directory: {root}{RESET}")
        return 2
    return run(root, a.list, fix=a.fix)


if __name__ == "__main__":
    sys.exit(main())
