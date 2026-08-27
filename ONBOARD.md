# ONBOARD — adopting OAR, for the agent doing the adopting

You are an AI agent asked to adopt this kit into a project. The project is the
**host**. This document is your entry point. Every other reader's entry point is
`README.md`. Terms used with a specific meaning are defined in `GLOSSARY.md`.

This document executes nothing. It adds **sequencing**, meaning what to read and
run in what order, and **division of labour**, meaning which half of an adoption
you may perform and which half is the owner's. Every state change in the host is
made by you, running a command a shipped document prints.

The shipped documents are the authority. Where this page and a shipped document
disagree, the shipped document wins, and the disagreement is a finding you report
[§8].

This route is unmeasured. Make no speed claim for it. The kit's adoption figures
live in `docs/START-HERE.md`, `LEVEL-1.md`, `DECISION-BRIEF.md` and
`EXISTING-PROJECT.md`, each carrying its own label. Do not restate them as this
route's numbers [§6].

---

## 1. Preconditions

Establish all five before anything else.

| # | Precondition | How you establish it |
|---|---|---|
| P1 | A host repository exists and you can run `git` and `python` in it | `git -C <host> rev-parse --show-toplevel`, `python --version` (3.10 or newer — `QUICKSTART.md` Step 0) |
| P2 | A kit checkout exists and you may treat it as read-only | `git -C <kit> rev-parse HEAD` — record the sha |
| P3 | The kit's own tooling is green **before** you touch the host | Run `QUICKSTART.md` **Step 0** in the kit clone: every line of its block exits 0 |
| P4 | You know who the host's owner is, and whether they can answer this session | Ask whoever dropped you in. This shapes the punch list [§7]; it does not decide whether you proceed |
| P5 | The host's starting state is recorded | `git -C <host> rev-parse HEAD`, `git -C <host> status --porcelain`, and the branch name, captured verbatim before your first write |

1. Treat a red P3 line as a HALT, not a warm-up [§8].
2. Record P5 before your first write, so the owner can tell their modifications
   from yours [source: `docs/walks/WALKING-YOUR-OWN-DOCUMENTS.md` §1].

---

## 2. Classify the host

The kit's documents assume a repository whose only uncommitted content is the
kit's own (`QUICKSTART.md`, opening; `EXISTING-PROJECT.md`, opening).
Classification decides which branch of every step you take. Do it before Step 1.

```bash
git -C <host> log --oneline -1              # is there history at all
git -C <host> status --porcelain            # uncommitted work
ls <host>/CLAUDE.md <host>/kit.config       # rules file, kit config
ls <host>/.claude/settings.json             # harness wiring
git -C <host> check-ignore -v .claude       # an ignore rule over a judged path
ls <host>/docs                              # ledgers under other names
git -C <host> grep -nIiE '\b(agents?|subagents?|lanes?|charters?|spawn(s|ing)?)\b|model tier|\b(opus|sonnet|haiku)\b'
grep -rnIiE '\b(agents?|subagents?|lanes?|charters?|spawn(s|ing)?)\b|model tier|\b(opus|sonnet|haiku)\b' <host> --exclude-dir=.git
```

```powershell
# ⚠ pwsh: `ls` is Get-ChildItem, and a MISSING path raises a non-terminating
# error rather than printing to stderr and moving on. Probe one path per line,
# and read Test-Path's boolean rather than an error stream.
git -C <host> log --oneline -1
git -C <host> status --porcelain
Test-Path <host>/CLAUDE.md                  # rules file
Test-Path <host>/kit.config                 # kit config
Test-Path <host>/.claude/settings.json      # harness wiring
git -C <host> check-ignore -v .claude       # exits 1 when nothing matches
Test-Path <host>/docs                       # ledgers under other names
git -C <host> grep -nIiE '\b(agents?|subagents?|lanes?|charters?|spawn(s|ing)?)\b|model tier|\b(opus|sonnet|haiku)\b'
Get-ChildItem <host> -Recurse -File | Where-Object { $_.FullName -notmatch '\\\.git\\' } | Select-String -Pattern '\b(agents?|subagents?|lanes?|charters?|spawn(s|ing)?)\b|model tier|\b(opus|sonnet|haiku)\b' | Select-Object -First 20
```

1. Record each probe's answer. Also look for a test suite the project trusts, and
   for CI.
2. Read output, not exit codes. A "not found" is an answer, and
   `git check-ignore` exits 1 when nothing matches.
