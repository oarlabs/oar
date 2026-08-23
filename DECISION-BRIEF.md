# DECISION BRIEF — OAR (Orchestration & Agent Rails)

For a lead, principal or security lead deciding whether to spend an hour here.
Every claim names its source; the few sourced outside this repository say so.

## What it is

Your agent stack can tell you what the agents did; it cannot tell you whether
the green was real. OAR fills that gap. It is a verification governance layer
for multi-agent software work, and it answers one question: *was the green
real?* — did the checks a project trusts exist, run, and ever get seen red. It
ships governance rules that
bind, an enforcement hook that fires before a tool call, a certification runner
that ends in one exit code, ledgers that map every human ruling to a named
check, and a collaboration contract with the owner. **It is not an
orchestration framework** — it does not route, schedule or run agents; why
the controls are plain files, and how the kit composes with a framework you
already run, is `README.md` §"Why files, and where this sits". **It is
not a security boundary** — it governs correctness and cost, not a hostile
agent. Every mechanism exists because a specific failure on the reference build
made it necessary.

**Do not buy the composition; buy the conduct.** Every mechanism here has an
older name (`BLUEPRINT.md` §12) and several have live competitors
(`COMPARISON.md`), so the proposition that nobody has assembled this before is a
claim with a short half-life and is not the one to weigh. The one that survives a prior-art audit
is narrower: this kit applies its own headline instrument to itself and
publishes the unflattering number with its denominators — including the rounds
where the number rose, 50.0% and 42.9%, named and kept in. An audit on
2026-08-22 found no other artifact publishing a self-applied miss rate that is
allowed to go up. Coverage scores point one way; a miss rate points the other.
Judge the kit on whether that discipline is one you want applied to your own
work.

**If you have sat in a GRC or PMO review, you already have a name for this
gap.** Watermelon reporting: green on the outside, red on the inside — cut the
dashboard open and it was lying. "Your agent stack can tell you what the agents
did; it cannot tell you whether the green was real" is that effect restated for
AI. Three shipped mechanisms are aimed straight at it. **Forced red** — every
check has been seen to fail on purpose, because a green never seen red is a hope
with a checkmark; module 03 ships the negative-control facility and the hooks
gate carries a dead-man clause. **The state-word contract** — instruments print
their state rather than a number that implies one, so `NO-ROUNDS-RECORDED` never
renders as `0.0%` and a skipped gate reports PARTIAL rather than PASS; the most
dangerous watermelon is an absence, not a lie. **The escape rate** — the
interior, counted: the share of findings an existing check should have caught,
computed from the judgment ledger by `escape_rate.py`, printed on every
certifying run and held to a ceiling. None of this stops a determined liar, and
this kit is not a security boundary. It makes the honest states cheaper than the
dishonest ones and the silent ones mechanically hard.

## What certifies per level, and what it costs

**Prerequisites, at every level:** git, Python 3.10 or newer (standard library
only — nothing to install), and a shell (`pwsh`, `bash` or Git Bash). Modules
02, 05 and 06 additionally assume a Claude Code-style harness; the doctrine is
portable, that wiring is not. pytest and GitHub Actions are optional and only
where a step already says so. `README.md`, "Prerequisites", is the full
statement, including what has and has not been measured about version floors.

| Level | What you install | What certifies | Cost |
|---|---|---|---|
| **1 — documents** | modules 04 (ledgers) and 08 (collaboration); 01 (governance) as prose. The path is `LEVEL-1.md`, and it installs no code into your repository. | **The documents, and nothing else.** `python <kit>/tools/kit_doctor.py --root . --level1` runs seven checks: the documents this level installs — five required, plus `CLAUDE.md` if you take the governance prose — exist where your config names them, carry no unsubstituted slot, no template header block and no shipped example value, are committed, record the two decisions this level asks for, and do not silently collide with a config or a set of ledgers the repository already had. **No behaviour is certified** — no gate runs, nothing is enforced, and the content is not judged: an empty ledger with a correct header passes. The green line states that limit, and the removal cost, on every run. | 30–45 min — kit estimate, unmeasured |
| **2 — partial** | add 03 (verification), then 02 (enforcement) once a rule has failed | `python tools/verify.py`: a judges gate (the files that decide verdicts are committed and clean), a hooks gate (the enforcement layer proves itself against fixtures, with a dead-man clause), an escapes gate (your escape rate, computed from the level-1 judgment ledger and held to a ceiling — it prints the number on every run, including `NO-ROUNDS-RECORDED` before your first round), and the gates you write. `--selftest` judges the judges; the runner can plant a defect against itself and must go red. | a day — kit estimate; the QUICKSTART walk that delivers most of it is the 90–120-minute figure below |
| **3 — full** | add 07 (CI), 05 (status board), 06 (sidequest) | the same verdict **minus the `hooks` gate**, re-judged on every push on a machine no agent session touches. A hosted runner is a second machine, so module 07 documents `--skip hooks` and an expected exit 3; a permanently skipped gate reports PARTIAL and certifies less, and the local full run stays the bar. | a week, mostly your own gates — kit estimate, unmeasured |

