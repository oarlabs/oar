# QUICKSTART — the first session

Work through the steps in order. **The order is a tested property**:
`tools/adoption_smoke.py` phase 9 executes **Steps 2, 4, 5, 6, 7 and 9** — the
steps with commands — against a throwaway repo, in this sequence, and asserts
each checkpoint is reachable where the document places it. It also asserts
**Step 1's checkpoint** against the `kit.config` it writes for that repo,
**Step 4's commit checkpoint** including the oracle worksheet page, and **Step
8's rendering checkpoint** over the copied collaboration profile. Steps 0 and 3
are not walked — Step 0 runs against the kit itself and Step 3 is a decision —
and Step 8's interview is a conversation, so only the file it produces is
checked. Note the check's
limit: it runs the *commands*, not the *prose*. A step whose explanation is
wrong while its commands still work will pass.

Every step ends in **something you can run and see**. If a step produces no
visible output, it is not finished.

**Budget:** **90 minutes to two hours of doing** (steps 0–2, 4–7, 9), plus **an
afternoon on Step 3** — your first oracle is thinking work and does not
compress — plus **the Step 8 seed interview**: fifteen minutes tonight if you
are the project's owner, or a scheduled slot on the owner's calendar if that
is someone else. The per-step figures sum to that range, and **Step 4 is most
of it** (45–60 minutes on a first adoption: a JSON template substituted by
hand, four constants and a gate table edited inside the runner, a selftest case
written, and two config keys reconciled). Someone who has adopted the kit
before will beat these numbers; the estimates are for the first time.

## Shell — measured, not asserted

The shell claim is **checked by a machine**: `adoption_smoke.py` phase 9
executes Step 4's shell block through `pwsh -NoProfile -Command` when pwsh is
on the PATH, and prints a skip-with-reason when it is not. What is written
below is what that check enforces.

> Every command block runs as-is in `pwsh`, `bash` and Git Bash **except in
> these seven places**, each marked inline where it occurs:
>
> 1. **Step 1** — the checkpoint that reads `kit.config` back (`grep` vs
>    `Select-String`).
> 2. **Step 2** — setting an environment variable for one command
>    (`VAR=x cmd` vs `$env:VAR = 'x'`, which persists and must be removed).
> 3. **Step 2** — the `<scratch-dir>` placeholder, used in two commands. Fill
>    it in with `/tmp/dead` or `$env:TEMP/dead`.
> 4. **Step 4** — appending lines to a file (`printf … >>`).
> 5. **Step 5** — the `<scratch-dir>` placeholder again, for a JSON file.
> 6. **Step 6** — the checkpoint that reads `CLAUDE.md` back (`grep` vs
>    `Select-String`).
> 7. **Step 8** — the checkpoint that reads the collaboration profile back
>    (`grep` vs `Select-String`).

Two things that are *not* exceptions, because the commands were made portable
instead: **one directory per `mkdir` line** (`mkdir -p a b` is a
positional-parameter error in pwsh) and **no backslash line-continuations**
anywhere (a pwsh parse error; long commands are single lines here).

Forward slashes work everywhere, including Windows.

> **`⚠ pwsh: -p` only gets you half of `mkdir -p`.** The flag prefix-matches
> `-Path`, so the lines below parse — but on a directory that **already
> exists** pwsh raises `New-Item: An item with the specified name ... already
> exists` where bash would say nothing. That error is expected and harmless:
> the directory you wanted is there, and the next command runs. It fires on
> any repo that already has `tools/`, `.claude/` or `docs/`, and on every
> re-run. To avoid it, use `New-Item -ItemType Directory -Force <dir>`, which
> is pwsh's real no-op.

> **`⚠ Debian/Ubuntu:` `python` may not exist** — those hosts ship `python3`
> and no `python` shim unless `python-is-python3` is installed. Substitute
> `python3` throughout, or install the shim. Nothing else changes.

> **`⚠ Windows: line endings.`** Before your first commit, consider a
> `.gitattributes` with `* text=auto` (and `*.py text eol=lf` if you care).
> Without it a Windows checkout can rewrite line endings and the `judges` gate
> will honestly report a tree full of modifications you did not make. The kit
> ships none, because adding one to an existing repository renormalises it —
> your decision, and cheapest on day one.

---

## Step 0 — Prove the tooling works before you configure anything (3 min)

Run these **inside the kit clone**, before you go near your own project.

```bash
python --version                        # 3.10 or newer
python tools/deident_scan.py --selftest      # DEIDENT SELFTEST: PASS
python tools/statusline.py --selftest       # STATUSLINE SELFTEST: PASS
python tools/expectation_lint.py --selftest # EXPECTATION-LINT SELFTEST: PASS
python tools/expectation_lint.py            # EXPECTATION LINT: clean
python tools/adoption_smoke.py              # ADOPTION SMOKE: PASS
python modules/03-verification/verify.py --selftest        # VERIFY SELFTEST: PASS
python modules/02-enforcement/hook_fixtures.py --selftest  # HOOK-FIXTURE SELFTEST: PASS
python modules/02-enforcement/hook_fixtures.py --strict --armed .claude/settings.json
```

**Checkpoint:** all nine lines exit 0 — a version check, **five selftests**,
one lint over the kit's own check registry, the adoption smoke, and the live
fixture run, which ends
`HOOK FIXTURES: 38/38 passed, 0 skipped, 2 n/a`. The two `n/a` are the
protected-path fixtures: `n/a` rather than `skipped` because the kit ships that
tripwire **off**, which is the same advice Step 1 gives you.

`expectation_lint.py` is worth reading the output of. It prints every
**waiver** on every run — the handful of checks that legitimately read their
expectation from the thing they are checking, each with the reason and what
covers the gap instead.

`adoption_smoke.py` is the interesting one: a throwaway repo, the steps below
performed mechanically, and the results asserted — including that a dirty
certified path really does turn the `judges` gate red, and that this document
can be obeyed in order.

> **Selftest counts are not contracts.** They fall when you delete the example
> gates and rise as you add checks. Read the word `PASS`.

---

## Step 1 — Create your repo, and copy the config OUT of the kit (10 min)

**Everything from here happens in YOUR project, not in the kit clone.** Treat
the kit as read-only: it may literally be a read-only clone, and its
`kit.config` is a worked example its own selftests depend on.

```bash
mkdir -p /path/to/your-project && cd /path/to/your-project
git init                       # git from minute one - the judges gate needs it

cp /path/to/kit/kit.config.example        ./kit.config
cp /path/to/kit/kit.config.local.example  ./kit.config.local
```

In `kit.config`, fill in five keys — **`PROJECT_NAME`, the three tier names, and
`FORBIDDEN_SPAWN_TIER`** (usually the same value as `ORCHESTRATOR_TIER`) — and
**confirm `GATE_COMMAND` matches how you run your runner**. That last one is a
check, not a fill: it ships as `python tools/verify.py`, which is already
correct for the layout Step 4 builds, so on that layout you change nothing.
Change it if your runner lands somewhere else or needs a different interpreter
name (`python3` on Debian/Ubuntu). Leave everything else for now. Four keys come back later, each
at the step that needs it: `JUDGE_PATHS` and `CERT_PATHS` at the end of Step 4,
`KNOWLEDGE_DIR` at Step 6 (in **this** file if the value is repo-relative, in
`kit.config.local` if it is an absolute path — see below), and `RATIO_CEILING`
at Step 7.

