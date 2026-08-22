#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
gate_line.py - produce and validate the ONE line `verify.py` judges a gate by.

    python tools/gate_line.py --pytest                    # run this project's
                                                          # pytest suite, print
                                                          # the line, exit 0/1
    python tools/gate_line.py --pytest --expect-skips 4
    python tools/gate_line.py --pytest --path tests -k parser
    python tools/gate_line.py --emit --passed 46 --failed 0 --skipped 4 \
                              --errored 0 --collected 50
    python tools/gate_line.py --validate -                # judge a line on stdin
    python tools/gate_line.py --gate-spec --floor 40      # the GATES entry to paste
    python tools/gate_line.py --selftest

    exit 0  GREEN - the required line was printed and nothing vetoed it
    exit 1  RED   - a veto line was printed; the required line is still there
    exit 2  ABORT - the runner could not be started at all

COPY THIS FILE into your project as `tools/gate_line.py` and put it in
`JUDGE_PATHS`. It decides what green means, so an uncommitted change to it must
invalidate certification the same way an uncommitted change to `kit.config`
does. `GATE-LINE.md` beside this file is the page; this docstring is the
contract.

==========================================================================
WHY THIS FILE EXISTS
==========================================================================
`verify.py` judges a gate by grepping ONE required line out of a command's
stdout. Real test runners do not print that line. `python -m pytest -q` prints:

    46 passed, 4 skipped in 0.06s

which carries no denominator. A run that collected three tests prints
`3 passed`, and that is indistinguishable in shape from a healthy run of a
three-test suite. **A gate pointed straight at pytest certifies a suite that
has stopped running** - the silent-green class this whole kit exists to
prevent. Nothing in the kit said so until a measured adoption walk hit it and
had to author the adapter from scratch (finding P3W-6). This is that adapter,
generalised, with the walk's design decisions kept and its reasoning stated.

==========================================================================
THE SHAPE CONTRACT
==========================================================================
Stated in `examples/fake_suite.py` and implemented here:

  * ONE summary line with the count IN it, as a SELF-CONSISTENT RATIO, so the
    gate's `(\d+)/\1` asserts "all of them" rather than "some of them";
  * a distinct FAILURE line the veto pattern matches, so a red run is red for
    a stated reason rather than by the absence of a line;
  * an honesty suffix when the run was a SUBSET.

THE LINE:

    unit_suite: 46/46 tests passed, 4 skipped, 0 errors

The denominator is SELECTED-AND-NOT-SKIPPED, not collected, so the ratio can
be self-consistent while tests legitimately skip. The skip count is a field of
its own so the gate table's `ceilings` can bound it.

THE VETO VOCABULARY, every line matched by `fail_pattern`:

    unit_suite: THESE FAILED: <nodeid>[, <nodeid>...]
    unit_suite: THESE ERRORED: <nodeid>[, <nodeid>...]
    unit_suite: SKIP SET CHANGED: expected 4, got 3
    unit_suite: COLLAPSED COLLECTION: 0 tests collected - the suite did not run
    unit_suite: NOTHING RAN: 0 of 50 collected tests were selected
    unit_suite: 46/46 tests passed, 4 skipped, 0 errors (subset: 46 of 50)

==========================================================================
THE COLLAPSE RULE, AND WHY THE VETO LINE CARRIES IT
==========================================================================
A collapsed collection produces `0/0 tests passed, 0 skipped, 0 errors`, and
`(\d+)/\1` MATCHES THAT. The required line alone cannot refuse it. Three
independent things refuse it instead, and the kit's own history says one would
not be enough:

  1. this payload prints `COLLAPSED COLLECTION` or `NOTHING RAN`, which
     `fail_pattern` vetoes, and it prints it BEFORE the required line;
  2. `expect_min` in the gate table is a floor on the first capture group, so
     a shrunken-but-nonzero collection is caught as well as a zero one;
  3. `emit()` returns green=False for any zero-selected run, so this file's own
     exit code is 1 even if a caller ignores both of the above.

`--selftest` proves all three, and proves the second direction too: that no
combination of counts with `collected == 0` can produce a green verdict.

==========================================================================
WHAT IS PROVEN, AND WHAT IS NOT
==========================================================================
**pytest is PROVEN.** Six golden fixtures in `examples/pytest_suites/` are run
for real by `--capture-golden`, and what pytest actually reported is stored in
`examples/pytest-golden.json`. `--selftest` replays them.

