# Adopting into an existing project

`QUICKSTART.md` is written for a repository whose only uncommitted content is
the kit's own. That is true of a new project and false of almost every
repository anyone is actually working in.

This page is the difference, measured. Each row below is a collision between
the printed steps and a repository that already exists: what the document says,
what the repository actually did, and the workaround that was proven on it. The
branches are also inline in the steps, at the step where each one lands. This
page is the list in one place, for reading before you start.

**Almost every collision below is a document that assumed an empty directory,
or a tool behaving correctly over a tree the document did not anticipate.** Two
were not: row 3's fix changed the remedy the runner itself prints, and the
missing test-runner adapter was a capability the kit did not ship. On the walk
this page comes from, every executable behaved as documented, including the
ones designed to fail — behaving as documented and printing the right advice
are different claims, and row 3 is where they came apart.

---

## Provenance

**One measured adoption walk, 2026-08-22**, into a small Python project with a
real pytest suite, a pre-existing `.gitignore`, existing CI, an existing
`CLAUDE.md`, an existing `.claude/settings.json` and uncommitted work in the
tree.

**The walker was a large language model running a written persona**, not a
person — the same instrument, and the same limit, as every other adoption walk
behind this kit. `docs/walks/README.md` states what that instrument can and
cannot establish. Its findings are recorded in `KNOWN-ISSUES.md` under
**Round #21**, each with its disposition. The timings that walk reported are
not on this page: they measure an agent executing tool calls, not a person
adopting a toolkit, and the walk's own report says so.

**No human has adopted this kit into an existing project and reported
findings.** `DECISION-BRIEF.md` names existing-project adoption as estimated
and never measured; this page narrows that gap by one LLM-persona walk. It does
not close it.

---

## The collisions

