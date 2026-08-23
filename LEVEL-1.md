# LEVEL 1 — the documents, in 30 to 45 minutes

This is the kit's entry path. It installs **documents only**: four ledgers, a
collaboration profile, and the standing rules as prose. It installs **no
settings file, no hook, no verification runner and no CI**, so nothing here
changes what your harness does, and nothing here can break a build.

It ends in a check you can run: `kit_doctor.py --level1` reads the documents
you installed and prints one summary line stating what it certifies, what it
does **not** certify, and what removing the level costs.

**Who this is for.** Anyone deciding whether the kit is worth an afternoon —
and anyone who is not the person whose judgment binds the project. Step 4's
seed interview needs the owner. If that is someone else, you schedule it and
finish this path green anyway; that is a designed end state, not a shortcut.

**What Level 1 is not.** It is not a trial version of Level 2. It is the level
whose value is what your project *records about itself*: what was decided, what
enforces it, what was learned, what it cost. `README.md` recommends starting
here for that reason, not as a warm-up.

---

## The budget, and where the number comes from

| Step | What it is | Time |
|---|---|---|
| 1 | Decide two things | 5 min |
| 2 | Copy the config and fill five keys | 5 min |
| 3 | Install the six documents | 10 min with the render tool; 20–25 by hand |
| 4 | Run the seed interview, or schedule it | 15 min if you are the owner; 2 min if you are not |
| 5 | Run the Level-1 check | 2 min |
| 6 | Commit, and scan before you publish | 5 min |

**30 minutes** is the fast path: the render tool, and an interview you schedule
rather than hold. **45 minutes** is the interview held today. Add 10–15 minutes
if you substitute the slots by hand, which is the kit's primary doctrine and
still a legitimate choice.

**These figures are estimates, not measurements.** They are a sum of per-step
first-time estimates by the kit's maintainer. No human has walked this path and
timed it; `KNOWN-ISSUES.md` records that all adoption evidence in this
repository comes from LLM-persona adoption walks, and `docs/walks/` publishes
the prompt behind each one.

**The honest dependency:** the 10-minute figure for step 3 assumes
`tools/kit_render.py`, the optional mechanical substitution path. That tool
ships. It is offered *beside* the by-hand path, not in place of it — the
templates are documents you are meant to read and argue with — so step 3 gives
both routes and the time cost of each.

## Shell, and where each command runs

Every command block below says which directory to run it in. Two locations are
involved and they are not interchangeable:

- **your project** — the repository you are adopting into;
- **the kit clone** — this checkout, which stays read-only. Nothing in this
  path copies an executable into your project, so the two tools you run are
  invoked by their path inside the kit clone.

The blocks run as-is in `pwsh` (7+), `bash` and Git Bash. Forward slashes work
everywhere, including Windows. **That claim is not machine-checked**, unlike
`QUICKSTART.md`'s equivalent section, which `adoption_smoke.py` phase 9
executes through `pwsh`. It was verified by hand on the shells named; treat it
the way this document treats its time budget.

> **`⚠ Debian/Ubuntu:` `python` may not exist** — those hosts ship `python3`
> and no `python` shim unless `python-is-python3` is installed. Substitute
> `python3` throughout, or install the shim. Nothing else changes.

---

## Step 1 — Decide two things (5 min)

Level 1 asks for two answers. Both are decisions, not fill-ins, and both are
checked in step 5.

**1. Where does durable knowledge live?** This is `KNOWLEDGE_DIR`: the notes
system, wiki or vault that outlives any one session. The documents you install
name it as the source of truth for the profile and for standing decisions.

- **You have such a place:** its absolute path is the answer.
- **You do not:** the answer is the repo path `docs`, and the repo copies then
  *are* source of truth rather than mirrors. Say so where a template says the
  repo copy is a mirror.
- **You want the key on record as "no such place":** the literal value `NONE`.
  Then substitute the repo path `docs` at the two sites that interpolate the
  slot — the templates do not branch on the value, so `NONE` substituted into a
  document produces a sentence pointing at a directory called NONE.

**2. Who owns the judgment?** Name the person whose ruling settles a question —
`OWNER_ROLE` in the config, and the person step 4's interview needs. If that is
not you, you cannot answer step 4's five questions on their behalf, and the
path does not ask you to.

## Step 2 — Copy the config out of the kit, and fill five keys (5 min)

Run this in: **your project**

```bash
cp /path/to/kit/kit.config.example ./kit.config
```

**If `kit.config` already exists, do not run that line.** `cp` overwrites
without asking on every shell named above, and it destroys the answers already
in the file. Check your config against the table below and **append** what is
missing at its shipped value. Step 5's `doctor:l1-config-complete` names every
key you are short.

