# Module 06 — Sidequest

A bounded detour with a guaranteed return, and a durable record of both.

## Files

| File | What it is |
|---|---|
| `SKILL.md` | The `/sidequest` skill: snapshot-first, flag lifecycle, vehicle choice, run-under-the-standing-rules, explicit close, durable record. |

## The problem it solves

Interruptions are not the problem — they are normal, and often correct. The
problem is that **the work survives an interruption and the queue does not.**
Code is in git. Reports are on disk. The list of things waiting on a human
decision lives in exactly one place: the working memory of the session that is
about to be replaced.

So the skill's first act is to write that list down, and its last act is to read
it back out loud. Everything in between is scaffolding for those two moments.

## The five load-bearing decisions

1. **Snapshot before anything.** Never start the quest before the snapshot is on
   disk. A quest that skipped it has already lost the thing the snapshot was
   protecting, and nobody notices until the return.
2. **Existence is the state machine.** The flag file is present or absent;
   there is no status field. A status field creates a state where the file
   exists and lies, and the banner's entire value rests on it never lying.
3. **The context capsule is a delegability test.** Writing "what a fresh session
   would need" tells you whether the quest can be handed off *before* you spend
   a lane's budget discovering it cannot.
4. **A side quest is a stage, not an exemption.** Same standing rules, same
   stage-close checklist. Detours are exactly where discipline is most tempting
   to skip and most expensive to have skipped.
5. **The durable record is written before the flag drops.** A quest that
   "finished" but has no record is a quest that will be re-litigated, and the
   ordering is what makes that structural rather than aspirational.

## File contract with other modules

- **↔ 05-statusboard** via `CONTRACT.md`, which is authoritative for the flag
  schema and lifecycle. The skill **writes and deletes**; the board **only
  reads**. Neither imports the other.
- **← 01-governance.** Step 3 defers wholesale to the standing rules and the
  stage-close checklist rather than restating them — a restatement is a copy
  that will drift.
- **`kit.config`** supplies `{{KNOWLEDGE_DIR}}`, `{{SIDEQUEST_FLAG}}`,
  `{{CERT_PATHS}}` and the tier names.

## What breaks if you adopt this module alone

Nothing. Without module 05 you lose the ambient banner — the flag is still
written and deleted, it simply has no reader. Everything durable (snapshot,
exit criteria, close record) is unaffected.

With `KNOWLEDGE_DIR = NONE`, fold Step 4b into the repo document. You lose the
copy that outlives the repository, which matters more than it sounds when the
repository is archived and the question comes back two years later.

## Adaptation notes

- **No skill mechanism in your harness?** This is a checklist. Put it in your
  standing rules under "when interrupted" and follow it by hand; every step
  works without automation.
- **Tune the vehicle default.** Solo work: in-session. A team with parallel
  capacity: delegate more, and let the capsule quality decide.
- **The staleness amber lives in the board, not here** — deliberately. The skill
  should not be in the business of judging how long a quest is allowed to run;
  the board just makes the duration impossible to overlook.
