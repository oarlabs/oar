# `sidequest.json` — the file contract

The one coupling surface between the sidequest skill (module 06) and the status
board (module 05). Both sides are written against **this document**, not against
each other, which is why either module can be adopted alone.

## Location

`{{PROJECT_ROOT}}/{{SIDEQUEST_FLAG}}` — default `.claude/sidequest.json`.

**Gitignore it. This rule is load-bearing twice over.**

1. It is *session* state, not *tree* state. Committing it means a colleague's
   checkout claims to be on your detour.
2. **It sits inside `.claude/`, which is very often inside a project's
   `JUDGE_PATHS` or `CERT_PATHS`.** If it is not ignored, then merely *opening a
   side quest* leaves an untracked file in a certified path, the verification
   module's `judges` gate correctly goes red, and the project cannot certify
   until the quest closes. Two modules that never import each other, coupled
   through one line of `.gitignore` — so it is written down on both sides
   (module 05's README says the same thing from the reader's end).

```gitignore
.claude/sidequest.json
```

## Schema — all five fields, no extras

```json
{
  "slug": "kebab-case-quest-name",
  "started": "2026-08-19",
  "ask": "a short verbatim fragment of the request that opened the quest",
  "doc": "docs/SIDEQUEST-2026-08-19-kebab-case-quest-name.md",
  "mainline_resume": "one line: the exact next main-line action"
}
```

| Field | Type | Rules |
|---|---|---|
| `slug` | string, kebab-case | Matches the snapshot document's slug. The board renders it verbatim, so keep it short and legible. |
| `started` | `yyyy-mm-dd` | The day the quest **opened**. Drives the day counter and the staleness amber. The fork day is day 1. |
| `ask` | string | A verbatim fragment of the request, for the record. Not rendered on the board. |
| `doc` | repo-relative path | The snapshot document. Must exist before this file does. |
| `mainline_resume` | string | The next main-line action. **Truncated to ~44 characters on the board — front-load it.** It is the "what you are NOT doing right now" reminder, and the useful half must survive the truncation. |

**No extra fields.** The board renders a fixed set; anything else is invisible
and will drift out of date, which is worse than absent because someone will
eventually read it and believe it.

## Lifecycle — who writes, who deletes

| Moment | Actor | Action |
|---|---|---|
| Quest opens, **after** the snapshot document is on disk | the sidequest skill, step 1b | **CREATE** |
| During the quest | nobody | The file is not edited. A quest whose resume line changed has changed scope: re-charter, do not patch the flag. |
| Quest closes, **after** the durable record is written | the sidequest skill, step 4 | **DELETE** |

**Existence is the entire state machine.** Present means forked; absent means
main line. There is no `"status": "closed"` field, deliberately — a status field
creates a state where the file exists and lies, and the whole value of the
banner rests on it never lying.

Corollary, and it is load-bearing: **a banner still showing means the quest is
still open.** That is the intended reading, so the file is deleted at close and
at no other time — never "to tidy up" mid-quest, never before the durable record
is on disk.

## Reader contract (the status board)

The board **only reads**, and it degrades in exactly three defined ways:

| Situation | Board behaviour |
|---|---|
| File absent | No banner. One `Test-Path` on the main-line path — the common case is the cheap case. |
| File present and valid | Coloured banner: slug, day counter, truncated resume line. |
| File present, unparseable, or missing `slug` | **A loud "state file unreadable" banner.** Never silence. |

That last row is the one people get wrong. Silence on a corrupt flag asserts
"you are back on the main line" — a silent lie, in exactly the situation where
you most need the truth.

## The staleness amber

Past `{{SIDEQUEST_STALE_DAYS}}` days the banner changes to an amber field and
appends `· STALE`.

A side quest that has quietly become the main line is a fact the board should
state, not a fact you should be expected to notice. The day counter alone is a
number people stop reading by day four — which is precisely when it starts
mattering.

The amber is **informational, not enforcing**: long quests are legitimate. It
exists so that when someone finally asks "wait, what happened to the main line?"
the board has been answering that question in colour for three days.

## Adopting one side without the other

- **Board without the skill:** write the file by hand, or delete the banner
  block. Nothing else on the board depends on it.
- **Skill without the board:** the skill still writes and deletes the flag; you
  simply lose the ambient reminder. Everything durable — the snapshot document,
  the exit criteria, the close record — is unaffected.
