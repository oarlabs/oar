# ORACLE — example_lint

**What this gate catches, in one paragraph.** `example_lint` runs
`modules/03-verification/examples/fake_lint.py`, the kit's shipped stand-in
linter, and requires a `N checks, 0 FAIL, M WARN, K OK` line (floor 10
checks, a ceiling of 1 on WARN so a second unratified warning is visible
rather than absorbed) plus a required rule-set banner line, so a summary
cannot pass without its own component step. Per the gate's `doc` field in
`verify.py`: "EXAMPLE — replace with your linter."

**What it looked like red, observed in this worktree.** Via `--nc` (file
kept outside the repository) with `{"expect_min": {"example_lint": 9999}}`:

```
RED   example_lint 12 < 9999  (0.0s)
line: example_lint: 12 checks, 0 FAIL, 1 WARN, 11 OK
FLOOR BREACH: 12 checks, floor 9999. The line is well-formed; the number SHRANK. Either something stopped being checked, or the floor is genuinely obsolete and lowering it is a reviewed commit.
```

Observed 2026-09-16, exit 2 INSTRUMENTED. Restore: nothing to revert — the
override lived outside the repository; the unmodified run reads green
(`GREEN example_lint 0 FAIL`), confirmed above.

**Lineage.** No row in `BLUEPRINT.md` §12 names static linting itself.
General-knowledge, unfetched this session: rule-based static analysis
linters (Lint, 1978; ESLint and its many successors) are the conventional
ancestor of the shape N rules, 0 hard failures, warnings visible but not
fatal. Stated as an honest, unfetched analogy, not a citation.

**Residual.** This is one of the kit's shipped EXAMPLE gates — QUICKSTART
Step 4.6 tells an adopter to replace it. Like `example_unit`, the oracle it
proves is only that the fixture linter's own committed rule set still runs;
nothing here checks a real project's source until the `cmd` is replaced.
The WARN ceiling (currently 1, and currently at exactly 1) means the next
new warning is the one this gate is built to surface.
