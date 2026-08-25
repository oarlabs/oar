#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
tools/count_lint.py - the count lint. Is the stated number the number, and is
the universal claim true of every element?

    python tools/count_lint.py                 # lint the kit's own documents
    python tools/count_lint.py --root <path>   # lint another tree
    python tools/count_lint.py --selftest      # incl. the negative controls
    python tools/count_lint.py --list          # print every claim seen, and
                                               # every phrase skipped

    exit 0  no located claim disagrees with what it names. The summary line
            says CLEAN or PARTIAL and prints the denominator - see THE STATE
            WORD below; a run that locates a target for 2% of its subject
            does not get to print the same word as a run that located all of
            them
    exit 1  at least one located claim disagrees with what it names
    exit 2  abort (no root, nothing to read)

==========================================================================
WHY THIS EXISTS
==========================================================================
Round 23 corrected `QUICKSTART.md` Step 0 from nine lines to ten, because a
tenth line (`git --version`) had landed. `ONBOARD.md`:41 still said nine, and
it says it about `QUICKSTART.md` Step 0 by name. Round 24's acceptance run
found it (F1): an agent obeying `ONBOARD.md` literally counts to nine and
stops before the live fixture run - the only line in Step 0 that exercises a
settings file rather than a selftest.

That is the SAME class the citation lint names in its own docstring and
declines to cover:

    "a claim in a document should be verifiable against the source it names
     - quoted strings, cited steps, stated counts."

The citation lint took the first. This tool takes the third, and it is
deliberately the NARROW version of it, for the same reason: a count is only
checkable when the thing being counted can be located and enumerated.

