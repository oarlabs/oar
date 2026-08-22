#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
escape_rate.py - THE INSTRUMENT FOR THE HEADLINE METRIC.

    python escape_rate.py                      # read the default ledger
    python escape_rate.py --ledger <file.md>   # read another one
    python escape_rate.py --ceiling 35.0       # the latest round's ceiling
    python escape_rate.py --json               # the same numbers, machine-read:
                                               #   stdout is JSON AND NOTHING
                                               #   ELSE, human lines to stderr
    python escape_rate.py --selftest           # prove this tool's own judging

==========================================================================
WHY THIS FILE EXISTS
==========================================================================
The kit's central claim is that the loop publishes its own escape rate, and
that trust is therefore measured rather than asserted. Until this tool
existed, nothing in the kit computed that number - for an adopter or for the
kit itself. A headline metric with no instrument is a slogan, and the kit's
own doctrine says a rule enforced only by prose is a rule that stops existing
the first time somebody is busy.

So the number is computed from a table, the table lives in the ledger the
doctrine already requires, and the computation runs inside certification.

==========================================================================
WHAT AN ESCAPE IS
==========================================================================
An **escape** is an item a human reported that an existing check should have
caught. Not every defect is an escape: a defect on a surface no check covered
is a coverage gap, and the honest response to it is a new check, not a worse
number. The escape rate measures whether the checks you already own are
learning.

The rate is `escapes / items`, per round, and the number that matters is the
trend. A rate that does not fall across rounds means the loop is witnessing
rather than learning.

==========================================================================
THE DATA SHAPE, AND WHY IT IS A MARKDOWN TABLE
==========================================================================
One table, in the judgment ledger, read by this tool:

    | Round | Items | Escapes | Notes |
    |---|---|---|---|
    | r7 | 7 | 3 | ... |

The alternative considered and rejected was a separate `judgments.jsonl`. It
would parse more easily and it would be a SECOND AUTHORITY: the doctrine
already binds every round to append its rows to the markdown ledger in the
same commit as its checks, so a JSONL file would have to be written twice and
would drift from the prose the moment somebody edited one and not the other.
Two readers of one rule, drifting, is this kit's oldest and most-repeated
defect class - it is why `checks-registry.json` and `expectation_lint.py`
exist. One authority, parsed strictly, is the smaller risk.

Strictly is the operative word. Every malformed row is an ABORT that names the
row. Nothing is skipped, because a skipped row is a row that quietly leaves
the denominator, and a metric you can improve by writing a bad row is not a
metric.

That sentence was once stronger than the code. The table is the unbroken run
of rows under the separator, and the first version stopped reading at the
break - so a row detached by a blank line, a prose line or an HTML comment was
dropped from the denominator at exit 0. Measured in spec-side review: a hidden
9/10 round left a published 25.0% MEASURED. Everything outside the table body
is now scanned for round-shaped rows and finding one is an ABORT that names
the line. The predicate is narrow on purpose (`round_shaped()`), because it
runs over every other table in the ledger and a false positive would abort on
somebody's escape log.

==========================================================================
THE UNCOUNTABLE ROUND
==========================================================================
`-` in BOTH the Items and Escapes cells declares a round uncountable: the
record exists but per-item counts cannot be recovered from it. Such a round is
excluded from the denominator AND its exclusion is printed on every run, with
a count, so that dropping an inconvenient round is a visible act rather than a
quiet one. Half a declaration (`-` in one cell, a number in the other) is an
ABORT.

==========================================================================
THE EXIT-CODE CONTRACT
==========================================================================
    0  the number was computed; the latest counted round is at or under the
       ceiling - OR there are no rounds recorded yet, which is a true fact
       about a new project and is printed as its own state word.
    1  OVER CEILING - the latest counted round exceeds the ceiling.
    2  ABORT - no ledger, no table, two tables, or a malformed row.

WHY "no rounds recorded" IS EXIT 0 AND NOT RED. A project on its first day
genuinely has no rounds, and a gate that is red until the first round is a
gate people learn to skip. The honesty is carried by a MANDATORY STATE WORD in
the required line - `state MEASURED` or `state NO-ROUNDS-RECORDED` - so the
absence of data is published on every single certification instead of reading
like a good score. A tool that dropped the state word would fail the gate's
pattern, exactly the way a two-number hook-fixture line does.

THE RESIDUAL, STATED: this tool cannot tell you that a project has been
running for a year without recording a round. It can only make the state
visible on every run. Nothing here reads a clock.

==========================================================================
--selftest
==========================================================================
Sections A-E run the pure parsing and judging layer against synthetic ledgers,
including the forced-red cases: a missing file, a missing table, two tables, a
non-integer count, more escapes than items, a half-declared uncountable row, a
round row detached from the table body, and a round over the ceiling. A check
with no negative control controls nothing.

