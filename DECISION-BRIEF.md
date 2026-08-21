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

## What certifies per level, and what it costs

| Level | What you install | What certifies | Cost |
|---|---|---|---|
| **1 — documents** | modules 04 (ledgers) and 08 (collaboration); 01 (governance) as prose | **Nothing mechanical.** This level changes what the project records about itself. A dedicated Level-1 path is planned but is not in this repository yet, so today you take the two modules by hand. | an afternoon — kit estimate, unmeasured |
| **2 — partial** | add 03 (verification), then 02 (enforcement) once a rule has failed | `python tools/verify.py`: a judges gate (the files that decide verdicts are committed and clean), a hooks gate (the enforcement layer proves itself against fixtures, with a dead-man clause), and the gates you write. `--selftest` judges the judges; the runner can plant a defect against itself and must go red. | a day — kit estimate; the QUICKSTART walk that delivers most of it is the 90–120-minute figure below |
| **3 — full** | add 07 (CI), 05 (status board), 06 (sidequest) | the same verdict **minus the `hooks` gate**, re-judged on every push on a machine no agent session touches. A hosted runner is a second machine, so module 07 documents `--skip hooks` and an expected exit 3; a permanently skipped gate reports PARTIAL and certifies less, and the local full run stays the bar. | a week, mostly your own gates — kit estimate, unmeasured |

**The one figure with a full walk behind it:** walking QUICKSTART into an empty
scratch repository budgets **90–120 minutes** of hands-on work — a sum of
per-step first-time estimates, reconciled after walk 11, then walked end to end
clean twice — plus an afternoon on Step 3 (your first oracle does not compress)
and a 15-minute owner interview. Adoption into an **existing project is
estimated at 3.5–5 hours and has never been measured**; that estimate is from
the kit's streamlining report, not this repository.

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
you already had. Level 1 is the genuinely reversible commitment.

## The limitations most likely to matter to you

1. **The largest independent evaluation recommended adopting partially, in a
   different order than the kit proposes** — the ledgers and the collaboration
   module immediately, verification and enforcement after. Walk 11 read the
   doctrine first and simulated a second machine, and found 18 defects, the
   largest round. It recommended adoption at all because every executable
   behaved as documented — *including the ones designed to fail* — and all 18
   findings were documentation defects. `KNOWN-ISSUES.md`, "Walk #11".
2. **The walks were AI agent personas, not humans.** Seven personas, seven
   rounds. The last two hands-on walks were clean, but the loop ended
   **not-dry by its own rule**: two consecutive zero-finding walks never
   happened. The 90–120 minute figure is a simulated stranger's, not a
   human-factors measurement. No human has run the walk.
3. **A silent green survived that loop.** After the walks closed, an
   adversarial read of the kit's own files found three hazards every walk had
   passed. One was a full `VERIFY: PASS` over a judge path the adopting
   repository's `.gitignore` was hiding — reachable on a real adoption, not a
   scratch one. Fixed, with a control that plants the case in a real
   repository: `KNOWN-ISSUES.md`, entry 15.