**EVERY OTHER RUNNER IS UNPROVEN.** unittest, jest, go test, cargo test, ctest
and the rest have no fixture in this kit, no captured output, and no adapter
here. `--emit` will build a correctly shaped line from counts you supply for
any runner, and it prints an UNPROVEN notice when you name one, because a
shape this file has never seen a real run of is a shape nobody has checked.
Building the second proven adapter means adding fixtures beside the pytest
ones and capturing them the same way; the word UNPROVEN is not a formality
here, it is the kit's own labelling rule applied to itself.

==========================================================================
NEGATIVE CONTROLS GO THROUGH THE RUNNER
==========================================================================
Do not edit a test to watch this gate go red. `python tools/verify.py --nc`
doctors the gate's own pattern and needs no file in your repository changed -
ORACLE-WORKSHEET Part 3, law 1.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

HERE = Path(__file__).resolve().parent

# THIS TOOL RUNS INSIDE A CERTIFICATION, over the tree being certified. Left on,
# importing a test module writes `__pycache__/` beside it, and on an adopting
# repository whose ignore file has no `__pycache__` rule those are untracked
# directories inside the judged surface - so the gate would report the residue
# it created as the adopter's dirty tree. `kit_doctor.py` carries the same line
# for the same measured reason (KNOWN-ISSUES, round 17, R17-7).
sys.dont_write_bytecode = True

GREEN, RED, YELLOW, BOLD, RESET = (
    "\033[32m", "\033[31m", "\033[33m", "\033[1m", "\033[0m")
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

DEFAULT_GATE = "unit_suite"

# The one runner this file has real captured output for. Everything else is
# UNPROVEN and says so - see the docstring.
PROVEN_RUNNERS = ("pytest",)

# Where the golden fixtures live, relative to this file. Two candidates: the
# kit's module layout, and beside this file in an adopting project that copied
# the fixtures too (most do not, and --selftest says so rather than passing).
GOLDEN_CANDIDATES = ("examples/pytest-golden.json", "pytest-golden.json")
SUITES_CANDIDATES = ("examples/pytest_suites", "pytest_suites")


# ==========================================================================
# THE PURE LAYER - counts in, lines out. No filesystem, no pytest, no clock.
# ==========================================================================
class Counts(NamedTuple):
    """What a runner reported. `collected` is POST-deselection, matching
    pytest's own hook, so a subset run's true denominator is
    collected + deselected."""
    collected: int = 0
    deselected: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errored: int = 0
    failed_ids: tuple = ()
    errored_ids: tuple = ()


def selected(c: Counts) -> int:
    """Tests that actually RAN to a verdict. Skips did not run, so they are
    not in the denominator; that is what lets the ratio stay self-consistent
    while a suite legitimately skips."""
    return c.passed + c.failed + c.errored


def emit(c: Counts, gate: str = DEFAULT_GATE, expect_skips=None):
    """(lines, green). PURE, and it is the whole judgement.

    Veto lines first, the required line last and ALWAYS - a red run that
    printed no required line would be indistinguishable from a run that
    crashed before reaching this code, and the gate would then be red for the
    wrong reason.

    `expect_skips` is the exact skip count you are willing to certify, or None
    for "do not assert on skips". It exists because the gate table cannot say
    it: `expect_min` is one floor bound to one capture group and `ceilings` are
    maxima, so a ceiling catches a NEW skip and lets a VANISHED one through. A
    skip that quietly turned into a pass is a change to what the suite proves,
    and moving this number is the explicit act that records it."""
    lines, green = [], True

    if c.failed:
        ids = ", ".join(sorted(c.failed_ids)) or f"{c.failed} test(s)"
        lines.append(f"{gate}: THESE FAILED: {ids}")
        green = False
    if c.errored:
        ids = ", ".join(sorted(c.errored_ids)) or f"{c.errored} test(s)"
        lines.append(f"{gate}: THESE ERRORED: {ids}")
        green = False

    # THE COLLAPSE RULE. Both spellings, because they are different accidents
    # with different first questions: nothing was collected at all (a renamed
    # directory, a broken conftest, a changed testpaths), or plenty was
    # collected and none of it ran (an over-eager -k, a marker expression, a
    # collection error that deselected everything).
    if c.collected <= 0:
        lines.append(f"{gate}: COLLAPSED COLLECTION: 0 tests collected - the "
                     f"suite did not run")
        green = False
    elif selected(c) <= 0:
        lines.append(f"{gate}: NOTHING RAN: 0 of {c.collected + c.deselected} "
                     f"collected tests were selected")
        green = False

    if expect_skips is not None and c.skipped != expect_skips:
        lines.append(f"{gate}: SKIP SET CHANGED: expected {expect_skips}, got "
                     f"{c.skipped}")
        green = False

    suffix = ""
    if c.deselected:
        suffix = f" (subset: {c.collected} of {c.collected + c.deselected})"
        green = False

    lines.append(f"{gate}: {c.passed}/{selected(c)} tests passed, "
                 f"{c.skipped} skipped, {c.errored} errors{suffix}")
    return lines, green