SECTION F IS THE ONE EXCEPTION TO THE PURE-LAYER RULE, and it is named rather
than smuggled in: it READS THE RUNNER'S SOURCE, because the defect it closes is
a disagreement between two files and no pure function of one file can see it.
The ceiling is written twice as an operative value - here as DEFAULT_CEILING
and in verify.py's `escapes` gate command - and section F requires them to
agree. If the runner is not reachable (this tool copied out of a kit checkout)
it says UNAVAILABLE out loud rather than passing in silence.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

GREEN, RED, YELLOW, BOLD, RESET = (
    "\033[32m", "\033[31m", "\033[33m", "\033[1m", "\033[0m")
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# The ledger this tool reads when nothing is passed. An adopting repo's
# LEDGERS_DIR is `docs` by default, and module 04's ledger keeps its shipped
# name. Override with --ledger; the verify gate always passes it explicitly so
# that the runner's startup assertion can prove the file exists before any
# gate runs.
DEFAULT_LEDGER = "docs/JUDGMENT-LEDGER.md"

# The default ceiling, in percent, on the LATEST counted round. Derived rather
# than adopted - see `KNOWN-ISSUES.md`, "The kit's own numbers", for the
# arithmetic behind 35.0 and the n behind it. An adopter's own ceiling comes
# from their own first rounds by the method in `TOKEN-LEDGER.md`; this value
# is a starting tripwire, not a target.
#
# THIS IS THE SECOND OF TWO AUTHORITIES, AND THEY ARE BOUND. The verify
# runner's `escapes` gate passes its own `--ceiling` literal, so the number is
# written in two files. Nothing related them until spec-side review measured
# the consequence: a drifted copy published `ceiling 90.0%` from the standalone
# command the documents tell an adopter to type, while the gate stayed green at
# 35.0 - two readers of one rule, disagreeing silently, which this file's own
# docstring calls the kit's oldest defect class. `--selftest` section F now
# reads the runner's source and requires the two to agree. Change one and the
# selftest goes red naming both files; there is no third copy (the CI step
# deliberately passes no `--ceiling` and takes this value).
DEFAULT_CEILING = 35.0

# Where section F looks for the runner, in order: beside this file (an adopter
# copies both into `tools/`), then the kit's own module layout. A tool copied
# out of any kit checkout finds neither, and section F says so out loud rather
# than passing in silence.
RUNNER_CANDIDATES = ("verify.py", "../03-verification/verify.py")

# The gate's ceiling literal, recovered from the runner's source. Anchored on
# the gate key so a `--ceiling` belonging to some future second gate cannot be
# read by mistake.
GATE_CEILING = re.compile(
    r'"escapes":\s*dict\(.*?"--ceiling",\s*"([0-9.]+)"', re.S)

# The uncountable declaration. One spelling, both cells, no synonyms - a
# metric with three ways to say "no data" is a metric with three ways to
# lose a round.
UNCOUNTABLE = "-"

# The table is found by its header row and by nothing else. `Notes` and any
# further columns are ignored by the parser and are for the reader.
HEADER_CELLS = ("round", "items", "escapes")


# ==========================================================================
# THE PURE LAYER
# Everything above the RUNNING LAYER banner is a pure function of its
# arguments: no filesystem, no clock, no subprocess. That is what makes
# --selftest possible, and keeping it that way is a maintenance rule.
# ==========================================================================

class LedgerError(Exception):
    """A malformed ledger. Carries the sentence printed to the operator."""


def split_row(line: str) -> list:
    """The cells of one markdown table row, outer pipes discarded."""
    s = line.strip()
    if not s.startswith("|"):
        return []
    parts = s.split("|")
    # A well-formed row is `| a | b |`, which splits to ['', ' a ', ' b ', ''].
    if len(parts) >= 2 and parts[-1].strip() == "":
        parts = parts[:-1]
    return [p.strip() for p in parts[1:]]


def is_separator(cells: list) -> bool:
    """`|---|---|` - the row markdown requires under a header."""
    return bool(cells) and all(
        re.fullmatch(r":?-{3,}:?", c or "") for c in cells)


def is_header(cells: list) -> bool:
    return (len(cells) >= 3
            and [c.lower() for c in cells[:3]] == list(HEADER_CELLS))


def parse_count(raw: str, field: str, where: str) -> int | None:
    """A count cell: a non-negative integer, or None for the uncountable mark.

    Bold and code markers are tolerated because a ledger is also read by
    people; nothing else is. `12 (approx)` is an ABORT, not a 12."""
    v = raw.strip().strip("*`").strip()
    if v == UNCOUNTABLE:
        return None
    if not re.fullmatch(r"\d+", v):
        raise LedgerError(
            f"{where}: the {field} cell is {raw.strip()!r}, which is neither a "
            f"non-negative integer nor the uncountable mark {UNCOUNTABLE!r}. A "
            f"count that cannot be read is not a count.")
    return int(v)


