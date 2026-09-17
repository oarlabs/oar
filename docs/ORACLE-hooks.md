# ORACLE — hooks

**What this gate catches, in one paragraph.** The enforcement hook
(`modules/02-enforcement/`) is the only code in the project that runs with
the authority to stop a tool call and is never exercised by ordinary work —
nothing calls it in development, nothing fails when it silently breaks. This
gate runs `hook_fixtures.py --strict --armed` against `.claude/settings.json`
and asks two questions mechanically: is the hook ARMED (wired at every
enforcement point the settings file names) and is it ALIVE (the dead-man
clause: a fixture that produced no verdict at all is scored zero, not
skipped-as-passed). `--strict` additionally forbids a skipped fixture from
reading as a pass.

**What it looked like red, observed in this worktree.** Using the runner's
own negative-control facility (`--nc`, a JSON override file kept OUTSIDE the
repository, per `ORACLE-WORKSHEET.md` Law 1) with `{"expect_min":
{"hooks": 9999}}`:

```
RED   hooks 38 < 9999  (2.4s)
line: HOOK FIXTURES: 38/38 passed, 0 skipped, 2 n/a
FLOOR BREACH: 38 fixtures, floor 9999. The line is well-formed; the number SHRANK. Either something stopped being checked, or the floor is genuinely obsolete and lowering it is a reviewed commit.
```

Observed 2026-09-16. The run reported `VERIFY: INSTRUMENTED (exit 2)` and
"NEGATIVE CONTROL ACTIVE, this run certifies nothing." Restore: nothing to
revert — the override file was never inside the repository, so no repo file
changed; the next ordinary run (no `--nc`) reads green again, as confirmed
above (`GREEN hooks 38/38 armed, 2 n/a`).

**Lineage.** No row in `BLUEPRINT.md` §12 names this specific mechanism by
title. The nearest general-knowledge analogue — not verified against a
fetched source this session — is policy-as-code admission control (for
example Open Policy Agent's Gatekeeper), where a webhook intercepts an
action before it completes and is itself health-checked separately from the
policies it enforces; that "is the enforcer itself alive" split is this
gate's own ARMED/ALIVE pair. Stated as an honest, unfetched analogy rather
than a citation.

**Residual.** The gate proves the hook is wired and answers on a fixture
battery; it does not prove the fixture battery itself covers every rule the
hook is meant to enforce — a rule added to the hook without a matching
fixture is invisible here (this is exactly READ TRIAGE P1's point, item 5
below, about a judge path added without a matching pattern).
