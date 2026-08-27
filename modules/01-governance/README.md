# Module 01 — Governance

The standing rules a session inherits before it does anything, and the charter
templates that bind each seat.

## Files

| File | What it is |
|---|---|
| `CLAUDE.md.template` | The standing coordinator rules. Copy to your repo root as the file your harness auto-loads every session. Model tiering, HALT authority, coordinator hygiene, certification, the optional protected-path tripwire, spec-side reviewers, oracle manufacture, the stage-close checklist, promotion/demotion, and the collaboration defaults. |
| `charters/CHARTER-implementer.md` | A lane that changes the tree. Seven-part anatomy; disposition-on-every-item; "consciously left out" written as a claim a reviewer will check. |
| `charters/CHARTER-reviewer.md` | Adversarial review, **spec-side onboarding** — punch list + rulings + diff, never the implementer's report. A standing file implementing lanes cannot edit. |
| `charters/CHARTER-scout.md` | Read-only archaeology. No execution, by charter, with the reason. Carries the six-verdict triage taxonomy. |
| `charters/CHARTER-synthesis-writer.md` | Report and document composition. Opens with the HALT-on-empty-inputs guard. |
| `PUNCH-LIST-TEMPLATE.md` | The document the working charters assume: verbatim items, triage verdicts, a numbered decision list with a lean on every line, and a disposition table where no row may be blank. It is also the reviewer's spec-side briefing, which makes its accuracy a verification property rather than a clerical one. |

## File contract with other modules

This module **declares**; other modules **enforce**. The coupling is by name
only:

- **→ 02-enforcement.** `CLAUDE.md.template` states the tiering rule, the
  blanket-add ban, and the protected-path tripwire in prose; the hook in module
  02 is what makes them fire. The two must agree on `{{MODEL_EXEMPT_TYPES}}`,
  `{{FORBIDDEN_SPAWN_TIER}}`, `{{PROTECTED_PATH}}`, and `{{CERT_TOKEN_FILE}}` —
  all four come from `kit.config`, which is why there is a config file at all.
  (`FORBIDDEN_SPAWN_TIER` is the key adopters historically skip — walk 7's
  MAJOR-1.)
- **→ 03-verification.** The rules name `{{GATE_COMMAND}}` as the definition of
  certified. If you adopt 01 without 03, that sentence points at whatever you
  already run — fine, as long as it is one command with one exit code.
- **→ 04-ledgers.** The stage-close checklist and the promotion/demotion rule
  name four ledger files by path. Without module 04 those steps are still
  meaningful; they just write into documents of your own shape.
- **→ 08-collaboration.** The final section is a one-line summary of the eight
  defaults; module 08 is where they are stated with their evidence and where the
  living profile lives.

## What breaks if you adopt this module alone

Nothing. You get a rules document and five charter templates, and they work as
prose the way every team's conventions work as prose. What you *do not* get is
any of it firing: an undeclared spawn still runs, a blanket add still stages, a
skipped gate still looks like a passed one.

That is the honest adoption level, and it is where most teams should start.
Prose that people actually follow beats a hook nobody has debugged. Add module
02 when a rule here has failed at least once — the failure is the evidence that
tells you which rule to promote first, and promoting rules that have never
failed is how a floor grows monotonically until people route around it.

## Adaptation notes

- **Delete aggressively.** Every rule you keep but do not enforce trains readers
  to skim, and a skimmed rules file is worse than a short one.
- **Keep it near one screen.** This text is re-read at the top of every session
  and competes with the actual work.
- **Traceability beats completeness.** A rule you cannot trace to a specific
  failure is a guess. Park guesses in `FAILURE-FLOOR.md` as proposals; promote
  them when they earn it.