def parse_rounds(text: str) -> list:
    """[(label, items, escapes)] with (None, None) for an uncountable round.

    Raises LedgerError for: no table, more than one table, a header with no
    separator under it, an empty label, a half-declared uncountable row, more
    escapes than items."""
    lines = text.splitlines()
    starts = [i for i, ln in enumerate(lines) if is_header(split_row(ln))]
    if not starts:
        raise LedgerError(
            "no escape-rate table found. The ledger must carry exactly one "
            "table whose first three columns are "
            f"{' | '.join(c.capitalize() for c in HEADER_CELLS)}. A missing "
            "instrument must never read as a good score.")
    if len(starts) > 1:
        raise LedgerError(
            f"{len(starts)} escape-rate tables found (lines "
            f"{', '.join(str(i + 1) for i in starts)}). Two tables are two "
            "authorities, and the tool must not choose between them.")

    i = starts[0]
    if i + 1 >= len(lines) or not is_separator(split_row(lines[i + 1])):
        raise LedgerError(
            f"line {i + 2}: the escape-rate table's header row is not followed "
            "by a |---|---| separator, so it is not a table.")

    rounds = []
    end = i + 2          # one past the table body; header and separator are in
    for n in range(i + 2, len(lines)):
        cells = split_row(lines[n])
        if not cells:
            break
        where = f"line {n + 1}"
        if len(cells) < 3:
            raise LedgerError(
                f"{where}: the escape-rate table needs at least three cells "
                f"(Round, Items, Escapes); this row has {len(cells)}.")
        label = cells[0].strip().strip("*`").strip()
        if not label:
            raise LedgerError(f"{where}: the Round cell is empty.")
        items = parse_count(cells[1], "Items", where)
        escapes = parse_count(cells[2], "Escapes", where)
        if (items is None) != (escapes is None):
            raise LedgerError(
                f"{where}: round {label!r} declares one cell uncountable "
                f"({UNCOUNTABLE!r}) and gives a number for the other. An "
                "uncountable round is uncountable in both cells or it is a "
                "round with a missing number.")
        if items is not None and escapes > items:
            raise LedgerError(
                f"{where}: round {label!r} records {escapes} escapes out of "
                f"{items} items. An escape is one of the items.")
        rounds.append((label, items, escapes))
        end = n + 1

    # THE DETACHED ROW. The block above ends at the first line that is not a
    # pipe row, which makes the table the CONTIGUOUS run under the separator.
    # That definition has a hole this file's own docstring forbids: a round row
    # separated from the body by a blank line, a prose line or an HTML comment
    # is not counted, not aborted, and not mentioned - it quietly leaves the
    # denominator and the run stays green. Measured in spec-side review: a
    # hidden 9/10 round left a published 25.0% MEASURED at exit 0.
    #
    # An editor inserting a blank line before an appended row does this, and so
    # does moving the HTML comment that sits above the real table down one row.
    # So: everything outside the body is scanned for anything ROUND-SHAPED, and
    # finding one is an ABORT that names the line.
    #
    # THE FALSE-POSITIVE SURFACE, checked rather than assumed: a row is
    # round-shaped only when its first cell is a non-empty label AND cells 2
    # and 3 are BOTH counts or both the uncountable mark. No other table in the
    # shipped ledgers has integers in both of those cells - the escape log's
    # are `<item>`/`<check>`, the backlog's second is `<ruling>`, the
    # instances table's second is prose. Separator rows and short rows are not
    # round-shaped either.
    #
    # WHAT IT STILL CANNOT SEE, stated: a detached row that is itself
    # malformed in cell 2 or 3 (`| r9 | - | 2 |`) is not round-shaped, so it is
    # invisible here as well. That row is broken in both places at once; the
    # cheap general answer is the one this check gives for the common case.
    for n, line in enumerate(lines):
        if i <= n < end:
            continue
        cells = split_row(line)
        if not round_shaped(cells):
            continue
        raise LedgerError(
            f"line {n + 1}: {cells[0].strip()!r} is a round row OUTSIDE the "
            f"table body. The table is the unbroken run of rows under the "
            f"separator, so this row is counted by nobody - it would leave the "
            f"denominator silently. Move it into the table, or delete it. A "
            f"metric you can improve by writing a bad row is not a metric.")
    return rounds


def gate_ceiling(runner_src: str):
    """The `--ceiling` literal from the runner's `escapes` gate, or None.

    Pure: takes the source text. None means "this source has no escapes gate"
    - which is what an adopter who deleted the gate has, and is reported as
    UNAVAILABLE rather than silently passing."""
    m = GATE_CEILING.search(runner_src or "")
    return float(m.group(1)) if m else None


