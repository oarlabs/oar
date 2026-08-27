# LEVEL 1 — the documents, in 30 to 45 minutes

Level 1 installs documents only: four ledgers, a collaboration profile, and the
standing rules as prose. It installs no settings file, no hook, no verification
runner and no CI. It ends in a check that prints what it certifies, what it does
not certify, and what removal costs.

Anyone can run this path. Step 4 needs the owner; if that is someone else,
schedule it and finish green.

Commands run in **your project**, the repository you are adopting into; both tools
stay in **the kit clone**, this read-only checkout. Every block runs as-is in
`pwsh` (7+), `bash` and Git Bash, forward slashes included, on Windows too. Verified
by hand, not machine-checked.

> **`⚠ Debian/Ubuntu:` `python` may not exist** — those hosts ship `python3`
> and no `python` shim unless `python-is-python3` is installed. Substitute
> `python3` throughout, or install the shim.

## Budget

| Step | What it is | Time |
|---|---|---|
| 1 | Decide two things | 5 min |
| 2 | Copy the config and fill five keys | 5 min |
| 3 | Install the six documents | 10 min with the render tool; 20–25 by hand |
| 4 | Run the seed interview, or schedule it | 15 min if you are the owner; 2 if not |
| 5 | Run the Level-1 check | 2 min |
| 6 | Commit, and scan before you publish | 5 min |

30 minutes is the fast path: `tools/kit_render.py`, and a scheduled interview. 45
minutes is the interview held today. These are estimates; no human has walked this
path and timed it. [record: `KNOWN-ISSUES.md`]

## Step 1 — Decide two things (5 min)

Both are decisions, not fill-ins, and both are checked in step 5.

1. **`KNOWLEDGE_DIR` — where does durable knowledge live?** The notes system, wiki
   or vault that outlives any one session. Three answers:
   - You have such a place: its absolute path.
   - You do not: the repo path `docs`. The repo copies then *are* source of truth
     rather than mirrors; say so where a template calls one a mirror.
   - "No such place" on record: the literal value `NONE`. The templates do not
     branch on it, so substitute `docs` at the two sites that interpolate the slot.
2. **`OWNER_ROLE` — who owns the judgment?** The person whose ruling settles a
   question. You cannot answer step 4's five questions on their behalf.

## Step 2 — Copy the config, and fill five keys (5 min)

Run this in **your project**:

```bash
cp /path/to/kit/kit.config.example ./kit.config
```

1. Do not run it if `kit.config` exists: `cp` overwrites without asking.
   Append the keys you are missing at their shipped value instead.
   [check: `doctor:l1-config-complete`]
2. Fill the keys below; leave every other key as it ships.
3. Put an absolute `KNOWLEDGE_DIR` in `kit.config.local`, never in the committed
   `kit.config`: copy `kit.config.local.example`, set the value, `.gitignore` it.
   Both halves are read from one directory, `.local` last.

| Key | Value |
|---|---|
| `PROJECT_NAME` | your project's name, as it reads in a ledger heading |
| `OWNER_ROLE` | how the documents refer to the owner (`the owner`, `the client`, a name) |
| `KNOWLEDGE_DIR` | step 1's first answer |
| `LEDGERS_DIR` | where the four ledgers live; ships as `docs` |
| `ORCHESTRATOR_TIER`, `LANE_TIER`, `SWEEP_TIER`, `FORBIDDEN_SPAWN_TIER` | the model tiers you actually use, if you run agents |

## Step 3 — Install the six documents (10 min with the tool, 20–25 by hand)

| Document | From |
|---|---|
| `<LEDGERS_DIR>/JUDGMENT-LEDGER.md` | `modules/04-ledgers/` |
| `<LEDGERS_DIR>/FAILURE-FLOOR.md` | `modules/04-ledgers/` |
| `<LEDGERS_DIR>/LESSONS.md` | `modules/04-ledgers/` |
| `<LEDGERS_DIR>/TOKEN-LEDGER.md` | `modules/04-ledgers/` |
| `docs/collaboration-profile.md` | `modules/08-collaboration/PROFILE-TEMPLATE.md` |
| `CLAUDE.md` *(recommended, not required)* | `modules/01-governance/CLAUDE.md.template` |

What each ledger answers: `modules/04-ledgers/README.md`.

**Ledger collisions.** The four ledger filenames are fixed; `LEDGERS_DIR` is the
only thing you can move. If it already holds a `LESSONS-LEARNED.md` or a
`TOKEN_LEDGER.md`, pick one route and record it. **Rename** it onto the kit's name
and carry its content forward, **freeze** it as the record up to adoption and say
so at the top of both files, or move `LEDGERS_DIR`.
[check: `doctor:l1-ledger-collision`, which changes nothing]

