# Adopting into an existing project

`QUICKSTART.md` assumes a repository whose only uncommitted content is the kit's
own. Almost no working repository matches that. Below is every collision measured
between it and a repository that already exists, each also inline at its step.
Read this page before you start.

## Provenance

One measured adoption walk, **2026-08-22**, into a small Python project. It had a
real pytest suite, a pre-existing `.gitignore`, existing CI, an existing
`CLAUDE.md`, an existing `.claude/settings.json` and uncommitted work in the tree. The walker was a
language model running a written persona, not a person. [record:
`KNOWN-ISSUES.md` **Round #21**; `docs/walks/README.md`]

That walk's timings are not here: they measure an agent executing tool calls, not a
person adopting a toolkit. No human has adopted this kit into an existing project
and reported findings.

Every executable behaved as documented, including the ones designed to fail. Two
collisions were not documents assuming an empty directory: row 3 changed the
runner's printed remedy, and row 6 was a capability the kit did not ship.

## 1. An existing `CLAUDE.md` — Step 6

Step 6 printed `cp <template> ./CLAUDE.md` unconditionally. On a repository holding
a 41-line rules file that destroys it with no backup and no warning, and an
overwritten `CLAUDE.md` still reaches `VERIFY: PASS`.

**Do not run the `cp`.** Render instead: `kit_render.py` writes
`CLAUDE.md.kit-new` beside the real file and prints a diff. Merge by hand — kit
rules as the base, the existing rules preserved **verbatim** under a marked heading
of their own, Step 6's three edits applied. Where they agree, keep one; where they
conflict, decide now and write it down.

## 2. An existing `.claude/settings.json` — Step 4

Step 4 said to substitute the template's slots into `.claude/settings.json`. The
template's `permissions` block contains only `ask`; the repository's file held 10
`allow` rules and 2 `deny` rules, one of which its `CLAUDE.md` depended on. Placing
the template at that path drops all twelve silently, and a permission that no
longer exists cannot fail.

**Use `kit_render.py`**, which merges the two as JSON: the kit's three hook blocks
and `statusLine` added, `permissions.allow` and `permissions.deny` left in place,
every changed key reported. Measured afterwards: **10 allow and 2 deny rules
preserved byte-identical.** On an existing settings file this is the only
non-destructive route. [check: `adoption_smoke.py` phase 13]

## 3. An ignore rule covering a judged path — Step 4

The repository's `.gitignore` began with `.claude/`. `verify.py` aborted correctly:
an ignored, untracked judged file is invisible to `git status`, so the `judges`
gate reads clean over it forever. The remedy it printed at the time — remove the
rule — also uncovers `.claude/sidequest.json`, `.claude/cert-green.json` and
`.claude/settings.local.json`, which the kit's own `.gitignore` says must never be
committed.

**Run `git add -f .claude/settings.json`**, force-tracking the one judged file,
then commit it. Run `git check-ignore -v` **before** the force-add: once a path is
tracked the diagnostic prints nothing. Keep the `-f`: on git 2.54, while the
`.claude/` rule stands, every later `git add` naming a path under it fails the same
way, even for a file already committed. [check: `adoption_smoke.py` phase 12]

## 4. A dirty tree against the printed directory pathspecs — Steps 4 and 9

Step 4 printed `git add tools .claude kit.config .gitignore src tests docs && git
commit -m "adopt the kit"`. Two failures on one repository. `src` is a directory
pathspec, and the tree held a half-finished feature, so the line commits unfinished
work into a commit titled *"adopt the kit"* alongside eleven kit files. And `git
add .claude` fails on an ignored directory with `The following paths are ignored by
one of your .gitignore files: .claude`, not `fatal: pathspec`. On git 2.54 it exits
1 and **stages every other path on the line anyway** while `&&` skips the commit;
the missing-path failure exits 128 with the index untouched.

**Read `git status` first, then edit the line.** Name the kit's own files and drop
`src` and `tests`, or `git stash push -- src tests` first with a backup. Force-track
the settings file per row 3 and name it, not its directory.

## 5. Work in progress inside `CERT_PATHS` — Step 4's and Step 9's `VERIFY: PASS`

`CERT_PATHS` is what is certified; the assumed layout is `src`, `tests`.
With one modified file under `src/`, both required green checkpoints are
unreachable: `VERIFY: FAIL (exit 1) … RED: judges`. `THE CERTIFIED TREE is NOT
COMMITTED` names the adopter's own file. The runner is correct.

**Back up, stash, certify, restore, report both states**. On the walk: the diff
saved outside the repository with its sha256 recorded, the stash taken as a second
backup, the certifying run performed, the work restored, byte-identity verified
afterwards. Both states are true.

## 6. A test suite you already trust — Step 3, and Step 4's existing-suite route

The kit promises to wire the gates you already have, but supplied only the
gate-table schema. `pytest` appeared exactly once in the kit, as a directory name
to skip. A gate reading `python -m pytest -q` gets
`46 passed, 4 skipped`, a numerator with no denominator, so a suite that has
stopped collecting prints `3 passed` and certifies. The walker wrote a 161-line
adapter.

**Use `modules/03-verification/gate_line.py`.** Copy it into `tools/`, run
`--gate-spec` to print the `GATES` entry, and put `tools/gate_line.py` in
`JUDGE_PATHS`. Size the floor with `--collect-only`. pytest is proven against six
committed golden fixtures; every other runner is UNPROVEN and says so on every run,
and `GATE-LINE.md` is then the contract you implement by hand.

## 7. CI that ends up weaker than the local gate — after Step 6

The repository's CI ran `python -m pytest -q` across three Python versions. After
adoption the certification is `python tools/verify.py`. It enforces the floor, the
skip ceiling, the subset veto, the hook arming and the
[judge surface](GLOSSARY.md) — **none of which CI runs**. From Step 6 the local
gate proves strictly more than CI.

**Log the divergence as adoption debt** in your own `docs/FAILURE-FLOOR.md`, and
close it when you adopt module 07.

## Also measured, at Level 1

`LEVEL-1.md` installs documents only, and two of its steps collide the same way.
[record: `KNOWN-ISSUES.md` Round #21]

- **An existing `kit.config`**. Step 2 printed `cp kit.config.example
  ./kit.config`, which overwrites a hand-written config. Append the keys you are
  missing at their shipped value instead [check: `doctor:l1-config-complete`].
- **Ledgers under other names**. The four ledger filenames are fixed and
  `LEDGERS_DIR` is the only thing you can move. A repository already keeping a
  `LESSONS-LEARNED.md` or a `TOKEN_LEDGER.md` therefore ends with two ledgers
  answering one question. Rename onto the kit's name, freeze the existing file as
  the record up to adoption, or move `LEDGERS_DIR`
  [check: `doctor:l1-ledger-collision`].

## What this page does not cover

- **Repositories larger or older than the one walked.** One project, one language,
  one test runner, one maintainer. A monorepo, or a repository whose CI is
  load-bearing, will meet collisions not listed here.
- **The team case**. `.claude/settings.json` is per-machine, committed and judged at
  once, and arrives on the second machine whatever the repository's age
  [record: `KNOWN-ISSUES.md`, "Whose settings file? — the team story"].
- **Anything a walk cannot see**. A walk finds commands that do not run as printed
  and checkpoints that do not match, not a step whose explanation is wrong while
  its commands work.