def round_shaped(cells: list) -> bool:
    """Is this row a round row? Used only to hunt rows OUTSIDE the table body.

    Deliberately narrow, and never raises: this predicate runs over every other
    table in the ledger, so a false positive would abort on somebody's escape
    log. Both count cells must read as counts (or both as the uncountable
    mark) before a row is claimed to be a round."""
    if len(cells) < 3 or is_separator(cells):
        return False
    if not cells[0].strip().strip("*`").strip():
        return False
    seen = []
    for raw in (cells[1], cells[2]):
        v = raw.strip().strip("*`").strip()
        if v == UNCOUNTABLE:
            seen.append(None)
        elif re.fullmatch(r"\d+", v):
            seen.append(int(v))
        else:
            return False
    return (seen[0] is None) == (seen[1] is None)


def pct(part: int, whole: int) -> float:
    """One decimal place, deterministic. 0/0 is 0.0 and the STATE WORD in the
    required line - not this number - is what says there was no data."""
    if whole <= 0:
        return 0.0
    # Round half away from zero rather than to even, so the published number
    # matches what a reader gets on a calculator.
    scaled = part * 1000.0 / whole
    return int(scaled + 0.5) / 10.0


def counted(rounds: list) -> list:
    return [r for r in rounds if r[1] is not None]


def trend(rates: list) -> str:
    """The direction of the last two counted rounds. Reported, never gated:
    at these sample sizes a single round moving up is noise, and a gate that
    reds on noise is a gate that gets skipped."""
    if len(rates) < 2:
        return "INSUFFICIENT-DATA"
    if rates[-1] < rates[-2]:
        return "FALLING"
    if rates[-1] > rates[-2]:
        return "RISING"
    return "FLAT"


def report(rounds: list, ceiling: float) -> dict:
    """Every published number, computed once, in one place."""
    cnt = counted(rounds)
    items = sum(r[1] for r in cnt)
    escapes = sum(r[2] for r in cnt)
    rates = [pct(r[2], r[1]) for r in cnt]
    latest_label, latest_items, latest_escapes = (
        cnt[-1] if cnt else ("none", 0, 0))
    return {
        "state": "MEASURED" if cnt else "NO-ROUNDS-RECORDED",
        "items": items,
        "escapes": escapes,
        "rate_pct": pct(escapes, items),
        "rounds_counted": len(cnt),
        "rounds_uncounted": len(rounds) - len(cnt),
        "uncounted_labels": [r[0] for r in rounds if r[1] is None],
        "latest_label": latest_label,
        "latest_items": latest_items,
        "latest_escapes": latest_escapes,
        "latest_pct": rates[-1] if rates else 0.0,
        "per_round": [{"round": r[0], "items": r[1], "escapes": r[2],
                       "pct": p} for r, p in zip(cnt, rates)],
        "trend": trend(rates),
        "ceiling_pct": round(float(ceiling), 1),
        "over_ceiling": bool(cnt and rates[-1] > round(float(ceiling), 1)),
    }


def required_line(rep: dict) -> str:
    """THE REQUIRED OUTPUT LINE. The verify gate judges this and nothing else.

    The `state` field is MANDATORY in the gate's pattern, so a future version
    that stopped distinguishing "no rounds yet" from "a measured zero" fails
    the gate instead of quietly publishing a flattering zero."""
    return (f"ESCAPE RATE: {rep['escapes']}/{rep['items']} items "
            f"({rep['rate_pct']:.1f}%) over {rep['rounds_counted']} rounds; "
            f"latest {rep['latest_escapes']}/{rep['latest_items']} "
            f"({rep['latest_pct']:.1f}%); "
            f"ceiling {rep['ceiling_pct']:.1f}%; state {rep['state']}")


def uncounted_line(rep: dict) -> str:
    """Always printed, including the zero. A field that only appears when it
    is interesting is a field whose absence nobody notices."""
    labels = (" — " + ", ".join(rep["uncounted_labels"])
              if rep["uncounted_labels"] else "")
    return (f"ESCAPE RATE UNCOUNTED: {rep['rounds_uncounted']} round(s) "
            f"declared uncountable and excluded from the denominator{labels}")


def trend_line(rep: dict) -> str:
    seq = " -> ".join(f"{r['pct']:.1f}" for r in rep["per_round"]) or "(none)"
    return (f"ESCAPE RATE TREND: {seq} (percent, oldest first); "
            f"direction {rep['trend']}")


