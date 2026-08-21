---
name: sidequest
description: Fork the session into a bounded side quest without losing the main-line context — snapshot the main work first, charter the quest with exit criteria, run it under the standing rules, and close back onto the main line explicitly. Use when the owner says "side quest", "detour", "pause that and…", or makes any bounded ask that is not the current phase's work.
---

<!--
TEMPLATE. Copy to your harness's skill directory (for Claude Code:
.claude/skills/sidequest/SKILL.md).
SLOTS: {{KNOWLEDGE_DIR}} {{SIDEQUEST_FLAG}} {{REPORTS_DIR}}
       {{OWNER_ROLE}} {{FORBIDDEN_SPAWN_TIER}} {{LANE_TIER}} {{CERT_PATHS}}
Delete this comment on adoption.
-->

# /sidequest — a bounded detour with a guaranteed return

**Why this exists.** A side quest that starts without a snapshot ends with
"wait, where were we?" — and the answer gets *reconstructed from memory* instead
of *read from a file*. Reconstruction is where pending decisions quietly
disappear: not the work, which is in git, but the queue of things waiting on a
human, which lives nowhere else.

The cost is asymmetric and that is the whole argument. Writing the snapshot
takes five minutes. Losing the awaiting-decisions list costs a round.

## On invoke — with the ask as `$ARGUMENTS`

### Step 1 — SNAPSHOT THE MAIN LINE FIRST, before any side-quest work

Write `{{REPORTS_DIR}}/../SIDEQUEST-<yyyy-mm-dd>-<slug>.md` containing:

- **Main-line state, one paragraph.** Current phase, tree and certification
  state (sha + the verify summary line), what is in flight, and the exact next
  main-line action.
- **AWAITING DECISION** — every pending question or ruling, verbatim where
  possible. **This list is the single most loss-prone asset in a context
  switch.** Capture it completely; it is the reason this step exists.
- **THE ASK, verbatim** — the request that opened the quest, uncompressed, in
  their words.
- **EXIT CRITERIA** — what "done" means, as checkable statements. Plus an
  explicit **scope fence**: what this quest may touch, and specifically whether
  `{{CERT_PATHS}}` are in bounds, because touching them invalidates the
  certification token and prices a re-certification into the quest.
- **CONTEXT CAPSULE** — the minimum a *fresh* session or subagent would need to
  run this quest: file pointers, prior decisions that bind it, and which
  documents are its sources. Written so the quest is **delegable**, even if this
  session runs it. If the capsule cannot carry the quest, the quest is not
  delegable — and knowing that is itself the useful output of writing it.
  The capsule is one instance of the general rule (BLUEPRINT §7): nothing
  crosses a context boundary except what was written for the crossing — side
  quests are one boundary; session clears and lane spawns are the others.

### Step 1b — RAISE THE FLAG

Write `{{SIDEQUEST_FLAG}}` (gitignored — session state, not tree state). Its
**existence** is the sidequest bit; the status board renders a banner while it
is present and nothing at all when it is absent.

Schema and lifecycle: **`CONTRACT.md` in the status-board module is
authoritative.** All five fields, no extras. `slug` matches the Step-1
document's slug; `started` is the fork date and drives the day counter and the
staleness amber; `mainline_resume` is truncated on the board, so front-load it.

### Step 2 — CHOOSE THE VEHICLE (recommend, do not ask, unless it is genuinely their call)

- **In-session** (default). Right when the quest needs this session's
  accumulated context, or when {{OWNER_ROLE}} is actively steering.
- **Delegated.** Spawn it, onboarded from the **CONTEXT CAPSULE alone**, with an
  explicit tier (`{{LANE_TIER}}`; never `{{FORBIDDEN_SPAWN_TIER}}`). Right when
  the quest is self-contained and the main line should keep moving in parallel.
  The capsule **is** the charter.

### Step 3 — RUN under the standing rules

Everything in the standing rules document binds inside a side quest: tiering,
the HALT guard, targeted adds, spec-side reviewers for anything that becomes a
judge, no certified paths without naming the re-certification cost.

**A side quest is a stage, not an exemption.** It gets the full stage-close
checklist: report → evidence → ledger row → commit → push → dashboard refresh →
lessons refresh.

### Step 4-GATE — the owner closes the quest, not the coordinator

Before ANY close action: present the close summary and ask, in so many words, *"Is this
quest done, or are you still holding items?"* The knowledge-base capture and the flag
drop happen only AFTER the owner's explicit sign-off. "Looks done to the coordinator"
is not a close — the owner may hold validation questions the coordinator cannot see.
(This gate exists because the reference build's first quest was closed on looks-done
while the owner still held two validation items, and had to be reopened.)

## Step 4 — CLOSE BACK ONTO THE MAIN LINE, explicitly

- Append a **CLOSED** section to the snapshot document: what shipped (with
  shas), what was deliberately not done, and any new pending decisions the quest
  generated.
- **Write the durable record (Step 4b)** — before the flag drops.
- **LOWER THE FLAG:** delete `{{SIDEQUEST_FLAG}}`. This single act flips the
  board back to the main line, so it happens at close and nowhere else — never
  "to tidy up" mid-quest, never before the durable record is on disk. A banner
  still showing means the quest is still open; that is the intended reading.
- **Re-read the AWAITING DECISION list from Step 1** and restate it, merged with
  anything new. **The main line resumes from the written queue, never from
  memory of it.** This is the step the whole skill exists to guarantee.
- State the next main-line action from the Step-1 snapshot, verbatim.

### Step 4b — THE DURABLE RECORD

Write one new file into the durable knowledge store — the copy that outlives the
repository and the session:

```
{{KNOWLEDGE_DIR}}/sidequests/SIDEQUEST-<yyyy-mm-dd>-<slug>.md
```

`<yyyy-mm-dd>` is the date the quest **opened**, so the record, the repo
document and the banner all name the same quest.

Required contents, **in order — this is a log, not a summary. Capture verbatim,
invent nothing:**

1. **Frontmatter** — title, type, opened, closed, session id, repo, and the list
   of shas the quest shipped.
2. **THE ASK, verbatim**, as recorded at Step 1.
3. **The main-line snapshot as it stood at the fork** — *copied* from the Step-1
   document, not re-derived. This is what makes the record readable a year
   later, and re-deriving it silently updates it to the world as it is now.
4. **What shipped** — commits (sha + subject), files changed with paths, and the
   reports produced.
5. **The report-out, verbatim** — the text as delivered at close, unedited.
6. **New pending decisions** the quest generated, merged into the awaiting list.
7. **Session log** — pointers, not copies: the stage reports, the agent
   observability record, the ledger rows.

## Rules

- **Never start Step 3 before Step 1 is on disk.** The snapshot is the whole
  point; a quest that skipped it has already lost the thing it was protecting.
- The flag is written at 1b and deleted at 4, **never in between**.
- **No durable record, no close.** A quest that skipped Step 4b is still open.
- **One side quest at a time.** A side quest inside a side quest is a HALT and
  a conversation.
- **If the quest grows past its exit criteria, stop and re-charter.** Scope
  growth inside a detour is how main lines die — quietly, with everyone busy.
