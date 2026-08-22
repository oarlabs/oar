# Module 03 — Verification

One command, one summary line, one exit code — plus the doctrine for inventing
the checks that command runs when nothing comes free.

## Files

| File | What it is |
|---|---|
| `verify.py` | The certification runner **skeleton**. Runs as shipped. Gate table with required-line judging, `expect_min` floors, ceilings, component-line assertions, the four-verdict exit contract, a `judges` (judge-paths-clean) gate, a `hooks` gate that certifies the enforcement layer, repo-root discovery plus a **startup assertion**, the `--nc` negative-control facility, and a `--selftest` that judges the judges. |
| `examples/fake_suite.py` | Example gate payload — a toy test suite. Shows the required-line shape, the failure shape, and the subset-honesty suffix. Replace it. |
| `examples/fake_lint.py` | Example gate payload — a toy linter. Shows a component line, a ratified-warning ceiling, and a FAIL count inside the required line. Replace it. |
| `gate_line.py` | The suite adapter. Turns a real test runner's output into the one required line this runner judges, and refuses to be green over a collapsed collection. **Proven for pytest** against six golden fixtures captured from real runs; every other runner is labelled UNPROVEN by the tool itself. |
| `GATE-LINE.md` | The page for the above: the trap, the line, the veto vocabulary, how to size the floor, and what is not proven. |
| `examples/pytest_suites/` | The six fixture suites `gate_line.py --capture-golden` runs for real — all pass, pass with skips, failures, errors, a collapsed collection, a deselected subset. |
| `examples/pytest-golden.json` | What pytest actually reported for those six, captured and committed. `gate_line.py --selftest` replays it. |
| `ORACLE-WORKSHEET.md` | How to manufacture a check when no oracle comes free: five shapes, a per-check worksheet, five laws, the continuity gate, and the escape rate. |

## Adopt it — the commands, in a working order

From your own repository root. Ordered so each command can run when you reach
it: directories before copies, config before anything reads it, and the harness
settings before the first `verify` run (its `hooks` gate names that file).

```bash
git init                       # the judges gate asks git; without a repo it aborts
mkdir -p tools
mkdir -p .claude
cp /path/to/kit/modules/03-verification/verify.py         tools/verify.py
cp /path/to/kit/modules/02-enforcement/hook_model_gate.py tools/   # module 02 only
cp /path/to/kit/modules/02-enforcement/hook_fixtures.py   tools/   # module 02 only
cp /path/to/kit/modules/04-ledgers/escape_rate.py         tools/   # module 04 only
mkdir -p docs
cp /path/to/kit/modules/04-ledgers/JUDGMENT-LEDGER.md     docs/    # module 04 only
cp /path/to/kit/kit.config.example                        kit.config
# substitute the kit's modules/02-enforcement/settings.json.template
# into .claude/settings.json           (module 02 only)
python tools/verify.py --list
```

**No module 02, or no module 04?** Then do Step 0 of *Adapting it* below
first — the shipped `RUN_ORDER` names one gate that needs module 02's files
and one that needs module 04's, and the startup assertion will refuse to start
without them. Without module 02, skip the two `hook_*` copies and the settings
file; without module 04, skip `escape_rate.py` and the judgment ledger.

`git init` is listed because it is genuinely load-bearing rather than assumed:
outside a work tree `git status` exits 128 with empty output, which is
byte-identical to a clean tree, so the runner refuses to run a git-judged gate
rather than believe it.

## Try it right now

```bash
cd modules/03-verification
python verify.py --selftest                       # PASS (the count grows as
                                                  # you add gates - read the word)
python verify.py --only example_unit,example_lint # PARTIAL (exit 3)
cd ../.. && python modules/03-verification/verify.py   # PASS (exit 0), clean tree
```

Then watch it fail, which matters more:

```bash
# a well-formed green line carrying a shrunken count
python verify.py --nc nc-example.json             # INSTRUMENTED (exit 2)
python examples/fake_suite.py --shrink            # the line the floor catches
python examples/fake_lint.py --warn               # the ceiling breach
```

## The exit contract

| Code | Verdict | Meaning |
|---|---|---|
| 0 | **PASS** | Every gate ran and was green, uninstrumented. **The only certifying outcome.** |
| 1 | FAIL | At least one gate went red. |
| 2 | INSTRUMENTED / ABORTED | `--nc` was passed, or the runner refused to start. Certifies nothing either way. |
| 3 | PARTIAL | Everything that ran was green, but gates were skipped. |

### `--mint-cert-token` — the one thing PASS is allowed to write

