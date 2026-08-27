# Module 04 — Ledgers

Four documents that stop the project's memory living in one person's head, and
one small tool that turns the headline number in one of them into a check.

## Files

| File | The question it answers |
|---|---|
| `JUDGMENT-LEDGER.md` | *What did the owner decide, and what would go red if we undid it?* Ruling → named check, or UNCHECKED + reason. Carries the escape log and the machine-read escape-rate table. |
| `FAILURE-FLOOR.md` | *What do we require of ourselves, and what actually enforces it?* Rule → layer + zone + last-fired + residual. Carries the demotion review. |
| `LESSONS.md` | *What did we learn the hard way?* Numbered, status-marked, each earned somewhere specific. Ships with thirteen portable seed lessons. |
| `TOKEN-LEDGER.md` | *What did it cost, and how much of that was ceremony?* Actuals, the process/implementation ratio, the rework column, and how to derive a ceiling instead of adopting one. |
| `escape_rate.py` | *Is the loop learning, or only witnessing?* The one executable in this module. It computes the escape rate from the table in `JUDGMENT-LEDGER.md`, prints a required output line, holds the latest round to a ceiling, and refuses to guess: a missing ledger, a missing table or a malformed row is an ABORT, never a zero. Zero dependencies, and a `--selftest` whose forced-red controls cover every refusal it makes. |

## Vocabulary: "stage", "round" and "phase", defined once

These three words appear throughout the kit and are used precisely. Everything
else references this definition rather than restating it.

- A **round** is one full pass of the delivery loop: the owner reports or
  requests, the work is chartered and done, checks are manufactured, and the
  result is certified. A round is the unit that produces an *escape rate*.
- A **stage** is one chartered unit of work *inside* a round — an
  investigation, a fix pass, a design pass, a review. A stage is the unit that
  gets a **ledger row**, a report, and a stage-close checklist run.
- A **phase** is the largest unit: one or more rounds delivering one milestone,
  ending at a **phase gate** where the owner rules on what ships. Two policies
  key off it — the demotion review below and the distill-then-prune transcript
  retention in `CONTEXT-ARCHITECTURE.md` §3. If your project has no grouping
  above the round, read "phase" as "round" throughout; both policies still work.

So: one phase contains one or more rounds, one round contains one or more
stages, and neither smaller unit ever spans two of the larger. When a rule says
"three stages without firing" (the demotion review) it means three chartered
units of work, not three rounds — that threshold is deliberately shorter than
it sounds.

If your project's cadence does not fit this shape, redefine the words here in
one place and leave every other document pointing at it. What must not happen
is two documents meaning different things by "stage" while both look right.

## Why four documents and not one

They answer different questions on different clocks, and merging them produces a
document nobody updates:

- the judgment ledger grows on every **ruling**;
- the failure floor changes when a **rule fails** or a gate is built;
- lessons grow when **a failure costs something**;
- the token ledger grows at every **stage close**.

The one hard boundary: **product rulings go in the judgment ledger, process
rules go in the failure floor.** Cross-reference; do not restate. When both
documents describe the same rule, one of them will drift, and you will not know
which.

## File contract with other modules

- **← 01-governance.** The stage-close checklist names all four by path and
  makes appending to them a step, not a virtue. The promotion/demotion rule is
  stated there and *lives* here.
- **← 03-verification.** Check names in `JUDGMENT-LEDGER.md` must match gate,
  case, and rule identifiers in the verify runner. A renamed check silently
  orphans every row that cited it, and orphaned rows are worse than absent ones
  because they read as coverage.
- **→ 03-verification.** The runner ships an `escapes` gate that runs
  `escape_rate.py` over `JUDGMENT-LEDGER.md`. Two constants in `verify.py`,
  `ESCAPE_TOOL` and `ESCAPE_LEDGER`, name them; the **ceiling** is a literal
  in the gate entry, inside `JUDGE_PATHS`, so raising it is a reviewed commit
  rather than a config edit. The ledger itself is deliberately **not** in
  `JUDGE_PATHS` — it is the subject the gate measures, and judging it would
  make every ordinary append invalidate certification. If you adopt this
  module without module 03, the tool still runs standalone; if you adopt
  module 03 without this one, delete the `escapes` gate as its own docstring
  instructs.
- **← 02-enforcement.** Every hook rule should be a row in `FAILURE-FLOOR.md`
  with its layer, zone and last-fired date. That row is where the demotion
  review finds it.
- **→ 08-collaboration.** `LESSONS.md` accumulates evidence about how the owner
  works; the profile in module 08 is where a *repeated* observation graduates
  from a lesson to a default.

## What breaks if you adopt this module alone

Nothing. Four markdown skeletons and their maintenance rules work as documents
in any project, with any tooling, with no agents involved at all. This is the
cheapest module to adopt and — measured by how much it changes what a team
notices about itself — plausibly the highest-yield. `escape_rate.py` runs
standalone too: `python escape_rate.py --ledger <your ledger>` needs nothing
but stock Python and prints the same number a gate would.

The coupling only appears when you *also* have module 03: then check names
become load-bearing, and the ledger stops being a diary and starts being an
index.

## Adaptation notes

- **Copy the four ledgers by name, not with a glob.** This directory also
  contains its own `README.md`; `cp modules/04-ledgers/*.md docs/` will silently
  overwrite a `docs/README.md` you already had.
- **Start them on day one, empty.** A ledger begun in month three is a ledger
  reconstructed from memory, and reconstruction is where confident wrong numbers
  are born.
- **Verbatim beats tidy.** Quote the owner's actual words in the ruling column.
  A paraphrase silently narrows the ruling to what the paraphraser understood,
  and nobody can tell later that it happened.
- **UNCHECKED rows are the point, not an embarrassment.** They are pre-declared
  escapes. A ledger with no UNCHECKED rows is a ledger someone is curating.
- **Publish the escape rate and the ratio in the same stage report.** One goes
  down when you cut corners and the other goes up; either alone can be gamed
  without noticing you are doing it.