def require_pattern(gate: str = DEFAULT_GATE) -> str:
    """The gate table's `require`. `(\\d+)/\\1` is the self-consistency
    assertion; the skip and error fields are MANDATORY so a future payload
    that quietly drops one fails this gate instead of losing a distinction."""
    g = re.escape(gate)
    return (rf"{g}:\s*(\d+)/\1\s+tests passed,\s*(\d+)\s+skipped,"
            rf"\s*(\d+)\s+errors")


def fail_pattern(gate: str = DEFAULT_GATE) -> str:
    """The gate table's `fail_pattern`. Every veto line in the vocabulary, plus
    the subset suffix - a partial run may not certify."""
    g = re.escape(gate)
    return (rf"{g}:\s*(THESE FAILED|THESE ERRORED|SKIP SET CHANGED|"
            rf"COLLAPSED COLLECTION|NOTHING RAN)|\(subset:")


def validate(text: str, gate: str = DEFAULT_GATE) -> dict:
    """Judge a candidate payload's stdout the way `verify.py` would.

    Returns {required_line, ratio_ok, vetoed, veto_hits, green, why}. This is
    the half that answers the question the walk had to answer by hand: is what
    my runner prints a required line at all? Point it at `pytest -q` output and
    it says no, and says why."""
    req = re.search(require_pattern(gate), text or "")
    veto = [m.group(0) for m in re.finditer(fail_pattern(gate), text or "")]
    why = []
    if not req:
        why.append("no line matches the required pattern: a gate needs one "
                   "summary line carrying a self-consistent ratio (N/N), a "
                   "skip count and an error count, all in one line")
    if veto:
        why.append(f"vetoed by {len(veto)} failure line(s): "
                   + "; ".join(sorted(set(veto))[:4]))
    return {
        "required_line": req.group(0) if req else None,
        "ratio_ok": bool(req),
        "vetoed": bool(veto),
        "veto_hits": veto,
        "green": bool(req) and not veto,
        "why": why,
    }


def gate_spec(gate: str = DEFAULT_GATE, floor: int = 1, max_skips: int = 0,
              payload: str = "tools/gate_line.py") -> str:
    """The GATES entry to paste into `verify.py`, built from THIS file's own
    patterns so the two cannot drift apart. `--selftest` section D proves the
    patterns in the printed spec are the ones `emit()` actually satisfies."""
    return f'''    "{gate}": dict(
        cmd=[sys.executable, "{payload}", "--pytest",
             "--gate", "{gate}", "--expect-skips", "{max_skips}"],
        timeout=600,
        require=r"{require_pattern(gate)}",
        fail_pattern=r"{fail_pattern(gate)}",
        expect_min={floor}, min_group=1, min_label="tests",
        ceilings=[(2, {max_skips}, "skipped tests")],
        head=lambda m: f"{{m.group(1)}}/{{m.group(1)}}",
        doc="this project's {gate.replace('_', ' ')} passes, whole",
    ),'''


# ==========================================================================
# THE PYTEST ADAPTER - the one runner this file has real captured output for
# ==========================================================================
class Recorder:
    """A pytest plugin that recovers the counts pytest's own summary line
    throws away. Registered in-process, so it reads pytest's verdicts rather
    than parsing pytest's prose - a terminal summary is a human artifact and
    its wording is not a contract."""

    def __init__(self) -> None:
        self.collected = 0
        self.deselected = 0
        self.passed: list = []
        self.failed: list = []
        self.skipped: list = []
        self.errored: list = []

    # fires once, AFTER collection and AFTER every deselection hook has run.
    # `pytest_collection_modifyitems` looks like the natural place and is not:
    # `-k` deselects from inside a modifyitems hook of its own, so whether a
    # plugin sees the list before or after that depends on hook ordering. The
    # first version of this file used it and reported `collected` = 4 with
    # `deselected` = 2 on a 4-test suite, making the subset denominator 6.
    def pytest_collection_finish(self, session) -> None:
        self.collected = len(session.items)

    # fires for each deselected batch (-k, -m, deselect marks)
    def pytest_deselected(self, items) -> None:
        self.deselected += len(items)

    # fires three times per test: setup, call, teardown
    def pytest_runtest_logreport(self, report) -> None:
        nodeid = report.nodeid
        if report.when == "call":
            if report.passed:
                self.passed.append(nodeid)
            elif report.failed:
                self.failed.append(nodeid)
            elif report.skipped:
                # skipif evaluated inside the test body
                if nodeid not in self.skipped:
                    self.skipped.append(nodeid)
        else:
            if report.skipped and nodeid not in self.skipped:
                self.skipped.append(nodeid)
            elif report.failed and nodeid not in self.errored:
                self.errored.append(nodeid)

    def counts(self) -> Counts:
        return Counts(collected=self.collected, deselected=self.deselected,
                      passed=len(self.passed), failed=len(self.failed),
                      skipped=len(self.skipped), errored=len(self.errored),
                      failed_ids=tuple(self.failed),
                      errored_ids=tuple(self.errored))