Module 02's protected-path tripwire reads a **cert-green token** and lets
writes through while the certification still describes the tree. Pass
`--mint-cert-token` and this runner writes that token from the single line that
returns `PASS`, carrying the sha, a timestamp and the gate headlines. Any other
verdict prints why it did not mint and writes nothing: `PARTIAL` and
`INSTRUMENTED` both mean the run certified nothing, and a token from either
would pre-authorise writes on the strength of a run that deliberately proved
less.

It is **opt-in**, because a run that lifts a control should be asked for rather
than happen as a side effect. And the token is a **convenience, not an
authorization** — unsigned, and forgeable by anything that can write a file.
The reasoning, and why a signature would make the label worse rather than the
control better, is in `cert_green()` and in the kit README's `Security scope`.

PARTIAL exists because **"the check did not run" and "the check passed" must
never look the same.** That is the single most valuable line in this module. CI
that runs a subset should assert *exactly* 3 — asserting `!= 1` would let a
silently-emptied skip list read as success, and asserting `== 0` would be a
claim the runner cannot support.

## Two things that only matter once somebody COPIES this file

**Repo-root discovery.** `Path(__file__).parent` is the obvious root and it is
wrong the moment the runner lives in `<repo>/tools/`. Every gate then runs with
`cwd=tools/`, and `git -C tools status -- src` returns an *empty string with
exit 0* for a path that does not exist there — an empty porcelain is exactly how
"clean" is spelled, so the gate whose whole job is noticing an uncommitted tree
becomes a gate that cannot fail. The root is therefore discovered: nearest
`.git` ancestor, then `PROJECT_ROOT` from `kit.config`, then this file's
directory as a last resort.

**The startup assertion.** Discovery is not trusted on its own. Before any gate
runs, every `JUDGE_PATHS` / `CERT_PATHS` entry and every gate command must exist
under the resolved root — and no judged path may be excluded by the repo's own
ignore rules — or the runner **aborts with exit 2 naming the path**. A runner
that cannot find what it is judging, or that git will never report on, must
refuse to start, never report green. `tools/adoption_smoke.py` at the kit root
is the regression test for two of the three conditions: phase 7 covers
existence, and phase 12 plants a real ignore rule over a real judge path and
asserts the abort names it. The work-tree condition is covered by the runner's
own selftest, not by the smoke. The smoke can also plant the original
repo-root defect back and prove it still detects that.

## Four design rules worth stealing even if you write your own runner

1. **Judge by a required output line, never an exit code.** Exit codes lie in
   both directions. A run that died half-way has no required line either, which
   makes the line strictly stronger. Use a backreference where "all of them" is
   the claim: `(\d+)/\1` matches `204/204` and never `203/204`.
2. **Every headline gate carries a floor.** `0/0 passed` is a well-formed
   success line describing a catastrophe. Put the floors inside the runner —
   which is inside the judge surface — so lowering one is a reviewed commit
   rather than a charter edit nobody sees.
3. **Separate the pure judging layer from the running layer.** Everything above
   the `RUNNING LAYER` banner is a pure function of its arguments. That is the
   only reason `--selftest` can exercise the floor logic, the veto logic, the
   dirty-tree parser and all eight branches of the verdict matrix in
   milliseconds, with no subprocesses and no repo mutation.
4. **Build the negative control into the runner.** `--nc` doctors patterns and
   floors from a scratch file, so a gate can be shown red without editing a
   single repo file — and it is armed by the *flag appearing in argv*, so a
   missing or malformed override file aborts rather than falling through to a
   clean run that looks like a proven control.

## File contract with other modules

- **← 02-enforcement.** The runner **ships** a `hooks` gate that shells out to
  `hook_fixtures.py --strict --armed <settings>`, so certification includes
  "the enforcement layer is armed, alive and deciding correctly". Its required
  line carries **three** counts —
  `HOOK FIXTURES: N/N passed, S skipped, A n/a` — with a floor on `N`, a
  **ceiling of 0 on `S`**, and `A` left free, because an `n/a` means a feature
  is switched off on purpose and is therefore not a gap. The full veto list is
  `UNARMED:` · `UNSTARTABLE:` · `DEAD-MAN` · `HOOK NOT ARMED` ·
  `CONFIG WARNING`. Point
  `HOOK_FIXTURES` and `HOOK_SETTINGS` at your copies, or delete the gate
  (see Step 0 of *Adapting it*, below).
- **→ 04-ledgers.** Gate names here are the check names the JUDGMENT LEDGER
  cites. Keep them stable — a renamed gate silently orphans every ledger row
  that named it.
- **→ 07-ci.** The CI workflow runs `{{GATE_COMMAND}}` and asserts
  `{{CI_EXPECTED_EXIT}}`. The `--skip` list and that expected code must agree,
  and the workflow header must say *why* each gate is skipped.
