<!--
SKELETON - copy to {{LEDGERS_DIR}}/TOKEN-LEDGER.md.
Slots: {{PROJECT_NAME}} {{OWNER_ROLE}} {{RATIO_CEILING}} {{LEDGERS_DIR}}
Delete this block on adoption.
-->

# {{PROJECT_NAME}} — Token Ledger

One row per stage, with **actual** cost, not forecast. The budget never silently
cuts scope — scope is {{OWNER_ROLE}}'s ruling. This ledger is **bookkeeping**;
it opens conversations at gates and never overrides a decision on its own.

## Declare your meter first

Every number here must come from the **same meter**, and the meter must be named
where the table can see it. This is not pedantry: in the reference build,
per-stage figures from task-completion notifications ran **1.37×–1.90× larger**
than summed per-agent output tokens for the same agents. Two meters, silently
mixed, produce a ratio that means nothing and looks authoritative.

> **METER FOR THIS LEDGER:** <e.g. "summed output tokens per agent, from the
> per-agent observability hook; input and cache excluded">
>
> **KNOWN BIAS:** <e.g. "output-token accounting UNDERSTATES the process share,
> because report writers receive enormous prompts and emit modest documents.
> Every ratio below is a floor, not a midpoint.">

## Per-stage actuals

| Stage | Tier(s) | Actual | Forecast | Halts | Escape rate | Outcome |
|---|---|---|---|---|---|---|
| <stage name> | <lane tier ×N> | **<actual>** | <forecast> | 0/N | N of M | <what shipped, what did not, what was found. Two lines maximum.> |

**Halts** is the andon-cord count (raised / lanes launched). Zero halts across a
phase is a finding, not a success — publish it either way.

## If your team spends HOURS, not tokens

Everything below works unchanged with **hours** as the unit — the ratio is
dimensionless, so the meter only has to be consistent. The mapping:

| Token-ledger term | Human-team equivalent |
|---|---|
| actual tokens per stage | logged hours per stage |
| IMPLEMENTATION | hours by people producing or repairing the shipped artefact |
| PROCESS | hours in review, planning, investigation, writing up, coordinating |
| rework column | hours spent redoing work already done once |
| the meter declaration | your time-tracking source, and its known bias |

The bias caveat matters *more* with hours, not less: self-reported time
under-counts coordination almost universally — the fifteen minutes explaining a
ticket rarely gets logged against it. Name that where the table can see it, the
same way the token version names its own meter.

Mixed teams (people plus agents) should keep **two tables, never one**. Adding
hours to tokens produces a number with no unit, and a number with no unit is a
number nobody can dispute — which is exactly the property this ledger exists to
avoid.

## The process / implementation ratio

The division most ledgers have the data for and never perform: **of what we
spend, how much builds the product and how much runs the machine that builds
the product?**

**Definitions — stated so anyone can re-derive or dispute them:**

- **IMPLEMENTATION** — seats that produce or directly repair the shipped
  artefact: implementers, smoke/floors engineers, fix-pass lanes.
- **PROCESS** — everything else: scouts, investigators, adversarial reviewers,
  report writers, design researchers, synthesis writers, and orchestrator
  overhead where it is measurable.
- **Ratio** = process ÷ implementation, per stage and cumulative. Lower is more
  product per token. **It is not a quality score.**

| Stage | Process | Implementation | **Ratio** | Rework held out | Ratio w/ rework |
|---|---|---|---|---|---|
| <stage> | <n> | <n> | **<r>** | <n> | <r> |

Ratios are on **kept composition** — the agents whose work reached the tree.
Killed and discarded runs live in their own column and are never silently folded
in; a stage that was launched twice should look more expensive than one launched
once, and folding rework into the headline hides exactly the thing the ratio is
good at finding.

Investigation and design rounds are **100% process by construction** — they
exist to produce a ruling, not an artefact. Reporting them as a ratio is a
category error; reporting them at all is the honesty.

### The rework column

| Event | Cost | Evidence |
|---|---|---|
| <e.g. "cohort killed and relaunched"> | <n> | <the primary source: identical prompts, timestamps, a verbatim failure line> |

Rework is a **fact**, not a classification. Record it with its evidence. In the
reference build, 32% of all measured rework came from a single failure mode —
synthesis prompts launched with empty inputs — *after* the rule against it was
written. That is an enforcement-layer datapoint for `FAILURE-FLOOR.md`, not a
new rule.

### The ceiling: {{RATIO_CEILING}}

**Derive it; do not adopt a number.** The method:

1. Take the ratios of your consecutive *successful* stages under the mature
   workflow. Find the cluster maximum.
2. Set the ceiling ~10–15% above it.
3. **Sanity-check backwards:** the ceiling should fire on exactly the stages you
   *already* judged as overruns on independent grounds, and on no others. If it
   fires on a stage you were happy with, it is in the wrong place. That
   retrospective agreement is the strongest evidence available that a threshold
   sits where it should.
4. State your **n** and your confidence. A ceiling from four stages in one
   session is a low-confidence tripwire, and saying so is what keeps it a
   conversation rather than a budget.

Consider a **secondary all-in tripwire** with rework charged to process — that
is the one that notices double-launches without punishing a round for having
reviewers.

### What this ratio must never be used for

The process seats are the ones that catch blockers before they land. A high
ratio is a signal to look at **orchestration shape** — duplicate launches,
dataless writers, scouts re-deriving what a report already holds — and **never a
licence to cut adversarial review**, and never a reason to reshape the product.

If you only ever report a cost number, cutting review will always look like
progress. That is why the escape rate is published beside it: one number goes
down when you cut corners, the other goes up, and you need both on the same page
to see it happening.

## Methodology

<Say exactly how to re-derive every number above: the source files, the query,
the date. A ledger nobody can re-derive is a ledger nobody can dispute, and a
number nobody can dispute is a number nobody should trust.>