@contextlib.contextmanager
def in_dir(path):
    """Run pytest with the fixture root as the working directory.

    NOT COSMETIC. A test's nodeid is spelled relative to pytest's invocation
    directory, and the nodeid is printed in the THESE FAILED / THESE ERRORED
    lines that the golden fixtures store. Captured from an absolute path, the
    fixtures would carry one machine's directory layout and the selftest would
    fail everywhere else."""
    old = os.getcwd()
    os.chdir(str(path))
    try:
        yield
    finally:
        os.chdir(old)


def run_pytest(extra_args: list, quiet: bool = False):
    """(Counts, None) or (None, abort_reason). Never raises for a missing
    pytest: a loud abort beats a silent drop (ORACLE-WORKSHEET Part 3, law 4),
    and no required line is printed, so the gate reds on absence as well."""
    try:
        import pytest  # noqa: F401
    except ImportError:
        return None, (f"pytest is not installed in this interpreter "
                      f"({sys.executable})")
    rec = Recorder()
    # -p no:cacheprovider keeps .pytest_cache out of the tree: the runner
    # judges a git-clean surface, and a cache directory is noise on it.
    argv = ["-q", "-p", "no:cacheprovider"] + list(extra_args)
    sink = io.StringIO()
    try:
        with contextlib.redirect_stdout(sink if quiet else sys.stdout), \
                contextlib.redirect_stderr(sink if quiet else sys.stderr):
            pytest.main(argv, plugins=[rec])
    except Exception as e:                                # pragma: no cover
        return None, f"pytest raised {type(e).__name__}: {e}"
    return rec.counts(), None


# ==========================================================================
# GOLDEN FIXTURES - real pytest output, captured, committed, replayed
# ==========================================================================
# Each case names a suite directory, the pytest arguments used, the counts
# pytest reported, the lines emit() built from them, and pytest's OWN `-q`
# summary line with its duration normalised. That last field is not decoration:
# it is the negative control for the whole file. It is what a gate pointed
# straight at pytest would have to judge, and --selftest requires validate()
# to REFUSE it.
GOLDEN_CASES = (
    ("all-pass", "all_pass", ()),
    ("pass-with-skips", "with_skips", ()),
    ("failures", "failures", ()),
    ("errors", "errors", ()),
    ("collapsed-collection", "collapsed", ()),
    ("subset", "subset", ("-k", "parser")),
)

# THE ROLL-CALL, written out in the form `tools/expectation_lint.py` recovers
# ids from. The selftest labels these cases with an f-string, which is right for
# a reader and unreadable to a lint that scans source text, so the literal list
# lives here - and section A binds it to GOLDEN_CASES, so the two cannot drift.
# Every id below has a `golden:` row in checks-registry.json and the lint
# cross-checks that list BOTH ways.
GOLDEN_ROLL_CALL = ("GOLDEN(all-pass) GOLDEN(pass-with-skips) "
                    "GOLDEN(failures) GOLDEN(errors) "
                    "GOLDEN(collapsed-collection) GOLDEN(subset)")

DURATION = re.compile(r"\bin\s+\d+\.\d+s\b")
ROLL_CALL_ID = re.compile(r"GOLDEN\(([a-z0-9-]+)\)")


def find_beside(candidates) -> Path:
    for rel in candidates:
        p = HERE / rel
        if p.exists():
            return p
    return HERE / candidates[0]


def load_golden():
    """(cases, source_path, note). `note` is non-empty when the fixtures are
    not here - an adopting project usually copies the tool and not the
    fixtures, and --selftest says which half it could run."""
    p = find_beside(GOLDEN_CANDIDATES)
    if not p.is_file():
        return [], p, (f"no golden fixtures at {p} - this file was copied out "
                       f"of a kit checkout without examples/. The pure layer "
                       f"is still proven below; the captured-pytest half is "
                       f"NOT.")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return [], p, f"{p} is not readable as golden fixtures: {e}"
    return data.get("cases", []), p, ""