Make five decisions — eight keys, four of which are the tier names — and leave
every other key exactly as it ships:

| Key | Value |
|---|---|
| `PROJECT_NAME` | your project's name, as it should read in a ledger heading |
| `OWNER_ROLE` | how the documents should refer to the owner (`the owner`, `the client`, a name) |
| `KNOWLEDGE_DIR` | step 1's first answer |
| `LEDGERS_DIR` | where the four ledgers live; ships as `docs` |
| `ORCHESTRATOR_TIER`, `LANE_TIER`, `SWEEP_TIER`, `FORBIDDEN_SPAWN_TIER` | the model tiers you actually use, if you run agents; the rules file names them in prose |

**An absolute `KNOWLEDGE_DIR` does not go in `kit.config`.** That file is the
committed half, and one machine's absolute path is wrong for everyone else who
clones it. Copy `kit.config.local.example` to `kit.config.local`, put the
absolute value there, and add `kit.config.local` to your `.gitignore`. Both
halves are read from the same directory, `.local` last. On the repo-path branch
(`docs`) you need neither the local file nor the `.gitignore` line.

Everything else in `kit.config` registers keys for modules Level 1 does not
install. Leaving them as shipped is correct here.

## Step 3 — Install the six documents (10 min with the tool, 20–25 by hand)

The six are four ledgers, the collaboration profile, and the standing rules:

| Document | From | Answers |
|---|---|---|
| `<LEDGERS_DIR>/JUDGMENT-LEDGER.md` | `modules/04-ledgers/` | what the owner decided, and what would go red if we undid it |
| `<LEDGERS_DIR>/FAILURE-FLOOR.md` | `modules/04-ledgers/` | what we require of ourselves, and what actually enforces it |
| `<LEDGERS_DIR>/LESSONS.md` | `modules/04-ledgers/` | what we learned the hard way |
| `<LEDGERS_DIR>/TOKEN-LEDGER.md` | `modules/04-ledgers/` | what it cost, and how much of that was ceremony |
| `docs/collaboration-profile.md` | `modules/08-collaboration/PROFILE-TEMPLATE.md` | how to work with the owner |
| `CLAUDE.md` *(recommended, not required)* | `modules/01-governance/CLAUDE.md.template` | the standing rules, as prose |

**If this repository already keeps ledgers, decide before you copy.** The four
filenames above are fixed — the checks read those names, and `LEDGERS_DIR` is
the only thing you can move. A `LESSONS-LEARNED.md` or a `TOKEN_LEDGER.md`
already in that directory answers the same question under a different
spelling, and installing beside it leaves two ledgers where one is the
repository's history and the other is the one the checks read. Pick one and
record it: **rename** the existing ledger onto the kit's name and carry its
content forward; **freeze** it as the record up to adoption and say so at the
top of both files; or point `LEDGERS_DIR` somewhere the two sets do not share
a directory. Step 5's `doctor:l1-ledger-collision` names any collision it
finds and changes nothing.

**Five of the six are required; `CLAUDE.md` is the sixth.** Take it if you run
agents — it is module 01 as prose, and it is what the ledgers are rules *for*.
Step 5's check treats it as optional and distinguishes three states, because on
a repository that already had a rules file *present* and *adopted* are
different facts:

- **Not there.** Reported as not taken, and green.
- **There, and carrying module 01's prose.** Counted as the sixth document, and
  the removal cost names it — as a revert, if you merged it into a file you
  already had.
- **There, and reading as your own file.** Not counted, named in the finding,
  and the removal cost **never** names it. The check decides this by counting
  module 01's own **fingerprints** — eight strings that carry no substitution
  slot and so survive rendering unchanged; seven are section headings and the
  eighth is a rule sentence — and two or more of them mean the file carries
  the kit's prose, however it got there.

  **What that count can and cannot tell you, because the output says only
  what it can support.** It is a count, not a provenance: the check cannot
  establish who wrote the file, whether it was touched, or whether this
  adoption installed it. The residual therefore runs both ways, and **both
  branches print the two numbers the decision used** — an adoption that
  reworded nearly every kit heading reads as your own file, and a file of
  yours that happens to carry two of them reads as adopted. Where you know
  which it is and the check cannot, say so in your report; the not-adopted
  line says the same thing on every run.

The profile's filename is fixed — the rules file names it — but its **location
follows step 1**. When `KNOWLEDGE_DIR` is a real directory outside the
repository, that copy is source of truth and `docs/collaboration-profile.md` is
a mirror you may skip entirely. On the repo-path branch the repo copy *is*
source of truth. Step 5's check looks in both places and reads the first it
finds.

