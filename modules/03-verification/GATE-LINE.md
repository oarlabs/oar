# `gate_line.py` — wiring a test runner you already have

`verify.py` judges a gate by grepping **one required line** out of a command's
stdout. Real test runners do not print that line. This file is the adapter that
does, and the page that says what it is proven to do.

Copy `gate_line.py` into your project as `tools/gate_line.py` and add that path
to `JUDGE_PATHS`. It decides what green means, so an uncommitted change to it
must invalidate certification the same way an uncommitted change to
`kit.config` does.

## The trap this exists for

`python -m pytest -q` prints:

```
46 passed, 4 skipped in 0.06s
```

There is no denominator in that line. A suite that has stopped running — a
renamed directory, a broken `conftest.py`, a changed `testpaths` — collects
three tests and prints `3 passed`, which is the same shape as a healthy run of
a three-test suite. **A gate pointed straight at pytest certifies a collapsed
collection.** That is the silent-green class the rest of this kit is built to
refuse, and until an adoption walk hit it (finding P3W-6) nothing in the kit
said so.

## The line it prints

```
unit_suite: 46/46 tests passed, 4 skipped, 0 errors
```

The denominator is **selected and not skipped**, so the ratio stays
self-consistent while tests legitimately skip, and the skip count is a field of
its own so the gate table's `ceilings` can bound it.

The veto vocabulary, every line matched by the gate's `fail_pattern`:

```
unit_suite: THESE FAILED: tests/test_parser.py::test_reads_an_empty_document
unit_suite: THESE ERRORED: tests/test_stats.py::test_needs_a_fixture
unit_suite: SKIP SET CHANGED: expected 4, got 3
unit_suite: COLLAPSED COLLECTION: 0 tests collected - the suite did not run
unit_suite: NOTHING RAN: 0 of 50 collected tests were selected
unit_suite: 46/46 tests passed, 4 skipped, 0 errors (subset: 46 of 50)
```

## Wiring it

```bash
python tools/gate_line.py --pytest --expect-skips 4     # see the line
python tools/gate_line.py --gate-spec --floor 40 --max-skips 4
```

`--gate-spec` prints the `GATES` entry to paste into `verify.py`, built from
this file's own patterns so the two cannot drift apart.

**Size the floor, do not guess it.** `expect_min` is a collapse detector, not a
coverage target. Set it above your largest single test module — count that with
`python -m pytest --collect-only`, do not estimate it — so that losing any one
module reds the gate.

**`--expect-skips` is an exact count, and the gate table cannot express one.**
`expect_min` is a floor on one capture group and `ceilings` are maxima, so a
ceiling catches a *new* skip and lets a *vanished* one through. A skip that
quietly turned into a pass is a change to what your suite proves. Moving the
number is the explicit act that records it.

## Negative controls

Do not edit a test to watch the gate go red. `python tools/verify.py --nc`
doctors the gate's own pattern and needs no file in your repository changed —
`ORACLE-WORKSHEET.md` Part 3, law 1.

## What is proven, and what is not

**pytest is PROVEN.** Six suites in `examples/pytest_suites/` — all pass, pass
with skips, failures, errors, a collapsed collection, and a deselected subset —
are run for real by `gate_line.py --capture-golden`, and what pytest actually
reported is committed in `examples/pytest-golden.json`. `--selftest` replays
all six against the pure layer, re-runs them live wherever pytest is installed,
and holds two negative controls: that no combination of counts with a zero
collection can produce a green verdict, and that pytest's own `-q` summary is
refused by the required pattern.

**Every other runner is UNPROVEN.** unittest, jest, `go test`, `cargo test` and
the rest have no fixture here, no captured output and no adapter. `--emit` will
build a correctly *shaped* line from counts you supply for any of them, and it
prints an UNPROVEN notice naming the runner every time it does. Adding the
second proven adapter means adding fixture suites beside the pytest ones and
capturing them the same way.

## The residual, stated

A collection that shrank from 50 to 3 still emits a self-consistent `3/3`, and
nothing in this file can see that. `expect_min` is the only control for it,
which is why the floor is a number you measure rather than a number you pick.
`--selftest` asserts this residual out loud rather than leaving it to be
discovered.