def capture_golden() -> int:
    """Run all six fixture suites for real and write what pytest reported.

    This is the ONLY writer of pytest-golden.json. Regenerating it is a
    reviewed commit on a judged path: the fixtures are the expectation the
    selftest reads, so quietly recapturing them over a defect would make the
    defect the new expectation."""
    suites = find_beside(SUITES_CANDIDATES)
    if not suites.is_dir():
        print(f"{RED}CAPTURE ABORT: no fixture suites at {suites}{RESET}",
              file=sys.stderr)
        return 2
    try:
        import pytest  # noqa: F401
    except ImportError:
        print(f"{RED}CAPTURE ABORT: pytest is not installed in this "
              f"interpreter ({sys.executable}). These fixtures are captured "
              f"from real pytest runs; there is nothing to capture without "
              f"one.{RESET}", file=sys.stderr)
        return 2

    import pytest as _pt
    out = {
        "_comment": [
            "GOLDEN FIXTURES - real pytest output, captured by",
            "`gate_line.py --capture-golden`, replayed by `--selftest`.",
            "",
            "`raw_summary` is pytest's OWN -q summary line with its duration",
            "normalised to <t>. It is the negative control: a gate pointed",
            "straight at pytest would have to judge that line, and the",
            "selftest requires validate() to refuse it.",
            "",
            "Regenerating this file is a reviewed commit. It is the",
            "expectation the selftest reads, so recapturing over a defect",
            "would install the defect as the new expectation.",
        ],
        "pytest_version": _pt.__version__,
        "python": f"{sys.version_info.major}.{sys.version_info.minor}",
        "cases": [],
    }
    for cid, sub, args in GOLDEN_CASES:
        with in_dir(suites):
            counts, abort = run_pytest([sub] + list(args), quiet=True)
        if abort:
            print(f"{RED}CAPTURE ABORT on {cid}: {abort}{RESET}",
                  file=sys.stderr)
            return 2
        # -B for the same reason the module sets dont_write_bytecode: this
        # subprocess runs inside the judged surface and must leave nothing in
        # it. Without it, six __pycache__ directories appear beside the
        # fixtures on every capture.
        proc = subprocess.run(
            [sys.executable, "-B", "-m", "pytest", "-q", "-p",
             "no:cacheprovider", sub] + list(args),
            capture_output=True, text=True, cwd=str(suites))
        tail = [l.strip() for l in proc.stdout.splitlines() if l.strip()]
        raw = DURATION.sub("in <t>s", tail[-1]) if tail else ""
        lines, green = emit(counts, DEFAULT_GATE)
        out["cases"].append({
            "id": cid,
            "suite": sub,
            "pytest_args": list(args),
            "counts": {k: v for k, v in counts._asdict().items()
                       if not k.endswith("_ids")},
            "failed_ids": list(counts.failed_ids),
            "errored_ids": list(counts.errored_ids),
            "lines": lines,
            "green": green,
            "raw_summary": raw,
            "raw_exit": proc.returncode,
        })
        print(f"  captured {cid:<22} {counts.passed}/{selected(counts)} "
              f"passed, {counts.skipped} skipped, {counts.errored} errors "
              f"-> green={green}")
    dest = find_beside(GOLDEN_CANDIDATES)
    dest.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"{GREEN}GOLDEN CAPTURE: {len(out['cases'])} case(s) written to "
          f"{dest}{RESET}")
    return 0