WHY A SEPARATE TOOL, and not an extension of one of the two lints beside it:

  - NOT the citation lint. That tool answers one question by string
    containment (is the needle in the haystack); this one answers a different
    question by parsing a target and counting it (a table's rows, a list's
    items, a fenced block's lines). Fusing them would put two matching
    problems behind one verdict line and one exit code, and the kit's
    convention is one decidable question per tool, each with its own selftest,
    its own forced red and its own summary line. They are siblings and each
    docstring names the other.
  - NOT the expectation lint. That tool judges the REGISTRY - it asks where a
    check's expectation comes from - and it never reads a document. This tool
    reads documents. What it does take from the expectation lint is
    registration: its negative controls are a `count:` family, cross-checked
    both ways, so a control quietly deleted here is reported there.

==========================================================================
WHAT IT CAN SEE, AND WHAT IT CANNOT
==========================================================================
A claim is a COUNT PHRASE (a number word or digits, then up to two words,
then a plural noun) that this tool can attach to an ENUMERABLE TARGET. Three
ways a phrase names a target, and nothing else counts as naming one:

  L1  INTRODUCER. The phrase OPENS a paragraph that ENDS in a colon, and the
      next block in the same document is a markdown table, a bullet or
      numbered list, or a fenced code block.
          "Seven checks run, and each red line names the step that fixes it:"
          followed by a seven-row table.
      Target: the table's body rows, the list's TOP-LEVEL items, or the
      fenced block's countable lines.
      THE OPENING RULE IS NOT DECORATION. Without it - the first build did
      without it - the tool reported 23 findings against this kit and 22 were
      its own, 21 of them this one class: any number sitting anywhere inside
      a paragraph that happened to end in a colon was read as a count of what
      followed ("one pass", "4 is what lets", "eight defaults"). The
      twenty-second own finding was the wrapped-command defect below. A count
      is a claim about the block below it only when it is what the sentence is
      about. The cost of the rule is stated too: "Run these ten commands:" is
      no longer seen.

  L2  TRAILING. The phrase's noun is a line noun (`lines`, `commands`) and the
      paragraph is the first thing after a fenced code block, with no heading
      between them.
          "**Checkpoint:** all ten lines exit 0"
      Target: that block's countable lines.

  L3  CROSS-DOCUMENT SECTION. The phrase names another kit document in
      backticks with a section locator, in the same sentence and the same
      table cell, and its noun is a line noun.
          "Run `QUICKSTART.md` **Step 0** in the kit clone: ten lines, all
           exit 0"
      Target: the single fenced block in that document's `Step 0` section.
      THIS IS F1's SHAPE, and it is the reason the tool is worth building:
      a count that travels between documents is the one nobody re-derives.

COUNTABLE LINES, defined: non-blank lines inside the fence, excluding
whole-line comments (`#`, `//`, `rem`), with a command that WRAPS counted
once - a line ending in `\`, `|` or a backtick is continued on the next one.
A shell block's trailing `# comment` is part of its line and is counted; a
line that is nothing but a comment is not a command and is not counted.
Stated because it is a judgment call, and an undisclosed one would make every
fenced-block count arguable. The wrap rule was forced by the first live run,
which reported `QUICKSTART.md` Step 4's correct "three lines" as a defect
because the third command is a pipeline written across two lines.

OUT OF SCOPE - stated plainly, because a check whose limits are not published
gets read as covering more than it does:

  - **Prose counts with no locatable target.** "Six findings against the
    documents", "eight rules", "three states" written as running prose. The
    tool SKIPS them and prints how many it skipped; it never guesses. This is
    the larger half of the class by volume.
  - **Semantic counts.** "two version checks, five selftests" describes what
    the ten lines ARE, not how many lines there are. No parser decides which
    line is a selftest, so this tool does not try.
  - **Counts of things outside the documents** - files in a directory, checks
    in a tool's output, rows in a database. A count phrase pointed at a
    directory is not enumerable from the markdown, and pretending otherwise
    would make the tool's answer depend on the tree it was run in.
  - **Ambiguous targets.** A named section with no fenced block, or with more
    than one, is skipped rather than guessed at. So is a section locator that
    matches no heading or several.
  - **Counts inside a findings register.** `KNOWN-ISSUES.md` records what a
    count USED TO BE beside the correction ("corrected from nine lines to
    ten"), so checking those against the fixed tree asks the wrong question.
    Exempt as a document class, the same way and for the same reason the
    citation lint exempts it, with the count printed on every run.
    RESIDUAL, STATED: a genuinely wrong count written INTO the register is
    exempt too.

  - **Numbers outside the checking vocabulary.** This tool CHECKS the words
    one..twenty and digit runs of up to three digits, and nothing else -
    "thirty rows", "twenty-five checks" and "1024 lines" are not decided.
    Narrow on purpose: every number the tool reads is a number it may go red
    on, and v1 buys its low false-positive rate by reading few of them. THE
    CEILING IS DISCLOSED RATHER THAN CLOSED - a wider vocabulary (the tens
    words, their hyphenated forms, and digit runs of four or more) is
    recognised for the SOLE purpose of counting those phrases as SKIPPED, so
    they reach the skip total with a reason of their own instead of being
    invisible. Found by round 24's review (m2), which planted five false
    counts using the word *ninety* and watched all five vanish: neither
    checked, nor skipped, nor counted anywhere. Residual of the disclosure
    itself, stated: "a hundred lines", "one thousand rows" and spelled
    compounds beyond the tens are outside even the wider vocabulary, so they
    remain invisible.

  - **Bare line citations.** `` `LEVEL-1.md`:320 `` names a line, not an
    enumerable section: `SECTION_REF` recognises `Step N` and `§N` and
    excludes the bare line form by design, so a citation whose line number has
    drifted is invisible here. It is invisible to `tools/citation_lint.py`
    too, which requires a quoted string - so BOTH lints are blind to the same
    shape, and neither one's silence about a `DOC.md`:N reference is evidence
    the number is right. Round 24 shipped two stale ones and its review (m1)
    found them by hand. Named as a shared gap rather than covered; the check
    that would cover it is an ORACLE-DECLINED row of round 24.

Two more residuals, named rather than discovered later:

  - The tool checks the ARITHMETIC of a count, not its SUBJECT. "Seven
    documents:" over a seven-row table of gate commands passes.
  - A target this tool cannot locate is invisible, and an invisible claim is
    indistinguishable from a claim that is right. The skip count on every run
    is the disclosure - and, since round 24's review, so is the vocabulary
    ceiling above.

==========================================================================
THE QUANTIFIER LAYER (round 30)
==========================================================================
A number is not the only claim a document makes about an enumerable thing.
"Every row carries a source in brackets" is the same claim shape as "eighteen
rows" - it names a target this tool can already enumerate and asserts
something about it - and it is the shape the program paid for four times in
rounds 26-29. Round 29's review found two MAJORs with one root cause: a
universal quantifier asserted over a target the writer could have enumerated
and did not. This layer is that check, built to the review's own spec:

    a sentence containing a universal quantifier plus a noun naming a target
    this tool can enumerate, where the predicate is the presence of a LITERAL
    token, is asserted against every element of that target.

WHAT COUNTS AS A CHECKABLE QUANTIFIER CLAIM. All four conditions, or the
phrase is skipped and disclosed:

  1. A QUANTIFIER WORD in the determiner form: `every`, `each`, `all`, `no`,
     `none of the`. `no` and `none` invert the test - NO element may carry the
     literal. The adverb absolutes (`never`, `always`) and the pronoun forms
     (`nothing`, `nobody`, `everything`, `everywhere`) take no noun and name
     no target, so they are recognised for the SOLE purpose of counting them
     as SKIPPED - the same disclosure-only device the vocabulary ceiling above
     uses, and for the same reason: a phrase this tool cannot decide should be
     visible as a skip rather than invisible.
  2. A TARGET NOUN whose kind this tool enumerates: `row`/`rows` (a markdown
     table), `item`/`items`/`bullet`/`bullets` (a list), `line`/`lines`/
     `command`/`commands` (a fenced block).
  3. A PRESENCE VERB in the same sentence, after the quantifier - `names`,
     `carries`, `contains`, `has`, `lists`, `cites`, `ends`, `starts`,
     `prints`, `states`, `holds`, `links`, and their kin. Without one the
     sentence is not a claim about token presence at all. It is excluded on
     relevance grounds and RECORDED AS A SKIP, and the exclusion is
     disclosed here because it raises the printed coverage percentage: a
     smaller denominator flatters the figure, so the excluded sentences are
     kept visible in the skip list rather than silently dropped.
  4. A LITERAL PREDICATE, one of exactly three forms:
       - a backticked literal in the same sentence, e.g. `` `[FETCHED]` ``
         (a backticked name ending in `.md` is a document reference, not a
         predicate, and does not count);
       - a double-quoted literal, e.g. "exit 0";
       - the bracket FORM - the words "in brackets" or "bracketed" - which
         asserts that each element carries some `[...]` tag. This is the one
         non-string predicate, and it is here because it is the exact shape
         of the defect that motivated the layer.

HOW THE TARGET IS LOCATED. Two shapes, both already in this tool:

  Q1  INTRODUCER, the L1 rule reused. The phrase OPENS a paragraph that ENDS
      in a colon and the next block is the table, list or fenced block.
  Q2  THE DOCUMENT'S SOLE CONSTRUCT. The noun names a kind of which the
      document holds EXACTLY ONE - one table, one list, one fenced block.
      More than one, or none, is ambiguity and is skipped rather than
      guessed at, the same rule `section_fence_count` already applies. This
      shape exists because a universal claim is usually written several
      paragraphs away from the thing it quantifies over, which the adjacency
      rule alone cannot reach.

PRECISION OVER RECALL, AND WHAT THAT COSTS. Stated plainly, because the
alternative is a reader assuming this layer covers the class:

  - A universal claim whose target is not enumerable from the markdown is
    SKIPPED and printed in the denominator. Round 29's F2 - "the prompt
    behind every finding count here" - is this case: `finding count` names no
    table, list or block, so the sentence is skipped with its reason. Before
    this layer it was invisible to every check in the kit; it is now a
    disclosed skip, which is partial cover and is not full cover. Restated
    over an enumerable target - a per-entry table with the prompt in each row
    - the same claim IS caught, and the selftest holds both halves so neither
    can be quietly moved.
  - A predicate requiring judgment ("every row is accurate") is not a literal
    and is skipped.
  - The layer checks PRESENCE of a token, not its correctness. "Every row
    carries a `[FETCHED]` tag" passes over eighteen rows tagged `[FETCHED]`
    whether or not anything was fetched.

==========================================================================
THE STATE WORD, AND WHY `clean` RETIRED (round 30)
==========================================================================
This tool used to print `COUNT LINT: clean - exit 0` over a run that located
a target for 15 of 769 count phrases. An outside reader ran it, did the
arithmetic, and filed the obvious finding: *clean* is the wrong word for a
run that could not locate a target for 98% of its subject, and this kit's own
state-word doctrine - PARTIAL exists because "the check did not run" and "the
check passed" must never render alike - was not being applied to this kit's
own lint.

So the summary line now carries a denominator and a state word:

    COUNT LINT: PARTIAL - 18 of 982 claim(s) located and checked (1.8%),
    0 disagree - exit 0

  CLEAN    every claim phrase this tool saw was located and decided.
  PARTIAL  at least one was skipped. The percentage is printed, and the
           skipped phrases are printed by `--list`.

THE EXIT CODE DOES NOT MOVE, and that is a decision rather than an oversight.
Over the claims it located, the tool's verdict is complete: nothing
disagrees. The coverage figure is a disclosure about the SUBJECT, not a
failure of the RUN, and making a partial run exit non-zero would give this
kit a permanently red lint whose red means "this document contains English",
which is a red people learn to skip. The residual is stated rather than
closed: a reader who reads only the exit code still learns nothing about
coverage, which is why the number is on the summary line where the exit code
is read.
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

NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20,
}
# Nouns naming the lines of a fenced block. L2 and L3 are restricted to these
# because a fenced block is the one target whose "items" are not marked up -
# any plural noun would let the tool count lines to answer a question about
# something else entirely.
LINE_NOUNS = frozenset({"lines", "commands"})

# Words that end in `s` and are not the noun of a count phrase. A short list on
# purpose: the load-bearing filter is whether a TARGET can be located, not
# whether the noun looks like a noun.
NOT_NOUNS = frozenset({
    "is", "was", "has", "its", "this", "as", "does", "goes", "says", "gets",
    "runs", "reads", "means", "carries", "holds", "names", "makes", "takes",
    "gives", "gives", "gaps", "gives", "hits", "his", "hers", "yours", "ours",
    "less", "unless", "plus", "versus", "thus", "always", "perhaps",
})

_NAME = r'[A-Za-z0-9][A-Za-z0-9._/<>-]*\.md'
MD_REF = re.compile(r'`(' + _NAME + r')`')

# A count phrase: the number, up to two intervening words (adjectives, and the
# markdown emphasis that often wraps them), then a plural noun.
COUNT = re.compile(
    r'(?<![\w.-])(?P<num>' + "|".join(NUMBERS) + r'|\d{1,3})(?![\w.-])'
    r'(?P<mid>(?:[ \t]+[*_`]{0,2}[A-Za-z][A-Za-z\'`*_-]*){0,2}?)'
    r'[ \t]+[*_`]{0,2}(?P<noun>[A-Za-z][A-Za-z-]{2,}s)\b',
    re.I)

# THE VOCABULARY CEILING, MADE VISIBLE (round 24 review, m2). `NUMBERS` stops
# at twenty and `COUNT`'s digit form is three digits, so "thirty lines" and
# "1024 lines" were matched by nothing: not checked, not skipped, absent from
# the skip total that the docstring calls "the disclosure". This second
# pattern exists ONLY to count them as skipped. It decides nothing and can
# never produce a finding - widening what the tool CHECKS would widen what it
# can be wrong about, and v1 keeps that surface small on purpose.
WIDE_NUM = (r'(?:thirty|forty|fifty|sixty|seventy|eighty|ninety)'
            r'(?:-(?:one|two|three|four|five|six|seven|eight|nine))?'
            r'|(?:twenty)-(?:one|two|three|four|five|six|seven|eight|nine)'
            r'|\d{4,}')
WIDE_COUNT = re.compile(
    r'(?<![\w.-])(?P<num>' + WIDE_NUM + r')(?![\w.-])'
    r'(?P<mid>(?:[ \t]+[*_`]{0,2}[A-Za-z][A-Za-z\'`*_-]*){0,2}?)'
    r'[ \t]+[*_`]{0,2}(?P<noun>[A-Za-z][A-Za-z-]{2,}s)\b',
    re.I)
WIDE_REASON = ("a number outside this tool's checking vocabulary - it reads "
               "one..twenty and up to three digits (see OUT OF SCOPE)")

# A section locator following a backticked document name: `` `DOC.md` Step 0 ``
# or `` `DOC.md` §2 ``. Deliberately the same vocabulary the citation lint
# recognises, minus the bare `:40-41` line form - a line range names no
# enumerable section.
SECTION_REF = re.compile(
    r'`(?P<f>' + _NAME + r')`'
    r'(?P<glue>[^|`]{0,40}?)'
    r'(?:\*{0,2}|_{0,2})'
    r'(?:(?P<kind>Step|step|Section|section|§)\s*(?P<n>[0-9]+[A-Za-z]?))')

# ==========================================================================
# THE QUANTIFIER VOCABULARY (round 30). See THE QUANTIFIER LAYER above.
# ==========================================================================
# The determiner forms, which take a noun and therefore can name a target.
QUANT_WORDS = ("every", "each", "all", "none of the", "no")
QUANT_NEGATIVE = frozenset({"no", "none of the"})

# Nouns whose target kind this tool enumerates. A noun outside these three
# sets names nothing this tool can count, which is most of them.
TABLE_NOUNS = frozenset({"row", "rows"})
BULLET_NOUNS = frozenset({"item", "items", "bullet", "bullets"})
QLINE_NOUNS = frozenset({"line", "lines", "command", "commands"})
QUANT_NOUNS = TABLE_NOUNS | BULLET_NOUNS | QLINE_NOUNS

QUANT = re.compile(
    r'(?<![\w.-])(?P<q>' + "|".join(QUANT_WORDS) + r')(?![\w.-])'
    r'(?P<mid>(?:[ \t]+[*_`]{0,2}[A-Za-z][A-Za-z\'`*_-]*){0,2}?)'
    r'[ \t]+[*_`]{0,2}(?P<noun>[A-Za-z][A-Za-z-]{1,}s?)\b',
    re.I)

# DISCLOSURE ONLY, and it decides nothing - the sibling of WIDE_COUNT above.
# These forms take no noun, so no target can be located from them; they are
# matched so that an absolute this tool cannot decide reaches the skip total
# with a reason of its own instead of being invisible.
QUANT_ABSOLUTE = re.compile(
    r'(?<![\w.-])(?P<q>never|always|nothing|nobody|everything|everywhere)'
    r'(?![\w.-])', re.I)
QUANT_ABSOLUTE_REASON = (
    "an absolute with no noun - it names no target this tool can enumerate "
    "(see THE QUANTIFIER LAYER)")

# Condition 3: without a presence verb the sentence is not a claim about
# token presence, and it is not in this layer's denominator either.
PRESENCE_VERB = re.compile(
    r'\b(names?|carr(?:y|ies)|contains?|has|have|includes?|lists?|cites?|'
    r'ends?|starts?|begins?|prints?|states?|mentions?|holds?|links?|'
    r'declares?|quotes?|shows?|spells?|uses?|reads?|publish(?:es|ed)?)\b',
    re.I)

# Condition 4: the three literal predicate forms.
BACKTICK_LIT = re.compile(r'`([^`\n]{2,60})`')
QUOTED_LIT = re.compile(r'"([^"\n]{2,60})"')
BRACKET_FORM = re.compile(r'\bin (?:square )?brackets\b|\bbracketed\b', re.I)
BRACKET_TAG = re.compile(r'\[[^\]\n]+\]')

# A sentence, for this layer: text between terminators, and a markdown table
# cell boundary is a terminator too - the same rule the count layer's
# cell-boundary control established.
SENTENCE_SPLIT = re.compile(r'(?<=[.:!?])\s+|\|')

# See the docstring: a register states counts as they were.
REGISTER_DOCS = frozenset({"KNOWN-ISSUES.md"})

# WAIVERS. Same convention as `tools/citation_lint.py` and
# `tools/expectation_lint.py`: a case the pattern cannot decide is named out
# loud with its reason and PRINTED ON EVERY RUN, never suppressed silently.
# Keyed by (document name, the stated number, the noun).
WAIVERS: dict = {}


# ==========================================================================
# THE PURE LAYER
# ==========================================================================
def to_int(word: str):
    """The integer a count word or numeral names, or None."""
    w = (word or "").strip().lower()
    if w.isdigit():
        return int(w)
    return NUMBERS.get(w)


def line_starts(text: str):
    """The character offset at which each line begins. Lets a match position
    be turned into a line index without re-scanning the document."""
    out, pos = [], 0
    for ln in text.splitlines(keepends=True):
        out.append(pos)
        pos += len(ln)
    return out


def line_of(starts, pos: int) -> int:
    lo, hi = 0, len(starts) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if starts[mid] <= pos:
            lo = mid
        else:
            hi = mid - 1
    return lo


def is_fence(line: str) -> bool:
    return line.lstrip().startswith("```")


def is_heading(line: str) -> bool:
    return bool(re.match(r'\s{0,3}#{1,6}\s', line))


def fence_spans(lines: list):
    """[(open_index, close_index)] for every fenced block. A document with an
    unclosed fence yields the block up to the end, which is what a reader
    sees."""
    spans, open_at = [], None
    for i, ln in enumerate(lines):
        if is_fence(ln):
            if open_at is None:
                open_at = i
            else:
                spans.append((open_at, i))
                open_at = None
    if open_at is not None:
        spans.append((open_at, len(lines) - 1))
    return spans


# A command that WRAPS is one command. `\` (sh), `|` (a pipeline continued on
# the next line, which is how the kit's pwsh blocks are written) and a trailing
# backtick (pwsh's own continuation) all mean "this line is not finished".
# THE SIBLING OF THE CITATION LINT'S LOAD-BEARING RULE: there, a quotation that
# wraps in its source must still be found; here, a command that wraps in its
# block must still count once. Both tools would otherwise manufacture findings
# against text that is correct.
CONTINUES = re.compile(r'(\\|\||`)$')


def countable_lines(lines: list, span) -> int:
    """Non-blank, non-whole-line-comment lines inside a fenced block, with a
    wrapped command counted once.

    The definition is in the module docstring and it is a judgment call, which
    is why it is one function and not four scattered rules."""
    o, c = span
    n, continued = 0, False
    for ln in lines[o + 1:c]:
        s = ln.strip()
        if not s:
            continued = False
            continue
        if s.startswith("#") or s.startswith("//") or s.lower().startswith("rem "):
            continued = False
            continue
        if not continued:
            n += 1
        continued = bool(CONTINUES.search(s))
    return n


def table_rows(lines: list, start: int) -> int:
    """Body rows of the markdown table starting at `start`, or -1 if there is
    no table there. The header row and the `|---|` separator are not data."""
    if not lines[start].lstrip().startswith("|"):
        return -1
    if start + 1 >= len(lines):
        return -1
    sep = lines[start + 1].strip()
    if not re.match(r'^\|?[\s:|-]+\|[\s:|-]*$', sep) or "-" not in sep:
        return -1
    n, i = 0, start + 2
    while i < len(lines) and lines[i].lstrip().startswith("|"):
        n += 1
        i += 1
    return n


LIST_ITEM = re.compile(r'^(?P<ind>\s*)(?:[-*+]|\d+[.)])\s+\S')


def list_items(lines: list, start: int) -> int:
    """TOP-LEVEL items of the list starting at `start`, or -1 if there is no
    list there.

    A loose list - blank lines between items - is one list, because that is
    what a reader sees. A continuation line and an indented sub-item are part
    of the item above them, not items of their own."""
    m = LIST_ITEM.match(lines[start])
    if not m:
        return -1
    base = len(m.group("ind"))
    n, i, blanks = 0, start, 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            blanks += 1
            i += 1
            continue
        mm = LIST_ITEM.match(ln)
        indent = len(ln) - len(ln.lstrip())
        if mm and len(mm.group("ind")) == base:
            n += 1
            blanks = 0
            i += 1
            continue
        if indent > base and blanks <= 1:
            # a continuation line or a nested item
            blanks = 0
            i += 1
            continue
        if blanks == 0 and indent >= base:
            # a lazy continuation of the item above
            i += 1
            continue
        break
    return n


def paragraph_bounds(lines: list, idx: int):
    """(first, last) line indices of the block of non-blank lines holding
    `idx`. A heading, a fence line and a table row are their own boundaries in
    the sense that matters here: the walk stops at a blank line."""
    first = idx
    while first > 0 and lines[first - 1].strip():
        first -= 1
    last = idx
    while last + 1 < len(lines) and lines[last + 1].strip():
        last += 1
    return first, last


def next_block(lines: list, after: int):
    """The index of the first non-blank line after `after`, or None."""
    i = after + 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    return i if i < len(lines) else None


def target_after(lines: list, first_line: int):
    """(kind, count) for the construct starting at `first_line`, or None."""
    ln = lines[first_line]
    if is_fence(ln):
        for span in fence_spans(lines):
            if span[0] == first_line:
                return "fenced block", countable_lines(lines, span)
        return None
    rows = table_rows(lines, first_line)
    if rows >= 0:
        return "table", rows
    items = list_items(lines, first_line)
    if items > 0:
        return "list", items
    return None


def section_span(lines: list, kind: str, num: str):
    """(first, last) line indices of the section a locator names, or None when
    it matches no heading or more than one.

    `Step 0` matches a heading containing `Step 0`; `§2` and `section 2` match
    a heading whose text starts `2.` or `2 `, which is how this kit numbers
    its sections."""
    if kind.lower() in ("step",):
        pat = re.compile(r'\bstep\s+' + re.escape(num) + r'\b', re.I)
        hits = [i for i, ln in enumerate(lines)
                if is_heading(ln) and pat.search(ln)]
    else:
        pat = re.compile(r'^\s{0,3}(#{1,6})\s+' + re.escape(num) + r'[.)\s]')
        hits = [i for i, ln in enumerate(lines) if pat.match(ln)]
    if len(hits) != 1:
        return None
    start = hits[0]
    level = len(re.match(r'\s{0,3}(#{1,6})', lines[start]).group(1))
    end = len(lines) - 1
    for i in range(start + 1, len(lines)):
        if is_heading(lines[i]):
            lvl = len(re.match(r'\s{0,3}(#{1,6})', lines[i]).group(1))
            if lvl <= level:
                end = i - 1
                break
    return start, end


def section_fence_count(lines: list, span):
    """Countable lines of the ONE fenced block in a section, or None when the
    section holds none or more than one. Ambiguity is skipped, never guessed
    at: a wrong target manufactures findings, which is worse than missing
    them."""
    first, last = span
    inside = [s for s in fence_spans(lines) if first <= s[0] <= last]
    if len(inside) != 1:
        return None
    return countable_lines(lines, inside[0])


# ==========================================================================
# THE QUANTIFIER LAYER - pure. Same discipline as the count layer above: the
# deciding is done on a string, so every rule is testable without a tree.
# ==========================================================================
def table_row_texts(lines: list, start: int):
    """The body rows of the table at `start`, as text, or None."""
    if table_rows(lines, start) < 0:
        return None
    out, i = [], start + 2
    while i < len(lines) and lines[i].lstrip().startswith("|"):
        out.append(lines[i].strip())
        i += 1
    return out


def list_item_texts(lines: list, start: int):
    """(texts, end_index) for the top-level items of the list at `start`, or
    None. A continuation line belongs to the item above it, which is what a
    reader sees and what `list_items` already counts."""
    m = LIST_ITEM.match(lines[start]) if start < len(lines) else None
    if not m:
        return None
    base = len(m.group("ind"))
    out, cur, i, blanks = [], None, start, 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            blanks += 1
            i += 1
            continue
        mm = LIST_ITEM.match(ln)
        indent = len(ln) - len(ln.lstrip())
        if mm and len(mm.group("ind")) == base:
            if cur is not None:
                out.append(" ".join(cur))
            cur = [ln.strip()]
            blanks = 0
            i += 1
            continue
        if cur is not None and ((indent > base and blanks <= 1)
                                or (blanks == 0 and indent >= base)):
            cur.append(ln.strip())
            blanks = 0
            i += 1
            continue
        break
    if cur is not None:
        out.append(" ".join(cur))
    return (out, i) if out else None


def fence_line_texts(lines: list, span):
    """The countable lines of a fenced block, as text, with a wrapped command
    joined into the one line it is. Same rule as `countable_lines`, which
    counts what this returns."""
    o, c = span
    out, continued = [], False
    for ln in lines[o + 1:c]:
        s = ln.strip()
        if not s:
            continued = False
            continue
        if s.startswith("#") or s.startswith("//") or s.lower().startswith("rem "):
            continued = False
            continue
        if continued and out:
            out[-1] = out[-1] + " " + s
        else:
            out.append(s)
        continued = bool(CONTINUES.search(s))
    return out


def all_constructs(lines: list, kind: str):
    """Every construct of `kind` in the document, each as its list of element
    texts. Used by shape Q2: exactly one is a target, and any other number is
    ambiguity this tool skips rather than guesses at."""
    spans = fence_spans(lines)
    inside = set()
    for o, c in spans:
        inside.update(range(o, c + 1))
    out = []
    if kind == "fenced block":
        return [fence_line_texts(lines, s) for s in spans]
    i = 0
    while i < len(lines):
        if i in inside:
            i += 1
            continue
        if kind == "table":
            rows = table_row_texts(lines, i)
            if rows:
                out.append(rows)
                i += 2 + len(rows)
                continue
        else:
            got = list_item_texts(lines, i)
            if got:
                texts, end = got
                out.append(texts)
                i = max(end, i + 1)
                continue
        i += 1
    return out


def sentence_at(text: str, pos: int) -> str:
    """The sentence holding `pos`. A table cell boundary ends a sentence, the
    same rule the count layer's cell-boundary control established."""
    start = 0
    for m in SENTENCE_SPLIT.finditer(text, 0, pos):
        start = m.end()
    end = len(text)
    m = SENTENCE_SPLIT.search(text, pos)
    if m:
        end = m.start()
    return text[start:end]


def literal_predicate(sentence: str, after: int):
    """(kind, literal) for the predicate of a quantifier claim, or None.

    Only the part of the sentence AFTER the quantifier is read: a literal
    sitting before it belongs to some other clause."""
    # A WINDOW, for the same reason the citation lint's locator has one: a
    # literal four clauses away is not this claim's predicate. 100 characters
    # is wide enough for "names an artifact and carries a source in brackets"
    # and narrow enough to exclude the next sentence's vocabulary.
    tail = sentence[after:after + 100]
    if BRACKET_FORM.search(tail):
        return ("a bracketed tag", None)
    for m in BACKTICK_LIT.finditer(tail):
        lit = m.group(1).strip()
        if lit.lower().endswith(".md"):
            continue          # a document reference, not a predicate
        if lit:
            return ("the literal", lit)
    for m in QUOTED_LIT.finditer(tail):
        lit = m.group(1).strip()
        if lit:
            return ("the literal", lit)
    return None


def element_satisfies(elem: str, kind: str, literal) -> bool:
    if kind == "a bracketed tag":
        return bool(BRACKET_TAG.search(elem))
    return literal in elem


def quantifier_claims(text: str):
    """Every universal-quantifier claim this tool can decide, plus the ones it
    had to skip.

    Returns (checked, skipped): `checked` a list of dicts, `skipped` a list of
    (phrase, reason). Pure - it decides a string, so every rule below is
    testable without a tree."""
    lines = text.splitlines()
    starts = line_starts(text)
    checked, skipped = [], []

    # THE DISCLOSURE PASS, FIRST AND SEPARATE - the sibling of WIDE_COUNT's.
    # An absolute that carries a presence verb but names no enumerable noun
    # decides nothing and is recorded as skipped so that it is visible
    # rather than absent.
    for m in QUANT_ABSOLUTE.finditer(text):
        sent = sentence_at(text, m.start())
        if not PRESENCE_VERB.search(sent):
            continue
        skipped.append((re.sub(r'\s+', " ", m.group(0)).strip(),
                        QUANT_ABSOLUTE_REASON))

    for m in QUANT.finditer(text):
        q = m.group("q").lower()
        noun = m.group("noun").lower()
        phrase = re.sub(r'\s+', " ", m.group(0)).strip()
        idx = line_of(starts, m.start())
        if idx >= len(lines):
            continue
        # THE SENTENCE IS SCOPED TO ITS PARAGRAPH. Found by the first CI
        # rehearsal: a page whose heading carries no full stop put the
        # heading and the claim in one "sentence", and the opening rule below
        # then rejected a claim that does open its paragraph's first
        # sentence. A blank line ends a sentence in markdown whatever the
        # punctuation says.
        first, last = paragraph_bounds(lines, idx)
        para_start = starts[first]
        para_end = starts[last] + len(lines[last])
        para = text[para_start:para_end]
        sent = sentence_at(para, m.start() - para_start)
        # Condition 3. Not a claim about token presence at all, and not in
        # this layer's denominator: see the docstring. Recorded as a skip so
        # the exclusion is visible (r30 review).
        qin = sent.find(m.group(0))
        if qin < 0:
            qin = 0
        if not PRESENCE_VERB.search(sent[qin:]):
            skipped.append((phrase, "no presence verb after the quantifier "
                                    "- not a token-presence claim; recorded "
                                    "rather than silently excluded"))
            continue
        # Condition 2. The word after the quantifier may be an adjective
        # ("every single row"); before deciding the sentence names no
        # target, prefer a QUANT_NOUNS member within the next few words
        # (r30 review).
        if noun not in QUANT_NOUNS:
            for cand in re.findall(r"[a-z]+",
                                   sent[qin:qin + 90].lower())[1:6]:
                if cand in QUANT_NOUNS:
                    noun = cand
                    break
        if noun not in QUANT_NOUNS:
            skipped.append((phrase, f"`{noun}` names no target this tool "
                                    f"enumerates (a table, a list, a fenced "
                                    f"block)"))
            continue
        # THE NARROWING THE FIRST LIVE RUN FORCED, and it is the count
        # layer's own opening rule one level up. Without it this layer's
        # first live run manufactured a finding against a published walk
        # prompt: "executing every command as printed" sits deep inside a
        # 400-word instruction whose later clause happens to quote the word
        # "done", and the tool read that quotation as the predicate of a
        # claim about a fenced block. A universal is a claim ABOUT a target
        # only when it is what the sentence is about, which in practice means
        # it opens the sentence.
        if not re.fullmatch(r'[\s>*_`#|-]*', sent[:qin] or ""):
            skipped.append((phrase, "does not open its sentence - a "
                                    "universal buried mid-sentence names no "
                                    "target this tool can attribute it to"))
            continue
        # Condition 4.
        pred = literal_predicate(sent, qin + len(m.group(0)))
        if pred is None:
            skipped.append((phrase, "no literal predicate - the sentence "
                                    "asserts nothing this tool can test by "
                                    "token presence"))
            continue
        pkind, literal = pred

        kind = ("table" if noun in TABLE_NOUNS else
                "list" if noun in BULLET_NOUNS else "fenced block")

        elems, where = None, ""
        # ---- Q1: the phrase introduces the construct ---------------------
        tail = lines[last].rstrip()
        opens = re.fullmatch(r'[\s>*_-]*', text[starts[first]:m.start()])
        if tail.endswith(":") and opens:
            nxt = next_block(lines, last)
            if nxt is not None:
                if kind == "table":
                    got = table_row_texts(lines, nxt)
                elif kind == "list":
                    g = list_item_texts(lines, nxt)
                    got = g[0] if g else None
                else:
                    span = next((s for s in fence_spans(lines)
                                 if s[0] == nxt), None)
                    got = fence_line_texts(lines, span) if span else None
                if got:
                    elems, where = got, f"the {kind} below it"
        # ---- Q2: the document's sole construct of that kind --------------
        if elems is None:
            found = [c for c in all_constructs(lines, kind) if c]
            if len(found) != 1:
                skipped.append((phrase, f"this document holds "
                                        f"{len(found)} {kind}(s) - a target "
                                        f"is located only when it introduces "
                                        f"one or the document holds exactly "
                                        f"one"))
                continue
            elems, where = found[0], f"the one {kind} in this document"

        want = q not in QUANT_NEGATIVE
        bad = [e for e in elems
               if element_satisfies(e, pkind, literal) != want]
        checked.append(dict(phrase=phrase, quant=q, noun=noun, kind=kind,
                            where=where, predicate=pkind, literal=literal,
                            total=len(elems), bad=bad, line=idx + 1,
                            negative=not want))

    return checked, skipped


def claims(text: str, self_name: str = "", resolve=None):
    """Every (stated, actual, noun, kind, where, locator) this tool claims to
    be able to decide, plus the phrases it had to skip.

    `resolve(name)` returns the text of another kit document, or None. With no
    resolver the L3 shape is skipped, which is what makes this function pure
    and testable on a single string.

    Returns (checked, skipped) where `checked` is a list of dicts and
    `skipped` a list of (phrase, reason)."""
    lines = text.splitlines()
    starts = line_starts(text)
    checked, skipped = [], []

    # THE DISCLOSURE PASS, FIRST AND SEPARATE. Count phrases whose number is
    # outside the checking vocabulary are recorded as skipped and never looked
    # at again - the two patterns match disjoint number tokens, so nothing is
    # counted twice. See WIDE_COUNT.
    for m in WIDE_COUNT.finditer(text):
        if m.group("noun").lower() in NOT_NOUNS:
            continue
        skipped.append((re.sub(r'\s+', " ", m.group(0)).strip(), WIDE_REASON))

    for m in COUNT.finditer(text):
        stated = to_int(m.group("num"))
        noun = m.group("noun").lower()
        if stated is None or noun in NOT_NOUNS:
            continue
        phrase = re.sub(r'\s+', " ", m.group(0)).strip()
        idx = line_of(starts, m.start())
        if idx >= len(lines):
            continue
        first, last = paragraph_bounds(lines, idx)

        # ---- L3: a count about another document's section ----------------
        ref = None
        for r in SECTION_REF.finditer(text[starts[first]:m.start()]):
            if "|" in text[starts[first] + r.end():m.start()]:
                continue      # a different table cell is a different sentence
            ref = r
        if ref is not None and noun in LINE_NOUNS:
            name = ref.group("f")
            other = resolve(name) if resolve else None
            loc = f"{ref.group('kind')} {ref.group('n')}"
            if other is None:
                skipped.append((phrase, f"names `{name}` {loc}, which is not "
                                        f"in this tree"))
                continue
            olines = other.splitlines()
            span = section_span(olines, ref.group("kind"), ref.group("n"))
            if span is None:
                skipped.append((phrase, f"`{name}` has no single heading for "
                                        f"{loc}"))
                continue
            actual = section_fence_count(olines, span)
            if actual is None:
                skipped.append((phrase, f"`{name}` {loc} holds no single "
                                        f"fenced block to count"))
                continue
            checked.append(dict(stated=stated, actual=actual, noun=noun,
                                kind="fenced block", where=f"`{name}` {loc}",
                                shape="L3", phrase=phrase, line=idx + 1))
            continue

        # ---- L1: the phrase introduces the next construct -----------------
        # THE NARROWING THE FIRST LIVE RUN FORCED. The phrase must OPEN the
        # introducing paragraph - it is the paragraph's subject, not a number
        # mentioned somewhere inside it. Without this the tool reported 23
        # findings against the kit, 22 of them its own and 21 of those this
        # class: "one pass", "4 is what lets", "eight defaults" - numbers that
        # happen to sit in a
        # paragraph which happens to end in a colon. A count is a claim about
        # the thing below it only when it is what the sentence is about.
        tail = lines[last].rstrip()
        opens = re.fullmatch(r'[\s>*_-]*', text[starts[first]:m.start()])
        if tail.endswith(":") and opens:
            nxt = next_block(lines, last)
            got = target_after(lines, nxt) if nxt is not None else None
            if got is not None:
                kind, actual = got
                if kind == "fenced block" and noun not in LINE_NOUNS:
                    skipped.append((phrase, "introduces a fenced block, and "
                                            f"`{noun}` is not a line noun"))
                    continue
                checked.append(dict(stated=stated, actual=actual, noun=noun,
                                    kind=kind, where=f"the {kind} below it",
                                    shape="L1", phrase=phrase, line=idx + 1))
                continue
            skipped.append((phrase, "introduces no table, list or fenced "
                                    "block"))
            continue

        # ---- L2: the phrase follows a fenced block ------------------------
        if noun in LINE_NOUNS and first > 0:
            prev = first - 1
            while prev >= 0 and not lines[prev].strip():
                prev -= 1
            if prev >= 0 and is_fence(lines[prev]) and not any(
                    is_heading(lines[i]) for i in range(prev + 1, first)):
                span = next((s for s in fence_spans(lines) if s[1] == prev),
                            None)
                if span is not None:
                    checked.append(dict(
                        stated=stated, actual=countable_lines(lines, span),
                        noun=noun, kind="fenced block",
                        where="the fenced block above it", shape="L2",
                        phrase=phrase, line=idx + 1))
                    continue

        skipped.append((phrase, "no locatable target"))

    return checked, skipped


def coverage_state(located: int, skipped: int):
    """(state word, percentage located) for a run. CLEAN only when nothing was
    skipped; PARTIAL otherwise, which is the kit's own state-word rule applied
    to this kit's own lint. One function so the summary line and its control
    read the same rule."""
    seen = located + skipped
    pct = (100.0 * located / seen) if seen else 100.0
    return ("CLEAN" if skipped == 0 else "PARTIAL"), pct


def waiver_for(doc_name: str, stated: int, noun: str):
    """The waiver covering this claim, or None. An empty reason is not a
    waiver - it is the silent case this tool exists to prevent."""
    reason = WAIVERS.get((doc_name, stated, noun))
    return reason if reason and reason.strip() else None


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


def run(root: Path, show_all: bool) -> int:
    docs = kit_documents(root)
    if not docs:
        print(f"{RED}COUNT LINT: ABORT — no markdown documents under "
              f"{root}{RESET}")
        return 2

    index = {}
    for p in docs:
        index.setdefault(p.name, p)
    cache: dict = {}

    def resolve(name: str):
        p = (root / name)
        if not p.is_file():
            p = index.get(Path(name).name)
        if p is None or not p.is_file():
            return None
        if p not in cache:
            try:
                cache[p] = p.read_text(encoding="utf-8")
            except OSError:
                return None
        return cache[p]

    checked, skipped, problems, waived, register = 0, 0, [], [], 0
    qchecked, qskipped, qproblems, qregister = 0, 0, [], 0
    for doc in docs:
        try:
            text = doc.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"{RED}COUNT LINT: ABORT — cannot read {doc}: {exc}{RESET}")
            return 2
        got, miss = claims(text, doc.name, resolve)
        qgot, qmiss = quantifier_claims(text)
        if doc.name in REGISTER_DOCS:
            register += len(got)
            qregister += len(qgot)
            continue
        qchecked += len(qgot)
        qskipped += len(qmiss)
        for c in qgot:
            ok = not c["bad"]
            if show_all:
                mark = f"{GREEN}{c['total']}/{c['total']}{RESET}" if ok else \
                    f"{RED}{c['total'] - len(c['bad'])}/{c['total']}{RESET}"
                print(f"  [Q] {doc.name}:{c['line']}  \"{c['phrase']}\" -> "
                      f"{c['where']}, {mark} element(s) satisfy it")
            if not ok:
                qproblems.append((doc, c))
        if show_all:
            for phrase, why in qmiss:
                print(f"  {YELLOW}skipQ{RESET} {doc.name}: \"{phrase}\" — {why}")
        checked += len(got)
        skipped += len(miss)
        for c in got:
            ok = c["stated"] == c["actual"]
            if show_all:
                mark = f"{GREEN}{c['actual']}{RESET}" if ok \
                    else f"{RED}{c['actual']}{RESET}"
                print(f"  [{c['shape']}] {doc.name}:{c['line']}  "
                      f"\"{c['phrase']}\" -> {c['where']} has {mark}")
            if not ok:
                reason = waiver_for(doc.name, c["stated"], c["noun"])
                if reason:
                    waived.append((doc, c, reason))
                else:
                    problems.append((doc, c))
        if show_all:
            for phrase, why in miss:
                print(f"  {YELLOW}skip{RESET}  {doc.name}: \"{phrase}\" — {why}")

    print()
    print(f"root      : {root}")
    print(f"documents : {len(docs)} scanned")
    print(f"counts    : {checked} located and checked, {skipped} skipped")
    print(f"quantifier: {qchecked} located and checked, {qskipped} skipped")
    # A skip nobody sees is not a skip - the same rule the citation lint and
    # the expectation lint apply to theirs. Since round 30 the skip is also in
    # the summary's denominator, so `clean` cannot be printed over 2% coverage.
    print(f"skipped   : {skipped + qskipped} phrase(s) this tool cannot locate "
          f"a target for (printed with --list)")
    print(f"register  : {register} count(s) and {qregister} quantifier "
          f"claim(s) NOT checked, in {', '.join(sorted(REGISTER_DOCS))} — a "
          f"findings register records what a claim used to be, beside the "
          f"correction")
    print(f"waivers   : {len(waived)} (each printed below, every run)")
    for doc, c, reason in waived:
        print(f"{YELLOW}  WAIVED {doc.name}: \"{c['phrase']}\" "
              f"(target has {c['actual']})\n    {reason}{RESET}")

    located = checked + qchecked
    seen = located + skipped + qskipped
    state, pct = coverage_state(located, skipped + qskipped)
    coverage = (f"{located} of {seen} claim(s) located and checked "
                f"({pct:.1f}%)")

    if problems or qproblems:
        print()
        for doc, c in problems:
            print(f"{RED}THE NUMBER IS NOT THE NUMBER{RESET}  "
                  f"[shape {c['shape']}]  {doc.as_posix()}:{c['line']}")
            print(f"  claim    : \"{c['phrase']}\"")
            print(f"  target   : {c['where']} ({c['kind']})")
            print(f"  counted  : {c['actual']}, stated {c['stated']}")
            print(f"  {BOLD}Either the number is wrong or the thing it counts "
                  f"has moved. Open the target, count it, and write that "
                  f"number - or drop the count and describe the thing.{RESET}")
        for doc, c in qproblems:
            word = "must not carry" if c["negative"] else "must carry"
            lit = (repr(c["literal"]) if c["literal"] is not None
                   else "a bracketed tag")
            print(f"{RED}THE CLAIM IS NOT TRUE OF EVERY ELEMENT{RESET}  "
                  f"[quantifier]  {doc.as_posix()}:{c['line']}")
            print(f"  claim    : \"{c['phrase']}\" — every element {word} "
                  f"{lit}")
            print(f"  target   : {c['where']} ({c['total']} element(s))")
            print(f"  failing  : {len(c['bad'])}")
            for e in c["bad"][:3]:
                print(f"    - {e[:110]}")
            if len(c["bad"]) > 3:
                print(f"    ... and {len(c['bad']) - 3} more")
            print(f"  {BOLD}Either the claim is wrong or the elements are. "
                  f"Enumerate the target, or narrow the sentence to what is "
                  f"true of all of it.{RESET}")
        print()
        n = len(problems) + len(qproblems)
        print(f"{RED}COUNT LINT: {n} located claim(s) disagree with what they "
              f"name — {coverage} — exit 1{RESET}")
        return 1

    colour = GREEN if state == "CLEAN" else YELLOW
    print(f"{colour}COUNT LINT: {state} - {coverage}, 0 disagree - "
          f"exit 0{RESET}")
    return 0