def ceiling_line(rep: dict) -> str:
    return (f"ESCAPE RATE: OVER CEILING — latest round {rep['latest_label']} "
            f"{rep['latest_escapes']}/{rep['latest_items']} "
            f"({rep['latest_pct']:.1f}%) exceeds the "
            f"{rep['ceiling_pct']:.1f}% ceiling. The loop is not learning "
            f"faster than it is escaping: fix the checks, not the number.")


# ==========================================================================
# THE RUNNING LAYER
# ==========================================================================

def read_ledger(path: Path) -> str:
    """The ledger's text, read the ONE way this tool reads it.

    utf-8-sig, not utf-8: a Windows editor writes a BOM, and a BOM in front of
    the header row makes it stop looking like a table row - so the same ledger
    would parse on one host and ABORT on another. Found by the second-machine
    sweep, before it could be found by an adopter.

    It is a named function rather than a line inside `main()` because it now
    has a second caller: module 05's status board renders this tool's numbers
    and must not grow its own reader. One encoding rule, one place.

    Raises whatever the filesystem raises; each caller decides what a missing
    or unreadable ledger means for it."""
    return path.read_text(encoding="utf-8-sig")


def abort(msg: str) -> int:
    """Exit 2, with the token the verify gate vetoes on.

    stdout carries it because that is where the runner and the CI control read
    from. The stderr copy is for a run whose stdout is redirected somewhere
    nobody is watching - so it is written only when stdout is NOT a terminal,
    which keeps an interactive run from printing the same sentence twice."""
    line = f"ESCAPE LEDGER ABORT: {msg}"
    print(RED + line + RESET)
    try:
        interactive = sys.stdout.isatty()
    except Exception:
        interactive = False
    if not interactive:
        print(line, file=sys.stderr)
    return 2


