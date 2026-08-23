# ONBOARD — adopting OAR, for the agent doing the adopting

You are an AI agent. You have been dropped into a project — the **host** — and
asked to adopt this kit into it. This document is your entry point. Every other
reader's entry point is `README.md`.

**This document executes nothing.** It is not an installer, not a script and not
a tool. It adds two things on top of the documents the kit already ships:
**sequencing** — what to read and run, in what order — and **division of
labour** — which half of an adoption you may perform and which half belongs to
the host's owner. Every state change in the host repository is made by you,
running a command a shipped document prints, through a tool the kit already
ships. The kit remains rails, not a runtime (`README.md`, opening section).

**The shipped documents are the authority.** Where this page summarises one, it
names the document and the step or section, so you can check the summary against
the source. Where this page and a shipped document disagree, the shipped
document wins and the disagreement is a finding you report. This page never
replaces a shipped instruction and never adds a step of its own to the adoption
path.

**What this document does not claim.** It has not been measured. Whether routing
an agent through it makes an adoption faster, safer or more complete than
handing that agent `README.md` is an open question with no data behind it. The
only adoption figures this kit publishes are the ones in `README.md`,
`LEVEL-1.md`, `DECISION-BRIEF.md` and `EXISTING-PROJECT.md`, each carrying its
own label; do not restate them as this route's numbers, and do not make a speed
claim for this route at all. See §6.

---

## 1. Preconditions

Run these before anything else. Each is a gate on whether the rest of this
document means anything.

| # | Precondition | How you establish it |
|---|---|---|
| P1 | A host repository exists and you can run `git` and `python` in it | `git -C <host> rev-parse --show-toplevel`, `python --version` (3.10 or newer — `QUICKSTART.md` Step 0) |
| P2 | A kit checkout exists and you may treat it as read-only | `git -C <kit> rev-parse HEAD` — record the sha |
| P3 | The kit's own tooling is green **before** you touch the host | Run `QUICKSTART.md` **Step 0** in the kit clone: every line of its block exits 0 — the step's own checkpoint enumerates them |
| P4 | You know who the host's owner is, and whether they can answer questions in this session | Ask whoever dropped you in. This shapes the punch list (§7); it does not decide whether you proceed |
| P5 | The host's starting state is recorded | `git -C <host> rev-parse HEAD`, `git -C <host> status --porcelain`, and the branch name — captured verbatim before your first write |

**P3 is a HALT condition, not a warm-up.** If any Step 0 line is red before you
have changed anything, stop and report it (§8). A kit whose own selftests do not
pass cannot tell you anything about the host, and every downstream green would
be meaningless.

**P5 is the preflight rule from `docs/walks/WALKING-YOUR-OWN-DOCUMENTS.md` §1**,
applied to an adoption rather than a walk: freeze the subject and name it by
commit. Without it you cannot tell the owner which of the modifications in their
tree are theirs and which are yours.

---

## 2. Classify the host

The kit's documents are written for a repository whose only uncommitted content
is the kit's own. That describes a new project and almost nothing else
(`QUICKSTART.md`, opening; `EXISTING-PROJECT.md`, opening). Classification
decides which branch of every step you take, so do it before Step 1.

Run these probes in the host and record each answer:

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
# error rather than printing to stderr and moving on - so one absent file in a
# two-path `ls` reads as a failed command to most tooling. Probe one path per
# line, and read Test-Path's boolean rather than an error stream.
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

Also look for a test suite the project already trusts and for CI.

These probes are this document's own rather than a step of any shipped path.
Read their output, not their exit codes: a "not found" is an answer, and
`git check-ignore` exits 1 when nothing matches.

**The last two lines are the agent-vocabulary probe, and §4 turns on it.**
The two searches answer the same question over different sets — `git grep`
reads tracked files, the second reads the whole working tree including
untracked ones — and both exit 1 with no output when nothing matches, which
is the answer, not a failure. What their result decides is **§4's third
classification case**: a host that is configured for an AI assistant (a
`CLAUDE.md`, a `.claude/settings.json`, or both) and returns **no** occurrence
of this vocabulary is neither "runs no agents" nor "runs agents with the tiers
unevidenced", and §4 says what to do about it. Record the command you ran and
the empty result verbatim; §4 has you write into the punch text what you
searched for and did not find, and this is the search it means. A hit does not
by itself put the host in the second case — read what it is: the word *lane*
in a road-mapping project is not evidence of tiered spawning.

- **Greenfield** — no history or an empty tree, no `CLAUDE.md`, no
  `.claude/settings.json`, no `kit.config`, no ledgers, no suite. Take
  `QUICKSTART.md` as printed, new-project route.
- **Existing project** — **any** probe hits. Read `EXISTING-PROJECT.md` in full
  before Step 1, and take the existing-project branch each step names.
  `QUICKSTART.md` Step 1 states the two routes; the branches are inline at Steps
  1, 4, 6 and 9, and `EXISTING-PROJECT.md` is the same list in one place with
  the measured behaviour and the proven workaround for each collision.

**The host's uncommitted work is protected by that branch, not by you.** Three
mechanisms in the shipped documents do the protecting, and you take all three
where they apply: the render route never overwrites (§5, R2), the commit line is
edited to name files rather than directories (R3), and the certifying run is
reached by the backup-stash-certify-restore cycle rather than by committing
unfinished work (R4). Do not invent a fourth. If you find a case none of them
covers, that is a HALT (§8).

