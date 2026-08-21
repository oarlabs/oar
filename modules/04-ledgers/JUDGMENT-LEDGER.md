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

---

## Backlog — the UNCHECKED rows, with the check each one needs

| # | Ruling | Why it is unchecked | Proposed check | Est. cost |
|---|---|---|---|---|
| 1 | <ruling> | <the honest reason: too expensive, no oracle yet, needs a harness that does not exist> | <shape, from ORACLE-WORKSHEET> | <hours> |

## Escape log — items an existing check should have caught

| Round | Item | The check that should have caught it | Why it did not | Fixed by |
|---|---|---|---|---|
| <r> | <item> | `<check>` | <the honest gap: wrong surface, floor too low, check ran but not on this path> | <the new/repaired check> |

**Escape rate this round: N of M items.** Publish it every round. If it does
not fall across rounds, the loop is witnessing, not learning.

## Where the checks live

<Fill in: which file holds test cases, which holds lint rules, which holds
proof steps, and what the ID conventions are. A reader who finds a check name in
a row above must be able to locate it in under a minute — otherwise the row is
decoration.>