3. Treat the last two searches in each block as the **agent-vocabulary probe**.
   `git grep` reads tracked files. The second reads the whole working tree,
   including untracked files. Both exit 1 with no output when nothing matches,
   which is the answer.
4. Record that command and its result verbatim. It decides §4's third tier-name
   case, and §4 has you write the result into the punch text.
5. Do not read a hit as evidence by itself. The word *lane* in a road-mapping
   project is not evidence of tiered spawning.

| Class | Condition | What you take |
|---|---|---|
| **Greenfield** | No history or an empty tree, no `CLAUDE.md`, no `.claude/settings.json`, no `kit.config`, no ledgers, no suite | `QUICKSTART.md` as printed, new-project route |
| **Existing project** | **Any** probe hits | Read `EXISTING-PROJECT.md` in full before Step 1, and take the existing-project branch each step names. `QUICKSTART.md` Step 1 states the two routes; the branches are inline at Steps 1, 4, 6 and 9 |

The host's uncommitted work is protected by that branch, not by you. Take all
three shipped mechanisms where they apply: the render route never overwrites
[§5, R2], the commit line names files rather than directories [R3], and the
certifying run uses backup-stash-certify-restore [R4]. Do not invent a fourth. A
case none of them covers is a HALT [§8].

### Which level you are adopting

Level 1 installs documents only and no code. Level 2 adds the certification
runner and the enforcement hook. `DECISION-BRIEF.md` states what certifies at
each level and what it costs. The level is the owner's decision.

1. You were instructed which level. Obey the instruction.
2. You were not, and the owner can answer now. Ask, before any work.
3. You were not, and the owner cannot answer. Take **Level 1**, which `README.md`
   recommends as the starting level and which is the reversible one. Record
   escalation to Level 2 as a punch item [§7, D-5]. Do not escalate on your own
   judgment.

---

## 3. Reading order, and the obedience rule

Read in this order. Branch conditions and failure signatures live in the prose,
so do not skim for commands.

| Order | Document | What it gives you |
|---|---|---|
| 1 | `README.md` | What the kit is and is not, the worked demonstration, the module map, the index to `docs/` |
| 2 | `DECISION-BRIEF.md` | What certifies per level, the exit cost, the limitations that constrain what you may claim |
| 3 | `LEVEL-1.md` **or** `QUICKSTART.md` | The path itself, per §2's level decision |
| 4 | `EXISTING-PROJECT.md` | Beside the path, **before Step 1**, on the existing-project branch |
| 5 | `modules/03-verification/GATE-LINE.md` | Before any gate line is written, and first if the thing the host must not break is a suite it already has |
| 6 | `modules/03-verification/ORACLE-WORKSHEET.md` | Step 3's material. Read it, do not fill it [§7, D-1] |
| 7 | `modules/08-collaboration/SEED-INTERVIEW.md` and `DEFAULT-CONTRACT.md`, plus `DEFAULTS.md` (optional) | Step 8's material. Read them, do not answer them [§7, D-2]. Read `DEFAULTS.md` here or do not cite it; its write-question-5-first rule binds on this route |
| 8 | `docs/walks/WALKING-YOUR-OWN-DOCUMENTS.md` | The conventions for recording a document that fails you [§8] |

| Clause | The rule |
|---|---|
| Run what is printed | Run the printed command, not your improvement on it. Evaluate a printed branch condition against the host. Compare a step's stated output line to what appeared |
| The shipped text is the authority | A citation on this page that does not match its source is a finding against this page. Report it |
| Stop rather than improvise | A printed command that would destroy host work with no permitted alternative, or two documents that contradict each other on the same action, is a HALT [§8] |
| You are an adopter, not a walker | The walk method's use-no-outside-knowledge rule does not bind you; general knowledge sometimes keeps the host safe. The recording rule does bind you: anything you do that the documents did not tell you how to do is a finding, recorded with what you authored [`docs/walks/WALKING-YOUR-OWN-DOCUMENTS.md` §2] |

---

## 4. The division of labour

Classify every instruction before acting on it, and record the class in your
report.

| Class | Definition | What you do |
|---|---|---|
| **MECHANICAL** | The documents say what to do and the answer is discoverable from the kit's text or the host tree | Do it |
| **SHIPPED DEFAULT** | The documents prescribe a default value and name the condition for revisiting it | Take it, cite the document, record a punch item in state `DEFAULT-TAKEN` |
| **OWNER JUDGMENT** | No document supplies the answer and no evidence in the host supplies it | Do not answer it. Record `DEFERRED`, or `BLOCKED` if the mechanical half stops there |

`QUICKSTART.md`'s nine steps. Level 1's six steps are the subset marked L1.