### Which level you are adopting

Level 1 installs documents only and installs no code into the host; Level 2 adds
the certification runner and the enforcement hook. `DECISION-BRIEF.md` states
what certifies at each level and what it costs. **The level is the owner's
decision.** Three states, and only one of them is yours:

1. **You were instructed which level.** Obey the instruction.
2. **You were not, and the owner can answer now.** Ask. One question, before any
   work, is cheaper than an adoption at the wrong level.
3. **You were not, and the owner cannot answer.** Take **Level 1** — `README.md`
   recommends it as the starting level and it is the reversible one — and record
   the escalation to Level 2 as a punch item (§7, D-5). Do not escalate on your
   own judgment.

---

## 3. Reading order, and the obedience rule

Read in this order. You are not skimming for commands: the branch conditions and
the failure signatures live in the prose.

| Order | Document | What it gives you |
|---|---|---|
| 1 | `README.md` | What the kit is and is not, the module map, the three levels, the routing |
| 2 | `DECISION-BRIEF.md` | What certifies per level, the exit cost, the limitations that constrain what you may claim |
| 3 | `LEVEL-1.md` **or** `QUICKSTART.md` | The path itself, per §2's level decision |
| 4 | `EXISTING-PROJECT.md` | Read beside the path, **before Step 1**, on the existing-project branch |
| 5 | `modules/03-verification/GATE-LINE.md` | Before any gate line is written, and first if the thing the host must not break is a test suite it already has |
| 6 | `modules/03-verification/ORACLE-WORKSHEET.md` | Step 3's material — read it, do not fill it (§7, D-1) |
| 7 | `modules/08-collaboration/SEED-INTERVIEW.md` and `DEFAULT-CONTRACT.md`, plus `DEFAULTS.md` (optional) | Step 8's material — read them, do not answer them (§7, D-2). §7 has you cite `DEFAULTS.md` by id if you take a value from it, so read it here or do not cite it — and `DEFAULTS.md`'s own write-question-5-first rule binds on this route too |
| 8 | `docs/walks/WALKING-YOUR-OWN-DOCUMENTS.md` | The conventions for recording a document that fails you (§8) |

The obedience rule has three clauses.

- **Run what is printed.** Where a document prints a command, run that command,
  not your improvement on it. Where it prints two routes with a branch
  condition, evaluate the condition against the host and take the route it
  names. Where a step's checkpoint states an output line, read that line and
  compare it to what appeared.
- **The shipped text is the authority.** This page's summaries carry citations
  so you can check them. A citation that does not match what the document says
  is a finding against this page; report it.
- **Where you cannot obey, stop rather than improvise.** A printed command that
  would destroy host work with no permitted alternative, or two documents that
  contradict each other on the same action, is a HALT (§8).

**You are an adopter, not a walker.** The walk method's hardest rule — use no
knowledge the documents did not give you — does not bind you here: your job is
to adopt the kit without damaging the host, and general knowledge is sometimes
what keeps the host safe. The recording rule does bind you. Every time you do
something the documents did not tell you how to do, it is a finding, and you
record it with what you had to author yourself
(`docs/walks/WALKING-YOUR-OWN-DOCUMENTS.md` §2).

---

## 4. The division of labour

Every instruction in the adoption path falls into one of three classes. Decide
the class before you act, and record the class in your report.

| Class | Definition | What you do |
|---|---|---|
| **MECHANICAL** | The documents say what to do and the answer is discoverable from the kit's text or from the host tree | Do it |
| **SHIPPED DEFAULT** | The documents prescribe a default value and name the condition for revisiting it | Take the default, cite the document, record it as a punch item in state `DEFAULT-TAKEN` so the owner can overrule it |
| **OWNER JUDGMENT** | No document supplies the answer and no evidence in the host supplies it | Do not answer it. Record it as a punch item in state `DEFERRED`, or `BLOCKED` if the mechanical half stops there |

The distinction that matters: taking a documented default is not judgment,
because the kit made that decision and published it. Choosing a value the kit
left open, on the owner's behalf, is judgment — and §7 is what you do with it
instead.

### The classes, step by step

`QUICKSTART.md`'s nine steps. Level 1's six steps are the subset marked L1.