| Collision, and where it lands | What was measured | The workaround that was proven |
|---|---|---|
| **An existing `CLAUDE.md`** — Step 6 | Step 6 printed `cp <template> ./CLAUDE.md` unconditionally. Run as printed on a repository holding a 41-line rules file, it destroys that file with no backup and no warning. The step's only acknowledgement of a pre-existing rules file was the Level-1 case, which is a file the kit itself put there. No check in the document can tell a merged rules file from a clobbered one: an overwritten `CLAUDE.md` reaches `VERIFY: PASS`. | Do not run the `cp`. Render instead — `kit_render.py` writes `CLAUDE.md.kit-new` beside the real file and prints a diff — then merge by hand: kit rules as the base, the existing rules preserved **verbatim** under a marked heading of their own, and Step 6's three edits applied to the result. Where the two sets say the same thing, keep one; where they conflict, decide now and write the decision down. |
| **An existing `.claude/settings.json`** — Step 4 | Step 4 said to *substitute the slots in the template into `.claude/settings.json`*. The template's `permissions` block contains only `ask`. The repository's file contained 10 `allow` rules and 2 `deny` rules, one of which was a control its `CLAUDE.md` depended on. Placing the substituted template at that path drops all twelve silently — a permission that no longer exists cannot fail, so nothing reddens. The verb throughout the step was *substitute and place*, which is correct on an empty repository only. | `kit_render.py`, which merges the two as JSON rather than replacing one with the other: the kit's three hook blocks and `statusLine` added, `permissions.allow` and `permissions.deny` left where they were, and every changed key reported. Measured afterwards: **10 allow and 2 deny rules preserved byte-identical.** `adoption_smoke.py` phase 13 asserts the tool's output is byte-identical to the hand-built model, so taking this route costs nothing. On an existing settings file it is not an optional convenience; it is the only non-destructive route. |
| **An ignore rule covering a judged path** — Step 4 | The repository's `.gitignore` began with `.claude/`. `verify.py` aborted correctly: an ignored, untracked judged file is invisible to `git status`, so the `judges` gate would read clean over it forever. The abort's printed remedy at the time was *remove the rule that covers it* — and that rule was a directory rule that also covered `.claude/sidequest.json`, `.claude/cert-green.json` and `.claude/settings.local.json`: session state and a certification token, all three named in the kit's own `.gitignore` as files that must never be committed. Obeying the printed remedy commits them. Cost: about four minutes reading a troubleshooting file the adopter was never routed to. | `git add -f .claude/settings.json` — force-track the one judged file, leaving the ignore rule intact — then commit it. `adoption_smoke.py` phase 12 proves this clears the abort. The abort message now prints this remedy first, the `git check-ignore -v` diagnostic second, and rule removal last and conditional on the rule covering nothing else. **Two follow-ons measured during the fix pass.** Run `git check-ignore -v` *before* the force-add: once a path is tracked it is no longer subject to the ignore rules, so the diagnostic prints nothing. And keep the `-f` — on git 2.54, while the `.claude/` rule stands, every later `git add` naming a path under it fails the same way, the directory and the exact already-tracked file alike, even when that file is committed and unchanged. Once it is committed, the simplest add line is one that does not name it. |
| **A dirty tree against the printed directory pathspecs** — Step 4, Step 9 | Step 4 printed `git add tools .claude kit.config .gitignore src tests docs && git commit -m "adopt the kit"`. Two independent failures on one repository. **First:** `src` is a directory pathspec and the tree held a half-finished feature under it, so the printed line commits unfinished work into a commit titled *"adopt the kit"*, mixed in with eleven kit files. **Second:** `git add .claude` fails on an ignored directory with `The following paths are ignored by one of your .gitignore files: .claude` — not `fatal: pathspec`, which was the only signature the troubleshooting note named. Re-measured on git 2.54 during the fix pass: that failure exits 1 and **stages every other path on the line anyway**, work in progress included, while `&&` skips the commit. So the next `verify.py` repeats the pre-commit red and looks like the commit did not help, and the index is left holding unfinished work. The missing-path failure behaves differently — exit 128, index untouched — which is why the two signatures are worth telling apart. | Read `git status` first — the step said so, in general terms, and that warning is why this was survivable. Then edit the line before running it: **name the kit's own files and drop `src` and `tests` entirely**, since nothing under them is being installed by that step, or `git stash push -- src tests` first with a backup of the diff taken beforehand. Force-track the settings file per the row above and name it rather than its directory. Both failure signatures are now in the step's troubleshooting note. |
| **Work in progress inside `CERT_PATHS`** — Step 4's and Step 9's `VERIFY: PASS` | `CERT_PATHS` is *what is being certified*, and the assumed layout is `src`, `tests`. With one modified file under `src/`, both required green checkpoints are unreachable: `VERIFY: FAIL (exit 1) … RED: judges`, with `THE CERTIFIED TREE is NOT COMMITTED` naming the adopter's own file. **The runner is correct** — certification is a property of a tree — but nine steps assumed a repository whose only uncommitted content was the kit's, and an adopter with unfinished work was left choosing unaided between committing it to manufacture a green and abandoning the document's final checkpoint. | Back up, stash, certify, restore, and report both states. On the measured walk: the diff saved outside the repository and its sha256 recorded, the stash taken as a second independent backup, the certifying run performed, the work restored, and byte-identity verified two ways afterwards. The red with the work on disk is the everyday state of a repository under active development; the green with it stashed is what the tree certifies as. Both are true, and a project that publishes only the second has learned to stash before it looks. |
| **A test suite you already trust** — Step 3, Step 4 item 5 | The kit's promise to an existing project is that it wires the gates you already have, and the documents supplied the gate-table schema and nothing else. The string `pytest` appeared exactly once in the whole kit, as a directory name to skip. There was no worked example for any real runner, and the one place the line's shape contract was written down was a file `QUICKSTART.md` tells the adopter stays behind in the kit. The consequence is reachable by obeying the documents: a gate pointed at `python -m pytest -q` reads `46 passed, 4 skipped`, a numerator with no denominator, so a suite that has stopped collecting prints `3 passed` and certifies. The walker authored a 161-line adapter from scratch and invented every design decision in it. | `modules/03-verification/gate_line.py`, which the kit now ships, with `GATE-LINE.md` as its page: copy it into `tools/`, run `--gate-spec` to print the `GATES` entry built from the tool's own patterns, and put `tools/gate_line.py` in `JUDGE_PATHS`. Size the floor with `--collect-only` rather than estimating it. **pytest is proven** against six committed golden fixtures; every other runner is UNPROVEN and the tool says so on every run, in which case `GATE-LINE.md` is the contract you implement by hand. |
| **CI that ends up weaker than the local gate** — after Step 6 | The repository's CI ran `python -m pytest -q` across three Python versions. After adoption the project's certification is `python tools/verify.py`, which the rendered `CLAUDE.md` names as the single command, and which enforces the floor, the skip ceiling, the subset veto, the hook arming and the judge surface — **none of which CI runs.** From the moment Step 6 lands, the local gate proves strictly more than CI does, and CI is the control outside the blast radius. Nothing in the nine steps told an existing-project adopter that this divergence had just opened; module 07 addresses CI, and `QUICKSTART.md` defers it to the following week. | None applied, deliberately: module 07 is outside the QUICKSTART path and changing CI would have been inventing beyond the documents. The divergence was **logged as adoption debt** in the project's own `docs/FAILURE-FLOOR.md` instead, which is the honest disposition for a gap you have found and are not closing this week. Do the same, and close it when you adopt module 07 — a gate your agents cannot edit is worth more than the same checks run locally twice. |

---

## Also measured, at Level 1

`LEVEL-1.md` installs documents only, and two of its steps have the same shape
of collision. Both are recorded in `KNOWN-ISSUES.md` Round #21 and both now
have a check.

- **An existing `kit.config`.** Step 2 printed `cp kit.config.example
  ./kit.config`, which overwrites a hand-written config and destroys the
  answers in it. Append the keys you are missing at their shipped value
  instead; `doctor:l1-config-complete` names every key you are short.
- **Ledgers under other names.** The kit's four ledger filenames are fixed and
  `LEDGERS_DIR` is the only thing you can move, so a repository already keeping
  a `LESSONS-LEARNED.md` or a `TOKEN_LEDGER.md` ends with two ledgers answering
  one question. Rename onto the kit's name and carry the content forward,
  freeze the existing file as the record up to adoption, or move `LEDGERS_DIR`.
  `doctor:l1-ledger-collision` names any collision and changes nothing.

---

## What this page does not cover

- **Repositories much larger or older than the one walked.** One project, one
  language, one test runner, one maintainer. A monorepo, a repository with many
  contributors, or one whose CI is load-bearing for releases will meet
  collisions that are not on this list.
- **The team case.** `.claude/settings.json` is per-machine, committed and
  judged at the same time. That is recorded as open in `KNOWN-ISSUES.md`
  ("Whose settings file? — the team story") with a fix shape, and it is not an
  existing-project problem specifically; it arrives on the second machine
  whatever the repository's age.
- **Anything a walk cannot see.** A walk finds commands that do not run as
  printed and checkpoints that do not match. It does not find a step whose
  explanation is wrong while its commands still work.
