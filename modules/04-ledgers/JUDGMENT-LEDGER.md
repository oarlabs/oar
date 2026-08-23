<!--
SKELETON - copy to {{LEDGERS_DIR}}/JUDGMENT-LEDGER.md and start appending on
the first ruling. Slots: {{PROJECT_NAME}} {{OWNER_ROLE}} {{LEDGERS_DIR}}
Delete this block on adoption.
-->

# {{PROJECT_NAME}} — The Judgment Ledger

**What this is.** {{OWNER_ROLE}} rules; a round implements; a later round can
quietly undo it. This ledger maps every **owner ruling** — a product decision a
human made — to the **named executable check** that would go red if the ruling
were inverted.

**What this is not.** Operating-process rules (model tiering, permissions, stage
hygiene) live in `FAILURE-FLOOR.md`, which audits *rule → enforcement layer*.
Where a product ruling is *also* enforced by a row there, this ledger
cross-references it rather than restating it. Two documents, two questions:
*what did they decide, and what holds it?* versus *what do we require of
ourselves, and what makes us?*

**The doctrine.** Every ruling becomes a permanent check, or it is written down
here as **UNCHECKED** with the reason and the shape the check would take.
Silence is the failure mode: **a ruling that lives only in prose is a ruling the
next round inverts in equally good faith.** Nobody is careless in that story.
That is exactly why prose is not enough.

**The escape-rate connection.** An item reported by a human that an existing
check *should have caught* is an **escape**. Escapes are the project's real
quality metric — not the size of the suite. Every row below whose status is
UNCHECKED is a *pre-declared* escape: if it comes back, the ledger said so
first, and that is a much cheaper conversation than a surprise.

## Status legend

| Status | Meaning |
|---|---|
| **CHECKED** | A named executable check exists and would fail on inversion. Name it precisely — the gate, the case ID, the rule code, the proof step. |
| **UNCHECKED** | The ruling landed; nothing would catch a future inversion. Reason given, plus the shape the check would take. |
| **PENDING** | Ruled, not yet implemented (awaiting a batch, or awaiting the owner). |
| **SUPERSEDED** | Reversed or narrowed later — citation given. Marked **in place**; rows are never deleted. |
| **ORACLE-DECLINED** | Not a ruling row: a check this round was offered and chose **not** to build, recorded as a bet. The row shape is module 01's, under WHEN THE LOOP ENDS, rule 7 — that clause is the authority and this legend describes it rather than redefining it. It is written in this table's own four columns: the first cell carries the literal `ORACLE-DECLINED:` then the class of finding the check would have covered and the check's shape in one line; **Landed in** carries `round <n>`; **Enforcing check** carries `not built: <why not now>; trigger: <what would build it>`; **Status** is `ORACLE-DECLINED`. A later finding of that class is attributed to the round that declined. |

### What "attributed to the round that declined" means, and how a bet closes

Two mechanics that rule 7 states as a consequence and this ledger has to make
usable. Both are **conventions of citation, not new metrics**: nothing here
changes the escape rate, and `escape_rate.py` neither reads nor counts an
ORACLE-DECLINED row.

- **A finding of a declined class is not an escape.** An escape is an item an
  existing check *should have caught*, and a declined class has no check by
  construction — calling it an escape would make the number mean two things.
  It is a **coverage gap with a named owner**. What "attributed" requires is
  one sentence in the finding's own register entry: cite the declining round's
  ORACLE-DECLINED row. The bet's cost then accumulates where anyone reading
  that class can see it, and the round that took it is named every time.
- **A bet closes two ways, both marked in place.** The check is later
  **built** — the row becomes `SUPERSEDED`, citing the new check, the same way
  every other reversal is marked. Or a later round is offered the same class
  and **declines it again** — that round appends its own ORACLE-DECLINED row
  and holds the bet from then on, and the older row becomes `SUPERSEDED`
  citing the newer one. A bet nobody closes stays open, which is the correct
  reading of a class still uncovered.

## Maintenance rule (binding)

Every round's **oracle-manufacture step** appends its rows here **in the same
commit that lands the round's checks** — ruling text (verbatim where possible),
where it landed, the check's *name*, and the status. A round that lands a ruling
without a check appends an UNCHECKED row and a backlog entry; it does not stay
silent. Rows are never deleted; a reversal is marked SUPERSEDED in place with
the citation.

Check names must match the gate/case/rule identifiers the verification module
uses. A renamed check silently orphans every row that cited it.

---

## Round / batch: <name> — <date> (source: <verbatim punch list or ruling doc>)

| Ruling (verbatim where possible) | Landed in | Enforcing check | Status |
|---|---|---|---|
| *"<their exact words>"* | `path/to/file.ext:LINE` | `<gate>` → `<case/rule id>` | **CHECKED** |
| *"<their exact words>"* | — (triaged to a lane that was held) | — | **PENDING** — unowned since <date> |
| *"<their exact words>"* | `path/to/file.ext:LINE` | **Nothing.** The behaviour is real but nothing asserts it. | **UNCHECKED** — see backlog #1 |
| ORACLE-DECLINED: <the class of finding it would cover> — <the check's shape, one line> | round <n> | not built: <why not now>; trigger: <what would build it> | **ORACLE-DECLINED** |

---

## Backlog — the UNCHECKED rows, with the check each one needs

| # | Ruling | Why it is unchecked | Proposed check | Est. cost |
|---|---|---|---|---|
| 1 | <ruling> | <the honest reason: too expensive, no oracle yet, needs a harness that does not exist> | <shape, from ORACLE-WORKSHEET> | <hours> |

## Escape log — items an existing check should have caught

| Round | Item | The check that should have caught it | Why it did not | Fixed by |
|---|---|---|---|---|
| <r> | <item> | `<check>` | <the honest gap: wrong surface, floor too low, check ran but not on this path> | <the new/repaired check> |

## Escape rate — the published number

**This table is machine-read.** `escape_rate.py` computes the rate from it,
the verify runner's `escapes` gate judges the result, and the number is
printed on every certification. Its first three columns are fixed; `Notes` is
for you. Append one row per round, in the same commit as that round's checks,
and never edit an old row to make a number look better — a metric you can
improve by editing history is not a metric.

An **escape** is an item a human reported that an existing check should have
caught. A defect on a surface no check covered is a *coverage gap*, not an
escape: the honest response to a coverage gap is a new check, not a worse
number. `Items` is every finding the round dispositioned, including the ones
rejected below the materiality bar — a finding you decided not to fix is
still a finding somebody had to make.

`-` in **both** count cells declares a round uncountable: the record exists
but per-round counts cannot be recovered from it. The tool excludes it from
the denominator and prints how many rounds that hid, every run, so dropping a
round is a visible act. `-` in one cell only is an error, not a shortcut.

| Round | Items | Escapes | Notes |
|---|---|---|---|

**Start it empty.** Until the first row lands, the gate prints
`state NO-ROUNDS-RECORDED` on every certification — the true state of a new
project, published rather than dressed up as a zero. If it does not fall
across rounds, the loop is witnessing, not learning.

Run it yourself at any time:

```bash
python tools/escape_rate.py --ledger docs/JUDGMENT-LEDGER.md
python tools/escape_rate.py --ledger docs/JUDGMENT-LEDGER.md --json
```

## Where the checks live

<Fill in: which file holds test cases, which holds lint rules, which holds
proof steps, and what the ID conventions are. A reader who finds a check name in
a row above must be able to locate it in under a minute — otherwise the row is
decoration.>