| Step | Class | Notes and citations |
|---|---|---|
| 0 — prove the tooling | MECHANICAL | In the kit clone. P3 above |
| 1 — repo and config (L1 steps 1–2) | MIXED | `PROJECT_NAME` is discoverable. `GATE_COMMAND` ships correct for the layout Step 4 builds — confirm, do not change. `PROTECTED_PATH_ENABLED = false` is SHIPPED DEFAULT ("Leave the protected-path tripwire OFF"). The four tier names are OWNER JUDGMENT and are asked for here. `OWNER_ROLE` (Step 7 on this path) and `KNOWLEDGE_DIR` (Step 6) are OWNER JUDGMENT too, but this step does not ask for them — see below |
| 2 — see the hook fire | MECHANICAL | In the kit clone. Watch the dead-man clause go red; a gate that has never been red is unproven |
| 3 — the first oracle | **OWNER JUDGMENT** | `QUICKSTART.md` Step 3 is headed "an afternoon of thinking" (:366), and its budget paragraph says the first oracle "is thinking work and does not compress" (:20). Two sentences from two places, not one quotation. You may prepare its inputs; you may not fill the worksheet. §7, D-1 |
| 4 — the runner and its wiring | MIXED | Copy list, render/merge, the six constants, the commit and its checkpoints are MECHANICAL. `CERT_PATHS` scope (§7, D-6), the gate floor and the escapes ceiling are below |
| 5 — the negative control | MECHANICAL, **blocked by D-1** | It is run against the gate Step 3 specifies. With Step 3 deferred there is no such gate, and this step is *not performed* — a named gap, not a skipped step |
| 6 — standing rules, prove the hook (L1 step 3) | MIXED | The copy, the `JUDGE_PATHS` edit and the hook proof are MECHANICAL. The `CLAUDE.md` merge on an existing rules file, and `KNOWLEDGE_DIR`, are below. **On the `LEVEL-1.md` path the rules file is conditional** — `LEVEL-1.md` Step 3 takes it if you run agents, and that document governs where this page's summary is shorter — so *whether* it is installed is the tier-name question below rather than a mechanical copy |
| 7 — the ledgers (L1 step 3) | MIXED | Copying, substituting and the first `FAILURE-FLOOR.md` row are MECHANICAL — the step states that row exactly. A ledger-name collision ruling and the keep-or-delete of each seed lesson are OWNER JUDGMENT (§7, D-7). `RATIO_CEILING` stays as shipped: SHIPPED DEFAULT, named by the step as the one placeholder allowed to survive |
| 8 — the seed interview (L1 step 4) | **OWNER JUDGMENT, absolutely** | §7, D-2. The one rule this document states as unforgivable |
| 9 — publish safety (L1 step 6) | MIXED | The commit, the scan, the `scope:` and `tokens : N` reads, the exclusion of reviewed files and the final certifying run are MECHANICAL. The content of the token list is partly the owner's |
| — the doctor | MECHANICAL | `kit_doctor.py` is outside the path's flow and reads the result of it. Run it and disposition every `[ATTENTION]` line |

### The four values that are decisions, not fill-ins

These four are not all Step-1 keys, and treating them as if they were is the
measured render-early defect `QUICKSTART.md` describes under "Substituting
mechanically". Each is named below with the step that actually asks for it.
`QUICKSTART.md`:202-209 is the authority: Step 1 fills `PROJECT_NAME`, the three
tier names and `FORBIDDEN_SPAWN_TIER` (:202-203), and "Four keys come back later,
each at the step that needs it" (:208-209).

- **`OWNER_ROLE` — `LEVEL-1.md` Step 2; on the `QUICKSTART.md` path, Step 7.**
  `LEVEL-1.md` Step 2 lists `the owner` among the legitimate values. Take `the
  owner` as a SHIPPED DEFAULT unless the owner has told you what to call them.
  **Never write a person's name you were not given.** It is not a Step-1 key on
  the `QUICKSTART.md` path: the string appears there once, in Step 7's slot list.
- **`KNOWLEDGE_DIR` — `LEVEL-1.md` Step 1; `QUICKSTART.md` Step 6.** This is
  **OWNER JUDGMENT**, not a default you may take, and the reason is what the
  evidence can and cannot reach. `LEVEL-1.md`:76-77 calls it one of two things
  that "are decisions, not fill-ins", and the question it asks — where the
  durable knowledge of this project lives — is a fact about the owner's working
  world. The host tree cannot answer it. A repository that never mentions a
  vault, wiki or notes system is not a repository whose owner has none; that is
  the likely case, not the edge one, and absence of a mention is not evidence of
  absence. So:
  - **The host names such a place.** Record `DEFERRED` for the owner to confirm.
  - **The host names none.** Still `DEFERRED`, with the repo path `docs` carried
    as the **provisional** value on `LEVEL-1.md`:84-86's second branch, so the
    mechanical half proceeds. The punch item must say in words that you could
    not observe whether such a place exists — you searched the repository, and
    the repository is not where the answer lives.
  Do not record this one as `DEFAULT-TAKEN`. `doctor:l1-knowledge-dir` goes
  green on a recorded decision, and a green over an answer the agent supplied is
  the exact end state §7 exists to prevent.
