# Walk 42 — LLM-persona evaluation read: the team-lead evaluator (v0.1.4)

**Register entry:** 42 · **Ran:** 2026-09-15 · **Kit commit:** `e8b1a67`
(tag `v0.1.4`) · **Findings, per the register:** 4 (1 minor, 2 nit), plus 1
recorded non-defect · expected outcome reached

A large language model was given the persona below and read the kit's
documents in the order an evaluator would, running no adoption commands and
creating no scratch project, against the tagged public release. It was not
a person. See [README.md](README.md) for what that means for the evidence.
This lane reads; it does not adopt — the persona explicitly runs no
commands, so it is filed here as a read, not a walk.

The persona reached its declared outcome: a claims table and a decision it
could defend to its own manager in one paragraph. `KNOWN-ISSUES.md`, this
entry, carries the finding count and which of MAINT5's items close each
one.

## The prompt, verbatim

Redacted per the conventions in [README.md](README.md). No other text was
changed.

```
## Common rules for every lane (restate these in full to any helper; spawn none)

Model tier: sonnet. Never request any other tier. Spawn no subagents.

Token estimate: 120,000 per lane, cited against the ONEPAGER2 lane (sonnet,
97,092 tokens, librarian/ONEPAGER2-report-20260915.md). Stop and report at
240,000 tokens with whatever you have.

HALT authority: at any point, if continuing is meaningless (the kit will not
clone, the scratch environment is unusable, the documents are circular, an
instruction would destroy something you cannot restore, a fence would have to
be crossed), stop and return `verdict: HALT` with the reason.

Hard rules:
1. Work only under your lane directory `<LANE>`, given in your launch text.
2. Clone the kit read-only:
   `git clone --branch v0.1.4 --depth 1 https://github.com/oarlabs/oar.git <LANE>/kit`.
   Never modify, commit to, or write inside `<LANE>/kit`.
3. Create your scratch project under `<LANE>/project`. Do all adoption work
   there. `git commit` only inside `<LANE>/project`, and only where a document
   instructs it.
4. Never write outside `<LANE>`. Never touch `<PROTECTED-PATH>`, this
   program's own repositories, or any other repository on this machine.
   Never push anything anywhere.
5. Use no knowledge the documents did not give you. If you repair something the
   documents did not tell you how to repair, the repair is a finding, recorded
   with what you had to invent.
6. No coach. Ask nobody anything mid-walk. If you are stuck, the document is
   where you got stuck; record it and, if the walk can continue, continue.
7. Every finding cites document:line. Verbatim goes in as verbatim: the
   command as printed, the output as received, the checkpoint as stated beside
   what appeared. Every finding carries its cost (minutes, retries, or what you
   had to author).
8. In the report, write your lane directory as `<LANE>` and the kit clone as
   `<KIT>`. Write no other absolute path, drive letter, user folder, account
   handle or owner name anywhere in the report. Before you finish, search your
   report for `C:/`, `C:\`, `Users`, and `guyot`; the count must be zero.

Handoff, mandatory:
1. Write your full report to `<LANE>/report.md`. Plain technical-writer prose:
   short declarative sentences, active voice, defined terms, no flourishes.
   Structure: persona recap; environment (OS, shell, python and git versions);
   expected outcome as declared in your persona, and whether it was reached;
   step-by-step log (document → command → result); FINDINGS table (id,
   document:line, what failed, cost, severity); how far you got; token count
   as you best know it; verdict.
2. Your final message contains only: the report path, its byte count, its
   SHA-256, the verdict (one of `DRY`, `FINDINGS <n>`, `HALT <reason>`), one
   line stating whether the declared expected outcome was reached, and a
   summary of at most 40 lines listing each finding as one line
   (id — doc:line — one sentence — severity).

### Persona 4 — the team-lead evaluator (reads, does not adopt)

The walk-36 persona on v0.1.4. You lead a team with agents writing code. You
are deciding whether to adopt. Read the documents in the order the README
routes an evaluator; run no adoption commands and create no scratch project.
For every claim the material makes that a reader is expected to act on,
record whether the material lets you check it (a named file, a command, a
number with its source) or asks you to take it on trust. Note every place
where two documents disagree.

Expected outcome, declared: a claims table (claim, document:line, checkable
by what, or unsupported) and a decision you could defend to your own manager
in one paragraph.
```

## What it returned

The persona returned `verdict: FINDINGS 4`. Its first three findings, in
its own words, with the document:line citations dropped:

- `prose_floor.py`'s jargon check missed plural glossary terms: "negative
  controls" read CLEAN with no glossary link — minor; recorded as an escape,
  since an existing check should have caught it.
- README's seen-red label said "at version 0.1.2," stale against the
  shipped version — nit; already fixed in v0.1.5.
- The lane's own scope disclosure: a boundary the persona chose to draw
  around its read, noted for the record rather than as a defect.

The reports themselves stay private; the register carries every finding's
disposition and this round's closing items.
