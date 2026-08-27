# DECISION BRIEF — OAR (Orchestration & Agent Rails)

For a lead, principal or security lead deciding whether to spend an hour here.

## What it is

A verification governance layer for multi-agent software work. It answers one
question: **was the green real?** — did the checks a project trusts exist, run, and
ever get seen red. It ships governance rules that bind and an enforcement hook that
fires before a tool call. It also ships a certification runner ending in one exit code,
ledgers mapping every human ruling to a named check, and a contract with the owner.

- **Not an orchestration framework.** It does not route, schedule or run agents.
  [`docs/WHY-FILES.md`]
- **Not a security boundary.** It governs correctness and cost, not a hostile
  agent.

Every mechanism exists because a specific failure on the reference build made it
necessary; every one has an older name (`BLUEPRINT.md` §12) and several have live
competitors (`COMPARISON.md`). The claim under evaluation is conduct, not
composition: the mechanisms are ordinary, and the discipline connecting them
is the product.
It turns its own headline instrument on itself and publishes the unflattering
number with its denominators, including the rounds where it rose — 50.0% and 42.9%.
A prior-art search on 2026-08-22 did not find another artifact publishing a
self-applied miss rate that is allowed to rise; `COMPARISON.md` carries the
search's scope and method, and the claim extends no further than that search.

## The gap it closes

Watermelon reporting: green on the outside, red on the inside. Three shipped
mechanisms aim at it, making the honest states cheaper than the dishonest ones.

| Mechanism | What ships |
|---|---|
| **Forced red** | Module 03's negative-control facility, a dead-man clause on the hooks gate, and `tools/adoption_smoke.py --plant-f1`, which makes the kit's own adoption gate refuse in front of you. |
| **The state-word contract** | Instruments print their state rather than a number that implies one: `NO-ROUNDS-RECORDED` never renders as `0.0%`, and a skipped gate reports PARTIAL rather than PASS. |
| **The escape rate** | The share of findings an existing check should have caught, computed from the judgment ledger by `escape_rate.py`, printed on every certifying run, held to a ceiling. |

A later review narrowed this. At 0.1.0 the registry's per-check
[`seen_red`](GLOSSARY.md) field has 35 dated rows of 208 and 173 NEVER. The claim
over every check is withdrawn until the backfill supports it.

## What certifies per level, and what it costs

**Prerequisites, every level:** git, Python 3.10 or newer (standard library only),
and a shell (`pwsh`, `bash` or Git Bash). Modules 02, 05 and 06 also assume a
Claude Code-style harness. pytest and GitHub Actions are optional; the full
statement is `docs/PREREQUISITES.md`.

| Level | You install | What certifies | Cost |
|---|---|---|---|
| **1 — documents** | 04, 08, and 01 as prose; no code enters your repository (`LEVEL-1.md`) | `python <kit>/tools/kit_doctor.py --root . --level1`, seven checks: the documents are where your config names them, are fully substituted with no template header block or example value left standing, are committed, record the two decisions, and do not collide with a config or ledgers you already had. **No behaviour is certified**; an empty ledger with a correct header passes, and every green run says so and prints the removal cost. | 30–45 min — kit estimate, unmeasured |
| **2 — partial** | add 03, then 02 once a rule has failed | `python tools/verify.py`: a judges gate (verdict-deciding files committed and clean), a hooks gate (enforcement proved against fixtures, with a dead-man clause), an escapes gate (your escape rate held to a ceiling, `NO-ROUNDS-RECORDED` before your first round), and the gates you write. `--selftest` plants a defect against the runner, which must go red. | a day — kit estimate |
| **3 — full** | add 07, 05, 06 | the same verdict **minus the `hooks` gate**, re-judged on every push on a machine no agent session touches. A hosted runner is a second machine, so module 07 documents `--skip hooks` and expects exit 3; a permanently skipped gate reports PARTIAL, and the local run stays the bar. | a week, mostly your own gates — unmeasured |

**The one figure with a full walk behind it** (an LLM-persona walk, limitation 2):
QUICKSTART into an empty scratch repository budgets **90–120 minutes** of hands-on
work, plus an afternoon on Step 3 and a 15-minute owner interview. That budget was
reconciled against the adoption walks, then walked end to end clean twice.

Adoption into an **existing project is estimated at 3.5–5 hours and has no human
measurement behind it**; that estimate is from the kit's streamlining report. One
LLM-persona walk has since adopted the kit into an existing project with a real test
suite, existing CI and uncommitted work. It
produced no usable human time estimate — it measures an agent executing tool calls
— but it produced sixteen findings, collected as one row per collision in
`EXISTING-PROJECT.md`. Read that page beside `QUICKSTART.md` if this is your case.

**Model spend**. Which tier runs a lane is an orchestration output, decided per task
under a written rule and enforced by module 02's hook, not a procurement decision
against a rate card. The expensive unit is a review round, not a token price. The program's own per-stage token ledgers are the only honest source of a
figure, and none is published, so none is quoted.

## What is not shipped

- **The team story, in active design**. The kit assumes one owner and one
  orchestrator seat: one committed `.claude/settings.json` with one machine's
  absolute paths, one collaboration profile, ratio ceiling, owner role and
  certification token. Measured on a second machine: three `UNSTARTABLE:`
  lines, `HOOK NOT ARMED`, and `VERIFY: FAIL — RED: judges, hooks`. [`ROADMAP.md`]
- **The resume hooks**. `CONTEXT-ARCHITECTURE.md` §6 describes SessionStart,
  PreCompact and a handoff PreToolUse gate in shipping-grade detail. None ships,
  and every such site carries a NOT SHIPPED banner.

## Exit cost

The adopter's footprint is **fourteen files plus an optional CI workflow**, not the
whole kit: five tools, four ledgers, one profile, one rules file, two configs, one
settings file. Most delete cleanly. **Some cannot:** the appended `.gitignore`
rules, and `.claude/settings.json` and `CLAUDE.md` where you merged them into
files you already had. Level 1 is the genuinely reversible commitment: six documents plus
`kit.config`, nothing in `.claude/`, and the file list printed on each green run.

## The limitations most likely to matter to you

1. **The largest LLM-persona evaluation recommended adopting partially, and in a
   different order**: ledgers and collaboration immediately, verification and
   enforcement after. Walk 11 found 18 defects, the largest round,
   and recommended adoption anyway because every executable behaved as documented,
   *including the ones designed to fail*, and all 18 were documentation defects.
   [`KNOWN-ISSUES.md`, "Walk #11"]
2. **The walks were LLM personas, not humans.** Seven personas, seven rounds, each
   a language model with a written charter and a scratch repository. The last two
   were clean, but the loop ended **not-dry by its own rule** (dry means two
   consecutive zero-finding rounds): two consecutive
   zero-finding walks never happened. No human has run it. All seven prompts are
   published under `docs/walks/`.
3. **A silent green survived that loop.** An adversarial read afterwards found
   three hazards every walk had passed. One was a full `VERIFY: PASS` over a judge
   path the adopting repository's `.gitignore` was hiding, reachable on a real
   adoption but not a scratch one. Fixed, with a control that plants the case in a
   real repository. [`KNOWN-ISSUES.md`, entry 15]