`FORBIDDEN_SPAWN_TIER` is easy to skip because it looks like a duplicate of
`ORCHESTRATOR_TIER`, and skipping it fails silently: the tier rule stays
unenforced, one fixture reports `SKIP`, and Step 6's `0 skipped` checkpoint
becomes unreachable.

**Do NOT put `PROJECT_ROOT` in `kit.config`.** It is an absolute path, and
`kit.config` is the committed half. Either omit it entirely — `.git` discovery
covers a normal checkout, which is almost certainly your case — or set it in
`kit.config.local`. The same goes for `PROTECTED_PATH` when you eventually turn
the tripwire on: `PROTECTED_PATH_ENABLED` is a shareable boolean and belongs in
the committed file; the path itself is one machine's geography and does not.
**The rule is general** — `PROJECT_ROOT`, `PROTECTED_PATH`, `STATUSLINE_CMD` and
`KNOWLEDGE_DIR` all follow it: whichever of them holds an absolute path on your
machine goes in `kit.config.local`, and only there.

**The config key `PROJECT_ROOT` and the template slot `{{PROJECT_ROOT}}` are two
different things.** The key is a *runtime* value with two narrow uses: the
runner and the status board resolve the repo by walking up to `.git` first and
read the key only when that fails, and the hook reads it to locate the tree a
cert-green token would pre-authorise — without it that pre-authorisation never
fires, which is the safe direction. (If you turn the protected-path tripwire on
later, set the key in `kit.config.local` then; module 02's README says why.)
The slot is *text you type once*, at Step 4, when you substitute the harness
settings template. There is no templating engine in this kit — substitution is
by hand — so nothing reads the key to fill the slot. Its value is the absolute
path to your repo root, forward slashes, and it goes into
`.claude/settings.json` whether or not the key is set anywhere. Leaving the key
empty is the recommended answer and does **not** mean leaving the slot empty: an
empty slot produces `python "/tools/hook_model_gate.py"`, which the next
`--armed` run reports as `UNSTARTABLE:`.

| File | Committed? | Holds |
|---|---|---|
| `kit.config` | **yes** | repo-relative, shareable values |
| `kit.config.local` | **no** (gitignored) | absolute paths, the protected location |

A config that is not in the repo is a config the tools do not find — and a rule
the tools do not find **silently stops existing** while every check still
reports green. That is why the committed half exists. A config full of one
machine's absolute paths is wrong for everyone else who clones, and publishes a
small map of your infrastructure besides. That is why the local half exists.
Both are read from the same directory, `.local` last, later wins.

**Leave the protected-path tripwire OFF** (`PROTECTED_PATH_ENABLED = false`).
Turn a control on when you know what it is protecting. Its two fixtures will
report `n/a` — a counted, printed third state, not a skip, not a gap, and not
something that blocks the clean run Step 6 asks for.

### The absolute paths you cannot avoid

A **harness settings file** must give absolute paths for its hook commands: the
harness does not promise a working directory, and a hook that fails to start
enforces nothing while looking fine. So your committed `.claude/settings.json`
will contain an absolute path, and on most machines that path contains your
username.

Three places want one, and they are all in that one file: each **hook command**,
the **`permissions.ask`** entries if you keep them, and the **`statusLine`**
command if you wire module 05's board. All three need absolute paths for the
same reason — a command that cannot start is a control that silently is not
there.

There is no clever fix, only a choice to make deliberately. Step 9 tells you
exactly how many hits to expect and how to clear them; the short version is that
`.claude/settings.json` is the single *tracked* file that will contain your
username, and `--exclude`-ing that one reviewed file is the honest remediation.
What you must not do is delete the token from your list.

**Checkpoint:** run these from your project root. The first line prints the five
keys you filled plus `GATE_COMMAND`, so you can read the values you chose and
confirm the runner command in the same glance. The second line looks for the
shipped placeholder values still sitting in the five and **must print nothing**.

```bash
grep -nE '^(PROJECT_NAME|ORCHESTRATOR_TIER|LANE_TIER|SWEEP_TIER|FORBIDDEN_SPAWN_TIER|GATE_COMMAND) *=' kit.config
grep -nE '^(PROJECT_NAME *= *Example Project *$|(ORCHESTRATOR|LANE|SWEEP|FORBIDDEN_SPAWN)_TIER *= *your-)' kit.config
```

```powershell
# ⚠ pwsh: no grep
Select-String -Path kit.config -Pattern '^(PROJECT_NAME|ORCHESTRATOR_TIER|LANE_TIER|SWEEP_TIER|FORBIDDEN_SPAWN_TIER|GATE_COMMAND) *='
Select-String -Path kit.config -Pattern '^(PROJECT_NAME *= *Example Project *$|(ORCHESTRATOR|LANE|SWEEP|FORBIDDEN_SPAWN)_TIER *= *your-)'
```

Read the output, not `$?`: `grep` exits 1 when it finds nothing, and finding
nothing is the pass here. Every *other* shipped value in `kit.config` is
supposed to still be there: `JUDGE_PATHS`, `CERT_PATHS`, `KNOWLEDGE_DIR` and
`RATIO_CEILING` come back at their own steps, and the rest are illustrative
defaults you may never need.

### Which shipped values legitimately survive in `kit.config` at done

`kit.config` is the registry of every slot the kit defines, so it ships keys for
modules you have not adopted yet. **A shipped value still sitting in this file
when the document finishes is not automatically a fill-in you missed** — two
kinds belong there, and one more is a named exception:

- **Keys for modules you have not adopted yet.** The toolchain pin and the
  runner's log directory (`TOOLCHAIN_NAME`, `TOOLCHAIN_VERSION_CMD`,
  `VERIFY_OUT_DIR`), module 05's optional board segments
  (`STATUS_BOARD_LINE_FILE`, `AGENT_TRANSCRIPT_DIR`), and module 07's CI keys
  (`CI_TOOLCHAIN_ARCHIVE`, `CI_TOOLCHAIN_SHA512` and the rest of section 6),
  which this document leaves for the following week. Fill each one at the step
  that adopts its module; nothing reads it before then.
- **Keys whose real value lives in `kit.config.local`.** `PROTECTED_PATH` stays
  `NONE` here while the tripwire is off, and `STATUSLINE_CMD` stays `NONE` here
  because Step 4 *requires* the real command to be in the gitignored half. In
  the committed file those are the correct values, not missed ones.
- **`RATIO_CEILING`**, the one deliberate survivor with its own instruction —
  Step 7 says why and when to replace it.