**The one figure with a full walk behind it (an LLM-persona walk — see
limitation 2):** walking QUICKSTART into an empty scratch repository budgets
**90–120 minutes** of hands-on work — a sum of per-step first-time estimates,
reconciled after walk 11, then walked end to end clean twice — plus an
afternoon on Step 3 (your first oracle does not compress)
and a 15-minute owner interview. Adoption into an **existing project is
estimated at 3.5–5 hours and has no human measurement behind it**; that
estimate is from the kit's streamlining report, not this repository. One
LLM-persona walk has since adopted the kit into an existing project with a real
test suite, existing CI and uncommitted work in the tree. It produced no usable
human time estimate — it measures an agent executing tool calls — but it
produced sixteen findings — almost all documents that assumed an empty
repository; one was a remedy the runner printed, and one was a capability the
kit did not ship — and they are collected as one row per collision in
`EXISTING-PROJECT.md`. Read that page beside
`QUICKSTART.md` if this is your case.

**The other cost question — model spend.** You're not choosing between the
orchestrator and a cheap model — you're paying the orchestrator to make that
choice per task. Which tier runs a given lane is an orchestration output,
decided per task under a written rule and enforced by module 02's hook, not a
procurement decision made once against a rate card. The false economy that
prevents is downgrading the seat that plans the work: the expensive unit is a
review round, not a token price, and the program's own per-stage token ledgers
— recorded under module 04's discipline, not yet published — are the only place
a figure could honestly come from, so none is quoted here.

## What is not shipped

- **The team story — in active design.** The kit assumes one owner and one
  orchestrator seat: one committed `.claude/settings.json` holding one
  machine's absolute paths, plus a single collaboration profile, ratio
  ceiling, owner role and per-machine certification token. Measured on a
  second machine: three `UNSTARTABLE:` lines, `HOOK NOT ARMED`, and
  `VERIFY: FAIL — RED: judges, hooks`. This is the one gap between adopt and
  full team adoption, and it is the current design focus — see
  `ROADMAP.md`. Today the kit is ready for a single owner or a one-owner
  team; multi-seat is coming.
- **The resume hooks.** `CONTEXT-ARCHITECTURE.md` §6 describes SessionStart,
  PreCompact and a handoff PreToolUse gate in shipping-grade detail. None of
  the three ships; every such site carries a NOT SHIPPED banner.

## Exit cost

The adopter's footprint is **fourteen files plus an optional CI workflow** —
five tools, four ledgers, one profile, one rules file, two configs, one
settings file — not the whole kit (`git ls-files | wc -l` gives its current
size). Most delete cleanly. **Some cannot:** the appended `.gitignore` rules,
and `.claude/settings.json` and `CLAUDE.md` where you merged them into files
you already had. Level 1 is the genuinely reversible commitment: its footprint
is six documents plus `kit.config`, it writes nothing into `.claude/`, and its
check prints the file list on every green run.

## The limitations most likely to matter to you

1. **The largest LLM-persona evaluation recommended adopting partially, in a
   different order than the kit proposes** — the ledgers and the collaboration
   module immediately, verification and enforcement after. Walk 11 read the
   doctrine first and simulated a second machine, and found 18 defects, the
   largest round. It recommended adoption at all because every executable
   behaved as documented — *including the ones designed to fail* — and all 18
   findings were documentation defects. `KNOWN-ISSUES.md`, "Walk #11".
2. **The walks were LLM personas, not humans.** Seven personas, seven rounds.
   Each was a language model given a written charter and a scratch repository;
   none was a person. The last two hands-on walks were clean, but the loop
   ended **not-dry by its own rule**: two consecutive zero-finding walks never
   happened. The 90–120 minute figure is a persona's, not a human-factors
   measurement. No human has run the walk. Every prompt is published under
   `docs/walks/`, with what it does and does not establish stated there.
3. **A silent green survived that loop.** After the walks closed, an
   adversarial read of the kit's own files found three hazards every walk had
   passed. One was a full `VERIFY: PASS` over a judge path the adopting
   repository's `.gitignore` was hiding — reachable on a real adoption, not a
   scratch one. Fixed, with a control that plants the case in a real
   repository: `KNOWN-ISSUES.md`, entry 15.
