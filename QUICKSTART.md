# QUICKSTART — the first session

Ten steps, Step 0 to Step 9, in dependency order. Each ends in output you can
read.

Budget: 90 minutes to two hours for Steps 0–2, 4–7 and 9, of which Step 4 is
45–60; an afternoon of thinking for Step 3, which does not compress; 15 minutes
for Step 8.

Per-step detail (rationale, measured failure modes, existing-repository
branches) is held in the maintainer's records, not shipped here; `[detail:
appendix, Step N]` marks point at it; each step here carries everything the
step needs. Terms: `GLOSSARY.md`.
`[check: X]` names the mechanical layer that enforces a rule; the register of
those layers is `checks-registry.json`. `[record: Y]` names where a rule's
history lives.
[check: `tools/adoption_smoke.py` phase 9 walks Steps 2 and 4–9 against a
throwaway repo, running the commands rather than the prose.]

Before Step 1: `LEVEL-1.md` if you have not decided to adopt,
`EXISTING-PROJECT.md` if the repository exists.

## Shell

Every command block runs as-is in `pwsh`, `bash` and Git Bash except in eight
places, each marked inline with a warning marker.

1. One directory per `mkdir` line.
2. No backslash line-continuations; long commands are single lines.
3. Forward slashes work everywhere, including Windows.
4. `⚠ Debian/Ubuntu:` substitute `python3` for `python`.
5. `⚠ Windows:` add a `.gitattributes` with `* text=auto` before your first
   commit. [detail: appendix, Shell]

---

## Step 0 — Prove the tooling works before you configure anything (3 min)

Run these in the kit clone, before you touch your own project.

```bash
git --version                           # any recent git; measured on 2.54
python --version                        # 3.10 or newer
python tools/deident_scan.py --selftest      # DEIDENT SELFTEST: PASS
python tools/statusline.py --selftest       # STATUSLINE SELFTEST: PASS
python tools/expectation_lint.py --selftest # EXPECTATION-LINT SELFTEST: PASS
python tools/expectation_lint.py            # EXPECTATION LINT: PASS - N checked, 0 self-referential
python tools/adoption_smoke.py              # ADOPTION SMOKE: PASS
python modules/03-verification/verify.py --selftest        # VERIFY SELFTEST: PASS
python modules/02-enforcement/hook_fixtures.py --selftest  # HOOK-FIXTURE SELFTEST: PASS
python modules/02-enforcement/hook_fixtures.py --strict --armed .claude/settings.json
```

**Checkpoint:** all ten lines exit 0 — two version checks, five selftests, one
lint over the kit's check registry, the adoption smoke, and the live fixture run,
which ends `HOOK FIXTURES: 38/38 passed, 0 skipped, 2 n/a`. Selftest counts are
not contracts; read the word `PASS`. [record: `docs/PREREQUISITES.md`]

---

## Step 1 — Create your repo, and copy the config OUT of the kit (10 min)

Everything from here happens in YOUR project; the kit is read-only.

```bash
# the first two lines are the NEW-PROJECT route; on an existing repository,
# `cd` there instead and start at the copies
mkdir -p /path/to/your-project && cd /path/to/your-project
git init                       # git from minute one - the judges gate needs it