Step 7 applies the opposite rule ("every other shipped placeholder is a fill-in
you missed") to the four **ledger** files it copies, which is where an unfilled
value is always a mistake. That rule is scoped to `docs/*.md`, and this list is
the answer for `kit.config`.

---

## Step 2 — See the enforcement layer fire (5 min)

Back in the kit clone for these, because they exercise the kit's own copies:

```bash
cd /path/to/kit/modules/02-enforcement
python hook_fixtures.py --strict

# and prove the dead-man clause, which matters more than the green run
python hook_fixtures.py --make-deadman <scratch-dir>
python hook_fixtures.py --hook <scratch-dir>/hook_model_gate.py    # 0/N — RED
```

`<scratch-dir>` is any writable directory — `/tmp/dead` on Unix,
`$env:TEMP/dead` in pwsh. `--make-deadman` creates it.

No `KIT_CONFIG` is needed: the tools find `kit.config` by walking **up** from
their own directory (search step 4, in Step 6 below). If you do set it in pwsh,
unset it afterwards or it leaks into the rest of your session:

```powershell
# ⚠ pwsh: bash's `VAR=x cmd` sets the var for ONE command; $env: persists
$env:KIT_CONFIG = "C:/path/to/kit/kit.config"
python hook_fixtures.py --strict
Remove-Item Env:KIT_CONFIG
```

**Checkpoint:** you have watched the gate deny an undeclared spawn, and watched
a *dead* gate report as failure rather than as permission. **A gate that has
never been red is unproven** — the cheapest possible demonstration of the rule
the rest of the kit is built on.

---

## Step 3 — Manufacture your first oracle (an afternoon of thinking)

**Do this before writing any gate.** Open
`modules/03-verification/ORACLE-WORKSHEET.md`, read Part 1 (the shapes), and
fill in **one** worksheet page for the single most important thing your project
must not break.

> If you cannot state the check for done, you are not ready to charter the lane.

You need, concretely: the **required output line** your check will print when
green, and the **floor** — the minimum count that line must carry. If you cannot
write the required line, you have just discovered that you do not yet know what
the check measures. That discovery is the point, and it is why this step is
measured in hours.

**If Step 1 left you with an empty repo**, create the subject before you write
the worksheet: one source file the gate will judge and one test file that
exercises it. `src/` and `tests/` is enough, and it is the layout Step 4's
commit line assumes.

**Where the filled page goes:** `docs/ORACLE-<gate-name>.md` in **your** repo —
one file per gate, named for the gate it specifies, so a gate called
`unit_suite` gets `docs/ORACLE-unit_suite.md`. Create `docs/` if you do not have
it; Step 7 puts the ledgers in the same directory, and Step 4's commit line
stages `docs`, so the worksheet is tracked by the time the certifying run
happens.

**Checkpoint:** one filled worksheet page, saved in your repo, containing a line
of text that does not exist yet, a number, and a negative control.

---

## Step 4 — Stand up the certification runner, wiring and all (45–60 min your first time)

First, the housekeeping that otherwise costs you two confusing reds:

```bash
printf '__pycache__/\n*.pyc\nkit.config.local\n.claude/sidequest.json\n' >> .gitignore
```

```powershell
# ⚠ pwsh: no printf
'__pycache__/','*.pyc','kit.config.local','.claude/sidequest.json' |
    Add-Content .gitignore
```

Python writes `__pycache__/` next to any script it imports; inside `JUDGE_PATHS`
or `CERT_PATHS` that is an uncommitted tree and a correct red you will spend
twenty minutes misdiagnosing. `.claude/sidequest.json` is the same trap with a
longer fuse: session state in a directory people put in `JUDGE_PATHS`, so
without the rule *opening a side quest* makes the project uncertifiable.

**If this repo already has a `.gitignore`, read it now for a rule that covers a
path you are about to judge** — `.claude/` is a common entry, and an ignored,
untracked `.claude/settings.json` is invisible to `git status`, so the `judges`
gate would read clean over the file that decides whether the hooks run at all;
`verify.py` refuses to start on that (`VERIFY: ABORTED`, naming the path and the
`git check-ignore -v` line that finds the rule).

Now copy the runner **and the enforcement files, and write the harness settings
— all before the first run**:

```bash
mkdir -p tools
mkdir -p .claude
cp /path/to/kit/modules/03-verification/verify.py         tools/verify.py
cp /path/to/kit/modules/02-enforcement/hook_model_gate.py tools/
cp /path/to/kit/modules/02-enforcement/hook_fixtures.py   tools/
cp /path/to/kit/tools/statusline.py                       tools/   # module 05
# then substitute the slots in the kit's
#   modules/02-enforcement/settings.json.template
# into .claude/settings.json
```

**This ordering is load-bearing.** `verify.py` ships a `hooks` gate that names
`tools/hook_fixtures.py` and `.claude/settings.json`, and the startup assertion
refuses to run without them — create the settings file later and Steps 4 and 5
abort. Doing it here is what leaves Step 6 as a pure proof step.

The template carries four slots. Two you fill unconditionally:
`{{PYTHON_BIN}}` is the interpreter name you type at a prompt (`python`, or
`python3` on Debian/Ubuntu), and `{{PROJECT_ROOT}}` is the **absolute path to
your repo root**, forward slashes, typed in by hand — see Step 1 for why the
`kit.config` key of the same name does not fill it for you. The other two are
conditional:

- **Tripwire off (Step 1's advice)?** Then **delete the whole `permissions.ask`
  block** from the settings file. Leaving it in with a placeholder path means
  the harness prompts about a directory that does not exist, and people learn to
  click through prompts.
- **`STATUSLINE_CMD`**: set it in **`kit.config.local`** *before* substituting,
  or the `statusLine` block lands with an unfilled slot. It is an absolute-path
  key, so it belongs in the gitignored half alongside `PROJECT_ROOT` and
  `PROTECTED_PATH`. Either point it at `tools/statusline.py` (the portable
  board — module 05) or delete the block; `NONE` is not a command.

  **No double quotes in that value.** It is substituted into a JSON *string*
  (`"command": "{{STATUSLINE_CMD}}"`), so one `"` produces a settings file that
  does not parse — and a harness that cannot parse its settings has no hooks
  either, which turns a cosmetic slip into a silently disarmed gate. Use an
  unquoted path; if it contains spaces, single quotes survive JSON and are
  accepted by pwsh and POSIX shells alike:

  ```
  STATUSLINE_CMD = python /home/you/project/tools/statusline.py
  STATUSLINE_CMD = python '/home/you/My Project/tools/statusline.py'
  ```

  **Module 05's README inlines the same `statusLine` block with the path in
  escaped double quotes** (`modules/05-statusboard/README.md`), and that is
  correct *there*: it is JSON you type into the settings file by hand, where
  `\"` is legal. The rule differs here because this route goes through
  substitution — `STATUSLINE_CMD` is pasted into an already-quoted JSON string,
  so a `"` closes it and the file stops parsing. Taking module 05 alone and
  adopting module 02 later is exactly how the quotes travel from one route to
  the other; `KNOWN-ISSUES.md`'s **SB-B** is that failure, already recorded as
  having happened once.

**Delete the template's `__COMMENT__` block once you have read it.** Its
reasoning has done its job by this point, and it contains three absolute-path
examples — so keeping it adds three more hits to the count Step 9 tells you to
expect, and Step 9's table assumes it is gone.

**Parse the result before you move on** — `python -c "import json;
json.load(open('.claude/settings.json'))"`. Substitution is the step that can
produce invalid JSON, and its failure mode is silence.

### Optional: having read all that, you can substitute mechanically instead

You have just read the substitution this step asks for, which is the point: the
templates are documents you have to argue with before they bind anything, and
that is why by-hand is this document's route. What by-hand is bad at is getting
the same string into the same places without a typo. If you would rather not
retype one absolute path into three matcher blocks, `tools/kit_render.py` in
the kit clone performs exactly the substitutions above, plus the ones at Steps
6, 7 and 8 — `CLAUDE.md`, the four ledgers, and the collaboration profile.

```bash
python /path/to/kit/tools/kit_render.py --selftest   # prove it works first
python /path/to/kit/tools/kit_render.py --list       # what it renders, and what it does not
python /path/to/kit/tools/kit_render.py --target .
```

It reads your `kit.config` and `kit.config.local` — and prints which file it
read — then writes each result to `<name>.kit-new` beside the real file, prints
a diff against whatever is there already, and names every slot it could not
fill. It never writes over your files, never writes outside the repo you point
it at, and never writes into the kit clone, so moving a `.kit-new` into place is
yours to do. **Add `*.kit-new` to the `.gitignore` line above before this
step's commit**, or `git add .claude` stages the scratch file next to the real
one.

Four things above are then already done for you and should not be done twice:
`{{PROJECT_ROOT}}` is **resolved**, not typed (the tool refuses a typed one);
the `permissions.ask` and `statusLine` blocks are deleted when their values are
unset, and it says so; the `__COMMENT__` block is stripped; and the result is
valid JSON by construction, so the double-quote trap above cannot fire on this
route. Everything else still applies — every checkpoint below unchanged, and
the guidance headers the tool strips are the ones you have just read here, so
open the templates the first time anyway. It renders the Step 6, 7 and 8 files
now, before you reach those steps; the collaboration profile in particular is
filled from a conversation at Step 8, and a rendered template looks finished.

**ONE MACHINE PER SETTINGS FILE — read this before the commit below if more
than one person will use this repo.** The `.claude/settings.json` you have just
written describes THIS machine.
Its hook commands, its `permissions.ask` entries and its `statusLine` all carry
absolute paths, for the reason above — a command that cannot start is a control
that is silently not there. It is also **committed** and **inside
`JUDGE_PATHS`**. Those three facts are individually correct and jointly mean the
file is per-machine, shared, and judged at the same time.

For one developer on one machine that is fine, and it is the case this document
walks. For a second developer, or your own second machine, the consequence has
been measured: the paths do not resolve, `--armed` reports **`UNSTARTABLE:` on
all three hook blocks**, and certification comes back
`VERIFY: FAIL — RED: judges, hooks`. Every recovery available today costs
something — edit the committed file and the first machine breaks; leave it
edited and the `judges` gate stays red for as long as the edit exists.

**The kit does not yet ship a split for this.** Its own `.gitignore` names
`.claude/settings.local.json`, which is the shape of the answer, but no
generator, no overlay convention and no guidance for one exists here. Designing
it is real work and it is not done: it is recorded as open in `KNOWN-ISSUES.md`
("Whose settings file? — the team story"), with a fix shape. If more than one
person will run this repo, read that row before you commit the settings file,
and budget the design.

**If you are not adopting module 02 at all**: delete the `hooks` entry from
`GATES`, delete `"hooks"` from `RUN_ORDER`, and delete the `HOOK_FIXTURES` /
`HOOK_SETTINGS` constants. `--skip hooks` also works, but a permanently skipped
gate means every run reports PARTIAL and the project can never certify.

Then, in your copy of `verify.py` — **four constants and one gate list are the
entire adoption surface:**

1. **`JUDGE_PATHS`** — what decides *what green means*. Name the actual judge
   **files**; `"tools"` sweeps in scratch scripts and cosmetics, and a gate that
   reddens for irrelevant reasons is a gate people route around. **Include
   `kit.config` itself** — the config parameterises the judges, so it is one.
   (Left out, an uncommitted `FORBIDDEN_SPAWN_TIER = nothing-is-forbidden` rides
   through a clean `PASS`: the fixture guarding that rule reads its expectation
   from the same file, so the two move together and the fixture sees nothing.)
   **One more judge joins this list at Step 6**, `tools/deident_scan.py` — it
   cannot go in here, because the file does not exist in your repo until Step 6
   copies it and a `JUDGE_PATHS` entry that is not in the tree aborts the runner.
2. **`CERT_PATHS`** — what is *being certified*. A different list, on purpose.
   Conflating them makes a docs commit invalidate a certification, and then
   nobody keeps the token honest.
3. **`HOOK_FIXTURES`** and **`HOOK_SETTINGS`** — `tools/hook_fixtures.py` and
   `.claude/settings.json`.
4. Replace `example_unit` with the gate from your Step-3 worksheet, delete the
   `example_lint` gate entry, and **add a check to `selftest()`** feeding your
   gate the *well-formed line that would be catastrophic* — the zero count, the
   shrunken count, the subset run.

Item 4 is not politeness: selftest **section I** asserts that every gate in
`RUN_ORDER` is named by a check that **actually ran**, so a replacement gate
with no selftest goes loudly red rather than silently uncovered. Deleting the
example gates breaks nothing — sections A/B are guarded and section F resolves a
live gate name at runtime. The `examples/` directory those two gates read stays
behind in the kit's `modules/03-verification/`; the copy list above never brings
it into your repo, so there is nothing of it to delete on your side.

**Then reconcile `kit.config` by hand.** It ships `JUDGE_PATHS` and
`CERT_PATHS` keys too, and they are *not* where the runner gets its values:
the gates read the constants you just edited, nothing reads `kit.config`'s
`JUDGE_PATHS` at all, and `hook_model_gate.py` reads `kit.config`'s
`CERT_PATHS` for the cert-green tripwire only. **The constants in `verify.py`
are authoritative; the config keys are documentation.** Copy the same two
lists into `kit.config` and keep them in agreement — a `CERT_PATHS` that
disagrees means the hook and the runner hold different opinions about what has
been certified, and neither of them will say so.

```bash
# this block requires the four constants and the gate-table edits above
python tools/verify.py --list
python tools/verify.py --selftest        # must print: VERIFY SELFTEST: PASS
python tools/verify.py                   # expect RED - see below
# EDIT THE NEXT LINE FIRST: drop any path you do not have yet - one missing
# path makes git refuse the whole add, and then nothing is staged at all
# AND RUN `git status` FIRST: most of these are DIRECTORY pathspecs. On a tree
# that holds anyone's unrelated uncommitted work - a colleague's, or your own -
# they stage it into this commit too. Stash or exclude what is not the kit's.
git add tools .claude kit.config .gitignore src tests docs && git commit -m "adopt the kit"
python tools/verify.py                   # must print: VERIFY: PASS
```

**Substitute your own paths in that commit line.** It names `src`, `tests` and
`docs` because that is the layout this document assumes — `docs` is where Step 3
put the oracle worksheet. `git add` is **atomic**: a single path that does not
exist yet makes it refuse the whole add with
`fatal: pathspec 'docs' did not match any files`, stage nothing, and skip the
commit entirely, so the run after it repeats the pre-commit red. Drop the paths
you do not have rather than creating empty directories to satisfy the line, and
add the path your gate payload lives under if it is somewhere else.

**Checkpoints — read the VERDICT WORD, never `$?` alone.** This kit judges runs
by their output line rather than by exit codes, and its own documentation has to
obey that (exit 2, for instance, means *either* `INSTRUMENTED` *or* `ABORTED`,
which are opposite kinds of news):

- `--selftest` prints **`VERIFY SELFTEST: PASS`**.
- The pre-commit run prints **`VERIFY: FAIL`** naming **`RED: judges`**. This is
  correct and documented: you just created files and have not committed them. A
  green here would mean the judges gate cannot see new uncommitted files.
- The commit lists **`docs/ORACLE-<gate-name>.md`** among the files it took —
  the worksheet page from Step 3, named for the gate you just installed. Check
  with `git show --stat --name-only HEAD`. **If that file does not exist, you
  skipped Step 3**: go back and fill one worksheet page before you certify a
  gate whose oracle nobody wrote.
- After committing, the run prints **`VERIFY: PASS`** — provided the commit
  staged **every** new file, your Step-3 gate payload included. **If you see the
  previous run's `VERIFY: FAIL … RED: judges` line again, the commit did not
  run.** The two states print the same string, so the run cannot tell them
  apart: check `git log` for the commit, and scroll up for a `fatal: pathspec`
  line from `git add`.

Note the commit line stages **named paths**, not everything. You installed a
gate one screen ago that denies blanket adds; this document will not teach you
to route around it on day one. Name what you meant to commit — if something is
missing from the list, the `judges` gate will tell you on the next run, which
is precisely its job. An unstaged gate payload leaves the run at
`VERIFY: FAIL — RED: judges`, naming the file it cannot see. That red is the
gate working; stage the file and re-run.

The runner also prints the repo root it resolved and how it found it. **Read
that line.** If it points at `tools/`, stop — every path-based gate would be
judging a directory that does not contain your project. It cannot silently do
that (the startup assertion aborts, naming the missing paths), but that line is
the fastest way to see what happened.

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
red on a floor breach.

Check the **word**, not the code. `ABORTED` also exits 2, and it means the runner
*refused to start* — the opposite of what you are testing here. A checkpoint
that reads `$?` would pass on a run that never judged anything, which is the
precise failure this kit exists to make impossible.

You now have a negative control that leaves **no trace in the repository** —
what stops it being one forgotten revert away from becoming permanent.

---

## Step 6 — Standing rules, and prove the hook (8 min)

```bash
cp /path/to/kit/modules/01-governance/CLAUDE.md.template ./CLAUDE.md
cp /path/to/kit/tools/deident_scan.py                    tools/
```

(The hook, the fixture harness and `.claude/settings.json` are already in place
from Step 4. `deident_scan.py` comes along now so Step 9 runs from your repo.)

**Now that the file exists, put it on the judge surface.** Add
`tools/deident_scan.py` to `JUDGE_PATHS` in **both** places Step 4 had you keep
in agreement: the constant in `tools/verify.py`, which is authoritative, and the
`JUDGE_PATHS` line in `kit.config`, which is documentation. Step 9 hands this
scanner the final publish-safety judgment, so it decides what green means — the
same reason `kit.config` is on the list. Left off, an uncommitted edit to the
scanner reddens nothing and a weakened scan certifies clean.

You just edited the runner, and the standing rule is: re-run its bench after
every runner change. Do it now — the same command as Step 4:

```
python tools/verify.py --selftest
```

It prints `VERIFY SELFTEST: PASS` with your check count. This covers the edit
itself; it does not touch the judge surface, so it stays green here.

Expect `judges` to stay **red** from here to the end of Step 9: you have just
modified `tools/verify.py` and `kit.config` and added an untracked
`tools/deident_scan.py`. Step 9's commit line stages all three, and the
certification run at the end of Step 9 is where that red clears.

Substitute the slots in `CLAUDE.md`, then **delete every rule you cannot yet
enforce or do not yet believe.** A rules file containing aspirations is a file
people learn to skim, and a skimmed rules file is worse than a short one.

> **Do not substitute inside a template's header comment.** Each template opens
> with a `SLOTS:` line listing the tokens it uses. That line is an *inventory*,
> not content — a blind find-and-replace turns it into an unreadable list of
> your own paths. Delete the whole header block once you have used it.

**`KNOWLEDGE_DIR` is a decision, not a fill-in — make it here.** It names where
durable knowledge lives **outside** the repo: the notes system, wiki or vault
that outlives any one session. `CLAUDE.md` interpolates the slot
unconditionally, so substituting without deciding lands the shipped placeholder
`/abs/path/to/your/knowledge-base` in your standing rules, pointing every
source-of-truth reference at a directory that does not exist.

- **You have such a place:** substitute its absolute path into `CLAUDE.md`. The
  repo copies of those documents are mirrors, and the rules file already says
  so — its profile line reads `(that copy is source of truth)`.
- **You do not:** substitute the repo path `docs` — not the literal word
  `NONE`, which is not a directory. The repo copy then **is** source of truth,
  so amend that same `(that copy is source of truth)` parenthetical to name the
  repo copy instead.

**Set the key as well as the slot — in the half that matches the value.**
`KNOWLEDGE_DIR` ships as `/abs/path/to/your/knowledge-base` and nothing fills it
in for you; leave it unset and your committed config and your rendered rules
state different answers to the same question from day one, with no check that
reads either. Which file the key goes in follows Step 1's principle without
exception: **an absolute path never enters the committed half.**

- **Repo-path branch (`docs`):** repo-relative and shareable, so write it into
  the committed `kit.config`. It is committed at Step 9 — see that step's commit
  line, which names `kit.config`.
- **Absolute-path branch:** write `KNOWLEDGE_DIR = /your/absolute/path` into
  **`kit.config.local`**, the gitignored overlay. Both halves are read from the
  same directory with `.local` last, so every tool that reads the key still sees
  your value. In the committed `kit.config`, either leave the shipped
  placeholder with a comment saying the real value is in the local half, or set
  a neutral repo value there; what you must not do is paste the absolute path
  in. That is the one edit that manufactures the "second tracked file" escape
  Step 9 tells you to hunt for.

  Your `CLAUDE.md` is the separate question, because the slot is substituted
  text rather than a config key. Substituting the absolute path there makes the
  rendered rules file a **tracked file carrying an absolute path** — a second
  reviewed file at Step 9, the same status Step 9 already gives `CLAUDE.md` on
  the tripwire-ON branch, and it gets the same `--exclude` treatment. If you
  would rather keep the tracked tree free of absolute paths entirely,
  substitute the repo path `docs` into `CLAUDE.md`, keep the absolute value in
  `kit.config.local` for the tools, and say in the rules file which copy is
  source of truth. Decide it here, out loud; Step 9 expects one answer or the
  other, not a surprise.

`{{KNOWLEDGE_DIR}}` appears in one other place, `PROFILE-TEMPLATE.md` at Step 8.
Same decision, same answer: Step 8 has you substitute that slot with the value
you choose here, delete that template's header block, and check both with a
runnable line of its own.

**The rules file's first line points at a file you do not have yet.** It reads
`ON RESUME: read the newest {{CHECKPOINT_GLOB}} FIRST` — and on day one there is
no checkpoint, because you write the first one at your first stage close. The
template says so in the same breath and carries the shape contract directly
below it: where the mainline stands, the owner's open decision queue verbatim, a
numbered cold-start resume list, and what supersedes what, at a measured norm of
about 90 lines. **No template ships for it and no check notices its absence** —
recorded in `KNOWN-ISSUES.md`. Read those four clauses now, while you are in the
file; they are the whole specification, and the alternative to writing one is
re-deriving your project's state by hand at every session boundary.

### Where the tools look for `kit.config` — four steps, in order

1. `$KIT_CONFIG`
2. `./kit.config` — the current working directory
3. `<the tool's own directory>/kit.config`
4. **the nearest `kit.config` walking UP** from the tool's directory

Step 4 is the one that matters: it lets `<repo>/tools/hook_model_gate.py` find
`<repo>/kit.config`. Whatever is found is overlaid with `kit.config.local` from
the same directory.

**Having `kit.config` in the repo root is the step people skip, and skipping it
is invisible.** The hook still runs, every fixture that does not need config
still passes, and `FORBIDDEN_SPAWN_TIER`, `MODEL_EXEMPT_TYPES` and the protected
path simply *do not exist*. The tools now print `CONFIG WARNING:` when that
happens and `--strict` fails on it.

```bash
python tools/hook_fixtures.py --strict --armed .claude/settings.json
grep -nE '\{\{|DELETE THIS COMMENT BLOCK' CLAUDE.md    # must print NOTHING
```

```powershell
# ⚠ pwsh: no grep
python tools/hook_fixtures.py --strict --armed .claude/settings.json
Select-String -Path CLAUDE.md -Pattern '\{\{|DELETE THIS COMMENT BLOCK'
```

**Checkpoint — two things, and the second is the one people miss:**

- **The hook:** `armed:` lines for Workflow, Agent, Bash and Edit; **no
  `UNARMED:`; no `CONFIG WARNING:`; `0 skipped`; exit 0.** Some `n/a` is expected
  and correct — that is the tripwire you deliberately left off in Step 1, and if
  you also deleted the `permissions.ask` block as Step 4 said, the two facts now
  agree with each other.
- **The rules file this step is named for:** **no `{{` surviving anywhere in
  `CLAUDE.md`, and no template header block left** — the second command above
  prints nothing. It is the same clause Step 7 puts on the ledgers, for the same
  reason. A green fixture run says nothing about `CLAUDE.md`: the hook and the
  rules file are different artefacts, and an unrendered rules file passes every
  other check in this document, up to and including `VERIFY: PASS` and a clean
  de-identification scan. This is the one document re-read at the top of every
  session; nothing downstream inspects it.

Three separate claims, and you need all three: fixtures prove what the hook
*decides*; `--armed` proves it is **wired at every enforcement point to a
script that exists** — as close to "the harness calls it" as anything short of
watching a live call can get; and `--strict` proves the config it decided with
was really loaded.

`--armed` reads your settings file and, for each matched block, resolves the
script the command names and checks it is there. A missing one reports
`UNSTARTABLE:` and fails, because a hook that cannot start enforces nothing
while looking perfectly wired. What it still cannot tell you is whether your
harness honours the settings file at all; for that, watch one real call.

---

## Step 7 — Start the ledgers empty (3 min)

```bash
mkdir -p docs/reports
cp /path/to/kit/modules/04-ledgers/JUDGMENT-LEDGER.md docs/
cp /path/to/kit/modules/04-ledgers/FAILURE-FLOOR.md   docs/
cp /path/to/kit/modules/04-ledgers/LESSONS.md         docs/
cp /path/to/kit/modules/04-ledgers/TOKEN-LEDGER.md    docs/
```

**That first line makes two directories, and the second one is not cosmetic.**
`docs/` already exists — Step 3's worksheet page went there — and the line
creates the missing `reports/` under it. `REPORTS_DIR` is `docs/reports` by
default, and the standing rules you rendered at Step 6 name it twice: subagents
never write there, and stage close saves the report there first. Creating it now
is cheaper than a first stage close discovering it. (Git does not track an empty
directory, so it will not appear in Step 9's commit; it starts being tracked
with the first report you save into it. In pwsh this line prints a small
directory-listing table for the new leaf the first time — that is success, not
an error — and reports `already exists` on any re-run. Expected and harmless;
see the Shell section.)

Four files, **named explicitly**. Do not glob that directory — it also contains
its own `README.md`, and the glob will silently overwrite `docs/README.md`.

**Then substitute their slots and delete their header blocks.** All four ship
as skeletons: a `SKELETON - ... Delete this block on adoption` comment opening
each file, and `{{PROJECT_NAME}}`, `{{OWNER_ROLE}}`, `{{LEDGERS_DIR}}` and
friends through the body. Each skeleton's own header lists the slots it uses.
Same rule as Step 6 — the `Slots:` line is an inventory, not content, so
delete the whole comment block rather than substituting inside it. A ledger
still full of `{{PROJECT_NAME}}` is a ledger nobody has read.

Empty is correct. A ledger begun in month three is a ledger reconstructed from
memory, and reconstruction is where confident wrong numbers are born.

Two things immediately:

- Add your **first rule row** to `FAILURE-FLOOR.md` — the model-tiering hook,
  layer `HOOK`, zone `B`, status `STRUCTURAL`, last fired `never`.
- Keep or delete each **seed lesson** in `LESSONS.md`, deliberately.

**Checkpoint:** four ledger files in your repo — slots substituted, no
`SKELETON` header block left, no `{{` surviving anywhere in them — one with a
real row in it, and your own `docs/README.md` untouched if you had one.

**One shipped placeholder is allowed to survive this checkpoint, by name:**
`RATIO_CEILING`, which ships as `derive-from-your-own-data` and lands in
`TOKEN-LEDGER.md`. That is deliberate. The kit's advice is to derive the number
from your own first few stages rather than adopt someone else's, and
`TOKEN-LEDGER.md` shows the derivation. **Replace it the first time you have
three stages of real numbers** — not before. Every *other* shipped placeholder
value **that reaches these four files** is a fill-in you missed: `your-…`,
`/abs/path/…`, `<paste …>` and the `NONE` family all read as UNSET to the kit's
config readers. Two adjacent standards, and this is the one exception between
them.

**The rule is scoped to the ledgers, which is what the scan below covers:**
`docs/*.md`, the four files this step just copied, where an unfilled value is
always a mistake. It says nothing about `kit.config` — several shipped values
belong in that file at done, because it registers keys for modules you have not
adopted yet. Step 1's "which shipped values legitimately survive" list is the
answer there.

**No shipped tool checks your tree for them.** `adoption_smoke.py` phase 9 does
assert that a rendered rules file and a rendered collaboration profile carry no
unfilled slot and no shipped placeholder value — but it renders those copies
into a throwaway scaffold of its own and never reads your repository. (If you
took Step 4's optional render path, `kit_render.py` names every slot it could
not fill in the seven files *it* wrote, and treats a shipped placeholder value
as unfilled — with the one exception named just above, `RATIO_CEILING`, which
it substitutes as shipped. It says nothing about a file you rendered by hand.)
The check
that covers *your* tree is the
`grep`/`Select-String` line in Step 6's checkpoint. Point it at `docs/*.md`,
with `SKELETON` in place of `DELETE THIS COMMENT BLOCK` — that is the word the
ledger headers use — and it covers this step's checkpoint too. It does **not**
cover the profile Step 8 creates: that template's header uses a different word,
so Step 8 carries its own line. The
`RATIO_CEILING` exception above is a config *value*, not a slot, so it never
appears in that output either way.

---

## Step 8 — Run (or schedule) the seed interview (15 min)

**Who it needs depends on who owns the judgment.**

- **The owner is someone else** — a client, a lead, a stakeholder: this step
  is not solo-schedulable. Put it on their calendar now and run it in the
  first week, unhurried; it is not a task you failed to finish tonight.
- **You are working solo** — you are the owner: answer the five questions
  yourself, in writing, today. The betrayal line is still worth stating even
  to yourself; it is the constraint you will otherwise discover by violating
  it.

Open `modules/08-collaboration/SEED-INTERVIEW.md`, ask the five questions,
capture verbatim, then fill in your own copy of the profile template:

```bash
cp /path/to/kit/modules/08-collaboration/PROFILE-TEMPLATE.md docs/collaboration-profile.md
```

**Then render your copy — the same two edits every other template in this
document gets, in this order:**

1. **Substitute `{{KNOWLEDGE_DIR}}` with the value you chose at Step 6.** This
   is the one other place that slot appears. Same decision, same answer: a
   profile naming a different knowledge directory than your rules file is two
   answers to one question. The slot sits in the template's header comment, in
   the sentence that tells you which copy is source of truth — substitute
   first, so you read that sentence as an instruction about *your* tree rather
   than deleting the decision unread.
2. **Delete the template's header block** once you have acted on it: the
   `<!-- … -->` comment that opens `TEMPLATE - the living collaboration
   profile` and ends `Delete this comment on adoption`. Its marker words are
   `TEMPLATE` and `Delete this comment on adoption` — **not** the `SKELETON`
   the ledgers use, which is why Step 7's scan pattern does not reach this file
   and why this step carries its own checkpoint line below.
3. If you took the repo-path branch, the profile's maintenance rule **"The
   durable copy is source of truth"** now means the repo copy. Amend it to say
   so, exactly as Step 6 had you amend the same claim in `CLAUDE.md`.

**Where that copy belongs.** Your `CLAUDE.md` names
`<your KNOWLEDGE_DIR value>/collaboration-profile.md` as source of truth — the
value you substituted at Step 6, because that slot is rendered by then and the
step's own checkpoint requires it. If that value is an absolute path outside the
repo, write the profile *there* and treat `docs/collaboration-profile.md` as a
mirror, or skip the repo copy entirely. If it is the repo path `docs`,
`docs/collaboration-profile.md` **is** source of truth — say so in the file, and
check that the `CLAUDE.md` line points at it. Either way the filename stays
`collaboration-profile.md`, because that is the name the rules file names.

**Question 5 — the betrayal line — is the highest-value question in this kit.**
Its answer is a hard constraint, not a preference, and it usually names
something you would otherwise have done cheerfully in week two.

```bash
grep -nE '\{\{|Delete this comment on adoption|TEMPLATE - the living' docs/collaboration-profile.md    # must print NOTHING
```

```powershell
# ⚠ pwsh: no grep
Select-String -Path docs/collaboration-profile.md -Pattern '\{\{|Delete this comment on adoption|TEMPLATE - the living'
```

**Checkpoint — two things:**

- **The content:** a profile with five verbatim answers and an explicit
  overrides table against `DEFAULT-CONTRACT.md`. An empty overrides table is a
  real answer.
- **The rendering:** the line above **prints nothing** — no `{{` surviving and
  no template header block left. Same clause as Step 6 puts on `CLAUDE.md` and
  Step 7 puts on the ledgers, and this is the file that needs it most: it is the
  one artefact holding a person's verbatim words, and Step 9 commits it. If your
  profile lives outside the repo, run the same line against it there.

---

## Step 9 — Prove nothing personal is about to be published (3 min)

**First, commit what Steps 6, 7 and 8 created.** The scan below runs
`--tracked-only`, and the last commit this document asked for was Step 4's.
Everything since — `CLAUDE.md`, the four ledgers, the scanner itself, and above
all `docs/collaboration-profile.md`, the file you have just filled with a
person's verbatim words — is untracked, and untracked means unscanned. A green
scan over a tree that does not contain the profile looks exactly like a green
scan over a tree that does.

```bash
# RUN `git status` FIRST: `docs` is a DIRECTORY pathspec. On a tree that holds
# unrelated uncommitted work it stages that work into this commit too. Stash or
# exclude what is not the kit's.
git add CLAUDE.md tools/deident_scan.py tools/verify.py docs kit.config && git commit -m "standing rules, ledgers, profile"
```

`kit.config` and `tools/verify.py` are in that line because **Step 6 edited
both**: the scanner's `JUDGE_PATHS` entry went into each of them, and on the
repo-path branch the `KNOWLEDGE_DIR` key went into `kit.config` as well. All
three of `kit.config`, `tools/verify.py` and the newly copied
`tools/deident_scan.py` are themselves inside `JUDGE_PATHS`, so leaving any of
them uncommitted ends the document at `VERIFY: FAIL (exit 1) — RED: judges`
naming the file it cannot see. Both branches need all three: the absolute-path
branch put `KNOWLEDGE_DIR` in the gitignored `kit.config.local`, but the
`JUDGE_PATHS` edit is in the committed half either way. `git add` on an
unchanged tracked path is a no-op, so leaving a path in the line costs nothing.

Named paths again, not `-A`: the gate you installed at Step 4 still denies
blanket adds. **Substitute your own paths.** If `KNOWLEDGE_DIR` is a real path,
the profile that matters lives outside this repo, so it is not in this commit
and this scan will never reach it — scan it where it lives, with the same
command and a `--root` that points there.

Then, from **your repo** (this is why Step 6 copied the scanner in):

```bash
# --tokens takes a plain text file, ONE TOKEN PER LINE - your name, your
# username, machine path fragments, your employer. `#` starts a comment.
python tools/deident_scan.py --root . --tokens <a-path-outside-this-repo> --strict --tracked-only
```

**The format matters more than it looks.** Nothing in this kit creates that
file, and a file in any other shape — JSON, comma-separated, one long line —
still parses: every non-blank line becomes one token, so the scanner ends up
hunting for a literal string that appears nowhere and reports `0 hits` over a
tree it never really searched. That reads exactly like a clean tree. The run
prints `tokens    : N (from <path>)` — **read `N`** and check it accounts for
the tokens you meant. (A file that yields *no* tokens is caught: the scanner
refuses to run a vacuous scan.)

**`N` is the count of *distinct* tokens, not of lines.** Matching is
case-insensitive by default (`--case-sensitive` turns that off, dedup included),
so the scanner de-duplicates case variants: a list containing
both `jsmith` and `JSmith` is two lines and reports `tokens    : 1`, and it
still finds both spellings. Blank lines and `#` comments are dropped the same
way.
Read `N` as "how many different things am I hunting for" — a number *lower* than
your line count is usually the dedup, and a number of **zero or one** when you
listed several is the shape problem above.

**Read the `scope:` line the run prints.** It states what the scan actually
covered — `scope     : git-tracked files only (N tracked)`. If `N` is still the
count from your Step 4 commit, the commit above did not take, and the run you
are about to call green judged a tree with no rules file, no ledgers and no
profile in it. The scan cannot notice that. The line is how you do.

Keep the token list outside the repo — a committed one is itself the leak: a
tidy, greppable index of exactly the words you did not want published.

**`--tracked-only` scans what git would actually publish.** Without it the scan
reddens on `kit.config.local` — a gitignored file that the kit itself told you to
create and to put absolute paths in. A scanner whose honest answer is "ignore
that one" every single time is a scanner people stop reading. The flag is **off
by default** because "everything on disk" is the right paranoid default;
narrowing it is a decision you make out loud. If git cannot answer, the scanner
falls back to a full walk and prints `SCOPE WARNING` rather than quietly
changing what it did.

**What to expect, concretely.** With your username on the token list, exactly
one tracked file should hit — **`.claude/settings.json`**. It is the only
committed file Step 1 said would carry an absolute path, and these are the
paths it carries:

| Absolute path in the settings file | Present when |
|---|---|
| three **hook commands** | you adopted module 02 (the default) |
| one **`statusLine`** command | you wired module 05's board |
| two **`permissions.ask`** entries | you kept that block, i.e. the tripwire is on |

**Do not count the hits — read the file list.** The scanner counts *token
occurrences*, not paths. On the recommended branch — module 02 plus the
portable board, tripwire off per Step 1 — that is four paths, so the run
reports four hits **only if your username appears exactly once in each of
them**. A checkout under a directory that repeats the token reports a multiple:
a walk on a path containing the token twice reported eight. The number is
arithmetic about your directory layout, not a property of the scan, and no
value of it is wrong by itself.

The diagnostic that *is* worth acting on: **if a second tracked file hits, an
absolute path has escaped into the committed half** — find it before you
exclude anything. Nothing else should hit, because `PROJECT_ROOT`,
`PROTECTED_PATH`, `STATUSLINE_CMD` — and `KNOWLEDGE_DIR` too, if Step 6 left you
on the absolute-path branch — all live in the gitignored `kit.config.local`,
which `--tracked-only` excludes.

**`CLAUDE.md` is the one documented second file, on two branches.** It
interpolates `{{PROTECTED_PATH}}` into its protected-path section, so with the
tripwire on it carries an absolute path once tracked; and Step 6's
absolute-path `KNOWLEDGE_DIR` branch puts one there for the same reason, whether
the tripwire is on or off. On the recommended branch neither applies — Step 1
left the tripwire off, Step 6 had you delete every rule you cannot enforce, and
`docs` is not an absolute path — so `CLAUDE.md` does not hit. Where either
branch does apply, `CLAUDE.md` is the second *reviewed* file and gets the same
`--exclude` treatment as the settings file. A **third** file is the escape.

*(`adoption_smoke.py` phase 9 walks this branch with the tripwire ON and asserts
four things: that the commit above lands and the scan's tracked scope grows to
cover it, that the hit is real, that every tracked hit is inside one of the two
reviewed files named here, and that the remediation below reaches zero.)*

Clear it the way Step 1 described, then re-run:

```bash
python tools/deident_scan.py --root . --tokens <list> --strict --tracked-only --exclude ".claude/settings.json"
```

(One line on purpose: a trailing `\` is a bash line-continuation and a **pwsh
parse error**. Double quotes rather than single so the same line works in
both.) `--exclude` repeats, so on the tripwire-ON branch add
`--exclude "CLAUDE.md"` to the same line.

**Checkpoint:** `DEIDENT SCAN: 0 hits - exit 0`, reached by *excluding one
reviewed file* — two on the tripwire-ON branch — not by deleting a token, and
over a tracked scope that includes everything Steps 6 to 8 produced. (This exact sequence — the commit, the widened
scope, the real hit, the `--tracked-only` narrowing, and the exclusion reaching
zero — is asserted by `adoption_smoke.py` phase 9, so the advice cannot silently
stop working.)

And because a clean scan from a scanner that cannot find anything looks
identical to a clean scan from one that works:

```bash
python tools/deident_scan.py --selftest    # proves it fires on a planted token
```

**Last, certify the tree the document leaves you with:**

```bash
python tools/verify.py                     # must still print: VERIFY: PASS
```

Steps 6 to 8 wrote files and Step 6 edited both `kit.config` and
`tools/verify.py`; the commit at the top
of this step is what keeps the `judges` gate green over all of it. A
`RED: judges` here names the file it cannot see — stage that file and re-run.
This is the state the document is finished in: `VERIFY: PASS` and
`DEIDENT SCAN: 0 hits`.

---

## Then, in the following week

| Do this | Because |
|---|---|
| Add CI (module 07) | The **first control your agents cannot edit**. Read `BRANCH-PROTECTION.md` and record honestly whether you have a gate or a tripwire. |
| Add the status board (module 05) | Agent tiers become visible while a mistake is still happening rather than at the invoice. `tools/statusline.py` is the portable one. |
| Add the sidequest skill (module 06) | The first real interruption is the one that loses your pending-decisions queue. |
| Publish your first **escape rate** | Items a human found that an existing check should have caught. If it does not fall across rounds, the loop is witnessing, not learning. |
| Turn on the protected-path tripwire | Once you have something — a deployed build, a client export, production config — that must not move without a nod. |
| Re-run `python tools/verify.py --selftest` after every change to the runner | This is the check that covers *your* runner, and the only one that does. Wire it into CI alongside the run itself. |
| Re-run `python tools/adoption_smoke.py` **from the kit clone** after you pull a kit update | No step copies that script into your repo, so it does not run from there, and its paths are relative to the kit. Plain, it re-walks this document against the kit's own runner and tells you the documented path still works. `--runner <absolute path to your tools/verify.py>` points it at your copy instead — but only while that copy still carries the shipped `example_unit` and `example_lint` gates, because the scaffold adapts the runner by renaming them. Step 4 deletes them, so on a finished adoption `--runner` aborts with `could not repoint the unit gate`. That is a limit of the flag, not a fault in your runner. |

## Why the nine steps are in this order

Each step exists where it does for a reason, and two of the reasons are
mechanical rather than editorial:

- **Step 3 before Step 4**, because a gate written without an oracle measures
  whatever was convenient. Step 4's commit line then stages the worksheet page,
  and its checkpoint names the file — a gate whose oracle nobody wrote cannot
  reach a green certification by accident.
- **Step 4 writes the settings file before the first run**, because the runner
  ships a `hooks` gate naming `.claude/settings.json` and the startup assertion
  refuses to run over paths that are not there. Create it later and Steps 4 and
  5 abort. This ordering is load-bearing and is walked by the smoke.
- **Step 5 immediately after Step 4**, because the cheapest moment to prove a
  gate can go red is the moment it first goes green.
- **Steps 6 to 8 after the machinery**, because the rules file, the ledgers and
  the profile are the artefacts you keep; they are written once the thing they
  describe exists and can be described accurately.
- **Step 9 last**, because it scans the *tracked* tree, and the tree is not
  complete until Steps 6 to 8 are committed.

**This is not the same order as the adoption levels**, and the difference is
deliberate. `README.md`'s three levels (documents → verification → CI and the
ambient modules) are an ordering by *commitment*: take the things that cost
nothing first, promote a rule to a hook only after it has failed once, and add
CI last because its value depends on everything else already existing. That is
advice about which months to spend. The nine steps above are an ordering by
*dependency* — what must exist before the next command can run — which is why
the runner and the enforcement files land at Step 4 and the ledgers at Step 7.
Take the levels as the adoption plan; take the steps as the sequence for the
session you are in now.