# ==========================================================================
# --selftest
# ==========================================================================
def selftest() -> int:
    ok_all, n = True, 0

    def check(label, got, want):
        nonlocal ok_all, n
        n += 1
        good = got == want
        ok_all = ok_all and good
        print(f"  [{'PASS' if good else 'FAIL'}] {label}"
              + ("" if good else
                 f"\n        got  {got!r}\n        want {want!r}"))

    cases, src, note = load_golden()
    by_id = {c["id"]: c for c in cases}

    print(f"{BOLD}=== A. the golden fixtures: real pytest output, replayed "
          f"==={RESET}")
    print(f"  source: {src}")
    if note:
        print(f"  {YELLOW}NARROWED: {note}{RESET}")
    check("every case this file declares is in the golden fixtures",
          sorted(by_id), sorted(c[0] for c in GOLDEN_CASES))
    check("...and the roll-call the expectation lint reads names the same set "
          "(a case dropped from one and not the other is invisible to it)",
          sorted(ROLL_CALL_ID.findall(GOLDEN_ROLL_CALL)),
          sorted(c[0] for c in GOLDEN_CASES))
    for cid, _, _ in GOLDEN_CASES:
        case = by_id.get(cid)
        if not case:
            check(f"GOLDEN({cid}) present", False, True)
            continue
        c = Counts(**case["counts"],
                   failed_ids=tuple(case.get("failed_ids", ())),
                   errored_ids=tuple(case.get("errored_ids", ())))
        lines, green = emit(c, DEFAULT_GATE)
        check(f"GOLDEN({cid}) the pure layer rebuilds the captured lines "
              f"exactly", lines, case["lines"])
        check(f"GOLDEN({cid}) ...and the captured verdict", green,
              case["green"])
        text = "\n".join(lines)
        check(f"GOLDEN({cid}) ...and verify.py's own patterns agree with it",
              validate(text)["green"], case["green"])

    print(f"\n{BOLD}=== B. THE NEGATIVE CONTROL: pytest's own summary is not "
          f"a required line ==={RESET}")
    # THE SILENT-GREEN CLASS, in one assertion. `46 passed, 4 skipped in 0.06s`
    # has no denominator, so a collapsed collection prints a line of the same
    # shape and a gate cannot tell them apart. Every captured raw summary must
    # be REFUSED by the required pattern - including the green ones, because
    # the point is that pytest's line is unjudgeable, not that it is wrong.
    for cid, _, _ in GOLDEN_CASES:
        case = by_id.get(cid)
        if not case:
            continue
        v = validate(case.get("raw_summary", ""))
        check(f"GOLDEN({cid}) pytest's own -q summary "
              f"{case.get('raw_summary', '')!r} is NOT a required line",
              (v["ratio_ok"], v["green"]), (False, False))

    print(f"\n{BOLD}=== C. THE COLLAPSE RULE: no zero-selected run can be "
          f"green ==={RESET}")
    # Exhaustive over a small grid rather than by example. The class is
    # "the suite stopped running and the line stayed green", and one worked
    # example proves one point on a surface.
    grid_green = []
    for coll in (0, 1, 5):
        for desel in (0, 3):
            for p in (0, 4):
                for f in (0, 1):
                    for k in (0, 2):
                        for e in (0, 1):
                            c = Counts(coll, desel, p, f, k, e)
                            _, g = emit(c)
                            if g and (coll == 0 or selected(c) == 0):
                                grid_green.append(tuple(c[:6]))
    check("NO combination with 0 collected or 0 selected is green "
          "(72-point grid)", grid_green, [])
    zero, gz = emit(Counts())
    check("a wholly collapsed run prints COLLAPSED COLLECTION",
          any("COLLAPSED COLLECTION" in l for l in zero), True)
    check("...and it is printed BEFORE the required line, so a reader sees "
          "the reason first",
          zero.index(next(l for l in zero if "COLLAPSED" in l))
          < len(zero) - 1, True)
    check("...and the required line is STILL printed, so the gate is red for "
          "a stated reason and not by absence",
          bool(re.search(require_pattern(), "\n".join(zero))), True)
    check("...and the verdict is red", gz, False)
    check("THE TRAP, NAMED: the required pattern alone MATCHES 0/0 - which is "
          "why the veto line exists",
          bool(re.match(require_pattern(),
                        "unit_suite: 0/0 tests passed, 0 skipped, 0 errors")),
          True)
    check("...and with the veto line present, validate() refuses it",
          validate("\n".join(zero))["green"], False)
    # THE RESIDUAL, STATED RATHER THAN HIDDEN. A collection that shrank from
    # 50 to 3 still emits a self-consistent `3/3`, and no pattern in this file
    # can see that. `expect_min` in the gate table is the control for it, and
    # that is why --gate-spec takes a --floor and why the floor should be
    # sized against your largest single test module rather than guessed.
    shrunk = "\n".join(emit(Counts(collected=3, passed=3))[0])
    check("A SHRUNKEN-BUT-NONZERO collection is GREEN here - the veto lines "
          "cannot see it", validate(shrunk)["green"], True)
    check("...so the gate spec carries a floor for exactly that case",
          "expect_min=40" in gate_spec("unit_suite", floor=40), True)
    check("a collected-but-none-selected run says NOTHING RAN by name",
          any("NOTHING RAN" in l
              for l in emit(Counts(collected=4, skipped=4))[0]), True)
    check("...and names the true denominator, deselections included",
          any("0 of 9 collected" in l
              for l in emit(Counts(collected=4, deselected=5, skipped=4))[0]),
          True)

    print(f"\n{BOLD}=== D. the gate spec and the payload cannot drift "
          f"apart ==={RESET}")
    # TWO AUTHORITIES, BOUND. The patterns printed by --gate-spec and the
    # lines built by emit() are the same contract written twice. The kit's
    # oldest defect class is two readers of one rule disagreeing silently.
    spec = gate_spec("unit_suite", floor=40, max_skips=4)
    check("the printed spec carries the require pattern this file emits for",
          require_pattern("unit_suite") in spec, True)
    check("...and the fail pattern", fail_pattern("unit_suite") in spec, True)
    good, _ = emit(Counts(collected=50, passed=46, skipped=4), "unit_suite", 4)
    check("a green payload matches the spec's require pattern",
          bool(re.search(require_pattern("unit_suite"), "\n".join(good))),
          True)
    check("...and is not vetoed by its fail pattern",
          bool(re.search(fail_pattern("unit_suite"), "\n".join(good))), False)
    for label, c, ex in (
            ("a failure", Counts(collected=3, passed=2, failed=1,
                                 failed_ids=("t.py::test_x",)), None),
            ("an error", Counts(collected=3, passed=2, errored=1,
                                errored_ids=("t.py::test_y",)), None),
            ("a vanished skip", Counts(collected=5, passed=5), 1),
            ("a subset", Counts(collected=2, deselected=2, passed=2), None)):
        txt = "\n".join(emit(c, "unit_suite", ex)[0])
        check(f"...and {label} IS vetoed by it",
              bool(re.search(fail_pattern("unit_suite"), txt)), True)

    print(f"\n{BOLD}=== E. the skip set, in BOTH directions ==={RESET}")
    # The asymmetry the gate table cannot express: `ceilings` is a maximum, so
    # it catches a NEW skip and lets a VANISHED one through.
    check("a NEW skip is caught", emit(Counts(collected=5, passed=4,
                                              skipped=1), DEFAULT_GATE, 0)[1],
          False)
    check("a VANISHED skip is caught too - the half a ceiling cannot see",
          emit(Counts(collected=5, passed=5), DEFAULT_GATE, 4)[1], False)
    check("...and the line says which direction",
          "expected 4, got 0" in "\n".join(
              emit(Counts(collected=5, passed=5), DEFAULT_GATE, 4)[0]), True)
    check("expect_skips=None asserts nothing about skips",
          emit(Counts(collected=5, passed=3, skipped=2))[1], True)

    print(f"\n{BOLD}=== F. the gate name is not hard-coded ==={RESET}")
    lines, _ = emit(Counts(collected=2, passed=2), "integration")
    check("emit() carries the caller's gate name",
          lines[0].startswith("integration: "), True)
    check("...and the patterns follow it",
          bool(re.search(require_pattern("integration"), lines[0])), True)
    check("...and a pattern for a DIFFERENT gate does not match it",
          bool(re.search(require_pattern("unit_suite"), lines[0])), False)

    print(f"\n{BOLD}=== G. what this file admits it has not proven ==={RESET}")
    # Asserted on the interpreter's own state rather than on the source text,
    # so an edit that moves the statement somewhere it does not take effect is
    # caught rather than matched.
    check("this tool writes no bytecode into the tree it judges",
          sys.dont_write_bytecode, True)
    check("pytest is the only runner listed as proven", PROVEN_RUNNERS,
          ("pytest",))
    check("an unproven runner is labelled, not silently accepted",
          "UNPROVEN" in unproven_notice("jest"), True)
    check("...and the notice names the runner asked for",
          "jest" in unproven_notice("jest"), True)
    check("...and pytest gets no notice", unproven_notice("pytest"), "")

    live = "not run"
    print(f"\n{BOLD}=== H. THE LIVE HALF: pytest, actually run ==={RESET}")
    try:
        import pytest  # noqa: F401
        have_pytest = True
    except ImportError:
        have_pytest = False
    suites = find_beside(SUITES_CANDIDATES)
    if not have_pytest or not suites.is_dir() or not cases:
        why = ("pytest is not installed in this interpreter"
               if not have_pytest else
               f"no fixture suites at {suites}" if not suites.is_dir()
               else "no golden fixtures to compare against")
        print(f"  {YELLOW}LIVE HALF NOT RUN: {why}. Sections A-G above are "
              f"the pure layer and the captured fixtures; they do NOT prove "
              f"that this interpreter's pytest still reports what the "
              f"fixtures recorded. Run this on a host with pytest to close "
              f"that half.{RESET}")
        live = f"skipped ({why})"
    else:
        live = "run"
        for cid, sub, args in GOLDEN_CASES:
            case = by_id.get(cid)
            if not case:
                continue
            with in_dir(suites):
                counts, abort = run_pytest([sub] + list(args), quiet=True)
            if abort:
                check(f"GOLDEN({cid}) live run", abort, None)
                continue
            got = {k: v for k, v in counts._asdict().items()
                   if not k.endswith("_ids")}
            check(f"GOLDEN({cid}) live pytest reports the captured counts",
                  got, case["counts"])
            check(f"GOLDEN({cid}) ...and the captured lines",
                  emit(counts, DEFAULT_GATE)[0], case["lines"])

    print()
    print((GREEN if ok_all else RED)
          + f"GATE-LINE SELFTEST: {'PASS' if ok_all else 'FAIL'} — {n} checks; "
            f"live pytest half {live}" + RESET)
    return 0 if ok_all else 1