def selftest() -> int:
    ok_all, n = True, 0

    def check(label, got, want):
        nonlocal ok_all, n
        n += 1
        good = got == want
        ok_all = ok_all and good
        print(f"  [{'PASS' if good else 'FAIL'}] {label}"
              + ("" if good else f"\n        got  {got!r}\n        want {want!r}"))

    def err(text):
        """The LedgerError message for a ledger, or '' if it parsed."""
        try:
            parse_rounds(text)
            return ""
        except LedgerError as e:
            return str(e)

    TBL = ("| Round | Items | Escapes | Notes |\n"
           "|---|---|---|---|\n")

    print(f"{BOLD}=== A. the FORCED-RED cases: a check with no negative "
          f"control controls nothing ==={RESET}")
    check("NC(i) a ledger with no table ABORTS, and says a missing "
          "instrument is not a good score",
          "must never read as a good score" in err("# a ledger\n\nno table\n"),
          True)
    check("NC(ii) TWO tables ABORT rather than the tool choosing an authority",
          "Two tables are two authorities" in err(TBL + "| r1 | 2 | 1 |\n\n"
                                                 + TBL + "| r1 | 2 | 0 |\n"),
          True)
    check("NC(iii) a header with no separator under it is not a table",
          "not followed by a |---|---| separator" in err(
              "| Round | Items | Escapes |\n| r1 | 2 | 1 |\n"), True)
    check("NC(iv) a non-integer count ABORTS and quotes the cell",
          "'12 (approx)'" in err(TBL + "| r1 | 12 (approx) | 1 |\n"), True)
    check("NC(v) more escapes than items ABORTS",
          "An escape is one of the items" in err(TBL + "| r1 | 3 | 4 |\n"),
          True)
    check("NC(vi) a HALF-declared uncountable row ABORTS - the quiet way to "
          "drop a round",
          "uncountable in both cells" in err(TBL + "| r1 | - | 2 |\n"), True)
    check("NC(vii) ...in the other direction too",
          "uncountable in both cells" in err(TBL + "| r1 | 5 | - |\n"), True)
    check("NC(viii) an empty Round label ABORTS",
          "the Round cell is empty" in err(TBL + "|  | 5 | 1 |\n"), True)
    check("NC(ix) a short row ABORTS rather than being skipped",
          "needs at least three cells" in err(TBL + "| r1 | 5 |\n"), True)
    check("NC(x) a negative count is not an integer here",
          "'-3'" in err(TBL + "| r1 | -3 | 0 |\n"), True)
    # NC(xiii) - THE DETACHED ROW, in all three shapes spec-side review
    # measured. Each one used to leave a 9/10 round out of the denominator at
    # exit 0, which is the one outcome this whole tool exists to prevent.
    for _shape, _sep in (("a blank line", ""),
                         ("a prose line", "a note to self"),
                         ("an HTML comment", "<!-- moved this -->")):
        check(f"NC(xiii) a round row detached by {_shape} ABORTS - it would "
              f"leave the denominator silently",
              "round row OUTSIDE the table body" in err(
                  TBL + "| r1 | 4 | 1 |\n" + _sep + "\n| r2 | 10 | 9 |\n"),
              True)
    check("NC(xiii) ...and the abort NAMES the detached row",
          "'r2'" in err(TBL + "| r1 | 4 | 1 |\n\n| r2 | 10 | 9 |\n"), True)
    check("NC(xiii) ...and a row ABOVE the header is caught too",
          "round row OUTSIDE the table body" in err(
              "| r0 | 5 | 5 |\n\n" + TBL + "| r1 | 4 | 1 |\n"), True)

    print(f"\n{BOLD}=== B. the parser ==={RESET}")
    # THE CONTROL FOR NC(xiii): the parser is otherwise strict, so the
    # difference between these two cases is the BREAK and not the row.
    check("CONTROL: a merely INDENTED row is still in the table body",
          parse_rounds(TBL + "| r1 | 4 | 1 |\n  | r2 | 10 | 9 |\n"),
          [("r1", 4, 1), ("r2", 10, 9)])
    check("CONTROL: the detached-row hunt does not fire on another table's "
          "rows - the escape log's cells are not counts",
          parse_rounds(TBL + "| r1 | 4 | 1 |\n\n| Round | Item | Check |\n"
                       "|---|---|---|\n| r1 | <item> | `<check>` |\n"),
          [("r1", 4, 1)])
    check("CONTROL: ...nor on a two-column table",
          parse_rounds(TBL + "| r1 | 4 | 1 |\n\n| Status | Meaning |\n"
                       "|---|---|\n| OK | fine |\n"), [("r1", 4, 1)])
    check("a well-formed table parses to its rows",
          parse_rounds(TBL + "| r7 | 7 | 3 | note |\n| r8 | 13 | 2 | n |\n"),
          [("r7", 7, 3), ("r8", 13, 2)])
    check("an uncountable round parses to None/None",
          parse_rounds(TBL + "| 1-6 | - | - | aggregated |\n"),
          [("1-6", None, None)])
    check("the table body ends at the first non-table line",
          parse_rounds(TBL + "| r1 | 2 | 1 |\n\n| Round | x |\n"),
          [("r1", 2, 1)])
    check("bold and code markers in a count are tolerated (a ledger is read "
          "by people too)",
          parse_rounds(TBL + "| r1 | **10** | `2` |\n"), [("r1", 10, 2)])
    check("a zero-row table is legal and empty",
          parse_rounds(TBL), [])
    check("column headers are matched case-insensitively",
          parse_rounds("| ROUND | items | Escapes |\n|---|---|---|\n"
                       "| r1 | 4 | 1 |\n"), [("r1", 4, 1)])
    check("extra columns beyond Notes are ignored, not an error",
          parse_rounds("| Round | Items | Escapes | Notes | Owner |\n"
                       "|---|---|---|---|---|\n| r1 | 4 | 1 | n | o |\n"),
          [("r1", 4, 1)])

    print(f"\n{BOLD}=== C. the arithmetic ==={RESET}")
    check("percentages round half away from zero, to one place",
          (pct(1, 3), pct(2, 3), pct(3, 7), pct(1, 8), pct(0, 5)),
          (33.3, 66.7, 42.9, 12.5, 0.0))
    check("0 of 0 is 0.0 - and the STATE WORD, not this number, is what says "
          "there was no data", pct(0, 0), 0.0)
    r = report(parse_rounds(TBL + "| 1-6 | - | - |\n| r7 | 7 | 3 |\n"
                            "| r8 | 13 | 2 |\n"), 35.0)
    check("uncountable rounds leave the denominator",
          (r["items"], r["escapes"], r["rounds_counted"]), (20, 5, 2))
    check("...and their exclusion is COUNTED and NAMED",
          (r["rounds_uncounted"], r["uncounted_labels"]), (1, ["1-6"]))
    check("the overall rate is escapes over items", r["rate_pct"], 25.0)
    check("the latest round is the last counted row",
          (r["latest_label"], r["latest_pct"]), ("r8", 15.4))
    check("the trend compares the last two counted rounds", r["trend"],
          "FALLING")
    check("one counted round cannot have a direction",
          report(parse_rounds(TBL + "| r1 | 4 | 1 |\n"), 35.0)["trend"],
          "INSUFFICIENT-DATA")
    check("a rise is reported as a rise, not smoothed away",
          report(parse_rounds(TBL + "| r1 | 10 | 1 |\n| r2 | 10 | 5 |\n"),
                 90.0)["trend"], "RISING")

    print(f"\n{BOLD}=== D. the ceiling, and its boundary ==={RESET}")
    over = report(parse_rounds(TBL + "| r1 | 8 | 5 |\n"), 35.0)
    check("NC(xi) a latest round OVER the ceiling is flagged",
          (over["latest_pct"], over["over_ceiling"]), (62.5, True))
    check("...and the OVER CEILING line names the round and both numbers",
          ("r1" in ceiling_line(over) and "62.5%" in ceiling_line(over)
           and "35.0%" in ceiling_line(over)), True)
    check("EXACTLY at the ceiling is not over it (the boundary, stated)",
          report(parse_rounds(TBL + "| r1 | 100 | 35 |\n"),
                 35.0)["over_ceiling"], False)
    check("a hair over is over",
          report(parse_rounds(TBL + "| r1 | 1000 | 351 |\n"),
                 35.0)["over_ceiling"], True)
    check("the ceiling is judged on the LATEST round, not the overall rate - "
          "an old bad round must not red every future run",
          report(parse_rounds(TBL + "| r1 | 4 | 4 |\n| r2 | 10 | 0 |\n"),
                 35.0)["over_ceiling"], False)
    check("no rounds at all cannot breach a ceiling",
          report(parse_rounds(TBL), 35.0)["over_ceiling"], False)

    print(f"\n{BOLD}=== E. the required line - the gate judges this and "
          f"nothing else ==={RESET}")
    rep = report(parse_rounds(TBL + "| 1-6 | - | - |\n| r7 | 7 | 3 |\n"
                              "| r8 | 13 | 2 |\n"), 35.0)
    check("the required line is exact",
          required_line(rep),
          "ESCAPE RATE: 5/20 items (25.0%) over 2 rounds; latest 2/13 "
          "(15.4%); ceiling 35.0%; state MEASURED")
    empty = report([], 35.0)
    check("an empty ledger says NO-ROUNDS-RECORDED in the state field",
          required_line(empty),
          "ESCAPE RATE: 0/0 items (0.0%) over 0 rounds; latest 0/0 (0.0%); "
          "ceiling 35.0%; state NO-ROUNDS-RECORDED")
    # THE CONTRACT WITH THE RUNNER, transcribed by hand. This pattern is the
    # SPECIFICATION of the line, written here as an inline literal; the verify
    # runner carries its own hand-written copy in its `escapes` gate. Two
    # independent transcriptions of one contract are deliberate - if they
    # drift, the live gate goes red in CI rather than both moving together.
    GATE_PATTERN = (
        r"ESCAPE RATE:\s*(\d+)/(\d+)\s+items\s+\((\d+\.\d)%\)\s+over\s+"
        r"(\d+)\s+rounds;\s+latest\s+(\d+)/(\d+)\s+\((\d+\.\d)%\);\s+"
        r"ceiling\s+(\d+\.\d)%;\s+state\s+(MEASURED|NO-ROUNDS-RECORDED)")
    check("the measured line matches the gate's pattern",
          bool(re.search(GATE_PATTERN, required_line(rep))), True)
    check("...and so does the no-rounds line",
          bool(re.search(GATE_PATTERN, required_line(empty))), True)
    check("NC(xii) a line that DROPPED the state word fails the pattern - the "
          "distinction cannot be lost quietly",
          bool(re.search(GATE_PATTERN,
                         required_line(rep).split("; state")[0])), False)
    check("the uncounted line is printed even when it is zero",
          uncounted_line(empty).startswith("ESCAPE RATE UNCOUNTED: 0 round(s)"),
          True)
    check("...and names the rounds it excluded when there are any",
          "1-6" in uncounted_line(rep), True)
    check("the trend line carries the whole sequence, oldest first",
          trend_line(rep),
          "ESCAPE RATE TREND: 42.9 -> 15.4 (percent, oldest first); "
          "direction FALLING")

    # ==================================================================
    print(f"\n{BOLD}=== F. THE CEILING'S TWO AUTHORITIES, BOUND ==={RESET}")
    # THE ONE SECTION OF THIS SELFTEST THAT TOUCHES THE FILESYSTEM, and it is
    # named rather than smuggled in: every check above is a pure function of
    # its arguments, and this one reads the runner's source. It has to, because
    # the defect it closes is a disagreement BETWEEN TWO FILES, and no pure
    # function of one file can see it.
    #
    # THE DEFECT, measured in spec-side review: `35.0` was written twice as an
    # operative value - the gate command in verify.py and DEFAULT_CEILING here
    # - and nothing compared them. A copy of the tool with DEFAULT_CEILING at
    # 90.0 published `ceiling 90.0%` from the standalone command the documents
    # tell an adopter to type, while the same tool through the gate published
    # 35.0. Both runs green. An adopter who raises the gate ceiling on the
    # reviewed-commit path leaves every hand run reporting the old number.
    #
    # NOT self-referential: this reads a DIFFERENT file and requires agreement,
    # the same shape as the fixture/registry and doctor/registry cross-checks.
    _here = Path(__file__).resolve().parent
    _runner = next((p for p in (_here / c for c in RUNNER_CANDIDATES)
                    if p.is_file()), None)
    check("the pure-layer checks above ran without touching a filesystem, and "
          "this section is the declared exception", True, True)
    if _runner is None:
        # STATED, NOT SKIPPED IN SILENCE. A tool copied out of a kit checkout
        # cannot find the runner, and a check that quietly passes in that case
        # is worse than one that says it could not look.
        check("the runner is NOT reachable from here, so the ceiling "
              "cross-check is UNAVAILABLE - said out loud, not passed in "
              "silence (looked in: "
              + ", ".join(RUNNER_CANDIDATES) + ")", True, True)
    else:
        _src = _runner.read_text(encoding="utf-8")
        _gate = gate_ceiling(_src)
        check("the runner's escapes gate is found and its --ceiling literal "
              f"is recoverable ({_runner.name})", _gate is not None, True)
        check("THE BINDING: the gate's ceiling and DEFAULT_CEILING agree - "
              f"gate {_gate}, tool {DEFAULT_CEILING}. Change one without the "
              f"other and this is the red.",
              _gate, DEFAULT_CEILING)
    # NC(xiv) - the forced red for the binding, on synthetic source so it runs
    # identically whether or not the runner was reachable above.
    _fake = ('    "escapes": dict(\n        cmd=[sys.executable, ESCAPE_TOOL,\n'
             '             "--ledger", ESCAPE_LEDGER, "--ceiling", "90.0"],\n')
    check("NC(xiv) a DRIFTED gate ceiling is recovered as the other number, "
          "so the binding above goes red instead of both copies moving "
          "together", gate_ceiling(_fake), 90.0)
    check("NC(xiv) ...and it does NOT equal DEFAULT_CEILING, which is what "
          "makes the binding a real assertion",
          gate_ceiling(_fake) == DEFAULT_CEILING, False)
    check("NC(xiv) a runner with the escapes gate DELETED reports None, not a "
          "number - an adopter who removed the gate is UNAVAILABLE, not green",
          gate_ceiling('    "hooks": dict(cmd=[], timeout=180)\n'), None)
    check("the pattern is anchored on the escapes gate, so a --ceiling "
          "belonging to some other gate is not read by mistake",
          gate_ceiling('    "other": dict(cmd=["--ceiling", "12.5"])\n'), None)

    print()
    print((GREEN if ok_all else RED)
          + f"ESCAPE RATE SELFTEST: {'PASS' if ok_all else 'FAIL'} "
            f"— {n} checks" + RESET)
    return 0 if ok_all else 1


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Compute and publish the escape rate from a ledger table.")
    ap.add_argument("--ledger", default=DEFAULT_LEDGER)
    ap.add_argument("--ceiling", type=float, default=DEFAULT_CEILING)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    if a.ceiling < 0 or a.ceiling > 100:
        return abort(f"--ceiling {a.ceiling} is not a percentage.")

    path = Path(a.ledger)
    try:
        # One reader, defined once - see read_ledger() for the BOM rule and
        # why it is a function.
        text = read_ledger(path)
    except FileNotFoundError:
        return abort(f"no ledger at {path.as_posix()}. The escape rate cannot "
                     f"be computed, and an uncomputed metric must not report "
                     f"a number.")
    except OSError as e:
        return abort(f"{path.as_posix()} could not be read: {e}")

    try:
        rounds = parse_rounds(text)
    except LedgerError as e:
        return abort(f"{path.as_posix()}: {e}")

    rep = report(rounds, a.ceiling)

    # UNDER --json, STDOUT IS JSON AND NOTHING ELSE. It used to carry the JSON
    # document followed by the four human lines on the same stream, so the
    # documented `--json` output did not parse - `json.load(sys.stdin)` failed
    # with "Extra data". A flag that says machine-read has to be machine-read.
    # The human lines still go somewhere (stderr), so an interactive `--json`
    # run reads the same as it did; only the pipe changed.
    out = sys.stderr if a.json else sys.stdout
    if a.json:
        print(json.dumps(rep, indent=2, sort_keys=True))

    print(f"ledger    : {path.as_posix()}", file=out)
    print(uncounted_line(rep), file=out)
    print(trend_line(rep), file=out)
    if rep["state"] == "NO-ROUNDS-RECORDED":
        print(YELLOW + "ESCAPE RATE: no rounds recorded in this ledger yet. "
              "This is the true state of a new project and it is printed on "
              "every run; it is not a score." + RESET, file=out)
    if rep["over_ceiling"]:
        print(RED + ceiling_line(rep) + RESET, file=out)
        print(required_line(rep), file=out)
        return 1
    print(GREEN + required_line(rep) + RESET, file=out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