- **The four tier names — `QUICKSTART.md` Step 1; `LEVEL-1.md` Step 2.**
  `ORCHESTRATOR_TIER`, `LANE_TIER`, `SWEEP_TIER`, `FORBIDDEN_SPAWN_TIER`
  describe the tiers the project actually uses. **There are three cases, not
  two.** The third was measured on a real host and is the likely one.
  - **The host runs no agents at all.** The tiering prose is a rule it cannot
    enforce. On the `LEVEL-1.md` path the rules file is conditional in the
    first place — Step 3 takes it if you run agents — so the honest act is not
    to install it, and to say in your report that you did not. On the
    `QUICKSTART.md` path, where Step 6 installs it, delete every rule you
    cannot yet enforce and **record that deletion**.
  - **The host runs agents and the tiers are evidenced nowhere in it.** They
    are OWNER JUDGMENT and they **block**: an unfilled tier name is a
    placeholder, `FORBIDDEN_SPAWN_TIER` left unset fails silently, and Step 6's
    `0 skipped` checkpoint becomes unreachable (`QUICKSTART.md` Step 1).
  - **The host is configured for an AI assistant and carries no agent
    vocabulary.** It has a `CLAUDE.md`, or a `.claude/settings.json`, or both,
    and no occurrence of *agent*, *subagent*, *lane*, *charter*, *spawn*,
    *model tier* or a model name in any of its files. **§2's last two probe
    lines are the search that decides this**, and they are where the strings
    are written as a command; run them there and carry the result here rather
    than composing a search of your own. Neither branch above
    fits: an assistant demonstrably works in this repository, so "runs no
    agents at all" is false, and nothing in it evidences tiered spawning, so
    "does run agents" in the sense these four keys describe is unevidenced.
    **Do not pick a branch.** The question underneath — does this project run
    agents in the sense the tier names describe — is a fact about how the owner
    works, and this section's own definition makes it OWNER JUDGMENT: no
    document supplies the answer and no evidence in the host supplies it.
    Record it in §7 as a punch item, `DEFERRED` where the mechanical half
    continued and `BLOCKED` where it stopped, leave all four keys unset, and
    write into the punch text what you searched for and did not find. At
    Level 1 nothing installed interpolates them — they reach a tree only
    through module 01's rules file, which this branch defers — so nothing is
    broken today, and they must be answered before module 01 is adopted or
    before Level 2.
- **`CERT_PATHS` — the end of `QUICKSTART.md` Step 4**, not Step 1. What is
  being certified is a scope decision, and it is **OWNER JUDGMENT** whichever
  layout the host has: a `VERIFY: PASS` over a scope nobody ruled certifies a
  boundary the owner never drew. Where the host has the `src`/`tests` layout the
  document assumes, take those paths as the provisional value so the runner
  stands up, and record `DEFERRED`; where the host's layout is anything else,
  name the paths the evidence supports and record `DEFERRED` the same way.
  Either way it is §7's **D-6**, and the punch text names the paths you used and
  the evidence you used them on.

### What a certification without the owner's oracle actually says