cp /path/to/kit/kit.config.example        ./kit.config
cp /path/to/kit/kit.config.local.example  ./kit.config.local
```

Skip a `cp` whose target exists; `cp` overwrites without asking. In `kit.config`:

1. Fill `PROJECT_NAME` and the three tier names.
2. Fill `FORBIDDEN_SPAWN_TIER`, usually `ORCHESTRATOR_TIER`'s value.
3. Confirm `GATE_COMMAND`; it ships as `python tools/verify.py`. That file does
   not exist yet — Step 4.2 creates it.
4. Set `PROTECTED_PATH_ENABLED = false`.
5. Omit `PROJECT_ROOT`. The key does not fill the `{{PROJECT_ROOT}}` slot.
6. Leave every other key at its shipped value. Four keys come back later,
   each at the step that needs it: `JUDGE_PATHS` and `CERT_PATHS` at the end
   of Step 4, `KNOWLEDGE_DIR` at Step 6, `RATIO_CEILING` at Step 7.
   `RATIO_CEILING` is the one you may leave as shipped: it ships as
   `derive-from-your-own-data`, and that value is allowed to survive adoption
   until you have measurements of your own. Every other shipped placeholder is
   a fill-in you owe.

`kit.config` is committed; `kit.config.local` is gitignored and holds the
absolute paths.

**Checkpoint:** the first line prints the five keys plus `GATE_COMMAND`; the
second prints nothing.

```bash
grep -nE '^(PROJECT_NAME|ORCHESTRATOR_TIER|LANE_TIER|SWEEP_TIER|FORBIDDEN_SPAWN_TIER|GATE_COMMAND) *=' kit.config
grep -nE '^(PROJECT_NAME *= *Example Project *$|(ORCHESTRATOR|LANE|SWEEP|FORBIDDEN_SPAWN)_TIER *= *your-)' kit.config
```

```powershell
# ⚠ pwsh: no grep
Select-String -Path kit.config -Pattern '^(PROJECT_NAME|ORCHESTRATOR_TIER|LANE_TIER|SWEEP_TIER|FORBIDDEN_SPAWN_TIER|GATE_COMMAND) *='
Select-String -Path kit.config -Pattern '^(PROJECT_NAME *= *Example Project *$|(ORCHESTRATOR|LANE|SWEEP|FORBIDDEN_SPAWN)_TIER *= *your-)'
```

Read the output, not `$?`. [detail: appendix, Step 1]

---

## Step 2 — See the enforcement layer fire (5 min)

This step is the one place you work inside the kit clone. It ends by returning
you to your project.

```bash
cd /path/to/kit/modules/02-enforcement
python hook_fixtures.py --strict

# and prove the dead-man clause, which matters more than the green run
python hook_fixtures.py --make-deadman <scratch-dir>
python hook_fixtures.py --hook <scratch-dir>/hook_model_gate.py    # 0/N — RED
```

`<scratch-dir>` is any writable directory: `/tmp/dead`, or `$env:TEMP/dead` in
pwsh; `--make-deadman` creates it.

```powershell
# ⚠ pwsh: bash's `VAR=x cmd` sets the var for ONE command; $env: persists
$env:KIT_CONFIG = "C:/path/to/kit/kit.config"
python hook_fixtures.py --strict
Remove-Item Env:KIT_CONFIG
```

Return to your project. Every step from here runs with your repo root as the
working directory, and the kit stays read-only.

```bash
cd /path/to/your-project
```

**Checkpoint:** you have watched the gate deny an undeclared spawn, and a dead
gate report as failure rather than permission. A gate never red is unproven.

---

## Step 3 — Manufacture your first oracle (an afternoon of thinking)

Do this before writing any gate. If you cannot state the check for done, you
cannot charter the lane. Work in your repo root, where Step 2 left you.

1. Read Part 1 of `modules/03-verification/ORACLE-WORKSHEET.md`.
2. Read `modules/03-verification/GATE-LINE.md`, the contract for the line: a
   self-consistent ratio rather than a bare count, a distinct failure line the
   gate's `fail_pattern` can veto on, and a subset-honesty suffix.
3. On an empty repo, create the subject: one source file and one test file, in
   `src/` and `tests/`.
4. Fill one worksheet page for the most important thing your project must not
   break: the required output line, and the floor it carries.
5. Create the directory the worksheet lands in, if it is not there yet:

```bash
mkdir -p docs
```

6. Save the page as `docs/ORACLE-<gate-name>.md`, named for the gate.

**Checkpoint:** one worksheet page holding a line of text that does not exist
yet, a number, and a negative control. [detail: appendix, Step 3, including the
`doctor:vacuous-gate` ATTENTION this leaves behind]

---

## Step 4 — Stand up the certification runner, wiring and all (45–60 min your first time)

### 4.1 Ignore rules first

```bash
printf '__pycache__/\n*.pyc\nkit.config.local\n.claude/sidequest.json\n' >> .gitignore
```

```powershell
# ⚠ pwsh: no printf, and Add-Content's own line terminator is CRLF - so this
# form reads the terminator the file already uses and keeps it
$raw = if (Test-Path .gitignore) { Get-Content .gitignore -Raw } else { '' }
$eol = if ($raw -match "`r`n") { "`r`n" } else { "`n" }
'__pycache__/','*.pyc','kit.config.local','.claude/sidequest.json' |
    ForEach-Object { "$_$eol" } | Add-Content .gitignore -NoNewline
