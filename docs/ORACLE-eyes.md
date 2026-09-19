# ORACLE — eyes

**What this gate catches, in one paragraph.** `eyes` shells out to
`modules/03-verification/eyes.py gate <dir>`, which reads a committed
`manifest.json` and `look-report.json` and prints one state word plus four
counts. The mechanical half needs no model — a PNG exists, is fresh against
the source's sha256, is the right dimensions, is not blank — and runs first;
the catalog half (ten questions per viewport, answered by a reader with no
vision of its own) needs one. `UNSEEN`/`STALE`/`NO-BROWSER` are vetoed the
same way every other gate in this table vetoes an honest non-result: "the
check did not run" and "the check passed" must never render alike.

**What it looked like red, observed in this worktree.** Via `--nc` (file
kept outside the repository) with `{"expect_min": {"eyes": 9999}}`:

```
RED   eyes 2 < 9999  (0.6s)
line: EYES: state SEEN; shots 2; viewports 1280x720,1920x1080; catalog 20/20 answered; yes 0
FLOOR BREACH: 2 shots, floor 9999. The line is well-formed; the number SHRANK. Either something stopped being checked, or the floor is genuinely obsolete and lowering it is a reviewed commit.
```

Observed 2026-09-16, exit 2 INSTRUMENTED. Restore: nothing to revert — the
override lived outside the repository; the unmodified run reads green
(`GREEN eyes SEEN, 2 shots, catalog 20/20, yes 0`), confirmed above.
(`checks-registry.json`'s `gate:eyes` row separately records a zero-shots
floor breach forced by `verify.py --selftest` section B3 on 2026-09-16 —
the same class of red, forced by a different, in-process route.)

**Lineage.** Named in `EYES.md`'s own lineage paragraph: "Chromium headless
screenshot (the render mechanism itself); pixel-diff visual regression (the
shape of gating a render — compare against a stored image, fail on
change)." The ten-question catalog answered by a reader is named there as
this module's own addition.

**The floor — a finding, not enacted here.** `kit_doctor.py`'s
`doctor:vacuous-gate` check flags the `eyes` gate's `expect_min=1` in
`verify.py` ("the floor is 1: any run producing one of anything clears
it"). `EYES.md`'s own `shot` documentation states the tool's default
render set is **three** viewports — `1280x720`, `1920x1080`, and `400x850`
for a phone — so three is the value this README recommends as the floor
(one shot per default viewport; a run that silently dropped a viewport
would still clear a floor of 1 but not a floor of 3). Raising `expect_min`
for the `eyes` entry to 3 requires editing `modules/03-verification/
verify.py`'s `GATES` table, which is **outside this lane's TOUCHES list**
(`kit.config` JUDGE_PATHS only, `kit.config.example`, `tools/
deident_scan.py`, new ORACLE pages, `read_triage.py` docstring only,
`KNOWN-ISSUES.md` rows only). It is also not cost-free: the committed
example render at `examples/eyes-render/` currently ships only 2 shots, so
raising the floor to 3 would also require re-rendering and re-committing
that example, a second file outside TOUCHES. This is recorded as a left-out
item in the lane report rather than acted on. `doctor:vacuous-gate` will
therefore continue to name the `eyes` gate's floor as ATTENTION after this
lane's ORACLE pages land; the `no ORACLE-eyes.md page` half of that same
row's finding is what this page closes.

**Residual.** A pixel check cannot find cut-off text — every catalog
question past "does a render exist" needs a reader, per `EYES.md`'s own
"What this does not prove" section.