### Route A — the render tool (optional, mechanical)

Run this in: **your project** (the tool lives in the kit clone and writes only
into the directory you point it at)

```bash
python /path/to/kit/tools/kit_render.py --target .
```

It writes `<name>.kit-new` beside each destination and moves nothing. Read each
one, then move the six above into place yourself.

**It renders seven files, and Level 1 uses six.** The seventh is
`.claude/settings.json`, the harness wiring — delete that `.kit-new` file.

The run ends `KIT RENDER: INCOMPLETE`, names every unfilled slot above that
line, and **that is the expected Level-1 result, not a failure.** How many it
names depends on step 1's `KNOWLEDGE_DIR` answer.

Three branches, because step 1 offers three answers and the number differs
between them:

| Step 1's answer | The summary line | What is unfilled |
|---|---|---|
| the value `kit.config.example` ships (`/abs/path/to/your/knowledge-base`) — you have not answered step 1 yet | `KIT RENDER: INCOMPLETE — 7 files written, 6 unfilled slot(s) in 1 file(s), each named above` | the four tier names, `{{PROTECTED_PATH}}`, and `{{KNOWLEDGE_DIR}}` |
| the literal `NONE` (step 1's third answer) | the same line, also **6** | the same six: `NONE` is one of the render tool's placeholder words, so that slot reads as UNSET |
| a real directory, or the repo path `docs` (step 1's first two answers) | `KIT RENDER: INCOMPLETE — 7 files written, 5 unfilled slot(s) in 1 file(s), each named above` | the four tier names and `{{PROTECTED_PATH}}` |

Every slot named is in `CLAUDE.md.kit-new`, whichever branch you are on. What
to do with each:

- **The four tier names** — `{{FORBIDDEN_SPAWN_TIER}}`, `{{LANE_TIER}}`,
  `{{ORCHESTRATOR_TIER}}`, `{{SWEEP_TIER}}`.
  `kit.config.example` ships them in the `your-…`
  shape (`kit.config.example`:131, :134, :137 and :148), and the render tool
  treats a shipped placeholder value as UNSET by the same rule the hook and
  the fixture harness use — `tools/kit_render.py`, `is_placeholder()`, with
  `RATIO_CEILING` the one exempt key by name. So a config copied from the
  example leaves all four unfilled. If you run agents, that is step 2's
  decision arriving late: fill them in `kit.config` and re-render. If you do
  not, `CLAUDE.md` is the conditional sixth document — the paragraph above
  that begins *Five of the six are required* — and the tiering prose it
  carries is a rule you cannot yet enforce, so it goes with it. Record that
  deletion.
- **`{{PROTECTED_PATH}}`.** That slot belongs to the module-02 tripwire, which
  Level 1 does not install. The template marks both sites that use it *delete
  if unused* — one bullet in the hygiene list and the section headed "The
  protected-path tripwire" — so delete them, the way the template tells you
  to.
- **`{{KNOWLEDGE_DIR}}`, on the first two branches of the table only.** This
  one is step 1's decision, not a slot to delete: the documents that
  interpolate it say where durable knowledge lives, and a rules file shipping
  the literal `{{KNOWLEDGE_DIR}}` tells a reader nothing. **Answer step 1 in
  `kit.config` and re-render** — with the repo path `docs` if you have no
  such place, and with `docs` substituted at the two sites if your answer is
  `NONE`, which is what step 1 already instructs. Do not move
  `CLAUDE.md.kit-new` into place with this slot unsubstituted: step 5's
  `doctor:l1-rendered` reads the file you moved and an unsubstituted slot in
  it is a red you will have to clear anyway.

**Which of these redden step 5, and which do not.** `doctor:l1-rendered`
reads the documents you moved into place, so a slot you deleted with its
section, or filled before re-rendering, is not there to find — that covers
the tier names and `{{PROTECTED_PATH}}`. `{{KNOWLEDGE_DIR}}` behaves
differently, and differently again on each of its two branches:

- **Carried through unanswered** (the shipped value). `doctor:l1-rendered`
  goes red on the surviving slot, and `doctor:l1-knowledge-dir` goes red a
  second time on the shipped value itself.
- **Carried through as `NONE`.** `doctor:l1-knowledge-dir` is **green** —
  `NONE` is a recorded decision, and this is the one key in the kit where
  that word is an answer rather than an absence — so `doctor:l1-rendered` is
  the only thing between you and a document telling your reader that durable
  knowledge lives in a directory called NONE. Substitute the repo path
  `docs` at the two sites, which is what step 1 already tells you to do.

**If this repository already had a `kit.config`, expect a longer list, and read
it rather than skipping past it.** The tool renders from the config it finds,
and a hand-written config that predates the kit carries only the keys its
author needed. Every key the templates interpolate and your config does not
define is named as unfilled in the same `KIT RENDER: INCOMPLETE` run — so on
that repository `INCOMPLETE` is a report about your config, not the single
documented `{{PROTECTED_PATH}}` case above. Step 5's
`doctor:l1-config-complete` names every missing key, and step 2 says what to do
about it: append the missing keys at their shipped value; never copy the
example over the file.

Add `*.kit-new` to your `.gitignore` if you keep using the tool.

### Route B — by hand (the primary doctrine)

Copy the six files, substitute their slots, and delete each template's header
block. Two rules that cost other adopters real time:

- **Do not substitute inside a header comment.** Each template opens with a
  `SLOTS:` inventory. It is a list of tokens, not content; delete the whole
  block once you have used it.
- **Delete every rule you cannot yet enforce or do not yet believe.** At
  Level 1 that includes the tripwire rules above, and anything in `CLAUDE.md`
  describing a hook you have not installed. A rules file full of aspirations is
  a file people learn to skim.

**One shipped value is allowed to survive, by name:** `RATIO_CEILING`, which
ships as `derive-from-your-own-data` and lands in `TOKEN-LEDGER.md`. Replace it
when you have three stages of your own numbers, not before.

**Every other shipped example value that reaches these documents is a fill-in
you missed, and step 5 names it** — `Example Project` (the shipped
`PROJECT_NAME`, which lands in six title lines), the `your-…` tier names,
`/abs/path/to/…` and `https://example.invalid`. Step 5 reads the same rule the
kit's own adoption check uses; it is a list of families, not of every string
the kit ships, so read your rendered documents as well as running the check.

## Step 4 — Run the seed interview, or schedule it (15 min, or 2)

`modules/08-collaboration/SEED-INTERVIEW.md` holds five questions. Each one's
answer changes something structural about how the work runs, and each is cheap
to ask and expensive to discover by collision. Capture the answers **verbatim**
in your copy of the profile; the phrasing carries information the summary loses.

**Optional second route.** `modules/08-collaboration/DEFAULTS.md` ships one
program's calibration, de-identified and labelled as that one program's values
rather than best practice, as a pre-filled starting state, and turns this step
into a walk down it — keep, override or delete each value — ending in the same
profile; the five questions above stay the shipped default path.

**You are the owner:** answer the five questions yourself, in writing, today,
and set the profile's status line to `INTERVIEW:  held <date>`.

**Someone else is the owner** — a client, a lead, a stakeholder, or simply
whoever outranks you on this project: put the interview on their calendar and
set `INTERVIEW:  scheduled <the date> confirmed by <who, or which calendar>`.
If you cannot get a date yet, `not yet held` is the honest value. **Both are
green in step 5, and neither is a placeholder.** The check is looking for a
stated answer, and "the owner has not answered yet" is one. What fails is
leaving the shipped menu in place, because then nobody ever said which is
true — and what also fails is a `scheduled` date with no confirmation on it.
A date that parses is not a date somebody agreed to: an invented one reads
exactly like a real calendar entry, so the check asks where it came from. If
it was never agreed, `not yet held` is the answer and it is green.

Until the interview is held, every default in `DEFAULT-CONTRACT.md` is in force
**unconfirmed**, and the betrayal line — question 5, the constraint whose
violation ends trust — is unknown. That is the single riskiest gap on the page,
and the profile is written to say so out loud rather than look complete.

## Step 5 — Run the Level-1 check (2 min)

Run this in: **your project** (the tool lives in the kit clone)

```bash
python /path/to/kit/tools/kit_doctor.py --root . --level1
```

Seven checks run, and each red line names the step that fixes it:

| Check | What it reads |
|---|---|
| `doctor:l1-documents` | the five required documents are where your config says they are, and whether the `CLAUDE.md` in your tree is module 01 as prose or a rules file of your own |
| `doctor:l1-config-complete` | your `kit.config` carries every key the templates interpolate — and the red says to APPEND the missing ones, never to copy the example over your file |
| `doctor:l1-ledger-collision` | nothing already in `LEDGERS_DIR` answers the same question as a kit ledger under a different spelling |
| `doctor:l1-rendered` | no unsubstituted slot, no template header block, no shipped example value (`RATIO_CEILING` exempted by name; text you have quoted in backticks, in a fenced block, or on a line marked `oar:quotes-example` is not scanned, and the run says how much it skipped) |
| `doctor:l1-committed` | git tracks them and they have no uncommitted change |
| `doctor:l1-knowledge-dir` | step 1's decision is recorded, and names somewhere that exists |
| `doctor:l1-interview` | the profile states the interview's status, and a `scheduled` date says where it came from |

A green run ends in three lines, and the second is the one to read:

- **CERTIFIES** — the documents exist, are rendered, are committed, and record
  the two answers.
- **DOES NOT CERTIFY** — any behaviour. No gate ran. Nothing enforces these
  rules, no agent is checked against them, no hook fires, and the *content* is
  not judged: a ledger with a correct header and no rows passes every check.
- **REMOVAL COST** — the files this level added, by name. A rules file that
  reads as your own is not among them, and the line above it says so with the
  numbers it read.

`PASS` is not the verdict word, and that is deliberate. `PASS` belongs to
`verify.py`, which runs a project's gates and returns one exit code. Level 1
installs no gates, so it reports `HEALTHY` over documents. Two different claims;
they do not share a word.

Run it again whenever you like — it reads files and asks git questions, writes
nothing, and stages nothing.

## Step 6 — Commit, and scan before you publish (5 min)

Run this in: **your project**

```bash
git add CLAUDE.md kit.config docs && git commit -m "adopt OAR at Level 1"
```

**Run `git status` first.** `docs` is a directory pathspec: on a tree holding
unrelated uncommitted work it sweeps that work into this commit too. Name the
files individually if that is your situation. Substitute your own
`LEDGERS_DIR` if it is not `docs`.

The commit matters to the check as well as to your history — an untracked
document is not adopted, and `doctor:l1-committed` says so.

**If this repository is going anywhere public**, the profile now contains a
person's verbatim words. Scan before you push:

Run this in: **your project** (the tool lives in the kit clone)

```bash
python /path/to/kit/tools/deident_scan.py --root . --tokens <a-path-outside-this-repo> --strict --tracked-only
```

`--tokens` takes a plain text file, **one token per line**: your name, your
username, machine path fragments, your employer. **It lives outside this
repository on purpose** — a list of the exact strings you do not want published,
kept inside the tree, is one force-add away from being published. If an AI agent
is running this step for you, it may only write that file at a path **you named
for the token list specifically**: `ONBOARD.md` §8's capability-grant clause is
the rule it follows, a path you gave it for something else — its report, for
instance — is not a grant for this, and with no token-list path named it records
the scan NOT RUN rather than inventing a location. Read the `tokens : N` line the
run prints and check `N` accounts for what you meant to hunt for — a file in
any other shape still parses, and reports `0 hits` over a search that never
really happened. If your profile lives outside the repository, scan it where it
lives with `--root` pointing there.

---

## What Level 1 does not give you

Stated here so the green line is not read as more than it is:

- **No enforcement.** No hook fires, no tool call is gated, and nothing stops
  an agent doing what the rules file forbids. That is module 02, at Level 2.
- **No certification.** No gate runs, so nothing can go red for the reason that
  matters: a check the project trusts failing. That is module 03, at Level 2.
- **No CI.** Nothing re-judges this on a machine you are not sitting at. That
  is module 07, at Level 3.
- **No content judgment.** The checks read shape. An empty ledger with a
  correct header passes, and so does a profile whose observations are wrong.
  The ledgers are worth what you put in them.

## Removing it (2 min)

Level 1 is the genuinely reversible commitment, and the check prints the file
list on every green run — every document this level installed, plus
`kit.config`. Delete what that line names and the level is gone. It does not
name a rules file that was already yours.

Two exceptions, and they are reverts rather than deletes:

- **`CLAUDE.md`**, if you merged the standing rules into a file you already
  had. Revert that section.
- **`.gitignore`**, if you added the `kit.config.local` or `*.kit-new` lines.

Nothing was written into `.claude/`, no hook was wired, and no harness
behaviour changed, so there is no wiring to unpick.

## When to go to Level 2

Go when you have a check worth trusting — when someone says "the tests were
green" and you want that sentence to mean something specific. `QUICKSTART.md`
is that path: 90 minutes to two hours of hands-on work, plus an afternoon on
your first oracle.

**What carries over.** Everything from this path stays. QUICKSTART Step 1's
config is the file you already have (it asks for more keys), Step 6's rules
file, Step 7's ledgers and Step 8's profile are already installed and already
rendered. Re-read those steps for the parts Level 1 skipped — Step 6 also
proves the hook, and Step 7 puts the ledgers on a judge surface that does not
exist yet at Level 1 — but you are not redoing the substitution.

What does not carry over is the thinking: Step 3 manufactures your first
oracle, and that is an afternoon whichever level you arrive from.
