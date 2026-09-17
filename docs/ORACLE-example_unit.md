# ORACLE — example_unit

**What this gate catches, in one paragraph.** `example_unit` runs
`modules/03-verification/examples/fake_suite.py`, the kit's shipped stand-in
test suite, and requires a self-consistent `N/N cases passed` line with a
floor of 3 cases and a veto on any `THESE FAILED`/`(subset:` text. It exists
to prove the *shape* of a unit-test gate — a ratio line, a floor above the
suite's largest single unit, a distinct failure phrase — before an adopter
points it at their real suite. Per the gate's own `doc` field in
`verify.py`: "EXAMPLE — replace with your test suite."

**What it looked like red, observed in this worktree.** Via `--nc` (file
kept outside the repository) with `{"expect_min": {"example_unit": 9999}}`:

```
RED   example_unit 4 < 9999  (0.0s)
line: example_unit: 4/4 cases passed
FLOOR BREACH: 4 cases, floor 9999. The line is well-formed; the number SHRANK. Either something stopped being checked, or the floor is genuinely obsolete and lowering it is a reviewed commit.
```

Observed 2026-09-16, exit 2 INSTRUMENTED. Restore: nothing to revert — the
override lived outside the repository; the unmodified run reads green
(`GREEN example_unit 4/4`), confirmed above.

**Lineage.** No row in `BLUEPRINT.md` §12 names unit testing itself (the
document's lineage table covers the kit's own governance mechanisms, not
the example gates it ships to be replaced). General-knowledge, unfetched
this session: the xUnit family (Kent Beck's SUnit, 1994, and its many
ports — JUnit, PyUnit) is the conventional ancestor of "assert N cases, one
at a time." Stated as an honest, unfetched analogy, not a citation.

**Residual.** This is one of the kit's shipped EXAMPLE gates — QUICKSTART
Step 4.6 tells an adopter to replace it. The oracle it proves is only that
the *table's own five example cases* still pass; it says nothing about a
real project's actual code paths until the `cmd` and the fixture file are
replaced.