- **← 01-governance.** The rules document defines certified as
  `{{GATE_COMMAND}}` — this runner is what that phrase points at.

## What breaks if you adopt this module alone

Nothing. You get a runner and a doctrine document. Without module 02 there is no
`hooks` gate (delete it or never add it); without 04 the ledgers it feeds do not
exist; without 07 nobody re-judges your push. All fine — the runner is useful the
day you have one real gate in it.

### The `judges` gate needs git

`git status` outside a work tree exits 128 with *empty stdout*, and an empty
porcelain is exactly how "clean" is spelled — a runner that reads only stdout
will print `VERIFY: PASS (exit 0) — judges clean` over a directory git has
never seen. (An early version of this runner did exactly that; an
adoption walk found it, and nothing in the kit's own suite could have.) The runner
now guards against it three times over:

- the startup assertion **refuses to run** (exit 2) when a git-dependent gate is
  selected and the resolved root is not a work tree, naming the root and
  offering `--skip judges`;
- it also refuses (exit 2) when a judged path is **excluded by the repo's ignore
  rules and untracked**, because `git status --porcelain -- <that path>` prints
  nothing whatever the file says. `.claude/` in a pre-existing `.gitignore` is
  the measured case: the gate read clean over the settings file that decides
  whether the hooks run at all;
- and if git fails for any other reason mid-run, its return code and stderr are
  turned into a `?? <git failed rc=N: …>` porcelain line, so the ordinary
  dirty-tree judge goes red with the reason quoted.

Three mechanisms because they catch three different things: the first catches
"there is no repository", the second catches "git will never mention this path",
and the third catches "git broke just now".

## Adapting it

**Step 0 — did you adopt modules 02 and 04?**

Two shipped gates name files that belong to another module, and the startup
assertion will correctly refuse to start over files you do not have — loud and
honest, but blocking, and the checklist below used to walk you straight into it.

If you did **not** adopt **module 02**: delete the `hooks` entry from `GATES`,
delete `"hooks"` from `RUN_ORDER`, and delete the `HOOK_FIXTURES` and
`HOOK_SETTINGS` constants. If you **did**: point those two constants at your
copies and keep the gate. Certification then includes "the enforcement layer is
armed and alive", which is the half everyone forgets.

If you did **not** adopt **module 04**: delete the `escapes` entry from
`GATES`, delete `"escapes"` from `RUN_ORDER`, and delete the `ESCAPE_TOOL` and
`ESCAPE_LEDGER` constants. If you **did**: point those two at
`tools/escape_rate.py` and your judgment ledger, and keep the gate.
Certification then publishes your **escape rate** — the share of findings an
existing check should have caught — on every run, and holds the latest round to
the ceiling written into the gate entry beside the other floors. Until your
first round lands a row it prints `state NO-ROUNDS-RECORDED`, which is the true
state of a new project rather than a zero. **If you change that ceiling, change
`DEFAULT_CEILING` in `escape_rate.py` to match** — the tool's `--selftest`
binds the two and goes red naming both. A gate and a hand run publishing
different ceilings while both stay green is the two-authorities defect this kit
keeps finding in itself, and it was measured here before it was closed.

`--skip <gate>` also works but is the worse answer in both cases: a permanently
skipped gate in `RUN_ORDER` means every run reports PARTIAL (exit 3) and **the
project can never certify**. Delete it properly.

1. Delete both example gates and their `examples/` payloads. Nothing in
   `--selftest` breaks — sections A/B are guarded and section F resolves a live
   gate name at runtime instead of naming an example.
2. Add your gates to `GATES`, in cost order, in `RUN_ORDER`.
3. For each, fill in the ORACLE-WORKSHEET page **first**. The `require` line and
   the floor come straight off it, and if you cannot write the required output
   line you have discovered that you do not yet know what the check measures.
4. Extend `selftest()` with the specific ways *your* gates could report a false
   green. The synthetic inputs in section B are the pattern: for every gate, ask
   "what is the well-formed line that would be catastrophic?" and add it.
5. Set `JUDGE_PATHS` and `CERT_PATHS` — the constants **in this runner**, which
   is where the gates read them from. The runner does not read those two keys
   out of `kit.config`; nothing does for `JUDGE_PATHS`, and `hook_model_gate.py`
   reads `CERT_PATHS` for the cert-green tripwire only. So `kit.config`'s copies
   are documentation, and **you must keep them in agreement with the constants
   by hand** — a `CERT_PATHS` that disagrees means the hook and the runner hold
   different opinions about what was certified. They are different *lists* on
   purpose — judge paths decide what green *means*, cert paths are what is
   *being* certified — and conflating them makes a docs commit invalidate a
   certification, which is how a team learns to stop caring about the token.