If Step 3 is deferred, the runner still stands up: the kit ships `judges`,
`hooks` and `escapes` gates. `QUICKSTART.md` Step 4 item 5 has you replace
`example_unit` with your own gate and delete `example_lint`; with the oracle
deferred there is nothing to replace `example_unit` with, so both example
entries go — **from `GATES` and from `RUN_ORDER`, both places, or the selftest
goes red.** Delete them from `GATES` alone and selftest **section I** ("every
gate in `RUN_ORDER` is actually exercised") fails naming both entries, because a
gate left in `RUN_ORDER` with no check that ran is exactly what that section
exists to catch (`QUICKSTART.md`:778-780; `verify.py`'s own header warns that a
permanently-skipped gate in `RUN_ORDER` reports PARTIAL and can never certify).
Under the complete edit it breaks nothing — the step says so, their payloads
stay behind in the kit clone, section F resolves a live gate name at runtime,
and section I passes with an empty want. This deferred-oracle route, deleting
**both** examples with nothing to replace them, is not a case `QUICKSTART.md`
contemplates; it is this page's, so the instruction is complete here.
A `VERIFY: PASS` over that runner is real and it is thin. It certifies that the
files deciding what green means are committed and clean, that the enforcement
layer proves itself against its fixtures, and that the escape rate is published.
**It certifies nothing about whether the host's own software works**, because no
gate in it judges the host's software. Say exactly that in your report, beside
the green line. A green nobody has bounded is a green that will be over-read.

Expect `[ATTENTION] doctor:vacuous-gate` on those three gates for want of an
`docs/ORACLE-<gate>.md` page. `QUICKSTART.md` Step 3 names three honest answers
to it (`:409-415`) and **prescribes none of them**, so this is not a SHIPPED
DEFAULT — a SHIPPED DEFAULT needs a value the documents prescribe and a named
condition for revisiting it, and neither exists here. It is **OWNER JUDGMENT**:
record it `DEFERRED`, name the three answers, and say which one you are holding
the tree in meanwhile. Hold it in the second answer — accept the ATTENTION and
record why — because it is the only one of the three that writes nothing on the
owner's behalf. Do not write the `docs/ORACLE-<gate>.md` pages to make the check
green; that is the first answer, and it is the owner's to choose.

---

## 5. Executing the mechanical half

Eight rules. All of them are restatements of shipped instructions, cited.

**R1 — Read the verdict word, never the exit code alone.** This kit judges runs
by their output line. Exit 2 means `INSTRUMENTED` or `ABORTED` from the runner —
opposite kinds of news — and `ABORT` from `kit_render.py` and `kit_doctor.py`.
`kit_doctor.py` reports `HEALTHY`/`ATTENTION` and never `PASS`, because it
diagnoses and does not certify. Run one command at a time and read its output
before the next.

**R2 — Over a pre-existing file, `kit_render.py` is the required route, not a
convenience.** `QUICKSTART.md`, "Substituting mechanically", states this
directly, and `EXISTING-PROJECT.md` rows 1 and 2 carry the measurements behind
it: a `cp` onto an existing `CLAUDE.md` destroys it with no backup, and placing
the substituted template at an existing `.claude/settings.json` drops its
`allow` and `deny` rules silently. The tool writes only `<name>.kit-new`, prints
a diff, merges the settings file structurally, and names every slot it could not
fill. **Moving a `.kit-new` into place is your act** — read the diff first, and
for a rules file build the merged result the way the step describes: kit rules as
the base, the host's existing rules preserved **verbatim** under a marked
heading of their own. Where the two rule sets conflict, that is not a merge
decision, it is an owner decision (§7).

**R3 — Never stage blindly.** No `git add -A`, no `git add .`, no `git add -u`.
Name paths, and on an existing host drop the directory pathspecs: `src` and
`tests` take everything under them, including work in progress, into a commit
titled "adopt the kit". Run `git status` before every add. After a **failed**
add run `git status` again and `git reset` if the index holds something you did
not mean to stage — the ignored-path failure exits 1 and stages every other path
on the line anyway, while the missing-path failure exits 128 and stages nothing
(`QUICKSTART.md` Step 4, the two failure signatures — `:896-900`, with the
missing-path half also at `:861`).

**R4 — Never commit unfinished work to manufacture a green.** On a host with
work in progress inside `CERT_PATHS`, the certifying run is red and the runner
is right. The sanctioned route is backup, stash, certify, restore: take both
backups, note the sha256, and verify byte-identity afterwards
(`QUICKSTART.md` Step 4). **Report both states** — red with the work on disk,
green with it stashed. A project that publishes only the second has learned to
stash before it looks. The first backup is written outside the host, so it needs
an operator-designated path like the report does; §8's capability grant is where
that path comes from and states the disposition when there is none.

**R5 — An ignore rule over a judged path is force-tracked, not deleted.** Run
`git check-ignore -v <path>` **before** `git add -f <path>`: once a path is
tracked the diagnostic prints nothing. Deleting a directory rule like `.claude/`
also uncovers the session state and the certification token the kit's own
ignore file says must never be committed (`QUICKSTART.md` Step 4;
`EXISTING-PROJECT.md` row 3).

**R6 — You do not write into the kit clone.** Treat it as read-only. Your writes
go into the host repository and nowhere else, plus the report path whoever
dropped you in gave you. `kit_render.py` refuses to write into the kit clone or
outside the target and aborts if it would; do not work around a guard that
fires. (`QUICKSTART.md` Step 1; `tools/kit_render.py`, guard 1.)

**R7 — Nothing destructive that no document printed.** No force push, no history
rewrite, no branch deletion, no `git clean`, no `git checkout --` or
`git restore` over a host file you did not create. If recovering from your own
mistake seems to need one of these, that is a HALT.

**R8 — Record it when you improvise.** Anything the documents did not tell you
how to do, and you did anyway, is a finding with what you authored attached
(§8).

---

## 6. Recording wall-clock, and labelling it honestly

**Read a real clock.** Two reads per step — one before the step's first command,
one after its checkpoint — and subtract. Never write a duration you did not
measure, and never reconstruct one afterwards from memory of how long it felt.

```bash
python -c "import time; print(time.strftime('%Y-%m-%dT%H:%M:%S'))"
```

```powershell
# ⚠ pwsh: the bash line runs as written, but the inner single quotes are the
# only thing keeping `%Y` out of PowerShell's way - use the native reader and
# there is nothing to quote.
Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
```

**Label it for what it is: agent tool-time.** It is the elapsed time of a model
executing tool calls. It is not a person adopting a toolkit, and the kit already
holds that line in two places — `EXISTING-PROJECT.md`'s provenance section keeps
the brownfield walk's timings off the page for exactly this reason, and
`DECISION-BRIEF.md`:76-77 says of that same walk that it "produced no usable
human time estimate — it measures an agent executing tool calls". Reuse the
kit's wording rather than inventing your own — but **copy it from the lines you
are citing, with the document open, and never from memory.** A quotation that
cannot be found in the document it names is a finding against this page (§3),
and it is worse than a paraphrase: an obedient reader will carry it onward
under a citation that does not hold it. If you cannot locate the string, drop
the quotation marks and cite the section for the idea instead.

**Do not compare it to the kit's published budgets.** The 90–120 minutes in
`README.md` and `QUICKSTART.md`, the 30–45 minutes in `LEVEL-1.md` and the
3.5–5 hours in `DECISION-BRIEF.md` are sums of per-step estimates, reconciled
against walks performed by LLM personas rather than by people; no human has
walked either document end to end. A tool-time number set beside them reads as a
speed-up and is not one, because the two are different instruments.

What the number is good for is **ratios inside one instrument**: which step
consumed the run, how much of it was blocked, and how one agent-led run compares
to another agent-led run of the same shape.

Record one row per step and hand the table to the owner:

| Step | Started | Ended | Elapsed | Verdict word | Punch items raised |
|---|---|---|---|---|---|

Two exclusions, stated in the table's caption: **time the owner spends is not in
your number**, and **time you spent blocked on an owner answer is recorded on
its own row** rather than folded into a step.

**No speed claim ships from this document.** Whether this route changes adoption
time against an agent working from `README.md` alone is unmeasured. Publish the
measurement or publish nothing.

---

## 7. The judgment half — the deferral punch list

The mechanical half compresses. The judgment half does not, and the failure mode
this section exists to prevent is an agent that compresses it anyway by
answering for the owner.

### The unforgivable failure

**Never write an answer the owner did not give.** Not in the collaboration
profile, not in a ledger, not in `kit.config`, not in the report. Not as a
guess, not as a placeholder phrased to read like an answer, not as a plausible
date. `LEVEL-1.md` Step 4 states the reason in one line: *a date that parses is
not a date somebody agreed to*, and an invented one reads exactly like a real
calendar entry. An invented answer does not merely record something false; it
removes the owner's chance to notice that nobody has decided yet. Every other
failure in this document is recoverable by re-running a command. This one is
not.

The kit's own precedent is the design to copy: at `LEVEL-1.md` Step 4 the
interview may be `held`, `scheduled … confirmed by …`, or `not yet held`, and
**all three are green**, because "the owner has not answered yet" is a stated
answer. What fails the check is leaving the shipped menu in place, so that
nobody ever said which is true. Deferral is a named, visible state. Silence and
invention are the two things that are not.

### The states

| State | Meaning | What it requires |
|---|---|---|
| `ANSWERED` | The owner answered in this session | Their words, verbatim, with when and where they said them |
| `DEFAULT-TAKEN` | A default the kit itself prescribes was taken | The citation, the value, and the condition the document names for revisiting it |
| `DEFERRED` | Owner judgment, not yet given, nothing blocked | Where the answer goes when it arrives — file and step |
| `BLOCKED` | Owner judgment, not yet given, and the mechanical half stopped here | Everything `DEFERRED` requires, plus what is unreachable until it is answered. A step recorded NOT RUN under §8's grant clause lands here, naming the path the owner must grant |

### The standing items

Raise these on every adoption, even when the answer arrives immediately — the
record of who decided is worth as much as the decision.

| ID | The decision | Why it is the owner's | Where the answer lands |
|---|---|---|---|
| D-1 | The first oracle: what this project must not break, its required output line, its floor, its negative control | `QUICKSTART.md` Step 3 — design work, "an afternoon of thinking", and it does not compress. Choosing what matters most is a claim about the project that only its owner can make | `docs/ORACLE-<gate>.md`, then Step 4 item 5 and Step 5 |
| D-2 | The seed interview's five questions, including question 5, the betrayal line | `modules/08-collaboration/SEED-INTERVIEW.md`. Answers are captured **verbatim**; the phrasing carries information a summary loses | `docs/collaboration-profile.md`, and its `INTERVIEW:` status line |
| D-3 | `KNOWLEDGE_DIR` — where durable knowledge lives, and which copy is source of truth | `LEVEL-1.md` Step 1, `QUICKSTART.md` Step 6. It is a fact about the owner's working world | `kit.config` or `kit.config.local`, `CLAUDE.md`, the profile |
| D-4 | `OWNER_ROLE` and the four tier names | `LEVEL-1.md` Step 2 for both; on the `QUICKSTART.md` path the tier names are Step 1 and `OWNER_ROLE` is Step 7. They name the project's own working vocabulary | `kit.config` |
| D-5 | The adoption level, and escalation from 1 to 2 | `DECISION-BRIEF.md`'s table is the input; the choice is a commitment of the project's time | The adoption report |
| D-6 | `CERT_PATHS` — what is being certified, and why these paths | `QUICKSTART.md`, end of Step 4. Scope is a claim about what the project must not break; a `VERIFY: PASS` over paths nobody ruled certifies a boundary the owner never drew (§4) | `tools/verify.py`'s `CERT_PATHS` constant — authoritative — and the matching `kit.config` key |
| D-7 | Each seed lesson: keep it, or delete it | `modules/04-ledgers/LESSONS.md` ships them under "Seed lessons — earned in the reference build" and says "Delete any that do not apply". They were earned somewhere else; a lesson this project never paid for reads in its ledger exactly like one it did | `<LEDGERS_DIR>/LESSONS.md` (`LEVEL-1.md` Step 3) |

You may prepare **inputs** for D-1 without answering it: the candidate gate
command, the suite's current collected count from `python -m pytest
--collect-only`, the `GATES` entry `tools/gate_line.py --gate-spec` prints, and
what the host's checks demonstrably do and do not cover today. Label them as
material for the owner's worksheet, not as a worksheet.

**An optional starting state for D-2.**
`modules/08-collaboration/DEFAULTS.md` ships one program's calibration,
de-identified to its shape and labelled as that one program's values rather than
best practice. It is a SHIPPED DEFAULT source for **the working contract you run
under before the owner has ruled**, extending `DEFAULT-CONTRACT.md`'s in-force
standing to the calibration classes the eight defaults do not cover: cite the
page and the value's id, and record `DEFAULT-TAKEN` with the revisit condition
that page names. It is **not** an answer to D-2. Do not copy a default into one
of the profile's verbatim answer blocks, do not enter one in the overrides table
as an override, and do not move the `INTERVIEW:` line off `not yet held` because
the page exists — D-2 stays `DEFERRED` until the owner has either walked that
page's realignment ask or answered the five questions cold. The page states the
same rule and cites this section for it.

### The items the host raises

Add one row per collision the host actually presents. Each already has a kit
document behind it — cite it rather than reasoning from first principles:

- **Ledger-name collision** — an existing `LESSONS-LEARNED.md` or
  `TOKEN_LEDGER.md`. Rename, freeze, or move `LEDGERS_DIR`
  (`LEVEL-1.md` Step 3; `EXISTING-PROJECT.md`, "Also measured, at Level 1").
- **Rules that conflict on merge** — where the host's `CLAUDE.md` and the kit's
  template say different things about the same act. `QUICKSTART.md`:1011-1012
  makes it an owner instruction: where the two rule sets conflict, "that is a
  decision to make now and write down, not a duplicate to leave standing".
- **CI weaker than the local gate** — after Step 6 the local certification
  proves strictly more than the host's CI does, and CI is the control outside
  the blast radius. The proven disposition is to log it as adoption debt in the
  host's `docs/FAILURE-FLOOR.md` and close it when module 07 lands
  (`EXISTING-PROJECT.md` row 7). Do not modify the host's CI during an adoption.
- **More than one machine or more than one person** — `.claude/settings.json` is
  per-machine, committed and judged at once. Read `KNOWN-ISSUES.md`, "Whose
  settings file? — the team story", before committing that file, and raise the
  design as a punch item (`QUICKSTART.md` Step 4, "ONE MACHINE PER SETTINGS
  FILE").
- **The de-identification token list** — machine path fragments and the username
  you can supply from the environment; the owner's name and employer you cannot.
  A scan is only as good as its list, so a green scan over a list you assembled
  alone is labelled as one (`QUICKSTART.md` Step 9). **Where the list may be
  written is §8's capability grant**, and with no path granted **for the token
  list itself** the scan is a punch item reading NOT RUN rather than a step you
  improvise a location for. The path you were given for your report is not one.

### Where the punch list lives

In the adoption report you hand the owner, and **also** in the tree wherever the
kit already has a place for it: the interview's state in the profile's
`INTERVIEW:` line, adoption debt in `docs/FAILURE-FLOOR.md`, and unset keys named
in the report. Create no new file for it. A punch list in a file nobody opens is
the same as no punch list.

---

## 8. Constraints, HALT, and reporting a document that fails you

**Fences.** You write into the host repository and into the report path you were
given. Not the kit clone (R6). Not anywhere else on the machine.

**The operator capability grant.** That fence already has one exception, and it
is worth naming rather than leaving implicit: the report path is a file outside
the host that whoever dropped you in designated — **for the report, and for
nothing else**. Other shipped steps need exceptions of the same kind for
different artifacts. `LEVEL-1.md`:398's de-identification scan (Step 6) takes
`--tokens <a-path-outside-this-repo>`; `QUICKSTART.md`:919's first backup writes
`wip.patch` outside the repository being certified. Each of those artifacts is
one this kit deliberately keeps out of the tree — the token list because it
holds the exact strings you do not want published, the backup because the tree
it protects is the tree about to be stashed — so an agent holding only the fence
above cannot run either step as printed, and the intersection of the two rules is
empty. The exception is therefore a **capability the operator grants**, with four
properties, all of them requirements:

- **DEFAULT-CLOSED, PER ARTIFACT.** If the operator designated no path **for
  a given artifact**, the capability to write that artifact does not exist. Do
  not create one. Record the step that needed it as **NOT RUN**, citing this
  clause and naming what it would have covered, as a punch item in §7.
- **HUMAN-GRANTED.** The operator names the path. You never choose one, never
  infer one from the environment, and never promote a directory you happened to
  create into a grant. **You never infer a grant from a path's existence.**
  That a path was handed to you, that a directory is there, that it is
  writable, or that an artifact of yours already sits in it — none of these is
  a grant. A grant is an act of designation by the operator, for a named
  purpose, or it is not a grant.
- **ENUMERATED PURPOSE, ONE PER PATH.** A grant covers **one artifact type at
  one path**, and **each artifact type requires its own explicitly designated
  path**. The current list, which the shipped documents set rather than this
  clause: the handoff report; the de-identification token list
  (`LEVEL-1.md`:398); the work-in-progress backup (`QUICKSTART.md`:915-927).
  **This is a current list, not a closed one, and the extension rule is part of
  the grant: every artifact type a shipped document requires to be written
  outside the host gets its own operator-designated path, on these same four
  properties. Where no path was designated for such an artifact, the step that
  needed it is recorded NOT RUN, citing this clause, as a punch item in §7 —
  the rule reaches a new artifact type by itself, so finding one is a finding
  you report (§3), never a reason to choose a path.** The report path is a
  grant for the report: it is not a token-list path, not a backup path, and
  neither is the directory it sits in. A granted path is a **file** unless the
  operator named a **directory**. Nothing outside the artifact type a path was
  granted for may be written under it — no host files, no scratch copies, no
  evidence, no notes.
- **USE-RECORDED.** Your run report names every granted path, the artifact type
  each was granted for, and every file you wrote there. A capability whose use
  is not recorded is indistinguishable from no fence at all. **Residual,
  stated:** this record is self-attested. The report attests to its own
  compliance and no independent artifact corroborates it, which is why the
  properties above are written as requirements rather than as checks.

**The common case, stated so the clause cannot be read the other way.** You are
handed a report path on essentially every run, and a token-list path on almost
none. The ordinary outcome is therefore: report written to its granted path,
de-identification scan **NOT RUN**, punch item raised citing this clause and
naming what the scan would have covered. That is the designed outcome, not a
degraded one — an operator who has not thought about the token list has not
consented to one being written, and the file in question holds the exact
strings they do not want published. **If you find yourself concluding that you
may write something because a path exists, stop: that is the reading this
clause forbids.**

**The work-in-progress backup, and its consequence stated.** §5's R4 route —
back up, stash, certify, restore — writes `wip.patch` outside the host, and
`QUICKSTART.md`:925 makes both backups mandatory rather than optional. So on a
host carrying uncommitted work inside `CERT_PATHS`, with no backup path
designated, the disposition is the same one: do not stash, do not certify,
record the certifying run **NOT RUN** citing this clause, and raise a punch item
naming the path the owner would have to grant for that host to be certifiable by
an agent. Hand it back rather than certifying around it — committing the work to
clear the tree is the thing R4 exists to forbid. That is the designed outcome
too, and it is why the brownfield case is covered rather than a HALT: §5's "do
not invent a fourth" holds because R4 is not missing here, only ungranted, and
§3's contradiction HALT does not fire because the two rules no longer disagree.

`LEVEL-1.md`:402's rule stands unchanged — the token file lives outside the
repository — and this clause is where the path it needs comes from, as it is for
the backup. **The rejected alternative, and why:** a token list inside the tree
is one force-add from published, and a `wip.patch` inside the tree is one
blanket `git add` from being the committed unfinished work R4 forbids.

**Commits.** Only in the host repository, only where a shipped document
instructs a commit — `QUICKSTART.md` Steps 4 and 9, `LEVEL-1.md` Step 6 — and
only naming paths (R3). Use the commit messages the documents print. Do not
commit on the host's behalf outside those points, and do not push unless you
were told to.

**HALT.** You hold halt authority at any depth. Return the verdict `HALT` with a
reason, the citation, and the tree state as you are leaving it. Halt when:

- a shipped command would destroy host work and no non-destructive alternative
  in the documents applies;
- two shipped documents contradict each other on the same action and you cannot
  tell which binds;
- a fence would have to be crossed to continue;
- a baseline check is red before you changed anything (P3);
- a tool aborts in a way no document describes;
- the only way forward is to answer for the owner, and no `DEFERRED` or
  `BLOCKED` state is available that lets the rest of the work proceed.

A halt is a verdict, not a failure. `docs/walks/WALKING-YOUR-OWN-DOCUMENTS.md`
§2 states the reason it exists: an agent that cannot stop will invent a way to
continue, and the invention is the thing you least want in the report.

**Reporting a document that failed you.** Every such finding carries:

- the citation as `document:line` — the line, not the section, not the gist;
- the command **as printed** and the output **as received**, verbatim; a
  paraphrased error message is a finding nobody can act on;
- the checkpoint as the document states it, beside what actually appeared;
- what it cost — minutes, retries, or the work you had to author yourself.

That is the convention in `docs/walks/WALKING-YOUR-OWN-DOCUMENTS.md` §4 and its
cost rule in §2. Findings go to whoever dropped you in. Recording them in the
kit's register with dispositions is the maintainer's act, not yours; you do not
edit the kit (R6).

---

## 9. Done, and what is not done

### Done — Level 2

- `python tools/verify.py` in the host prints **`VERIFY: PASS`**.
- `python tools/hook_fixtures.py --strict --armed .claude/settings.json` prints
  `armed:` for every block, no `UNARMED:`, no `CONFIG WARNING:`, `0 skipped`.
- `python tools/deident_scan.py … --strict --tracked-only` prints
  **`DEIDENT SCAN: 0 hits`**, reached by excluding **reviewed** files and never
  by deleting a token, over a `scope:` line you read — with the token list
  written where §8's capability grant permits, and the granted path named in
  your report beside the artifact type it was granted for. Where no path was
  granted **for the token list**, the scan is **NOT RUN**, recorded as a punch
  item citing that clause; that is a complete Level-2 done list with one line
  open, not a green one.
- `python <kit>/tools/kit_doctor.py --root .` has been run and **every**
  `[ATTENTION]` line has a disposition — fixed, or a punch item.
- The punch list (§7), the wall-clock table (§6) and the findings list (§8) are
  handed to the owner.

### Done — Level 1

- `python <kit>/tools/kit_doctor.py --root . --level1` prints **`HEALTHY`** —
  the verdict word is not `PASS`, and that is deliberate: nothing here certifies
  behaviour.
- Its three lines are read out in your report: **CERTIFIES**, **DOES NOT
  CERTIFY**, **REMOVAL COST**.
- The documents are committed, and the punch list, wall-clock table and findings
  list are handed over.

### Not done until the owner acts

State this list in the report. Every line is a limit on the green above it.

- **The project has no oracle of its own** until D-1 is answered. The runner
  certifies its judge surface and its enforcement layer, not the host's
  software (§4).
- **Step 5's negative control has not been performed** for the host's own gate,
  because there is no host gate yet.
- **Every default in `DEFAULT-CONTRACT.md` is in force unconfirmed, and the
  betrayal line is unknown**, until D-2 is answered. `LEVEL-1.md` Step 4 calls
  this the single riskiest gap on that page, and the profile is written to say
  so out loud rather than look complete.
- **The escape rate reads `NO-ROUNDS-RECORDED`** until the project's first round
  lands a row in `docs/JUDGMENT-LEDGER.md`. That is the true state of a new
  adoption, published rather than dressed up as a zero.
- **Nothing above judges content.** The checks read shape: an empty ledger with
  a correct header passes, and so does a profile whose observations are wrong
  (`LEVEL-1.md`, "What Level 1 does not give you").
- **Any `DEFAULT-TAKEN` item is a decision the owner has not made yet**, taken
  from a document rather than from them, and revisitable on the condition that
  document names.
