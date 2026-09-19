# ORACLE — escapes

**What this gate catches, in one paragraph.** The kit's headline claim is
that its review loop publishes its own defect escape rate — the share of
reported items an existing check should have caught. A claim with no
instrument is a slogan, so this gate computes the rate from the judgment
ledger's own table on every certifying run (`modules/04-ledgers/
escape_rate.py --ledger KNOWN-ISSUES.md --ceiling 35.0`) and holds the
latest round to a declared ceiling, printing the honest state word
(`MEASURED`/`SMALL-N`/`NO-ROUNDS-RECORDED`) rather than a bare number, so
"no data yet" can never render like "a measured zero."

**What it looked like red, observed in this worktree.** Via `--nc` (file
kept outside the repository) with `{"expect_min": {"escapes": 9999}}`:

```
RED   escapes 37 < 9999  (0.1s)
line: ESCAPE RATE: 37/243 items (15.2%) over 26 rounds; latest 0/6 (0.0%); ceiling 35.0%; state MEASURED
FLOOR BREACH: 37 items, floor 9999. The line is well-formed; the number SHRANK. Either something stopped being checked, or the floor is genuinely obsolete and lowering it is a reviewed commit.
```

Observed 2026-09-16, exit 2 INSTRUMENTED. Restore: nothing to revert — the
override lived outside the repository; the unmodified run reads green
(`GREEN escapes 37/243 (15.2%)`), confirmed above.

**Lineage.** Named in `BLUEPRINT.md` §12: "Defect escape rate, a standard QA
and delivery metric: the share of defects that reached the user because the
process that should have caught them did not, with published benchmark
bands" — search-result
sources `https://dzone.com/articles/how-to-measure-defect-escape-rate-to-keep-bugs-out`
and `https://plandek.com/blog/escaped-defects`. What this kit adds, per the
same row: the denominator is computed from the judgment ledger rather than a
bug tracker, published per round, held to a declared ceiling, and printed as
a required line on a certifying run.

**Residual.** There is deliberately no `expect_min` on the real (non-`--nc`)
gate — a floor asks "did enough happen," and for a metric where LOW is good
that question cannot be a red on a project's first day. The `SMALL-N` state
(gate ceiling gated by `min_countable()`) means a sustained run of
sub-floor rounds can go quiet without a mechanical red; the disclosure is
loud (the cumulative rate and trend print every run) but its only reader is
a person, per the owner's 2026-08-23 ruling recorded in
`checks-registry.json`'s `escape:nc-xv` row.
