<!--
TEMPLATE - the punch list / decision list. Copy per round to
{{REPORTS_DIR}}/../punch-lists/PUNCH-<yyyy-mm-dd>-<round>.md
SLOTS: {{PROJECT_NAME}} {{OWNER_ROLE}} {{REPORTS_DIR}} {{LEDGERS_DIR}}

WHY THIS FILE EXISTS: every charter in this module demands one. The implementer
charter says "the verbatim ask"; the reviewer charter is onboarded from "the
verbatim punch list + rulings + the diff" and is explicitly forbidden the
implementer's report; the judgment ledger's first column is the ruling text.
All three assumed a document that the kit never shipped, so each round invented
its own shape and the reviewer's "verbatim" was whoever's paraphrase arrived.

Delete this comment block on adoption.
-->

# PUNCH LIST — {{PROJECT_NAME}} — round <n>, <date>

**Source:** <where these came from: a drive, a session, a bug report, a review>
**Captured by:** <who typed it> · **Captured:** <when, relative to the session>

> **Capture verbatim. Invent nothing.** {{OWNER_ROLE}}'s words are the
> specification. A paraphrase silently narrows a request to what the paraphraser
> understood, and nobody can tell afterwards that it happened. Quote first;
> interpret in a separate, labelled field.

---

## Part 1 — ITEMS, as reported

One row per item. Numbered, because everything downstream cites these numbers —
the triage, the rulings, the dispositions, the ledger rows.

| # | Verbatim | Evidence | First read |
|---|---|---|---|
| 1 | *"<their exact words, uncompressed>"* | <screenshot / log line / commit / timestamp> | <your one-line interpretation, clearly YOURS> |
| 2 | | | |

**"First read" is not the spec.** It is your guess at what they meant, kept
beside the words rather than replacing them, so a later reader can see where a
misunderstanding entered.

---

## Part 2 — TRIAGE (investigation round output — no fixing yet)

Each item gets exactly one verdict. The vocabulary is the scout charter's,
because the same taxonomy has to survive from investigation to ledger.

| # | Verdict | Evidence for the verdict | Est. |
|---|---|---|---|
| 1 | REGRESSED · NEVER-SHIPPED · NEVER-WORKED · FIXED-THE-FLOOR-NOT-THE-COMPLAINT · NEW-ASK · NEEDS-REPRO | `file:line`, sha, log line | S/M/L |

**Before triage, run the backtest:** for each item, ask *should an existing
check have caught this?* If yes it is an **ESCAPE** — record it in the escape
log and fix the check alongside the code. The escape rate is the number this
whole apparatus is trying to move.

| # | Escape? | Which check should have caught it | Why it did not |
|---|---|---|---|
| 1 | yes/no | `<check name>` | wrong surface · floor too low · never ran on this path |

---

## Part 3 — DECISION LIST (numbered, with a lean on every line)

{{OWNER_ROLE}} rules in batches. Make that cheap: number the decisions, state a
recommendation on **every** one, and leave a column they can mark.

| # | Decision | Options | **Lean, and why** | Ruling |
|---|---|---|---|---|
| D1 | <the question, in one sentence> | A: … · B: … | **A** — <the reason, one sentence> | |

A decision with no lean is analysis handed back. If you genuinely have no
preference, say *why* it is genuinely their call (taste, money, priorities) —
that is a lean too, and a useful one.

---

## Part 4 — DISPOSITIONS (filled at close; none may be blank)

**Every item from Part 1 appears here. A silent skip is the betrayal.** The
reader must never have to re-derive the list to find out what happened to it.

| # | Disposition | Landed in | Enforcing check | Ledger row |
|---|---|---|---|---|
| 1 | DONE · NOT DONE + reason · OUT OF SCOPE + owner · SUPERSEDED by D<n> | `file:line` | `<gate/case/rule id>` or UNCHECKED + reason | JUDGMENT-LEDGER ✓ |

**Round totals:** items <n> · escapes <n> of <n> · halts raised <n> ·
UNCHECKED closures <n>

Zero halts across a phase is a finding, not a success. Publish the escape rate
in the stage report whether it moved or not.

---

## How this file is used, and by whom

| Seat | Reads | Never sees |
|---|---|---|
| investigator / scout | Parts 1–2 | — |
| {{OWNER_ROLE}} | Part 3 | — |
| implementer | Parts 1, 3 (rulings) | — |
| **reviewer** | Parts 1 and 3, plus the diff | **the implementer's report** — that is the point of spec-side onboarding |
| ledger maintainer | Parts 3–4 | — |

Because the reviewer is onboarded from this document, **its accuracy is a
verification property, not a clerical one.** A punch list that quietly drifts
toward what got built is a reviewer briefed by the thing they are reviewing.

Archive the closed list next to the round's report in `{{REPORTS_DIR}}`, and
land its rulings in `{{LEDGERS_DIR}}/JUDGMENT-LEDGER.md` in the same commit as
the checks they name.