**`CLAUDE.md` is the conditional sixth.** Take it if you run agents. Step 5 counts
module 01's eight fingerprint strings — seven section headings and one rule
sentence — to decide whether your `CLAUDE.md` carries the kit's prose or is your
own, and prints the two numbers. Only the first appears in the removal cost, as a
revert if you merged the rules into a file you already had.

**The profile's filename is fixed; its location follows step 1.** Outside the
repository that copy is source of truth and `docs/collaboration-profile.md` is a
mirror you may skip; on the repo-path branch the repo copy is source of truth.
Step 5 reads whichever it finds.

### Route A — the render tool (optional, mechanical)

Run this in **your project**; it writes only into the directory you name.

```bash
python /path/to/kit/tools/kit_render.py --target .
```

1. Read each `<name>.kit-new`, then move the six documents into place
   yourself. The tool moves nothing.
2. Delete `.claude/settings.json.kit-new` — seven files are rendered, Level 1 uses
   six — and remove `.claude/` if the render created it. Level 1 installs no
   settings file.
3. Delete leftover `.kit-new` files before re-rendering, or pass `--force`. A
   second run otherwise aborts: `KIT RENDER: ABORTED —
   .claude/settings.json.kit-new already exists. This tool never overwrites`.
4. Add `*.kit-new` to your `.gitignore` if you keep using the tool.