```

`verify.py` prints `VERIFY: ABORTED` over a judged path an ignore rule covers.
Run `git check-ignore -v <the path>`, then force-track. Never delete the rule:

```bash
git add -f .claude/settings.json      # substitute the path the abort named
```

### 4.2 Copy the runner and the enforcement files, before the first run

```bash
mkdir -p tools
mkdir -p .claude
cp /path/to/kit/modules/03-verification/verify.py         tools/verify.py
cp /path/to/kit/modules/02-enforcement/hook_model_gate.py tools/
cp /path/to/kit/modules/02-enforcement/hook_fixtures.py   tools/
cp /path/to/kit/tools/statusline.py                       tools/   # module 05
cp /path/to/kit/modules/04-ledgers/escape_rate.py         tools/   # module 04
mkdir -p docs
cp /path/to/kit/modules/04-ledgers/JUDGMENT-LEDGER.md     docs/    # module 04
cp /path/to/kit/VERSION                                   ./VERSION
cp /path/to/kit/modules/02-enforcement/settings.json.template .claude/settings.json
```

That last copy leaves an unfilled template in place. Fill it now, following
§4.3 below: substitute its four slots, delete its header block, and parse the
result. Steps 4.7 and 5 both abort if `.claude/settings.json` is missing or
does not parse.

The ordering is load-bearing: the startup assertion refuses to run over a path
not in the tree. Refresh `VERSION` on every kit update [check: `doctor:version`].
Dropping a module means deleting its gate from `GATES` and `RUN_ORDER`, and its
constants. [detail: appendix, Step 4]

### 4.3 Fill the settings template — four slots

1. `{{PYTHON_BIN}}`: the interpreter name you type at a prompt.
2. `{{PROJECT_ROOT}}`: the absolute path to your repo root, forward slashes,
   typed by hand. Left empty, `--armed` reports `UNSTARTABLE:`.
3. `permissions.ask`: delete the block if the tripwire is off, per Step 1.
4. `STATUSLINE_CMD`: set it in `kit.config.local` **before** substituting, with
   no double quotes. [record: `KNOWN-ISSUES.md`, SB-B]

```
STATUSLINE_CMD = python /home/you/project/tools/statusline.py
STATUSLINE_CMD = python '/home/you/My Project/tools/statusline.py'
```

Delete the header block — here it is the `__COMMENT__` key — then parse the
result: `python -c "import json; json.load(open('.claude/settings.json'))"`.
Every template in this kit opens with a header block; deleting it is the same
action each time, and only the marker changes.

### 4.4 Substituting mechanically — optional on an empty repo, required on one that already holds these files

```bash
python /path/to/kit/tools/kit_render.py --target .   # after --selftest and --list
```

Renders land at `<name>.kit-new` with a diff; the settings file is merged as
JSON. [detail: appendix, Step 4]

### 4.5 ONE MACHINE PER SETTINGS FILE

`.claude/settings.json` describes THIS machine, is committed, and is judged. On
a second machine certification returns `VERIFY: FAIL — RED: judges, hooks`, and
the kit ships no split.
[record: `KNOWN-ISSUES.md`, "Whose settings file? — the team story"]

### 4.6 Edit the runner: nine edits

The runner ships two example gates, `example_unit` and `example_lint`. They run
against toy scripts in the kit's `modules/03-verification/examples/`. Both go,
and your Step-3 gate takes their place.

1. **`JUDGE_PATHS`**: what decides what green means. Name the judge files, not
   `"tools"`; include `kit.config`.
2. **`CERT_PATHS`**: what is being certified. A different list, on purpose.
3. **`HOOK_FIXTURES`**, **`HOOK_SETTINGS`**: `tools/hook_fixtures.py`,
   `.claude/settings.json`.
4. **`ESCAPE_TOOL`**, **`ESCAPE_LEDGER`**: `tools/escape_rate.py`,
   `docs/JUDGMENT-LEDGER.md`. Repoint them or the startup assertion aborts.
5. That gate's ceiling is a literal in the gate entry; ship-value 35.0 is the
   kit's own number. [record: `modules/04-ledgers/TOKEN-LEDGER.md`] [check:
   `python tools/escape_rate.py --selftest` requires it to match `DEFAULT_CEILING`]
6. Rename `example_unit` to your Step-3 gate, in both `GATES` and `RUN_ORDER`,
   and point its command at the command your gate runs.
7. Delete `example_lint` from `GATES` and `RUN_ORDER` both. Deleting it from
   `GATES` alone leaves the selftest red.
8. Add a `selftest()` check that feeds your gate the three lines it must
   refuse: a zero count, a count below your Step-3 floor, and a subset run.
   Each one is well formed, so your `require` pattern accepts it and the run
   would certify. The check is what stops it.
9. Copy `JUDGE_PATHS` and `CERT_PATHS` into `kit.config`. The `verify.py`
   constants are authoritative; the config keys document them.

For a test suite you already have, use the adapter rather than the runner, and
add `tools/gate_line.py` to `JUDGE_PATHS`:

```bash
cp /path/to/kit/modules/03-verification/gate_line.py tools/
python tools/gate_line.py --pytest --expect-skips <your skip count>   # see the line
python tools/gate_line.py --gate-spec --floor <your floor> --max-skips <your skip count>
```

Set the floor above your largest test module (`--collect-only`).

### 4.7 Run, commit, run again

```bash
# this block requires the nine edits in 4.6 above
python tools/verify.py --list
python tools/verify.py --selftest        # must print: VERIFY SELFTEST: PASS
python tools/verify.py                   # expect RED - see below
# EDIT THE NEXT LINE FIRST: drop any path you do not have yet, and run
# `git status` first - most of these are DIRECTORY pathspecs, and on a tree with
# unrelated uncommitted work they stage it into this commit too
git add tools .claude kit.config .gitignore VERSION src tests docs && git commit -m "adopt the kit"
python tools/verify.py                   # must print: VERIFY: PASS
```

That line is the most dangerous command here. On a repository with other work
in it, use the file-targeted form instead:

```bash
git add tools/verify.py tools/hook_model_gate.py tools/hook_fixtures.py tools/statusline.py tools/escape_rate.py kit.config .gitignore VERSION docs
```

`.claude/settings.json` is deliberately absent: the `git add -f` earlier in
the step already staged it. A failed `git add` skips the commit through `&&`
and can still leave the index loaded. [detail: appendix, Step 4]

**Checkpoints. Read the VERDICT WORD, never `$?` alone.** Exit 2 is either
`INSTRUMENTED` or `ABORTED`, opposite kinds of news.

| Run | Expect |
|---|---|
| `--selftest` | **`VERIFY SELFTEST: PASS`** |
| pre-commit | **`VERIFY: FAIL`** naming **`RED: judges`** — the new files are uncommitted |
| the commit | **`docs/ORACLE-<gate-name>.md`** among the files taken. If absent, you skipped Step 3. |
| post-commit | **`VERIFY: PASS`**, if nothing in `CERT_PATHS` is uncommitted |

Read the repo root the runner resolved; if it is `tools/`, stop.

**Work in progress inside `CERT_PATHS`.** The run reads
`THE CERTIFIED TREE is NOT COMMITTED` naming your file. Certification is a
property of a tree, so back up, stash, certify, restore. Never commit unfinished
work to manufacture a green:

```bash
git diff > /path/outside/this/repo/wip.patch   # backup 1, and note its sha256
git stash push -m "wip: certifying"            # backup 2
python tools/verify.py                         # the certifying run
git stash pop
```

Take both backups; record both states, not only the flattering one.

---

## Step 5 — Prove your gate can go red without editing a file (5 min)

```bash
echo '{"expect_min": {"<your-gate>": 999999}}' > <scratch-dir>/nc.json
python tools/verify.py --only <your-gate> --nc <scratch-dir>/nc.json
```

```powershell
# ⚠ pwsh: /tmp does not exist
'{"expect_min": {"<your-gate>": 999999}}' | Set-Content "$env:TEMP/nc.json"
python tools/verify.py --only <your-gate> --nc "$env:TEMP/nc.json"
```

**Checkpoint:** the summary line reads **`VERIFY: INSTRUMENTED`**, with your gate
red on a floor breach. `ABORTED` also exits 2, and means it refused to start.

---

## Step 6 — Standing rules, and prove the hook (8 min)

```bash
# the first line is the NEW-FILE route. If you ALREADY HAVE a CLAUDE.md, do
# not run it - read the merge instruction below instead.
cp /path/to/kit/modules/01-governance/CLAUDE.md.template ./CLAUDE.md
cp /path/to/kit/tools/deident_scan.py                    tools/
```

**If this repository already has a `CLAUDE.md`, that first line destroys it.**
Merge instead, your rules preserved verbatim under a heading of their own. Where
the two rule sets conflict, that is a decision to make now and write down, not a
duplicate to leave standing. [detail: appendix, Step 6]

1. Add `tools/deident_scan.py` to `JUDGE_PATHS` in `tools/verify.py` and
   `kit.config`.
2. Re-run `python tools/verify.py --selftest`.
3. Substitute the slots in `CLAUDE.md`; delete every rule you cannot yet enforce
   or do not yet believe.
4. Delete the header block rather than substituting inside it. Here the marker
   is `DELETE THIS COMMENT BLOCK`.
5. Read the checkpoint shape contract under the rules file's first line; no
   template ships for it. [record: `KNOWN-ISSUES.md`]

Expect `judges` red until the end of Step 9.

**`KNOWLEDGE_DIR` is a decision, not a fill-in: make it here.** It names where
durable knowledge lives outside the repo; the same slot appears in
`PROFILE-TEMPLATE.md` at Step 8. An absolute path goes in `kit.config.local`, the
repo path `docs` in `kit.config`. Amend the rules file's
`(that copy is source of truth)` parenthetical to name whichever copy is.
[detail: appendix, Step 6]

```bash
python tools/hook_fixtures.py --strict --armed .claude/settings.json
grep -nE '\{\{|DELETE THIS COMMENT BLOCK' CLAUDE.md    # must print NOTHING
```

```powershell
# ⚠ pwsh: no grep
python tools/hook_fixtures.py --strict --armed .claude/settings.json
Select-String -Path CLAUDE.md -Pattern '\{\{|DELETE THIS COMMENT BLOCK'
```

**Checkpoint — two things:**

- **The hook:** `armed:` lines for Workflow, Agent, Bash and Edit; no `UNARMED:`;
  no `CONFIG WARNING:`; `0 skipped`; exit 0. Some `n/a` is expected.
- **The rules file:** no `{{` surviving in `CLAUDE.md`, no header block left. A
  green fixture run says nothing about `CLAUDE.md`.
  [check: `tools/kit_doctor.py --level1`]

---

## Step 7 — Start the ledgers empty (3 min)

```bash
mkdir -p docs/reports
# JUDGMENT-LEDGER.md is already in docs/ - Step 4 copied it, because the
# runner's escapes gate reads it. These are the other three.
cp /path/to/kit/modules/04-ledgers/FAILURE-FLOOR.md   docs/
cp /path/to/kit/modules/04-ledgers/LESSONS.md         docs/
cp /path/to/kit/modules/04-ledgers/TOKEN-LEDGER.md    docs/
```

Name them explicitly; do not glob `docs/`, which holds its own `README.md`.

1. Substitute the slots in all four ledgers; delete each header block. Here the
   marker is `SKELETON`. `TOKEN-LEDGER.md` carries `{{RATIO_CEILING}}`, which
   takes whatever `kit.config` holds — the shipped value or your own.
2. Add your first rule row to `FAILURE-FLOOR.md`: the model-tiering hook, layer
   `HOOK`, zone `B`, status `STRUCTURAL`, last fired `never`. Zone `B` means
   inside the agents' blast radius; `docs/FAILURE-FLOOR.md` defines both zones
   above its table.
3. Keep or delete each seed lesson in `LESSONS.md`, deliberately.

**Checkpoint:** four ledger files — slots substituted, no `SKELETON` header block
left, no `{{` surviving — one with a real row, and your `docs/README.md`
untouched. Run Step 6's checkpoint line over `docs/*.md`, with `SKELETON` for
`DELETE THIS COMMENT BLOCK`. In these files `RATIO_CEILING`'s shipped value is
the one allowed survivor, per Step 1; every other shipped placeholder is a
fill-in you missed. [detail: appendix, Step 7]

---

## Step 8 — Run (or schedule) the seed interview (15 min)

If the owner is someone else, put this on their calendar for the first week.
Working solo, answer the five questions yourself, in writing, today.

1. Open `modules/08-collaboration/SEED-INTERVIEW.md`, ask the five questions, and
   capture verbatim. Question 5, the betrayal line, is the highest-value one: its
   answer is a hard constraint, not a preference.
2. Copy the template:

```bash
cp /path/to/kit/modules/08-collaboration/PROFILE-TEMPLATE.md docs/collaboration-profile.md
```

3. Substitute `{{KNOWLEDGE_DIR}}` with the Step 6 value before deleting the
   header block the slot sits in.
4. Delete the header block: the `<!-- … -->` comment opening
   `TEMPLATE - the living collaboration profile`. Step 7's scan misses it.
5. On the repo-path branch, amend the profile's maintenance rule
   "The durable copy is source of truth" to name the repo copy.

`CLAUDE.md` names `<your KNOWLEDGE_DIR value>/collaboration-profile.md` as source
of truth. If that is outside the repo, write the profile there and treat the repo
copy as a mirror. [detail: appendix, Step 8]

```bash
grep -nE '\{\{|Delete this comment on adoption|TEMPLATE - the living' docs/collaboration-profile.md    # must print NOTHING
```

```powershell
# ⚠ pwsh: no grep
Select-String -Path docs/collaboration-profile.md -Pattern '\{\{|Delete this comment on adoption|TEMPLATE - the living'
```

**Checkpoint — two things:**

- **The content:** five verbatim answers and an explicit overrides table against
  `modules/08-collaboration/DEFAULT-CONTRACT.md`. An empty table is a real
  answer.
- **The rendering:** the line above prints nothing. If your profile lives outside
  the repo, run the same line there.

---

## Step 9 — Prove nothing personal is about to be published (3 min)

First, commit what Steps 6, 7 and 8 created: the scan is `--tracked-only`, and
untracked means unscanned.

```bash
# RUN `git status` FIRST: `docs` is a DIRECTORY pathspec - the same hazard, and
# the same edit, as Step 4's commit line
git add CLAUDE.md tools/deident_scan.py tools/verify.py docs kit.config && git commit -m "standing rules, ledgers, profile"
```

Every file on that line is inside `JUDGE_PATHS`. Named paths, not `-A`.

```bash
# --tokens takes a plain text file, ONE TOKEN PER LINE - your name, your
# username, machine path fragments, your employer. `#` starts a comment.
python tools/deident_scan.py --root . --tokens <a-path-outside-this-repo> --strict --tracked-only
```

Keep the token list outside the repo: a committed one is itself the leak. Read
the `tokens    :` line, which counts distinct tokens rather than lines; the
`scope     :` line; and the file list, since the tool counts occurrences.

Three hits are expected: `.claude/settings.json`, `docs/collaboration-profile.md`
and pre-existing package metadata. Anything else is the escape. Every hit is
reviewed and explained, and the remediation is `--exclude` per reviewed file,
never deleting a token. [detail: appendix, Step 9]

```bash
python tools/deident_scan.py --root . --tokens <list> --strict --tracked-only --exclude ".claude/settings.json"
```

On the tripwire-ON branch add `--exclude "CLAUDE.md"`.

**Checkpoint:** `DEIDENT SCAN: 0 hits - exit 0`, reached by excluding reviewed
files — one on the recommended branch, two with the tripwire on, plus one per
pre-existing file you accounted for.

```bash
python tools/deident_scan.py --selftest    # proves it fires on a planted token
python tools/verify.py                     # must still print: VERIFY: PASS
```

The document is finished at `VERIFY: PASS` and `DEIDENT SCAN: 0 hits`. With
unfinished work in `CERT_PATHS` the run is red and correct: use Step 4's stash
cycle.

---

## Then, in the following week

1. Add CI (module 07): the first control your agents cannot edit. Read
   `modules/07-ci/BRANCH-PROTECTION.md`; record whether it is a gate or a
   tripwire.
2. Add the status board (module 05); `tools/statusline.py` is the portable one.
3. Add the sidequest skill (module 06).
4. Publish your first escape rate: items a human found that an existing check
   should have caught. Append the round to `docs/JUDGMENT-LEDGER.md`, which
   `python tools/escape_rate.py` reads.
5. Turn on the protected-path tripwire once something must not move unnoticed.
6. Re-run `python tools/verify.py --selftest` after every runner change, and wire
   it into CI. It is the only check that covers *your* runner.
7. Re-run `python tools/adoption_smoke.py` from the kit clone after a kit update.
   `--runner <path to your tools/verify.py>` points it at your copy, but only
   while that copy still carries the shipped example gates.

## Notes

This order is by dependency; `docs/ADOPTION-LEVELS.md` orders by commitment. The
smoke check runs the commands, not the prose, so a step whose explanation is
wrong while its commands work will pass. [record: `smoke:phase9-document-order`]