| Step | Class | Notes |
|---|---|---|
| 0 — prove the tooling | MECHANICAL | In the kit clone. P3 above |
| 1 — repo and config (L1 steps 1–2) | MIXED | `PROJECT_NAME` is discoverable. `GATE_COMMAND` ships correct for the layout Step 4 builds: confirm, do not change. `PROTECTED_PATH_ENABLED = false` is SHIPPED DEFAULT. The four tier names are OWNER JUDGMENT and are asked for here. `OWNER_ROLE` (Step 7) and `KNOWLEDGE_DIR` (Step 6) are OWNER JUDGMENT but are not asked for here |
| 2 — see the hook fire | MECHANICAL | In the kit clone. Watch the dead-man clause go red; a gate that has never been red is unproven |
| 3 — the first oracle | **OWNER JUDGMENT** | `QUICKSTART.md` Step 3 is headed "an afternoon of thinking" (:366), and its budget paragraph says the first oracle is thinking work that does not compress. Prepare its inputs; do not fill the worksheet. D-1 |
| 4 — the runner and its wiring | MIXED | Copy list, render and merge, the six constants, the commit and its checkpoints are MECHANICAL. `CERT_PATHS` scope is D-6 |
| 5 — the negative control | MECHANICAL, **blocked by D-1** | It runs against the gate Step 3 specifies. With Step 3 deferred it is *not performed*: a named gap, not a skipped step |
| 6 — standing rules, prove the hook (L1 step 3) | MIXED | The copy, the `JUDGE_PATHS` edit and the hook proof are MECHANICAL. The `CLAUDE.md` merge on an existing rules file, and `KNOWLEDGE_DIR`, are below. On the `LEVEL-1.md` path the rules file is conditional: Step 3 takes it if you run agents, so *whether* it installs is the tier-name question below |
| 7 — the ledgers (L1 step 3) | MIXED | Copying, substituting and the first `FAILURE-FLOOR.md` row are MECHANICAL. A ledger-name collision ruling and each seed lesson are OWNER JUDGMENT (D-7). `RATIO_CEILING` stays as shipped: SHIPPED DEFAULT, the one placeholder allowed to survive |
| 8 — the seed interview (L1 step 4) | **OWNER JUDGMENT, absolutely** | D-2 |
| 9 — publish safety (L1 step 6) | MIXED | The commit, the scan, the `scope:` and `tokens : N` reads, the exclusion of reviewed files and the final certifying run are MECHANICAL. The token list's content is partly the owner's |
| — the doctor | MECHANICAL | `kit_doctor.py` sits outside the path and reads its result. Run it and disposition every `[ATTENTION]` line |

### The four values that are decisions, not fill-ins

These are not all Step-1 keys. Treating them as such is the measured render-early
defect `QUICKSTART.md` describes under "Substituting mechanically".
`QUICKSTART.md`:77-89 is the authority: Step 1 fills `PROJECT_NAME`, the three
tier names and `FORBIDDEN_SPAWN_TIER`, and "Four keys come back later, each at
the step that needs it".

| Value | The step that asks for it | Class and instruction |
|---|---|---|
| `OWNER_ROLE` | `LEVEL-1.md` Step 2; on the `QUICKSTART.md` path, Step 7 | SHIPPED DEFAULT. Take `the owner` unless the owner told you what to call them. Never write a person's name you were not given |
| `KNOWLEDGE_DIR` | `LEVEL-1.md` Step 1; `QUICKSTART.md` Step 6 | OWNER JUDGMENT. See the branches below |
| The four tier names | `QUICKSTART.md` Step 1; `LEVEL-1.md` Step 2 | `ORCHESTRATOR_TIER`, `LANE_TIER`, `SWEEP_TIER`, `FORBIDDEN_SPAWN_TIER`. Three cases, below |
| `CERT_PATHS` | The end of `QUICKSTART.md` Step 4, not Step 1 | OWNER JUDGMENT. See the branches below |

**`KNOWLEDGE_DIR`.** `LEVEL-1.md`:37 calls it one of two things that "are
decisions, not fill-ins". It asks where the project's durable knowledge lives,
which the host tree cannot answer. Absence of a mention is not evidence of
absence.

1. The host names such a place: record `DEFERRED` for the owner to confirm.
2. The host names none: still `DEFERRED`, carrying the repo path `docs` as the
   **provisional** value from `LEVEL-1.md`, "Decide two things", so the
   mechanical half proceeds.
