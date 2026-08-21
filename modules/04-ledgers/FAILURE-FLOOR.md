<!--
SKELETON - copy to {{LEDGERS_DIR}}/FAILURE-FLOOR.md.
Slots: {{PROJECT_NAME}} {{OWNER_ROLE}} {{DEMOTION_REVIEW_STAGES}}
{{LEDGERS_DIR}}
Delete this block on adoption.
-->

# {{PROJECT_NAME}} — The Failure Floor

**Structure over sentences.** A rule enforced only by prose is debt. It must
either be structuralised or **consciously accepted here with its residual risk
named**. This document is the audit: every operating rule, its enforcement
layer, its zone, when it last fired, and what it does not cover.

The standing rules document points here so every future session inherits it.
Update it whenever a rule is added, a gap closes, or a prose rule fails — and
that failure goes into `LESSONS.md` too.

## The two axes

**LAYER — how loudly it fires.** Strongest first:

**PERMISSION** (harness ask/deny rules — bind every agent at every depth) >
**HOOK** (pre-tool gates — bind this project's sessions) > **TOPOLOGY**
(workflow shape: read-only stages cannot collide, serial stages cannot race) >
**HUMAN** (a person stands at the gate and looks — the strongest layer there
is, and the most expensive; spend it sparingly) > all of the above >
**CHECKLIST** (steps in the standing rules) > **PROSE** (charter text, restated
per round).

**ZONE — who can rewrite the enforcer.** The layer ladder cannot see this, and
it is the axis that actually decides whether a control is real.

- **Zone A — outside the agents' blast radius.** A human standing at a gate; a
  server-side required check on a protected branch; code ownership on
  judgment-bearing paths. These are the only controls that stop an agent from
  authoring its own judge.
- **Zone B — inside it.** Permissions, hooks, topology, checklists and prose all
  run in the operator's own session, out of files in a tree every implementer
  can write. A Zone B rule is **real** — it fires, it blocks, it has caught
  things. It is simply enforced by the same hands it governs.

Most projects are all Zone B for a long time, and saying so is the honesty this
document exists for. Write the zone down; defend every judge with the strongest
Zone A control you can currently afford; stop pretending the ladder alone is a
threat model.

## The table

| Rule | Layer | Zone | Status | Last fired | Failure mode covered / residual |
|---|---|---|---|---|---|
| <the rule, one line> | HOOK (what it matches) | B | **STRUCTURAL** | <date it last actually caught something> | Covered: <the class>. Residual: <what still gets through, and whether that is ACCEPTED>. |
| <a rule you have not structuralised> | PROSE (charter preamble) | B | **AMBER, accepted** | never | <Why accepting it is reasonable, and what would change that.> |
| <a rule a human enforces> | HUMAN (a person at the gate) | **A** | **ACCEPTED** | <date> | <Inherently social; what makes it hold.> |

**Status vocabulary:** **STRUCTURAL** (a machine enforces it) · **AMBER** (prose
or checklist only — debt, visible) · **AMBER, accepted** (debt with a stated
reason not to pay it yet) · **ACCEPTED** (deliberately never structuralised).

**Last fired** is the day it last actually caught or blocked something. `never`
where it has caught nothing yet; `unknown — predates recording` where the record
does not say. Guessing a date here destroys the only input the demotion review
has.

## Standing review trigger

Any time a PROSE or AMBER rule fails in practice:

1. record the failure in `LESSONS.md`;
2. **promote it a layer here**, or mark it ACCEPTED with the reason;
3. update the standing rules document if the change binds future sessions.

The failure is the evidence. Promoting rules that have never failed is how a
floor grows monotonically until people route around it — and a routed-around
floor enforces nothing while costing everyone attention.

## Demotion review (at every phase gate)

Promotion has a reverse gear, because **under-enforcement produces an incident
with a timestamp while over-enforcement produces work that never happened and
leaves no artefact.** Only one of those defends itself.

At each phase gate, every rule quiet for {{DEMOTION_REVIEW_STAGES}} stages gets
one of three dispositions:

- **RETIRE** — the failure class is gone.
- **DEMOTE** a layer — the carrying cost now exceeds what it still catches.
- **RE-AFFIRM** — it is quiet *because it is working*. Say so, and reset the
  clock.

A quiet rule is not automatically a dead rule: a tripwire is quiet because
nothing has tried to cross it, and a lint's entire purpose is to stop firing.
That is what re-affirm is for.

But **zero demotions across an entire phase is itself a finding** — it means
either the review was performed as a formality, or the floor is growing
monotonically and nobody is naming the carrying cost out loud. Record that
outcome, with its reason, instead of reporting a clean sweep.

The review produces a **recommendation**; {{OWNER_ROLE}} rules. No rule leaves
this table silently, and **no agent retires anything.**

**Next review due:** <phase gate>
