<!--
SKELETON - copy to {{LEDGERS_DIR}}/LESSONS.md.
Slots: {{PROJECT_NAME}} {{OWNER_ROLE}} {{REPORTS_DIR}} {{LEDGERS_DIR}}
Delete this block on adoption.
-->

# {{PROJECT_NAME}} — Lessons Learned

A living distillation of what this project learned the hard way, written so a
future seat — human or model, with **zero context** — repeats the wins and not
the tuition. Sources: every stage report in `{{REPORTS_DIR}}`, the decisions
log, and the ledgers.

**This document is law.** The standing rules point at it and every session
inherits it.

## Status vocabulary

Every numbered item carries a `Status:` marker.

- **BINDING** — the default, and **the only status an agent may ever write**.
  The lesson is law; a session that ignores it pays the tuition a second time.
- **BINDING — DEMOTION CANDIDATE** — a *proposal*, not a change in force. The
  item is still fully binding; it is nominated for review at the next phase
  gate because a later lesson, or an enforcement layer built since, appears to
  cover it entirely.
- **RETIRED** / **SUPERSEDED** — applied **only** by {{OWNER_ROLE}}'s ruling at
  a phase-gate demotion review (`FAILURE-FLOOR.md` → Demotion review). No agent
  and no coordinator retires a lesson. Nothing here goes quiet silently.

## How to write one

Each item, in this order and no longer than it needs to be:

1. **A bolded imperative sentence.** The lesson, phrased as the thing to do or
   not do. Someone skimming reads only these, so they have to work alone.
2. **The concrete incident**, with numbers. *"A comparator kept only
   `{`-prefixed lines and silently discarded ~260 runtime errors per run —
   three stages of 'clean' results carried invisible errors."* Numbers are what
   make a lesson survive being retold.
3. **Where it was earned** — the stage, round, or date.
4. **The generalisation**, one sentence, if it has one.
5. `*Status: BINDING.*`

**Write the lesson, not the incident.** "Be careful with the cache" is a mood.
"A green result from a cache that was never invalidated is the same shape as a
green result from correct code — assert the cache generation in the check" is a
lesson.

**Every lesson should eventually become a row in `FAILURE-FLOOR.md`** or be
consciously accepted as prose there. Lessons are the input to promotion; the
failure floor is the record of what promotion did.

---

## 1. <Theme — e.g. verification>

1. **<Imperative sentence.>** <The incident, with numbers.> (<where earned>)
   *Status: BINDING.*

2. **<Imperative sentence.>** <Incident.> (<where earned>)
   *Status: BINDING.*

## 2. <Theme — e.g. orchestration>

3. **<Imperative sentence.>** <Incident.> (<where earned>)
   *Status: BINDING.*

## 3. <Theme — e.g. tooling and environment>

4. **<Imperative sentence.>** <Incident.> (<where earned>)
   *Status: BINDING — DEMOTION CANDIDATE.* <Which layer now covers it, and why
   the item is nominated for review rather than retired here.>

---

## Seed lessons — earned in the reference build, portable as-is

Delete any that do not apply. Renumber into your themes above. Each of these
cost real money somewhere; they are offered as a starting floor, not as
decoration.

- **A gate that has never been red is unproven.** Prove every check red before
  you count on it, and prove it *without editing a repo file* — an edit-based
  negative control is one forgotten revert from becoming permanent.
  *Status: BINDING.*
- **"The check did not run" and "the check passed" must never look the same.**
  Give subset runs their own verdict and their own exit code.
  *Status: BINDING.*
- **A harness will happily prove that two sides do nothing identically.** Assert
  *did-something* counters (deliveries > 0, cases > 0, events > 0) before any
  "identical" verdict is trusted. Five separate passing runs in the reference
  build tested nothing at all.
  *Status: BINDING.*
- **Audit the harness itself.** A comparator that silently discards output it
  does not recognise turns three clean stages into three stages of invisible
  errors. Comparators fail loudly on anything unexpected.
  *Status: BINDING.*
- **Defensive improvements are parity defects.** In a port or a rewrite, an
  added bounds guard that "obviously" improves the original changes behaviour
  something depended on. Statement-for-statement means porting the ugly parts.
  *Status: BINDING.*
- **A synthesis prompt with no interpolated data produces a confident,
  fluent, entirely invented document.** It happened twice in one day in the
  reference build for a measured ~297k tokens of rework, *after* the rule
  against it was written. The structural fix is two-sided: a pre-launch check on
  the launcher, and a HALT guard as the first line of every writer charter.
  *Status: BINDING.*
- **An agent permitted to fix while it investigates will always find the problem
  it can already solve.** Investigation rounds are execution-free by charter.
  *Status: BINDING.*
- **Stage targeted paths, always — never `git add -A` or `git add .`.** Not
  "not while an agent is in flight": never. The narrower rule invited the
  judgement call ("nothing is running, so this is fine"), and the judgement was
  wrong at least once. A blanket add sweeps somebody's scratch file into your
  commit and you find out three commits later.
  *Status: BINDING.*
- **Retrospective prose hallucinates exactly like a model does.** A confident
  wrong number, once written, gets cited by the next document. Every numeric
  claim in a report cites a primary source or is labelled UNVERIFIED.
  *Status: BINDING.*
- **Certification is a property of a TREE, not of a commit.** A green run over a
  dirty judge surface certifies nothing.
  *Status: BINDING.*
- **A precise alarm and a loud alarm are different requirements, and you need
  both.** An over-firing gate gets skimmed, and a skimmed gate is a dead gate —
  the reference build's own tier gate blocked its own documentation minutes
  after birth because its pattern was unanchored.
  *Status: BINDING.*