3. State in the punch text that you could not observe whether such a place
   exists. You searched the repository, and the repository is not where the
   answer lives.
4. Never record this one as `DEFAULT-TAKEN` [check: `doctor:l1-knowledge-dir`
   goes green on a recorded decision, and a green over an answer the agent
   supplied is what §7 exists to prevent].

**The four tier names.** They describe the tiers the project actually uses.

| Case | What is true of the host | What you do |
|---|---|---|
| 1 | It runs no agents at all | The tiering prose is a rule it cannot enforce. On the `LEVEL-1.md` path the rules file is conditional, so do not install it and say so in your report. On the `QUICKSTART.md` path, where Step 6 installs it, delete every rule you cannot yet enforce and record the deletion |
| 2 | It runs agents, and the tiers are evidenced nowhere in it | OWNER JUDGMENT, and they **block**. An unfilled tier name is a placeholder, `FORBIDDEN_SPAWN_TIER` left unset fails silently, and Step 6's `0 skipped` checkpoint becomes unreachable (`QUICKSTART.md` Step 1) |
| 3 | It is configured for an AI assistant and carries no agent vocabulary: a `CLAUDE.md`, a `.claude/settings.json`, or both, and no occurrence of *agent*, *subagent*, *lane*, *charter*, *spawn*, *model tier* or a model name [check: §2's agent-vocabulary probe] | Neither case above fits, so do not pick one. Record a punch item in §7, `DEFERRED` where the mechanical half continued and `BLOCKED` where it stopped. Leave all four keys unset. Write into the punch text what you searched for and did not find |

In case 3 nothing installed at Level 1 interpolates those keys, so nothing is
broken today. Answer them before module 01 is adopted, or before Level 2.

**`CERT_PATHS`.** Scope is OWNER JUDGMENT whichever layout the host has. A
`VERIFY: PASS` over a scope nobody ruled certifies a boundary the owner never
drew.

1. On the `src`/`tests` layout the document assumes, take those paths as the
   provisional value so the runner stands up, and record `DEFERRED`.
2. On any other layout, name the paths the evidence supports and record
   `DEFERRED` the same way.
3. Name in the punch text the paths you used and the evidence for them
   [record: §7, D-6].

### A certification without the owner's oracle

If Step 3 is deferred the runner still stands up. The kit ships `judges`, `hooks`
and `escapes` gates. `QUICKSTART.md` Step 4 item 5 has you replace `example_unit`
with your own gate and delete `example_lint`. With the oracle deferred there is
nothing to replace `example_unit` with, so both example entries go.

1. Delete both from `GATES` **and** from `RUN_ORDER`, or the selftest goes red.
   Deleting from `GATES` alone fails selftest **section I** ("every gate in
   `RUN_ORDER` is actually exercised"), naming both entries. A gate left in
   `RUN_ORDER` with no check that ran is what that section exists to catch.
   The header of `verify.py` warns that a
   permanently-skipped gate in `RUN_ORDER` reports PARTIAL and can never certify.
2. Under the complete edit nothing breaks. The payloads stay behind in the kit
   clone, section F resolves a live gate name at runtime, and section I passes
   with an empty want. This deferred-oracle route is this page's instruction, not
   a case `QUICKSTART.md` contemplates.
3. State beside the green line what a `VERIFY: PASS` over that runner certifies:
   that the files deciding what green means are committed and clean, that the
   enforcement layer proves itself against its fixtures, and that the escape rate
   is published. It certifies nothing about whether the host's own software
   works, because no gate in it judges the host's software.
4. Expect `[ATTENTION] doctor:vacuous-gate` on those three gates for want of a
   `docs/ORACLE-<gate>.md` page. `QUICKSTART.md` Step 3 names three honest
   answers (`:409-415`) and prescribes none, so this is OWNER JUDGMENT, not a
   SHIPPED DEFAULT. Record it `DEFERRED` and name the three answers. Hold the
   tree in the second: accept the ATTENTION and record why. It is the only one of
   the three that writes nothing on the owner's behalf.
5. Do not write the `docs/ORACLE-<gate>.md` pages to make the check green.

---

## 5. Executing the mechanical half

Eight rules, all restatements of shipped instructions.

| # | Rule | What you do, and the source |
|---|---|---|
| R1 | Read the verdict word, never the exit code alone | Exit 2 means `INSTRUMENTED` or `ABORTED` from the runner, which are opposite kinds of news, and `ABORT` from `kit_render.py` and `kit_doctor.py`. `kit_doctor.py` reports `HEALTHY`/`ATTENTION` and never `PASS`. Run one command at a time |
| R2 | Over a pre-existing file, `kit_render.py` is the required route | `QUICKSTART.md`, "Substituting mechanically", states this. `EXISTING-PROJECT.md` rows 1 and 2 carry the measurements: a `cp` onto an existing `CLAUDE.md` destroys it with no backup, and placing the substituted template at an existing `.claude/settings.json` drops its `allow` and `deny` rules silently. The tool writes only `<name>.kit-new`, prints a diff, merges the settings file structurally, and names every slot it could not fill. Moving a `.kit-new` into place is your act: read the diff first. For a rules file, use kit rules as the base with the host's existing rules preserved **verbatim** under a marked heading of their own. A conflict between the two rule sets is an owner decision [§7] |
| R3 | Never stage blindly | No `git add -A`, no `git add .`, no `git add -u`. Name paths, and on an existing host drop the directory pathspecs: `src` and `tests` take work in progress into a commit titled "adopt the kit". Run `git status` before every add. After a **failed** add, run `git status` again and `git reset` if the index holds something you did not mean to stage. The ignored-path failure exits 1 and stages every other path on the line anyway; the missing-path failure exits 128 and stages nothing (`QUICKSTART.md` Step 4, `:896-900`, with the missing-path half also at `:861`) |
| R4 | Never commit unfinished work to manufacture a green | With work in progress inside `CERT_PATHS` the certifying run is red and the runner is right. The sanctioned route is backup, stash, certify, restore: take both backups, note the sha256, and verify byte-identity afterwards (`QUICKSTART.md` Step 4). Report both states, red with the work on disk and green with it stashed. The first backup is written outside the host, so it needs an operator-designated path [§8] |
| R5 | An ignore rule over a judged path is force-tracked, not deleted | Run `git check-ignore -v <path>` **before** `git add -f <path>`: once a path is tracked the diagnostic prints nothing. Deleting a directory rule like `.claude/` also uncovers the session state and the certification token the kit's own ignore file says must never be committed (`QUICKSTART.md` Step 4; `EXISTING-PROJECT.md` row 3) |
| R6 | You do not write into the kit clone | Your writes go into the host and to the report path you were given, nowhere else. `kit_render.py` refuses to write into the kit clone or outside the target and aborts if it would. Do not work around a guard that fires (`QUICKSTART.md` Step 1; `tools/kit_render.py`, guard 1) |
| R7 | Nothing destructive that no document printed | No force push, no history rewrite, no branch deletion, no `git clean`, no `git checkout --` or `git restore` over a host file you did not create. If recovering from your own mistake seems to need one, that is a HALT |
| R8 | Record it when you improvise | Anything the documents did not tell you how to do, and you did anyway, is a finding with what you authored attached [§8] |

---

## 6. Recording wall-clock, and labelling it honestly

1. Read a real clock twice per step, once before its first command and once after
   its checkpoint, and subtract. Never write a duration you did not measure.

```bash
python -c "import time; print(time.strftime('%Y-%m-%dT%H:%M:%S'))"
```

```powershell
# ⚠ pwsh: the bash line runs as written, but the inner single quotes are the
# only thing keeping `%Y` out of PowerShell's way - use the native reader and
# there is nothing to quote.
Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
```

2. Label the number **agent tool-time**: the elapsed time of a model executing
   tool calls, not a person adopting a toolkit. `DECISION-BRIEF.md`:66 says of
   the brownfield walk that it "produced no usable human time estimate — it
   measures an agent executing tool calls". The provenance section of
   `EXISTING-PROJECT.md` keeps that walk's timings off the page for the same
   reason.
3. Copy any wording you reuse from the lines you cite, with the document open,
   never from memory. If you cannot locate the string, drop the quotation marks
   and cite the section for the idea instead.
4. Do not compare the number to the kit's published budgets. The 90–120 minutes
   in `docs/START-HERE.md` and `QUICKSTART.md`, the 30–45 minutes in
   `LEVEL-1.md` and the 3.5–5 hours in `DECISION-BRIEF.md` are sums of per-step
   estimates, reconciled against walks performed by LLM personas rather than by
   people. No human has walked either document end to end.
5. Use the number for ratios inside one instrument: which step consumed the run,
   how much was blocked, and how one agent-led run compares to another.
6. Record one row per step and hand the table to the owner.

| Step | Started | Ended | Elapsed | Verdict word | Punch items raised |
|---|---|---|---|---|---|

7. State two exclusions in the caption. Time the owner spends is not in your
   number, and time spent blocked on an owner answer gets its own row.
8. Ship no speed claim. Publish the measurement or publish nothing.

---

## 7. The judgment half — the deferral punch list

### The unforgivable failure

Never write an answer the owner did not give. Not in the collaboration profile,
not in a ledger, not in `kit.config`, not in the report. Not as a guess, not as a
placeholder phrased to read like an answer, not as a plausible date.
`LEVEL-1.md` Step 4 states the reason: *a date that parses is not a date somebody
agreed to*. An invented answer removes the owner's chance to notice that nobody
has decided yet. Every other failure here is recoverable by re-running a command.

Copy the kit's precedent. At `LEVEL-1.md` Step 4 the interview may be `held`,
`scheduled … confirmed by …`, or `not yet held`, and all three are green, because
"the owner has not answered yet" is a stated answer. What fails the check is
leaving the shipped menu in place.

### The states

| State | Meaning | What it requires |
|---|---|---|
| `ANSWERED` | The owner answered in this session | Their words, verbatim, with when and where they said them |
| `DEFAULT-TAKEN` | A default the kit prescribes was taken | The citation, the value, and the document's condition for revisiting it |
| `DEFERRED` | Owner judgment, not yet given, nothing blocked | Where the answer goes when it arrives: file and step |
| `BLOCKED` | Owner judgment, not yet given, and the mechanical half stopped here | Everything `DEFERRED` requires, plus what is unreachable until it is answered. A step recorded NOT RUN under §8's grant clause lands here, naming the path the owner must grant |

### The standing items

Raise these on every adoption, even when the answer arrives immediately.

| ID | The decision | Source | Where the answer lands |
|---|---|---|---|
| D-1 | The first oracle: what this project must not break, its required output line, its floor, its negative control | `QUICKSTART.md` Step 3. Design work, "an afternoon of thinking", and it does not compress | `docs/ORACLE-<gate>.md`, then Step 4 item 5 and Step 5 |
| D-2 | The seed interview's five questions, including question 5, the betrayal line | `modules/08-collaboration/SEED-INTERVIEW.md`. Answers captured **verbatim** | `docs/collaboration-profile.md`, and its `INTERVIEW:` status line |
| D-3 | `KNOWLEDGE_DIR`: where durable knowledge lives, and which copy is source of truth | `LEVEL-1.md` Step 1, `QUICKSTART.md` Step 6 | `kit.config` or `kit.config.local`, `CLAUDE.md`, the profile |
| D-4 | `OWNER_ROLE` and the four tier names | `LEVEL-1.md` Step 2 for both. On the `QUICKSTART.md` path the tier names are Step 1 and `OWNER_ROLE` is Step 7 | `kit.config` |
| D-5 | The adoption level, and escalation from 1 to 2 | `DECISION-BRIEF.md`'s table is the input; the choice commits the project's time | The adoption report |
| D-6 | `CERT_PATHS`: what is certified, and why these paths | `QUICKSTART.md`, end of Step 4 [§4] | `tools/verify.py`'s `CERT_PATHS` constant, which is authoritative, and the matching `kit.config` key |
| D-7 | Each seed lesson: keep it, or delete it | `modules/04-ledgers/LESSONS.md` ships them under "Seed lessons — earned in the reference build" and says "Delete any that do not apply" | `<LEDGERS_DIR>/LESSONS.md`, per `LEVEL-1.md` Step 3 |

You may prepare **inputs** for D-1 without answering it: the candidate gate
command, the suite's collected count from `python -m pytest --collect-only`, the
`GATES` entry `tools/gate_line.py --gate-spec` prints, and what the host's checks
demonstrably do and do not cover. Label them as material for the owner's
worksheet, not as a worksheet.

`modules/08-collaboration/DEFAULTS.md` is an optional starting state for D-2. It
is a SHIPPED DEFAULT source for the working contract you run under before the
owner has ruled. It extends the in-force standing of `DEFAULT-CONTRACT.md` to the
calibration classes the eight defaults do not cover. Cite the page and the
value's id, and record `DEFAULT-TAKEN` with the revisit condition it names.

1. Do not copy a default into one of the profile's verbatim answer blocks.
2. Do not enter one in the overrides table as an override.
3. Do not move the `INTERVIEW:` line off `not yet held` because the page exists.
4. Keep D-2 `DEFERRED` until the owner has walked that page's realignment ask or
   answered the five questions cold.

### The items the host raises

Add one row per collision the host presents, citing the kit document behind it.

| Collision | Disposition |
|---|---|
| Ledger-name collision: an existing `LESSONS-LEARNED.md` or `TOKEN_LEDGER.md` | Rename, freeze, or move `LEDGERS_DIR` (`LEVEL-1.md` Step 3; `EXISTING-PROJECT.md`, "Also measured, at Level 1") |
| Rules that conflict on merge | `QUICKSTART.md`:379-380 makes it an owner instruction: where the two rule sets conflict, "that is a decision to make now and write down, not a duplicate to leave standing" |
| CI weaker than the local gate | After Step 6 the local certification proves strictly more than the host's CI. Log it as adoption debt in the host's `docs/FAILURE-FLOOR.md` and close it when module 07 lands (`EXISTING-PROJECT.md` row 7). Do not modify the host's CI during an adoption |
| More than one machine, or more than one person | `.claude/settings.json` is per-machine, committed and judged at once. Read `KNOWN-ISSUES.md`, "Whose settings file? — the team story", before committing that file, and raise the design as a punch item (`QUICKSTART.md` Step 4, "ONE MACHINE PER SETTINGS FILE") |
| The de-identification token list | You can supply machine path fragments and the username from the environment. The owner's name and employer you cannot. A green scan over a list you assembled alone is labelled as one (`QUICKSTART.md` Step 9). With no path granted **for the token list itself** [§8], the scan is a punch item reading NOT RUN. Your report path is not one |

### Where the punch list lives

In the adoption report, and also in the tree wherever the kit already has a place
for it: the interview's state in the profile's `INTERVIEW:` line, adoption debt
in `docs/FAILURE-FLOOR.md`, and unset keys named in the report. Create no new
file for it. A punch list in a file nobody opens is the same as no punch list.

---

## 8. Constraints, HALT, and reporting a document that fails you

**Fences.** You write into the host repository and into the report path you were
given. Not the kit clone [R6]. Not anywhere else on the machine.

### The operator capability grant

The report path is the first exception: a file outside the host that whoever
dropped you in designated, for the report and nothing else. Other shipped steps
need the same exception for different artifacts. The de-identification scan in
`LEVEL-1.md`, "scan before you publish", takes
`--tokens <a-path-outside-this-repo>`. The first backup in `QUICKSTART.md` §4.7
writes `wip.patch` outside the repository being certified. An agent holding only
the fence above cannot run either step as printed. The exception is a capability
the operator grants, with four properties, all of them requirements.

| Property | What it requires |
|---|---|
| **DEFAULT-CLOSED, PER ARTIFACT** | With no path designated for a given artifact, the capability to write it does not exist. Do not create one. Record the step that needed it as **NOT RUN**, citing this clause and naming what it would have covered, as a punch item in §7 |
| **HUMAN-GRANTED** | The operator names the path. You never choose one, never infer one from the environment, and never promote a directory you created into a grant. That a path was handed to you, that a directory exists, that it is writable, or that an artifact of yours already sits in it is not a grant |
| **ENUMERATED PURPOSE, ONE PER PATH** | A grant covers one artifact type at one path, and each artifact type requires its own designated path. The current list, set by the shipped documents: the handoff report; the de-identification token list, from `LEVEL-1.md`, "scan before you publish"; the work-in-progress backup, from `QUICKSTART.md` §4.7. The list is current, not closed. Every artifact type a shipped document requires to be written outside the host gets its own designated path on these same four properties, so finding a new one is a finding you report [§3], never a reason to choose a path. The report path is a grant for the report only; neither it nor its directory is a token-list or backup path. A granted path is a **file** unless the operator named a **directory**. Write nothing under it except the artifact type it covers |
| **USE-RECORDED** | Your report names every granted path, the artifact type each was granted for, and every file you wrote there. Residual, stated: this record is self-attested, which is why these properties are requirements rather than checks |

**The common case.** You are handed a report path on essentially every run and a
token-list path on almost none. The ordinary outcome is a report written to its
granted path, a de-identification scan recorded **NOT RUN**, and a punch item
citing this clause and naming what the scan would have covered. That is the
designed outcome. If you find yourself concluding that you may write something
because a path exists, stop.

**The work-in-progress backup.** R4's route writes `wip.patch` outside the host,
and `QUICKSTART.md` §4.7 makes both backups mandatory. On a host carrying
uncommitted work inside `CERT_PATHS` with no backup path designated: do not
stash, do not certify, record the certifying run **NOT RUN** citing this clause,
and raise a punch item naming the path the owner would have to grant. Hand it
back rather than certifying around it. This is a designed outcome and not a HALT.
The instruction in §5 not to invent a fourth mechanism holds, because R4 is not
missing, only ungranted, and §3's contradiction HALT does not fire because the
two rules no longer disagree. The rule in `LEVEL-1.md`, "scan before you
publish", stands unchanged: the token file lives outside the repository, and
this clause is where its path comes from. The rejected alternative is a token
list inside the tree, one force-add from published, and a `wip.patch` inside the
tree, one blanket `git add` from being the committed unfinished work R4 forbids.

**Commits.** Only in the host repository, only where a shipped document instructs
a commit (`QUICKSTART.md` Steps 4 and 9, `LEVEL-1.md` Step 6), and only naming
paths [R3]. Use the commit messages the documents print. Do not commit outside
those points, and do not push unless you were told to.

**HALT.** You hold halt authority at any depth. Return the verdict `HALT` with a
reason, the citation, and the tree state as you are leaving it. A halt is a
verdict, not a failure. Halt when:

| # | Halt condition |
|---|---|
| 1 | A shipped command would destroy host work and no non-destructive alternative in the documents applies |
| 2 | Two shipped documents contradict each other on the same action and you cannot tell which binds |
| 3 | A fence would have to be crossed to continue |
| 4 | A baseline check is red before you changed anything (P3) |
| 5 | A tool aborts in a way no document describes |
| 6 | The only way forward is to answer for the owner, and no `DEFERRED` or `BLOCKED` state lets the rest of the work proceed |

**Reporting a document that failed you.** Every such finding carries:

| Element | Requirement |
|---|---|
| The citation | As `document:line`. The line, not the section, not the gist |
| The command and its output | The command **as printed** and the output **as received**, verbatim. A paraphrased error message is a finding nobody can act on |
| The checkpoint | As the document states it, beside what actually appeared |
| The cost | Minutes, retries, or the work you had to author yourself |

That is the convention in `docs/walks/WALKING-YOUR-OWN-DOCUMENTS.md` §4, and its
cost rule is in §2. Findings go to whoever dropped you in. Recording them in the
kit's register with dispositions is the maintainer's act, not yours [R6].

---

## 9. Done, and what is not done

| Level 2 is done when | Detail |
|---|---|
| `python tools/verify.py` in the host prints **`VERIFY: PASS`** | |
| `python tools/hook_fixtures.py --strict --armed .claude/settings.json` | Prints `armed:` for every block, no `UNARMED:`, no `CONFIG WARNING:`, `0 skipped` |
| `python tools/deident_scan.py … --strict --tracked-only` prints **`DEIDENT SCAN: 0 hits`** | Reached by excluding **reviewed** files and never by deleting a token, over a `scope:` line you read, with the token list written where §8's grant permits and that path named in your report. Where no path was granted **for the token list**, the scan is **NOT RUN** and recorded as a punch item citing that clause: a complete Level-2 done list with one line open, not a green one |
| `python <kit>/tools/kit_doctor.py --root .` has been run | **Every** `[ATTENTION]` line has a disposition, fixed or a punch item |
| The handover is made | The punch list [§7], the wall-clock table [§6] and the findings list [§8] go to the owner |

| Level 1 is done when | Detail |
|---|---|
| `python <kit>/tools/kit_doctor.py --root . --level1` prints **`HEALTHY`** | The verdict word is not `PASS`, deliberately: nothing here certifies behaviour |
| Its three lines are read out in your report | **CERTIFIES**, **DOES NOT CERTIFY**, **REMOVAL COST** |
| The handover is made | The documents are committed, and the punch list, wall-clock table and findings list are handed over |

### Not done until the owner acts

State this list in the report. Every line is a limit on the green above it.

- **The project has no oracle of its own** until D-1 is answered. The runner
  certifies its judge surface and its enforcement layer, not the host's software
  [§4].
- **Step 5's negative control has not been performed** for the host's own gate,
  because there is no host gate yet.
- **Every default in `DEFAULT-CONTRACT.md` is in force unconfirmed, and the
  betrayal line is unknown**, until D-2 is answered. `LEVEL-1.md` Step 4 calls
  this the single riskiest gap on that page.
- **The escape rate reads `NO-ROUNDS-RECORDED`** until the project's first round
  lands a row in `docs/JUDGMENT-LEDGER.md`.
- **Nothing above judges content.** The checks read shape. An empty ledger with a
  correct header passes, and so does a profile whose observations are wrong
  (`LEVEL-1.md`, "What Level 1 does not give you").
- **Any `DEFAULT-TAKEN` item is a decision the owner has not made yet**, taken
  from a document rather than from them, and revisitable on the condition that
  document names.
