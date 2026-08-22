# Roadmap

This file states what is being worked on and what is deliberately not, so an
evaluator can tell a gap from an omission. It is honest about maturity: the
kit is early, single-maintainer, and labeled that way throughout.

## Ready now

- **Single-owner adoption**, Levels 1–3 as `README.md` describes them. This is
  the configuration the reference build ran in and the LLM-persona adoption
  walks measured.
- The **verification layer** (module 03): one command, one exit code, negative
  controls, a dead-man clause, a self-test that judges the judges.
- The **enforcement layer** (module 02) for one seat.
- The **doctrine and ledger layers** (modules 01, 04, 08), which transfer to
  any stack, including projects with no AI at all.
- `tools/kit_doctor.py`, `tools/kit_render.py`, CI on Linux and Windows.
- The **escape-rate instrument** (`modules/04-ledgers/escape_rate.py`): the
  headline metric computed from the judgment ledger's table, published as a
  required output line, and enforced by the runner's `escapes` gate against a
  derived ceiling. The kit's own number is published in `KNOWN-ISSUES.md`
  ("The kit's own numbers") and recomputed on both CI hosts on every push. The
  status board (module 05) renders the same instrument's number and a per-round
  sparkline as an opt-in segment; it imports the tool rather than parsing the
  ledger, so there is one authority for the number and not two.
- The **Level-1 entry path** (`LEVEL-1.md`): documents only, reversible, no
  settings file, ending in `kit_doctor.py --level1`. Its 30–45 minute figure is
  a sum of per-step estimates and has not been measured on a real adoption.

## In active design — the team story

Multi-seat team adoption is the one gap between the current state and full
team use, and it is the current design focus. The kit assumes one committed
`.claude/settings.json` carrying one machine's absolute paths, one owner role,
one ratio ceiling, and a per-machine certification token. None of that is
wrong for a team; it is undecided. The design must answer how a team shares
one certification contract without one machine's paths, one person's role, or
one token becoming everyone's. `KNOWN-ISSUES.md` under "Whose settings file?"
records the fix shape; `tools/kit_render.py` already builds the first half of
it (mechanical settings rendering per machine). "Enterprise-ready" for OAR
means this design landing.

## Planned, not started

- A **measured existing-project adoption walk**. Today the existing-project
  integration cost is an estimate (3.5–5 hours); one measured walk replaces it
  with data.
- A **human adoption walk** on record. All current adoption evidence comes from
  LLM-persona adoption walks, labeled as such throughout and with their prompts
  published under `docs/walks/`; the protocol transfers to a human walk
  unchanged.
- **De-identified ledgers** for `judgments` and `tokens`, so a reader can
  recompute the remaining headline numbers, published with a dedicated review.
  The `escapes` third of this is done and shipped — see Ready now. What is
  still missing there is an *independent* classification: the kit's escape
  table is the maintainer's reading of the maintainer's own register, with
  each disputable call disclosed in place.

## Deliberately not shipped

- The **resume hooks** described in `CONTEXT-ARCHITECTURE.md` §6 — every such
  site carries a NOT SHIPPED banner.
- Any **security boundary**. OAR governs correctness, cost and process
  integrity; it is not a defense against a hostile agent, prompt injection,
  credential exfiltration, or supply-chain compromise. See `README.md`
  "Security scope".

## How this is maintained

One person, working with AI agents, best-effort, no SLA. Issues are read;
fixes land when the materiality bar says they should. The bus factor is one
and disclosed rather than dressed up.