The run ends `KIT RENDER: INCOMPLETE`, naming every unfilled slot [record:
`KNOWN-ISSUES.md` Round #30, the slot-count arithmetic]. That is expected,
not a failure. Each is in `CLAUDE.md.kit-new`:

| Slot | What to do |
|---|---|
| `{{FORBIDDEN_SPAWN_TIER}}`, `{{LANE_TIER}}`, `{{ORCHESTRATOR_TIER}}`, `{{SWEEP_TIER}}` | If you run agents, fill them in `kit.config` and re-render. If not, delete `CLAUDE.md` — its tiering prose is a rule you cannot yet enforce — and record the deletion. |
| `{{PROTECTED_PATH}}` | Module 02's tripwire, not installed here. Delete both sites the template marks *delete if unused*: one hygiene-list bullet, and the section headed "The protected-path tripwire". |
| `{{KNOWLEDGE_DIR}}` | Step 1's decision, not a slot to delete. Answer step 1 and re-render. Never move `CLAUDE.md.kit-new` into place with it unsubstituted. |

Expected summary line, by Step 1's answer:

| Step 1's answer | The summary line | What is unfilled |
|---|---|---|
| the value `kit.config.example` ships (`/abs/path/to/your/knowledge-base`) — you have not answered step 1 yet | `KIT RENDER: INCOMPLETE — 7 files written, 6 unfilled slot(s) in 1 file(s), each named above` | the four tier names, `{{PROTECTED_PATH}}`, and `{{KNOWLEDGE_DIR}}` |
| the literal `NONE` (step 1's third answer) | the same line, also **6** | the same six: `NONE` is one of the render tool's placeholder words, so that slot reads as UNSET |
| a real directory, or the repo path `docs` (step 1's first two answers) | `KIT RENDER: INCOMPLETE — 7 files written, 5 unfilled slot(s) in 1 file(s), each named above` | the four tier names and `{{PROTECTED_PATH}}` |
| any of the above with the four tier names already filled in Step 2 | each count above drops by four | `{{PROTECTED_PATH}}`, and `{{KNOWLEDGE_DIR}}` per the rows above |

`NONE` satisfies `doctor:l1-knowledge-dir`: it is a recorded decision, not an
absence. An existing `kit.config` produces a longer list. [record:
`EXISTING-PROJECT.md`, "Also measured, at Level 1"]

### Route B — by hand (the primary doctrine)

1. Copy the six files and substitute their slots.
2. Delete each template's `SLOTS:` header block once you have used it, and never
   substitute inside it.
3. Delete every rule you cannot yet enforce or do not yet believe: the tripwire
   rules above, and anything describing a hook you have not installed.

One shipped value may survive, by name: `RATIO_CEILING`, which ships as
`derive-from-your-own-data` and lands in `TOKEN-LEDGER.md`. Replace it when you
have three stages of your own numbers. Step 5 names every other shipped value that
survived, but it scans families rather than every string, so read your rendered
documents too.

## Step 4 — Run the seed interview, or schedule it (15 min, or 2)

`modules/08-collaboration/SEED-INTERVIEW.md` holds five questions. Each answer
changes something structural about how the work runs. [alternative:
`modules/08-collaboration/DEFAULTS.md`]

1. Capture the answers **verbatim** in your copy of the profile.
2. Set the profile's status line to one of three values:
   - You are the owner and answer today: `INTERVIEW:  held <date>`.
   - Someone else is the owner: `INTERVIEW:  scheduled <the date> confirmed by
     <who, or which calendar>`.
   - You cannot get a date yet: `not yet held`.

All three are green in step 5; the check looks for a stated answer, and "the owner
has not answered yet" is one. Two things fail: the shipped menu left in place, and
a `scheduled` date with no confirmation. A date that parses is not a date somebody
agreed to.

Until the interview is held, every default in `DEFAULT-CONTRACT.md` is in force
**unconfirmed**, and the betrayal line — question 5, the constraint whose
violation ends trust — is unknown.

## Step 5 — Run the Level-1 check (2 min)

Run this in **your project**:

```bash
python /path/to/kit/tools/kit_doctor.py --root . --level1
```

Seven checks run; each red line names the step that fixes it.

| Check | What it reads |
|---|---|
| `doctor:l1-documents` | the five required documents are where your config says, and whether `CLAUDE.md` is module 01's prose or your own |
| `doctor:l1-config-complete` | `kit.config` carries every key the templates interpolate; the red says APPEND, never copy the example over your file |
| `doctor:l1-ledger-collision` | nothing in `LEDGERS_DIR` answers a kit ledger's question under another spelling |
| `doctor:l1-rendered` | no unsubstituted slot, header block or shipped value (`RATIO_CEILING` exempt by name; quoted and fenced text skipped, with the count printed) |
| `doctor:l1-committed` | git tracks them, with no uncommitted change |
| `doctor:l1-knowledge-dir` | step 1's decision is recorded and names somewhere that exists |
| `doctor:l1-interview` | the profile states the interview's status, and a `scheduled` date says where it came from |

A green run ends in **CERTIFIES**, **DOES NOT CERTIFY** — any behaviour; the next
section is that list — and **REMOVAL COST**, the files added. The verdict word is
`HEALTHY`, not `PASS`: `PASS` belongs to `verify.py`, and Level 1 installs no
gates. The check writes and stages nothing.

## Step 6 — Commit, and scan before you publish (5 min)

Run this in **your project**:

```bash
git add CLAUDE.md kit.config .gitignore docs && git commit -m "adopt OAR at Level 1"
```

1. Run `git status` first. `docs` is a directory pathspec, so on a tree with
   unrelated uncommitted work it sweeps that in too. Name the files individually
   if so.
2. Substitute your own `LEDGERS_DIR` if it is not `docs`.
3. Drop `.gitignore` if you did not add the `*.kit-new` rule in Step 3.
   `doctor:l1-committed` does not read it.

An untracked document is not adopted. [check: `doctor:l1-committed`]

If this repository is going anywhere public, the profile holds a person's verbatim
words. Scan before you push:

```bash
python /path/to/kit/tools/deident_scan.py --root . --tokens <a-path-outside-this-repo> --strict --tracked-only
```

- `--tokens` takes a plain text file, **one token per line**: your name, username,
  machine path fragments, employer. Check the `tokens : N` line; a file in any
  other shape still parses and reports `0 hits`.
- Keep that file outside this repository. A list of the strings you do not want
  published is one force-add from being published.
- Point `--root` at the profile if it lives outside the repository.
- An AI agent may write it only at a path **you named for the token list
  specifically**; with none named it records the scan NOT RUN.
  [rule: `ONBOARD.md` §8, the capability-grant clause]

## What Level 1 does not give you

- **No enforcement.** No hook fires and no tool call is gated. Module 02, Level 2.
- **No certification.** No gate runs, so no check the project trusts is ever seen
  failing. Module 03, Level 2.
- **No CI.** Nothing re-judges this on a machine you are not at. Module 07,
  Level 3.
- **No content judgment.** The checks read shape: an empty ledger with a correct
  header passes, and so does a profile whose observations are wrong.

## Removing it (2 min)

Delete what the green run's REMOVAL COST line names: the documents this level
installed, plus `kit.config`. Nothing was written into `.claude/` and no hook was
wired. Two exceptions are reverts: `CLAUDE.md`, if you merged the standing rules
into a file you already had, and `.gitignore`, if you added the
`kit.config.local` or `*.kit-new` lines.

## When to go to Level 2

Go when you want "the tests were green" to mean something specific.
`QUICKSTART.md` is that path: 90 minutes to two hours of hands-on work, plus an
afternoon on your first [oracle](GLOSSARY.md). Everything here carries over, so
re-read only what Level 1 skipped: its Step 6 also proves the hook, and its Step 7
puts the ledgers on a [judge surface](GLOSSARY.md) this level does not build.