def unproven_notice(runner: str) -> str:
    """The label, as a pure function, so --selftest can assert it exists."""
    if runner in PROVEN_RUNNERS:
        return ""
    return (f"UNPROVEN RUNNER: {runner!r} has no fixture, no captured output "
            f"and no adapter in this kit. The line below is correctly SHAPED, "
            f"and nothing here has checked that your {runner} counts mean what "
            f"you think they mean. Only {', '.join(PROVEN_RUNNERS)} is proven "
            f"- see gate_line.py's docstring, 'WHAT IS PROVEN'.")


# ==========================================================================
def main() -> int:
    ap = argparse.ArgumentParser(
        description="Produce and validate the one line verify.py judges a "
                    "gate by.",
        epilog="PROVEN for pytest only. Every other runner is UNPROVEN: "
               "--emit will shape a line from counts you supply and will say "
               "so on every run.")
    ap.add_argument("--gate", default=DEFAULT_GATE,
                    help=f"the gate name that prefixes every line "
                         f"(default {DEFAULT_GATE})")
    ap.add_argument("--runner", default="pytest",
                    help="which test runner the counts come from; only "
                         "pytest is proven")
    ap.add_argument("--expect-skips", type=int, default=None,
                    help="the exact skip count you are willing to certify")
    mode = ap.add_argument_group("modes")
    mode.add_argument("--pytest", action="store_true",
                      help="run this project's pytest suite and print the line")
    mode.add_argument("--path", default=None,
                      help="what to hand pytest (default: pytest's own "
                           "discovery)")
    mode.add_argument("--emit", action="store_true",
                      help="build the line from counts you supply")
    mode.add_argument("--validate", metavar="FILE",
                      help="judge a payload's stdout ('-' for stdin)")
    mode.add_argument("--gate-spec", action="store_true",
                      help="print the GATES entry to paste into verify.py")
    mode.add_argument("--capture-golden", action="store_true",
                      help="re-run the fixture suites and rewrite the golden "
                           "file (a reviewed commit)")
    mode.add_argument("--selftest", action="store_true")
    counts = ap.add_argument_group("counts, for --emit")
    for f in ("collected", "deselected", "passed", "failed", "skipped",
              "errored"):
        counts.add_argument(f"--{f}", type=int, default=0)
    spec = ap.add_argument_group("thresholds, for --gate-spec")
    spec.add_argument("--floor", type=int, default=1,
                      help="expect_min: the collapse floor, sized against "
                           "your largest single test module")
    spec.add_argument("--max-skips", type=int, default=0)
    a, rest = ap.parse_known_args()

    if a.selftest:
        return selftest()
    if a.capture_golden:
        return capture_golden()
    if a.gate_spec:
        print(gate_spec(a.gate, a.floor, a.max_skips))
        return 0
    if a.validate:
        text = (sys.stdin.read() if a.validate == "-"
                else Path(a.validate).read_text(encoding="utf-8",
                                                errors="replace"))
        v = validate(text, a.gate)
        print(f"required line : {v['required_line'] or 'NONE FOUND'}")
        print(f"veto lines    : {len(v['veto_hits'])}")
        for w in v["why"]:
            print(f"  {YELLOW}{w}{RESET}")
        print((GREEN if v["green"] else RED)
              + f"GATE LINE: {'GREEN' if v['green'] else 'RED'}" + RESET)
        return 0 if v["green"] else 1
    if a.emit:
        notice = unproven_notice(a.runner)
        if notice:
            print(f"{YELLOW}{notice}{RESET}", file=sys.stderr)
        c = Counts(a.collected, a.deselected, a.passed, a.failed, a.skipped,
                   a.errored)
        lines, green = emit(c, a.gate, a.expect_skips)
        for l in lines:
            print(l)
        return 0 if green else 1
    if a.pytest:
        if a.runner not in PROVEN_RUNNERS:
            print(f"{RED}ABORT: --pytest runs pytest; --runner "
                  f"{a.runner!r} asks for something this file cannot run. "
                  f"{unproven_notice(a.runner)}{RESET}", file=sys.stderr)
            return 2
        extra = ([a.path] if a.path else []) + list(rest)
        c, abort = run_pytest(extra, quiet=True)
        if abort:
            # Loud abort over silent drop. No required line is printed, so the
            # gate reds on absence as well as on this.
            print(f"{a.gate}: ABORTED: {abort}", file=sys.stderr)
            return 2
        lines, green = emit(c, a.gate, a.expect_skips)
        for l in lines:
            print(l)
        return 0 if green else 1

    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