# ==========================================================================
def selftest() -> int:
    """The negative controls. Each is labelled COUNT(<id>) so the expectation
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

    # The other document, used by every L3 control: a Step 0 with TEN
    # countable lines, which is what `QUICKSTART.md` Step 0 actually holds.
    OTHER = ("# Q\n\n## Step 0 — prove the tooling (3 min)\n\n"
             "```bash\n"
             "git --version\n"
             "python --version\n"
             "a --selftest\n"
             "b --selftest\n"
             "c --selftest\n"
             "d\n"
             "e\n"
             "f --selftest\n"
             "g --selftest\n"
             "h --strict --armed .claude/settings.json\n"
             "```\n\n"
             "## Step 1 — next\n")

    def other(name):
        return OTHER if name == "QUICKSTART.md" else None

    print(f"{BOLD}=== A. the forced-red half: a stale count must be caught "
          f"==={RESET}")

    # F1, REPLANTED. The exact shape that shipped: a count in one document
    # about a fenced block in another, left behind when the block grew.
    f1 = ("| P3 | The kit's own tooling is green | Run `QUICKSTART.md` "
          "**Step 0** in the kit clone: nine lines, all exit 0 |\n")
    got, _ = claims(f1, "ONBOARD.md", other)
    check("COUNT(stale-cross-doc): F1's own shape is SEEN, and seen as a "
          "cross-document claim",
          [(c["shape"], c["stated"], c["actual"]) for c in got],
          [("L3", 9, 10)])
    check("COUNT(stale-cross-doc): ...and the stated number does not match",
          [c["stated"] == c["actual"] for c in got], [False])

    # The introducer shape, forced red: a table that lost a row.
    stale_table = ("Seven checks run, and each red line names the step:\n\n"
                   "| Check | What it reads |\n|---|---|\n"
                   "| a | x |\n| b | x |\n| c | x |\n| d | x |\n"
                   "| e | x |\n| f | x |\n")
    got, _ = claims(stale_table, "LEVEL-1.md")
    check("COUNT(stale-introducer): a stated count over the table it "
          "introduces is checked, and a missing row is caught",
          [(c["kind"], c["stated"], c["actual"]) for c in got],
          [("table", 7, 6)])

    # The trailing shape, forced red: the checkpoint under a block that grew.
    stale_trailing = ("```bash\na\nb\nc\n```\n\n"
                      "**Checkpoint:** all two lines exit 0.\n")
    got, _ = claims(stale_trailing, "QUICKSTART.md")
    check("COUNT(stale-trailing): a checkpoint under the block it counts is "
          "checked too",
          [(c["shape"], c["stated"], c["actual"]) for c in got],
          [("L2", 2, 3)])

    print()
    print(f"{BOLD}=== B. the controls that keep it from manufacturing "
          f"findings ==={RESET}")

    # THE MOST IMPORTANT CONTROL IN THE FILE. A checker that only ever goes
    # red on a true count is not a checker, it is a defect generator: every
    # correct sentence in the kit would become a finding.
    true_claim = ("| P3 | green | Run `QUICKSTART.md` **Step 0**: ten lines, "
                  "all exit 0 |\n")
    got, _ = claims(true_claim, "ONBOARD.md", other)
    check("COUNT(true-count): the TRUE count passes - the same shape, the "
          "right number",
          [(c["stated"], c["actual"], c["stated"] == c["actual"])
           for c in got], [(10, 10, True)])

    got, _ = claims("Three commands, and the blank lines are not among "
                    "them:\n\n```bash\na\n\nb\n\nc\n```\n", "X.md")
    check("COUNT(blank-lines): blank lines inside a fenced block are not "
          "countable lines",
          [c["actual"] for c in got], [3])
    got, _ = claims("Two commands:\n\n```bash\n# a whole-line "
                    "comment\na  # a trailing comment\nb\n```\n", "X.md")
    check("COUNT(comment-line): a whole-line comment is not a command, and a "
          "TRAILING comment does not stop its line being one",
          [c["actual"] for c in got], [2])
    # FOUND BY THE FIRST LIVE RUN, NOT BY DESIGN. `QUICKSTART.md` Step 4's
    # pwsh block is three commands on four physical lines - the third is a
    # pipeline continued on the next line - and the tool reported the correct
    # sentence as a defect. A checker that manufactures findings against right
    # answers is worse than no checker; the citation lint's own most important
    # control is the same shape one level down.
    got, _ = claims("Three commands:\n\n```powershell\n"
                    "$raw = 'a'\n$eol = 'b'\n'x','y' |\n"
                    "    ForEach-Object { $_ }\n```\n", "X.md")
    check("COUNT(wrapped-command): a command that WRAPS across a line counts "
          "once - the same rule the citation lint applies to a quotation",
          [c["actual"] for c in got], [3])
    got, _ = claims("Two rows:\n\n| a | b |\n|---|---|\n| 1 | 2 |\n"
                    "| 3 | 4 |\n", "X.md")
    check("COUNT(table-header): the header row and the |---| separator are "
          "not data rows",
          [c["actual"] for c in got], [2])
    got, _ = claims("Three states, and only one of them is yours:\n\n"
                    "1. **You were instructed.** Obey it.\n\n"
                    "2. **You were not, and the owner can answer.** Ask.\n"
                    "   One question is cheaper.\n\n"
                    "3. **You were not, and they cannot.** Take Level 1.\n",
                    "X.md")
    check("COUNT(loose-list): a list with blank lines between its items is "
          "ONE list, and a continuation line is not an item",
          [(c["kind"], c["actual"]) for c in got], [("list", 3)])
    got, _ = claims("Two rules:\n\n- the first\n  - a sub-point\n  - another\n"
                    "- the second\n", "X.md")
    check("COUNT(nested-item): an indented sub-item is part of the item "
          "above it, not a top-level one",
          [c["actual"] for c in got], [2])

    print()
    print(f"{BOLD}=== C. what is NOT a checkable claim (the false-positive "
          f"floor) ==={RESET}")

    got, miss = claims("The run found six findings against the documents.\n",
                       "X.md")
    check("COUNT(prose-count): a count with no locatable target is SKIPPED, "
          "not failed", (got, [r for _, r in miss]),
          ([], ["no locatable target"]))
    got, miss = claims("Two exclusions, stated in the caption: time the owner "
                       "spends is not in your number, and blocked time is "
                       "its own row.\n", "X.md")
    check("COUNT(mid-paragraph-colon): a colon inside a paragraph that keeps "
          "going does not introduce anything",
          (got, [r for _, r in miss]), ([], ["no locatable target"]))
    two_fences = ("# Q\n\n## Step 0 — prove it\n\n```bash\na\nb\n```\n\n"
                  "```powershell\na\nb\n```\n\n## Step 1\n")
    got, miss = claims("Run `QUICKSTART.md` **Step 0**: two lines.\n", "X.md",
                       lambda nm: two_fences)
    check("COUNT(ambiguous-section): a section with TWO fenced blocks is "
          "skipped, never guessed at",
          (got, [r for _, r in miss]),
          ([], ["`QUICKSTART.md` Step 0 holds no single fenced block to "
                "count"]))
    got, miss = claims("| `QUICKSTART.md` **Step 0** | nine lines, all exit "
                       "0 |\n", "X.md", other)
    check("COUNT(cell-boundary): a document reference in a PREVIOUS table "
          "cell does not carry a count phrase in this one",
          (got, [r for _, r in miss]), ([], ["no locatable target"]))
    got, miss = claims("`QUICKSTART.md` **Step 0** installs five documents.\n",
                       "X.md", other)
    check("COUNT(semantic-count): a cross-document count whose noun is not a "
          "line noun is skipped - no parser decides what a document is",
          (got, [r for _, r in miss]), ([], ["no locatable target"]))
    check("COUNT(register): a findings register's counts are not checked - it "
          "records what a count used to be",
          "KNOWN-ISSUES.md" in REGISTER_DOCS, True)
    check("COUNT(register): ...and the exemption is by document, so an "
          "ordinary page gets no such pass",
          "ONBOARD.md" in REGISTER_DOCS, False)
    check("COUNT(waiver): every shipped waiver carries a non-empty reason (an "
          "empty one is the silent case wearing a label)",
          [k for k, v in WAIVERS.items() if not (v or "").strip()], [])

    # ROUND 24's REVIEW, m2. Five false counts written with the word *ninety*
    # were matched by nothing at all: not checked, not skipped, and absent
    # from the skip total the docstring calls the disclosure. The ceiling
    # stays where it is; what changes is that a phrase above it is now VISIBLE
    # as a skip. These controls hold both halves - the ceiling and its
    # disclosure - so neither can be quietly moved.
    got, miss = claims("Thirty lines run in that block:\n\n```bash\na\nb\n"
                       "```\n", "X.md")
    check("COUNT(vocabulary-ceiling): a number above the checking vocabulary "
          "is SKIPPED WITH ITS OWN REASON - never checked, never invisible",
          (got, [r.split(" - ")[0] for _, r in miss]),
          ([], ["a number outside this tool's checking vocabulary"]))
    got, miss = claims("Twenty-five commands:\n\n```bash\na\n```\n", "X.md")
    check("COUNT(vocabulary-ceiling): ...and so is a hyphenated form, which "
          "`NUMBERS` cannot spell",
          (len(got), len(miss)), (0, 1))
    got, miss = claims("Here are 1024 lines:\n\n```bash\na\n```\n", "X.md")
    check("COUNT(vocabulary-ceiling): ...and so is a digit run longer than "
          "the three the checking pattern reads",
          (len(got), len(miss)), (0, 1))
    got, miss = claims("Two commands:\n\n```bash\na\nb\n```\n", "X.md")
    check("COUNT(vocabulary-in-range): the disclosure pass takes nothing away "
          "from the checking pass - a number INSIDE the vocabulary is still "
          "decided, and is not also skipped",
          (len(got), len(miss)), (1, 0))

    print()
    print(f"{BOLD}=== E. the quantifier layer: the forced-red half "
          f"==={RESET}")

    # ROUND 29's F1, REPLANTED. The sentence that shipped on the front of
    # COMPARISON.md, over the shape of the table it quantifies: three of the
    # rows carry no bracketed source at all. This is the claim the program
    # paid for four times in rounds 26-29.
    F1_ROWS = ("Every row names an artifact and carries a source in "
               "brackets:\n\n"
               "| Claim | Verdict | Source |\n|---|---|---|\n"
               "| C1 | REDUNDANT-BY | [FETCHED] |\n"
               "| C11 | NO-MATCH-FOUND | none |\n"
               "| C13 | NO-MATCH-FOUND | [FETCHED, as above] |\n"
               "| C17 | NO-MATCH-FOUND | none |\n"
               "| C18 | COMPOSITION-STANDS | none |\n")
    got, _ = quantifier_claims(F1_ROWS)
    check("QUANT(f1-shape): round 29's F1 sentence is SEEN, and the rows "
          "that carry no bracketed source are named",
          [(c["total"], len(c["bad"])) for c in got], [(5, 3)])

    # ...AND NOT ONLY WHEN IT IS ADJACENT. The shipped defect sat several
    # paragraphs above its table, which the introducer rule alone cannot
    # reach. Shape Q2: the document holds exactly one table.
    F1_APART = ("# Verify these rows yourself\n\n"
                "These rows were compiled by the program they describe.\n\n"
                "Every row names an artifact and carries a source in "
                "brackets.\n\n"
                "Some other paragraph entirely.\n\n"
                "| Claim | Verdict | Source |\n|---|---|---|\n"
                "| C1 | REDUNDANT-BY | [FETCHED] |\n"
                "| C11 | NO-MATCH-FOUND | none |\n")
    got, _ = quantifier_claims(F1_APART)
    check("QUANT(f1-nonadjacent): the same claim written pages from its "
          "table is still located, because the document holds exactly one",
          [(c["where"], c["total"], len(c["bad"])) for c in got],
          [("the one table in this document", 2, 1)])

    # ROUND 29's F2, RESTATED OVER AN ENUMERABLE TARGET. The shipped sentence
    # is skipped (control below); the same claim written against a per-entry
    # table is caught. Both halves are held so neither can be quietly moved.
    F2_TABLE = ("Every row of this register names a published prompt in "
                "`docs/walks/`:\n\n"
                "| Entry | Prompt |\n|---|---|\n"
                "| 8 | `docs/walks/walk-08-windows-literalist.md` |\n"
                "| 13 | `docs/walks/walk-13-thorough-adopter.md` |\n"
                "| 29 | none - the read was unprompted |\n")
    got, _ = quantifier_claims(F2_TABLE)
    check("QUANT(f2-restated): round 29's F2 claim, written over a target "
          "this tool can enumerate, is CAUGHT on the entry with no prompt",
          [(c["literal"], c["total"], len(c["bad"])) for c in got],
          [("docs/walks/", 3, 1)])

    # THE NEGATIVE QUANTIFIER INVERTS. "No row carries X" is red when one
    # does, which is the other half of the class and is not the same test.
    NEG = ("No row carries `[UNVERIFIED]`:\n\n"
           "| Claim | Source |\n|---|---|\n"
           "| C1 | [FETCHED] |\n| C14 | [UNVERIFIED] |\n")
    got, _ = quantifier_claims(NEG)
    check("QUANT(negative-red): `no`/`none` invert the test - the row that "
          "DOES carry the literal is the finding",
          [(c["negative"], len(c["bad"])) for c in got], [(True, 1)])

    print()
    print(f"{BOLD}=== F. the quantifier layer: the controls that keep it "
          f"from manufacturing findings ==={RESET}")

    # THE MOST IMPORTANT CONTROL IN THIS SECTION, for the same reason
    # COUNT(true-count) is the most important one in section B.
    TRUE = ("Every row carries a source in brackets:\n\n"
            "| Claim | Source |\n|---|---|\n"
            "| C1 | [FETCHED] |\n| C2 | [SEARCH-URL] |\n")
    got, _ = quantifier_claims(TRUE)
    check("QUANT(true-claim): the TRUE universal passes - the same shape, "
          "and every row satisfies it",
          [(c["total"], c["bad"]) for c in got], [(2, [])])

    # THE ADJECTIVE CONTROL (r30 review, F6). "Every single row" must reach
    # the noun past the adjective, not skip on `single` as a non-target.
    ADJ = ("Every single row carries a source in brackets:\n\n"
           "| Claim | Source |\n|---|---|\n"
           "| C1 | [FETCHED] |\n| C2 | none |\n")
    got, _ = quantifier_claims(ADJ)
    check("QUANT(adjective): `every single row` decides on `row` - the "
          "adjective does not defeat the noun match",
          [(c["total"], len(c["bad"])) for c in got], [(2, 1)])

    got, _ = quantifier_claims("No row carries `[TODO]`:\n\n"
                              "| Claim | Source |\n|---|---|\n"
                              "| C1 | [FETCHED] |\n")
    check("QUANT(negative-true): ...and so does the true negative",
          [c["bad"] for c in got], [[]])

    # THE LIMIT, HELD AS A CONTROL. Round 29's F2 as it actually shipped has
    # no enumerable target, so it is SKIPPED WITH ITS REASON - partial cover,
    # disclosed, and not full cover. Before round 30 it was invisible.
    got, miss = quantifier_claims(
        "- **`docs/walks/`** — the prompt behind every finding count here, "
        "published so the method can be disputed rather than trusted.\n")
    check("QUANT(f2-as-shipped): F2's sentence as it shipped is SKIPPED with "
          "its reason - never checked, never invisible",
          (got, [r.split(" names no")[0] for _, r in miss]),
          ([], ["`finding`"]))

    # FOUND BY THE FIRST LIVE RUN, NOT BY DESIGN - the sibling of
    # COUNT(wrapped-command). `docs/walks/walk-13-thorough-adopter.md` holds a
    # 400-word persona prompt in one fenced block; "executing every command as
    # printed" sits deep inside it and a later clause quotes the word "done".
    # The layer read that quotation as the claim's predicate and reported the
    # correct sentence as a defect.
    got, miss = quantifier_claims(
        "THE WALK: follow the route, executing every command as printed and "
        "verifying it names the step it belongs to; anything degraded at "
        "\"done\" is a finding.\n\n"
        "```\na\nb\n```\n")
    check("QUANT(mid-sentence): a universal buried mid-sentence is SKIPPED, "
          "not tested against a literal from some other clause",
          (got, [r.split(" - ")[0] for _, r in miss]),
          ([], ["does not open its sentence"]))

    got, miss = quantifier_claims("Every row states a verdict that is "
                                  "accurate:\n\n"
                                  "| a | b |\n|---|---|\n| 1 | 2 |\n")
    check("QUANT(no-literal): a predicate that needs judgment is not a "
          "literal, and is skipped rather than guessed at",
          (got, [r.split(" - ")[0] for _, r in miss]),
          ([], ["no literal predicate"]))

    got, miss = quantifier_claims(
        "Every row cites `BLUEPRINT.md`:\n\n| a |\n|---|\n| 1 |\n")
    check("QUANT(doc-ref): a backticked DOCUMENT NAME is a reference, not a "
          "predicate - the claim is skipped, not tested against a filename",
          (got, [r.split(" - ")[0] for _, r in miss]),
          ([], ["no literal predicate"]))

    two = ("Every row carries a `[FETCHED]` tag.\n\n"
           "| a | b |\n|---|---|\n| 1 | 2 |\n\n"
           "| c | d |\n|---|---|\n| 3 | 4 |\n")
    got, miss = quantifier_claims(two)
    check("QUANT(ambiguous): a document with TWO tables and no adjacency is "
          "skipped, never guessed at",
          (got, [r[-30:] for _, r in miss]),
          ([], ["the document holds exactly one"]))

    got, miss = quantifier_claims("Every reader carries their own priors, and "
                                  "no document names them all.\n")
    check("QUANT(no-target): a noun this tool cannot enumerate is skipped "
          "with the noun named",
          (len(got), len(miss)), (0, 2))

    got, miss = quantifier_claims("The runner never prints a bare count.\n")
    check("QUANT(absolute): `never` and `always` take no noun, decide "
          "nothing, and are recorded as skipped so they are visible",
          (got, [r[:22] for _, r in miss]),
          ([], ["an absolute with no no"]))

    got, miss = quantifier_claims("Every row in that table was written on a "
                                  "Tuesday.\n")
    check("QUANT(no-verb): a sentence with no presence verb decides nothing "
          "and is recorded as a skip - out of the denominator, visible in "
          "the skip list (r30 review)",
          (len(got), len(miss)), (0, 1))

    # THE STATE WORD ITSELF. The stranger's finding, held as a control: this
    # tool may not print CLEAN over a run that skipped anything.
    check("QUANT(state-word): a run that skipped nothing is CLEAN",
          coverage_state(18, 0), ("CLEAN", 100.0))
    st, pc = coverage_state(15, 754)
    check("QUANT(state-word): a run that located 15 of 769 is PARTIAL, and "
          "the percentage is printed rather than the word `clean`",
          (st, round(pc, 1)), ("PARTIAL", 2.0))

    print()
    print(f"{BOLD}=== D. this tool against the kit it ships in ==={RESET}")
    root = Path(__file__).resolve().parent.parent
    docs = kit_documents(root)
    check("the kit's own documents are found", len(docs) > 10, True)
    index = {}
    for p in docs:
        index.setdefault(p.name, p)

    def live(name):
        p = index.get(Path(name).name)
        return p.read_text(encoding="utf-8") if p else None

    total, qtotal, qseen = 0, 0, 0
    for d in docs:
        text = d.read_text(encoding="utf-8")
        total += len(claims(text, d.name, live)[0])
        qgot, qmiss = quantifier_claims(text)
        qtotal += len(qgot)
        qseen += len(qmiss)
    # A pattern that matches nothing is a check that proves nothing - the same
    # assertion the citation lint's section E makes about itself.
    check("...and the lint decides real claims in them", total > 0, True)
    check("the quantifier layer SEES universal claims in this kit's own "
          "documents (they reach the skip total rather than vanishing)",
          qseen > 0, True)
    # AND DECIDES AT LEAST ONE. A layer that locates a target for none of the
    # claims in the tree it ships in is a layer nobody has run in anger; the
    # front door carries one universal claim in checkable shape on purpose,
    # and this control is what stops that claim being quietly deleted.
    check("...and DECIDES at least one of them", qtotal > 0, True)

    print()
    print((GREEN if ok_all else RED)
          + f"COUNT-LINT SELFTEST: {'PASS' if ok_all else 'FAIL'} "
            f"— {n} checks" + RESET)
    return 0 if ok_all else 1


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Is the stated number the number? Checks counts of "
                    "enumerable things against the thing they name.",
        epilog="exit 0 clean · 1 a count disagrees · 2 abort")
    ap.add_argument("--root", default="", help="the tree to lint")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--list", action="store_true",
                    help="print every claim decided and every phrase skipped")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    root = Path(a.root).resolve() if a.root \
        else Path(__file__).resolve().parent.parent
    if not root.is_dir():
        print(f"{RED}COUNT LINT: ABORT — no such directory: {root}{RESET}")
        return 2
    return run(root, a.list)


if __name__ == "__main__":
    sys.exit(main())
